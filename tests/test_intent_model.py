import os
from ml import train, predict


def test_intent_training_and_prediction(tmp_path):
    model_path = os.path.join(tmp_path, 'model.joblib')
    data_path = os.path.join(os.path.dirname(train.__file__), 'data', 'intents.csv')
    texts, labels = train.load_dataset(data_path)
    model = train.train_model(texts, labels)
    from joblib import dump
    dump(model, model_path)
    pred = model.predict(['hello there'])[0]
    assert pred in {'greeting', 'question', 'command'}
