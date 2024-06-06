import pandas as pd
import numpy as np
import requests
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score
from joblib import dump

# URLs of the datasets on GitHub
benign_url = "https://raw.githubusercontent.com/forta-network/labelled-datasets/main/labels/1/benign_token_contracts.csv"
malicious_url = "https://raw.githubusercontent.com/forta-network/labelled-datasets/main/labels/1/malicious_smart_contracts.csv"


# Function to download CSV file from GitHub
def download_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        response.raise_for_status()


# Download datasets
benign_df = download_csv(benign_url)
malicious_df = download_csv(malicious_url)

# Combine datasets
benign_df["label"] = 0
malicious_df["label"] = 1
df = pd.concat([benign_df, malicious_df], ignore_index=True)

# Extract opcodes (assuming a column 'opcodes' contains the opcode sequences)
opcodes = df["opcodes"].tolist()
labels = df["label"].tolist()

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(ngram_range=(1, 4), token_pattern=r"\b\w+\b")

# Transform opcodes into numerical features
X = tfidf.fit_transform(opcodes)
y = np.array(labels)

# Initialize SGD Classifier
model = SGDClassifier(loss="log_loss", random_state=42)

# Cross-validation
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
precision_scores = []
recall_scores = []
f1_scores = []

for train_index, test_index in kf.split(X, y):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    precision_scores.append(precision_score(y_test, y_pred))
    recall_scores.append(recall_score(y_test, y_pred))
    f1_scores.append(f1_score(y_test, y_pred))

# Calculate average scores
avg_precision = np.mean(precision_scores)
avg_recall = np.mean(recall_scores)
avg_f1 = np.mean(f1_scores)

print(f"Average Precision: {avg_precision}")
print(f"Average Recall: {avg_recall}")
print(f"Average F1-Score: {avg_f1}")

# Save the model
model_path = "malicious_token_model_06_06_24_exp6.joblib"
dump(model, model_path)
print(f"Model saved to {model_path}")
