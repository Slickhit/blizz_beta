import csv
import os
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'intents.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'intent_clf.joblib')


def load_dataset(path: str = DATA_PATH) -> Tuple[List[str], List[str]]:
    texts, labels = [], []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row['text'])
            labels.append(row['intent'])
    return texts, labels


def train_model(texts: List[str], labels: List[str]) -> Pipeline:
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(max_iter=1000)),
    ])
    pipe.fit(texts, labels)
    return pipe


def train_and_save(model_path: str = MODEL_PATH) -> Pipeline:
    texts, labels = load_dataset()
    model = train_model(texts, labels)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    return model


if __name__ == '__main__':
    train_and_save()
