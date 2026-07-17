import os
import argparse
import torch
from torch import nn, optim
import helper_utils
from model import MyModel
from dataset import QuickDrawDataset, SubsetQuickDraw

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--root_dir", type=str, default="dataset")
    parser.add_argument("--save_path", type=str, default="checkpoints")

    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=30)
    
    parser.add_argument("--val_factor", type=float, default=0.1)
    parser.add_argument("--test_factor", type=float, default=0.1)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--dropout", type=float, default=0.3)

    parser.add_argument("--pin_memory", type=bool, default=False)

    return parser.parse_args()

def main():
    args = get_args()
    
    root_dir = args.root_dir
    batch_size = args.batch_size
    num_workers = args.num_workers
    pin_memory = args.pin_memory
    dropout = args.dropout
    epochs = args.epochs
    save_path = args.save_path
    lr = args.lr
    val_factor = args.val_factor
    test_factor = args.test_factor

    dataset = QuickDrawDataset(root_dir)
    train_dataset, val_dataset, test_dataset = helper_utils.create_data_splits(dataset, val_factor, test_factor)
    print(f"Lenght of train dataset:            {len(train_dataset)}")
    print(f"Length of val dataset:              {len(val_dataset)}")
    print(f"Length of test dataset:             {len(test_dataset)}")
    mean, std = helper_utils.get_mean_std(dataset)
    print(f"Mean of dataset: {mean.tolist()}")
    print(f"Std of dataset: {std.tolist()}")
    train_transform, val_transform = helper_utils.define_transform(mean, std)
    train_dataset = SubsetQuickDraw(train_dataset, train_transform)
    val_dataset = SubsetQuickDraw(val_dataset, val_transform)
    test_dataset = SubsetQuickDraw(test_dataset, val_transform)

    train_loader, val_loader, test_loader = helper_utils.get_data_loader(train_dataset, val_dataset, test_dataset, batch_size, pin_memory, num_workers)
    print("Create dataloader successfully!")

    num_classes = len(dataset.classes)
    model = MyModel(num_classes=num_classes, dropout=dropout)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max")
    loss_fn = nn.CrossEntropyLoss()
    history = helper_utils.train(model=model, optimizer=optimizer, loss_fn=loss_fn,
                                        train_loader=train_loader, val_loader=val_loader,
                                        epochs=epochs, scheduler=scheduler, save_path=save_path)
    helper_utils.plot_history(history)
    results = helper_utils.evaluate(model, test_loader, test=True)
    print(results)

if __name__ == "__main__":
    main()
    
    