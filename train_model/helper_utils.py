from tqdm.auto import tqdm
import os
import time
import json
import torch 
from torch import nn, optim
from torch.utils.data import random_split, DataLoader, Dataset
from torchvision import transforms
import matplotlib.pyplot as plt
import numpy as np
import cv2
from sklearn.metrics import confusion_matrix
import seaborn as sns

def create_data_splits(dataset, val_factor, test_factor):
    length = len(dataset)
    val_size = int(length * val_factor)
    test_size = int(length * test_factor)
    train_size = length - (val_size + test_size)
    train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])
    return train_dataset, val_dataset, test_dataset

def get_mean_std(dataset: Dataset):
    transform = transforms.ToTensor()
    total_pixels = 0
    sum_pixels = torch.zeros(3)
    mean_loader = tqdm(dataset, desc="Pass 1/2: Computing Mean")
    for img, _ in mean_loader:
        img_processed = transform(img)
        pixels = img_processed.view(3, -1) # [channels, pixels]
        sum_pixels += pixels.sum(dim=1)
        total_pixels += pixels.size(1)
    mean = sum_pixels / total_pixels
    sum_squared_diff = torch.zeros(3)
    std_loader = tqdm(dataset, desc="Pass 2/2: Computing Std")
    for img, _ in std_loader:
        img_processed = transform(img)
        pixels = img_processed.view(3, -1) # [channels, pixels]
        diff = pixels - mean.unsqueeze(1)
        sum_squared_diff += (diff ** 2).sum(dim=1)
    std = torch.sqrt(sum_squared_diff / total_pixels)
    return mean, std

def define_transform(mean, std):
    train_transform = transforms.Compose([transforms.RandomHorizontalFlip(0.3),
                                          transforms.RandomVerticalFlip(0.3),
                                          transforms.RandomRotation(10),
                                          transforms.ColorJitter(0.2, 0.2),
                                          transforms.ToTensor(),
                                          transforms.Normalize(mean, std)])
    val_transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize(mean, std)])
    return train_transform, val_transform

def get_data_loader(train_dataset, val_dataset, test_dataset, batch_size):
    train_loader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size)
    val_loader = DataLoader(val_dataset, shuffle=False, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, shuffle=False, batch_size=batch_size)
    return train_loader, val_loader, test_loader

def compute_p_r_f1(num_classes, tp_per_cls, fp_per_cls, fn_per_cls, epsilon=1e-8):
    precisions, recalls, f1s = [], [], []
    for c in range(num_classes):
        tp = tp_per_cls[c]
        fp = fp_per_cls[c]
        fn = fn_per_cls[c]
        p = tp / (tp + fp + 1e-8) 
        r = tp / (tp + fn + 1e-8)  
        f1 = (2 * p * r) / (p + r + epsilon)
        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)
    macro_precision = sum(precisions) / num_classes
    macro_recall    = sum(recalls)    / num_classes
    macro_f1 = sum(f1s) / num_classes
    return macro_precision, macro_recall, macro_f1

def train(model, optimizer, loss_fn, train_loader, val_loader, epochs, device, scheduler, save_path, epsilon=1e-8):
    model = model.to(device)
    best_val_acc = 0
    total_time = 0
    num_classes = model.num_classes
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": [],
               "train_precision": [], "val_precision": [], "all_preds": [], "actuals": [],
               "train_recall": [], "val_recall": [], "train_f1": [], "val_f1": []}
    os.makedirs(save_path, exist_ok=True)
    best_save_path = os.path.join(save_path, "best.pth")
    last_save_path = os.path.join(save_path, "last.pth")
    his_save_path = os.path.join(save_path, "history.json")
    for epoch in range(epochs):
        start = time.time()
        model.train()
        running_loss, running_correct, running_total = 0, 0, 0
        epoch_time = 0
        tp_per_cls = {k: 0 for k in range(num_classes)}
        fp_per_cls = {k: 0 for k in range(num_classes)}
        fn_per_cls = {k: 0 for k in range(num_classes)}
        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Training]", leave=False)
        for images, labels in train_pbar:
            images = images.to(device)
            labels = labels.to(device)   
            optimizer.zero_grad()
            output = model(images)
            loss = loss_fn(output, labels)
            loss.backward()
            optimizer.step()

            running_total += labels.size(0)
            running_loss += loss.item() * images.size(0)
            _, prediction = output.max(1)
            running_correct += (prediction == labels).sum().item()

            # Calculate Precision Recall
            for act, pred in zip(labels, prediction):
                if act == pred:
                    tp_per_cls[act.item()] += 1
                else:
                    fp_per_cls[pred.item()] += 1
                    fn_per_cls[act.item()] += 1

        epoch_train_loss = running_loss / len(train_loader.dataset)
        epoch_train_acc = running_correct / running_total
        train_p, train_r, train_f1 = compute_p_r_f1(num_classes, tp_per_cls, fp_per_cls, fn_per_cls)
        
        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        tp_per_cls = {k: 0 for k in range(num_classes)}
        fp_per_cls = {k: 0 for k in range(num_classes)}
        fn_per_cls = {k: 0 for k in range(num_classes)}
        val_pbar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Validating]", leave=False)
        with torch.no_grad():
            for images, labels in val_pbar:
                images = images.to(device)
                labels = labels.to(device) 
                output = model(images)

                loss = loss_fn(output, labels)
                val_loss += loss.item() * images.size(0)

                _, prediction = output.max(1)
                val_total += labels.size(0)
                val_correct += (prediction == labels).sum().item()

                # Calculate Precision Recall
                for act, pred in zip(labels, prediction):
                    if act == pred:
                        tp_per_cls[act.item()] += 1
                    else:
                        fp_per_cls[pred.item()] += 1
                        fn_per_cls[act.item()] += 1
                
                # Save log to calc confusion matrix
                history["all_preds"].append(prediction)
                history["actuals"].append(labels)
        end = time.time()
        epoch_time = (end - start) / 60
        total_time += epoch_time
        epoch_val_loss = val_loss / len(val_loader.dataset)
        epoch_val_acc = val_correct / val_total
        val_p, val_r, val_f1 = compute_p_r_f1(num_classes, tp_per_cls, fp_per_cls, fn_per_cls)

        print(f"Epoch {epoch+1}/{epochs} | "
            f"Train Loss={epoch_train_loss:.4f} "
            f"Val Loss={epoch_val_loss:.4f} | "
            f"Train Acc={epoch_train_acc:.4f} "
            f"Val Acc={epoch_val_acc:.4f} | "
            f"Train P={train_p:.4f} "
            f"Val P={val_p:.4f} | "
            f"Train R={train_r:.4f} "
            f"Val R={val_r:.4f} | "
            f"Train F1={train_f1:.4f} "
            f"Val F1={val_f1:.4f} | "
            f"Time - {epoch_time:.2f} minutes")
        
        history["train_loss"].append(epoch_train_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_loss"].append(epoch_val_loss)
        history["val_acc"].append(epoch_val_acc)
        history["train_precision"].append(train_p)
        history["val_precision"].append(val_p)
        history["train_recall"].append(train_r)
        history["val_recall"].append(val_r)
        history["train_f1"].append(train_f1)
        history["val_f1"].append(val_f1)

        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save(model.state_dict(), best_save_path)
            print(f"Best model is saved at epoch {epoch+1}")
            
        torch.save(model.state_dict(), last_save_path)

        if scheduler is not None:
            if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(epoch_val_acc)
            else:
                scheduler.step()

    history["all_preds"] = torch.cat(history["all_preds"]).tolist()
    history["actuals"] = torch.cat(history["actuals"]).tolist()
    with open(his_save_path, "w") as f:
        json.dump(history, f)
    
    print(f"Spended {total_time} to training model.")
    print(f"Model is saved at {save_path}.")
    print(f"History log is saved at {his_save_path}.")
    return history


def plot_history(history):
    train_loss = history["train_loss"]
    val_loss = history["val_loss"]
    p_train = history["train_precision"]
    p_val = history["val_precision"]
    r_train = history["train_recall"]
    r_val = history["val_recall"]
    f1_train = history["train_f1"]
    f1_val = history["val_f1"]
    train_acc = history["train_acc"]
    val_acc = history["val_acc"]
    all_preds = np.array(history["all_preds"])
    actuals = np.array(history["actuals"])
    epochs = [i+1 for i in range(len(train_loss))]

    fig, ax = plt.subplots(2, 3, figsize=(36, 20))

    # Loss
    idx = np.argmin(val_loss)
    min_epoch = epochs[idx]
    min_val = val_loss[idx]
    ax[0, 0].plot(epochs, train_loss, label="Train Loss")
    ax[0, 0].plot(epochs, val_loss, label="Val Loss")
    ax[0, 0].annotate(text=f"Min Val Loss at\n(Epoch: {min_epoch}, Loss: {min_val:.4f})",
                 xy=(min_epoch, min_val), textcoords="offset points",
                 xytext=(20, 20), arrowprops=dict(arrowstyle="->", color="red"),
                 fontsize=10, color="red")
    ax[0, 0].set_title("Training Loss & Validation Loss")
    ax[0, 0].set_xlabel("Epoch")
    ax[0, 0].set_ylabel("Loss")
    ax[0, 0].legend()

    # Accuracy
    idx = np.argmax(val_acc)
    best_epoch = epochs[idx]
    best_val = val_acc[idx]
    ax[0, 1].plot(epochs, train_acc, label="Train Acc")
    ax[0, 1].plot(epochs, val_acc, label="Val Acc")
    ax[0, 1].scatter(best_epoch, best_val, s=50)
    ax[0, 1].annotate(
        f"Best Val Acc\n({best_epoch}, {best_val:.4f})",
        xy=(best_epoch, best_val),
        xytext=(20, 20),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="red"),
        color="red")
    ax[0, 1].set_title("Training Accurcay & Validation Accurcay")
    ax[0, 1].set_xlabel("Epoch")
    ax[0, 1].set_ylabel("Accuracy")
    ax[0, 1].legend()

    # Precision
    idx = np.argmax(p_val)
    best_epoch = epochs[idx]
    best_val = p_val[idx]
    ax[0, 2].plot(epochs, p_train, label="Train Precision")
    ax[0, 2].plot(epochs, p_val, label="Val Precision")
    ax[0, 2].scatter(best_epoch, best_val, s=50)
    ax[0, 2].annotate(
        f"Best Val Precision\n({best_epoch}, {best_val:.4f})",
        xy=(best_epoch, best_val),
        xytext=(20, 20),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="red"),
        color="red")
    ax[0, 2].set_title("Training Precision & Validation Precision")
    ax[0, 2].set_xlabel("Epoch")
    ax[0, 2].set_ylabel("Precision")
    ax[0, 2].legend()

    # Recall
    idx = np.argmax(r_val)
    best_epoch = epochs[idx]
    best_val = r_val[idx]
    ax[1, 0].plot(epochs, r_train, label="Train Recall")
    ax[1, 0].plot(epochs, r_val, label="Val Recall")
    ax[1, 0].scatter(best_epoch, best_val, s=50)
    ax[1, 0].annotate(
        f"Best Val Recall\n({best_epoch}, {best_val:.4f})",
        xy=(best_epoch, best_val),
        xytext=(20, 20),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="red"),
        color="red")
    ax[1, 0].set_title("Training Recall & Validation Recall")
    ax[1, 0].set_xlabel("Epoch")
    ax[1, 0].set_ylabel("Recall")
    ax[1, 0].legend()

    # F1
    idx = np.argmax(f1_val)
    best_epoch = epochs[idx]
    best_val = f1_val[idx]
    ax[1, 1].plot(epochs, f1_train, label="Train F1")
    ax[1, 1].plot(epochs, f1_val, label="Val F1")
    ax[1, 1].scatter(best_epoch, best_val, s=50)
    ax[1, 1].annotate(
        f"Best Val F1\n({best_epoch}, {best_val:.4f})",
        xy=(best_epoch, best_val),
        xytext=(20, 20),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="red"),
        color="red")
    ax[1, 1].set_title("Training F1 & Validation F1")
    ax[1, 1].set_xlabel("Epoch")
    ax[1, 1].set_ylabel("F1")
    ax[1, 1].legend()

    # CM
    cm = confusion_matrix(actuals, all_preds)
    sns.heatmap(cm, 
        annot=True,
        fmt='g',
        annot_kws={"size": 7},        
        linewidths=0.5,               
        cmap="Blues",                 
        ax=ax[1, 2])
    ax[1, 2].set_ylabel('Actual', fontsize=11)
    ax[1, 2].set_title('Confusion Matrix', fontsize=14, pad=20)
    ax[1, 2].xaxis.set_label_position('top')
    ax[1, 2].set_xlabel('Prediction', fontsize=11)
    ax[1, 2].xaxis.tick_top()
    ax[1, 2].tick_params(axis='x', labelsize=7, rotation=90) 
    ax[1, 2].tick_params(axis='y', labelsize=7, rotation=0)

    plt.tight_layout()
    plt.show()

def preprocess(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_inv = cv2.bitwise_not(gray)
    dist = cv2.distanceTransform((gray_inv > 0).astype(np.uint8), cv2.DIST_L2, 5)
    mean_thickness = np.mean(dist[dist > 0])
    if mean_thickness < 2:  
        kernel = np.ones((7, 7), np.uint8)
        gray_inv = cv2.dilate(gray_inv, kernel, iterations=1)
    coords = np.where(gray_inv > 20)
    if len(coords[0]) == 0:
        print("Not found drawing in the image")
        return None, None
    y_min, y_max = np.min(coords[0]), np.max(coords[0])
    x_min, x_max = np.min(coords[1]), np.max(coords[1])
    cropped = gray_inv[y_min:y_max + 1, x_min:x_max + 1]
    h, w = cropped.shape
    diff = abs(h - w)
    pad1, pad2 = diff // 2, diff - diff // 2
    if h > w:
        squared = np.pad(cropped, ((0, 0), (pad1, pad2)), constant_values=0)
    else:
        squared = np.pad(cropped, ((pad1, pad2), (0, 0)), constant_values=0)
    margin = int(squared.shape[0] * 0.15)
    padded = np.pad(squared, ((margin, margin), (margin, margin)), constant_values=0)
    resized = cv2.resize(padded, (64, 64), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
    return rgb

def inference(img_path, model, device):
    img = preprocess(img_path)
    trans = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize([0.1577, 0.1577, 0.1577], [0.3355, 0.3355, 0.3355])])
    class_names = [
        "Apple", "Bowtie", "Circle", "Cloud", "Cup",
        "Diamond", "Fish", "Guitar", "Hat", "Headphones",
        "Ladder", "Laptop", "Leaf", "Moon", "Pants",
        "Pencil", "Smiley Face", "Soccer Ball", "Sock",
        "Star", "Sun", "T-Shirt", "Triangle",
        "Watermelon", "Wine Glass"
    ]
    img = trans(img)
    img = img.unsqueeze(0)
    model.to(device)
    img = img.to(device)
    model.eval()
    softmax = nn.Softmax()
    with torch.no_grad():
        preds = model(img)[0]
        preds = softmax(preds)
        idx_max = torch.argmax(preds)
        best_logit = preds[idx_max]
        categorical = class_names[idx_max]
    return best_logit, categorical


            
