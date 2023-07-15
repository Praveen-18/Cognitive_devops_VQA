import cv2
from torchvision.models import resnet50
import torch
import torch.nn as nn
from torchvision.transforms import transforms
import pickle
import collections

pickle_file = "VQA/VQA_Image_Classifier/image_classifier.pkl"
qa_file = "VQA/VQA_Image_Classifier/q&a_pair.txt"

# Load the QA pairs
qa_pairs = collections.defaultdict(list)

with open(qa_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
        image_name, question, answer = line.strip().split("|")
        qa_pairs[image_name.lower()].append((question, answer))


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


def classify_image(image_path,question):
    with open(pickle_file, 'rb') as f:
        rf_classifier = pickle.load(f)

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image_transforms(image).unsqueeze(0)
    image = image.to(device)
    with torch.no_grad():
        features = feature_extractor(image)
        features = features.view(features.size(0), -1).cpu().numpy()
    predicted_label = rf_classifier.predict([features.flatten()])[0]
    print(predicted_label)
    return answer_question(predicted_label, question)


def answer_question(image_name, question):
    key = image_name.lower()
    if key in qa_pairs:
        for question1, answer1 in qa_pairs[key]:
            if question1.lower() == question.lower():
                return answer1
    return "Sorry, I don't have an answer for that question."
