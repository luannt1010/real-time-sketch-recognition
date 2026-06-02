import cv2
import numpy as np
import torch
from torchvision import transforms

def preprocess(img):
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

def define_transform():
    mean = torch.tensor([0.1577, 0.1577, 0.1577])
    std = torch.tensor([0.3355, 0.3355, 0.3355])
    trans = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize(mean, std)])
    return trans