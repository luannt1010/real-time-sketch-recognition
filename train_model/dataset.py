import os
import random
from PIL import Image
from torch.utils.data import Dataset, Subset
import helper_utils

class QuickDrawDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        super().__init__()

        self.root_dir = root_dir
        self.transform = transform
        self.classes = sorted(os.listdir(self.root_dir))
        self.class2idx = self.create_class2idx()
        self.images, self.labels = self.get_all_images()

    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        cls = self.labels[idx]
        img_processed = helper_utils.preprocess(img_path)
        img = Image.fromarray(img_processed).convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        return img, cls


    def create_class2idx(self):
        res = {}
        for i, cls in enumerate(self.classes):
            if cls not in res:
                res[cls] = i
        return res

    def get_all_images(self):
        images, labels = [], []
        for cls in self.classes:
            path = os.path.join(self.root_dir, cls)
            for img in os.listdir(path):
                if img.lower().endswith((".png", ".jpg", ".jpeg")):
                    images.append(os.path.join(path, img))
                    labels.append(self.class2idx[cls])
        return images, labels

class SubsetQuickDraw(Dataset):
    def __init__(self, subset: Subset, transform=None):
        self.subset = subset
        self.transform = transform
        
    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        img, cls = self.subset[idx]
        if self.transform is not None:
            img = self.transform(img)
        return img, cls
