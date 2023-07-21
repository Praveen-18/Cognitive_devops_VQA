import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from torchvision.models import resnet50
import torch
import torch.nn as nn
from torchvision.transforms import transforms
import joblib
import collections
import tempfile
import pickle
from collections import OrderedDict


# Paths to your joblib files
pickle_file_1 = "VQA/VQA_Image_Classifier/image_classifier1.joblib"
pickle_file_2 = "VQA/VQA_Image_Classifier/image_classifier2.joblib"


# Initialize the feature extractor
feature_extractor = resnet50(pretrained=True)
feature_extractor = nn.Sequential(*list(feature_extractor.children())[:-1])
feature_extractor.eval()

# Set device for feature extraction
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
feature_extractor.to(device)

# Define the image transformation pipeline for feature extraction
image_transforms = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def answer_question(image_name, question):
    new_question = question
    new_classname = image_name

    # Load the trained model
    print("Loading the trained model...")
    with open('VQA/VQA_Image_Classifier/model1.pkl', 'rb') as f:
        loaded_model = pickle.load(f)

    # Load the fitted vectorizer from the training phase
    print("Loading the fitted vectorizer...")
    with open('VQA/VQA_Image_Classifier/vectorize1.pkl', 'rb') as f:
        vectorizer = pickle.load(f)


    # Transform the input question and class name
    new_input = vectorizer.transform([new_question + ' ' + new_classname])

    # Retrieve the answer using the trained model
    print("Retrieving the answer...")
    predicted_answer = loaded_model.predict(new_input)

    print(f"Question: {new_question}")
    print(f"Class name: {new_classname}")
    print(f"Predicted answer: {predicted_answer[0]}")
    return predicted_answer[0]


def classify_image(image_path , question):
    with open(pickle_file_1, 'rb') as f:
        model1_classifier = joblib.load(f)

    with open(pickle_file_2, 'rb') as f:
        model1_classifier = joblib.load(f)

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image_transforms(image).unsqueeze(0)
    image = image.to(device)

    with torch.no_grad():
        features = feature_extractor(image)
        features = features.view(features.size(0), -1).cpu().numpy()
    predicted_label1 = model1_classifier.predict([features.flatten()])[0]
    predicted_label1 = predicted_label1.lower()
    predicted_label1 = answer_question(predicted_label1, question)
    if predicted_label1 != "Sorry, not trained.":
        return predicted_label1
    else:
        return "no"


