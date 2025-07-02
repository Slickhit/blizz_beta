import os
try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None

from .train import MODEL_PATH

_model = None

def load_model(path: str = MODEL_PATH):
    global _model
    if _model is None:
        if not os.path.exists(path):
            from .train import train_and_save
            _model = train_and_save()
        elif joblib:
            _model = joblib.load(path)
        else:
            from .train import train_model, load_dataset
            texts, labels = load_dataset()
            _model = train_model(texts, labels)
    return _model


def predict_intent(text: str) -> str:
    model = load_model()
    return model.predict(text)


if __name__ == '__main__':
    import sys
    query = ' '.join(sys.argv[1:])
    print(predict_intent(query))
