import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from torchvision.models import resnet50
import torch
import torch.nn as nn
from torchvision.transforms import transforms
import joblib

# Define the dataset path and pickle file path
dataset_path = "ezyzip (3)"
pickle_file = "image_classifier2.joblib"
print("OK")
# Initialize the feature extractor
feature_extractor = resnet50(pretrained=True)
feature_extractor = nn.Sequential(*list(feature_extractor.children())[:-1])
feature_extractor.eval()
print("OK")
# Set device for feature extraction
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
feature_extractor.to(device)
print("OK")
# Define the image transformation pipeline for feature extraction
image_transforms = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
print("OK")
# Define the number of samples to use for training
max_samples = 1600

X = []  # Features
y = []  # Labels
print("OK")
# Iterate through the dataset and collect features and labels
for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".png"):
            image_path = os.path.join(root, file)
            print("Processing image:", image_path)
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image_transforms(image).unsqueeze(0)
            image = image.to(device)
            with torch.no_grad():
                features = feature_extractor(image)
                features = features.view(features.size(0), -1).cpu().numpy()
            X.append(features.flatten())
            y.append(file.split(".")[0])

# Convert X and y to numpy arrays
X = np.array(X)
y = np.array(y)
print("OK")
# Limit the number of samples for faster training
if len(X) > max_samples:
    indices = np.random.choice(len(X), size=max_samples, replace=False)
    X = X[indices]
    y = y[indices]
print("OK")
print("Number of images:", len(X))
print("Number of labels:", len(y))

rf_classifier = RandomForestClassifier(n_estimators=100, n_jobs=-1)
print("Training started")
rf_classifier.fit(X, y)
print("Training completed")

# Save the trained model as a joblib file
with open(pickle_file, 'wb') as f:
    joblib.dump(rf_classifier, f)

print("Classifier saved to {}".format(pickle_file))

def classify_image(image_path):
    with open(pickle_file, 'rb') as f:
        rf_classifier = joblib.load(f)

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image_transforms(image).unsqueeze(0)
    image = image.to(device)
    with torch.no_grad():
        features = feature_extractor(image)
        features = features.view(features.size(0), -1).cpu().numpy()
    predicted_label = rf_classifier.predict([features.flatten()])[0]
    return predicted_label

print("OK")