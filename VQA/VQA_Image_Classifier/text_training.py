import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Load and preprocess the dataset
print("Loading and preprocessing the dataset...")
data = pd.read_csv('test_dataset.txt', delimiter='|', header=None)
data.columns = ['classname', 'question', 'answer']

# Feature engineering and extraction
print("Performing feature extraction...")
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['question'] + ' ' + data['classname'])
y = data['answer']

# Train the machine learning model
print("Training the model...")
model = RandomForestClassifier()
model.fit(X, y)

# Save the trained model and vectorizer
print("Saving the trained model and vectorizer...")
with open('model1.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('vectorize1.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("Training and saving the model complete.")
