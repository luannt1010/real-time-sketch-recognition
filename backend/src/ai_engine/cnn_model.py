import torch
import torch.nn as nn
from .model_architecture import MyModel

def get_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MyModel(25)
    state_dict_path = r"YOUR PATH OF WEIGHT"
    state_dict = torch.load(state_dict_path, map_location=device)
    model.load_state_dict(state_dict)
    return model

def inference(model, tensor):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tensor = tensor.unsqueeze(0)
    tensor = tensor.to(device)
    model = model.to(device)
    model.eval()
    sm = nn.Softmax()
    labels = [
        "Apple", "Bowtie", "Circle", "Cloud", "Cup",
        "Diamond", "Fish", "Guitar", "Hat", "Headphones",
        "Ladder", "Laptop", "Leaf", "Moon", "Pants",
        "Pencil", "Smiley Face", "Soccer Ball", "Sock",
        "Star", "Sun", "T-Shirt", "Triangle",
        "Watermelon", "Wine Glass"
    ]
    with torch.no_grad():
        preds = model(tensor)[0]
        preds = sm(preds)
        idx_max = torch.argmax(preds)
        best_logit = torch.max(preds)
        label = labels[idx_max.item()]
    return label, best_logit.item()
