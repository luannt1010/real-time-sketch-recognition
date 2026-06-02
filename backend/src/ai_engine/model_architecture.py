from torch import nn

class CNNBlock(nn.Module):
    def __init__(self, in_channels, out_channels, skip_connection=False):
        super().__init__()

        self.conv1 = nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False),
                                   nn.BatchNorm2d(out_channels))
        self.conv2 = nn.Sequential(nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False),
                                   nn.BatchNorm2d(out_channels))
        self.relu = nn.ReLU()
        self.max_pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.skip_connection = skip_connection
        if self.skip_connection:
            self.shortcut = self.make_shortcut(in_channels, out_channels) if in_channels != out_channels else nn.Identity()
    
    def make_shortcut(self, in_channels, out_channels):
        return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
                             nn.BatchNorm2d(out_channels))
        
    def forward(self, x):
        identity = x
        x = self.conv1(x)
        x = self.relu(x)
        x = self.conv2(x)
        if self.skip_connection:
            x += self.shortcut(identity)
        x = self.relu(x)
        x = self.max_pool(x)
        return x 


class MyModel(nn.Module):
    def __init__(self, num_classes, dropout=0.3):
        super().__init__()
        self.block1 = CNNBlock(in_channels=3, out_channels=32, skip_connection=True)
        self.block2 = CNNBlock(in_channels=32, out_channels=64, skip_connection=True)
        self.block3 = CNNBlock(in_channels=64, out_channels=128, skip_connection=True)
        self.num_classes = num_classes
        self.dropout = dropout
        self.classifier = nn.Sequential(nn.Flatten(), 
                                        nn.Linear(128*8*8, 512), nn.ReLU(), nn.Dropout(self.dropout), 
                                        nn.Linear(512, 256), nn.ReLU(), nn.Dropout(self.dropout), 
                                        nn.Linear(256, self.num_classes))
    
    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.classifier(x)
        return x
