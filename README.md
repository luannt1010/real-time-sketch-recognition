# Hand Drawing Recognition System

## Overview

Hand Drawing Recognition System is a web-based application that allows users to draw simple sketches on a digital canvas and receive real-time predictions from a deep learning model.

The system integrates a React frontend, a Django REST API backend, and a custom Convolutional Neural Network (CNN) built with PyTorch. Users can also submit feedback when the prediction is incorrect, helping improve future versions of the model.


## Features

* Draw objects directly on an interactive canvas
* Real-time image classification
* Confidence score display
* Inference time measurement
* Feedback collection system
* Camera-based drawing recognition
* Responsive web interface


## Technology Stack

### Frontend

* React
* JavaScript
* Framer Motion

### Backend

* Django
* Django REST Framework

### Deep Learning

* PyTorch
* OpenCV
* NumPy
* Pillow

### Database

* SQLite


## Dataset Classes

The model is trained to recognize the following 25 classes:

* ["Apple", "Bowtie", "Circle", "Cloud", "Cup",
  "Diamond", "Fish", "Guitar", "Hat", "Headphones",
  "Ladder", "Laptop", "Leaf", "Moon", "Pants",
  "Pencil", "Smiley Face", "Soccer Ball", "Sock",
  "Star", "Sun", "T-Shirt", "Triangle",
  "Watermelon", "Wine Glass"]


# Model Architecture

The recognition model is a custom CNN architecture enhanced with residual (skip) connections.

## CNN Block

Each CNN block consists of:

* Convolution Layer (3×3)
* Batch Normalization
* ReLU Activation
* Convolution Layer (3×3)
* Batch Normalization
* Residual Skip Connection
* ReLU Activation
* Max Pooling (2×2)

### Block Structure

Input → Conv → BN → ReLU → Conv → BN → Skip Connection → ReLU → MaxPool


## Network Architecture

Input Image: 64 × 64 × 3

### Feature Extractor

Block 1:

* Input Channels: 3
* Output Channels: 32

Block 2:

* Input Channels: 32
* Output Channels: 64

Block 3:

* Input Channels: 64
* Output Channels: 128

Output Feature Map:

128 × 8 × 8


### Classifier

Flatten

→ Linear(8192 → 512)

→ ReLU

→ Dropout(0.3)

→ Linear(512 → 256)

→ ReLU

→ Dropout(0.3)

→ Linear(256 → Number of Classes)


## Model Summary

| Layer       | Output Size  |
| ----------- | ------------ |
| Input       | 3 × 64 × 64  |
| CNN Block 1 | 32 × 32 × 32 |
| CNN Block 2 | 64 × 16 × 16 |
| CNN Block 3 | 128 × 8 × 8  |
| Flatten     | 8192         |
| FC1         | 512          |
| FC2         | 256          |
| Output      | Num classes  |


## Project Structure

```text
project/
│
├── frontend/
│   ├── src/
│   └── public/
│
├── backend/
│   ├── src/  
│   │   ├── config/
│   │   ├── recognition/
│   │   ├── ai_engine/
│   │   │   ├── model_weights/
│   │   │   ├── cnn_model.py
│   │   │   ├── preprocess.py
│   │   │   ├── camera_service.py
│   │   │   └── model_architecture.py
│   │   │
│   │   ├── manage.py
│   └───└── db.sqlite3
│
└── README.md
```


## Installation

### Clone Repository

```bash
git clone <repository-url>
cd project
```


## Backend Setup

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Linux / MacOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Run Django server:

```bash
python manage.py runserver
```

Backend will be available at:

```text
http://localhost:8000
```


## Frontend Setup

Navigate to frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run development server:

```bash
npm run dev
```

Frontend will be available at:

```text
http://localhost:5173
```


## Future Improvements

* Data augmentation pipeline
* Transfer learning using ResNet
* Online model retraining from feedback
* Deployment on cloud platforms
* User authentication system
* Model performance dashboard


## Author

Developed as a Deep Learning and Computer Vision project using PyTorch, Django, and React.
