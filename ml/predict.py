import os
import joblib

from .train import MODEL_PATH

_model = None

def load_model(path: str = MODEL_PATH):
    global _model
    if _model is None:
        if not os.path.exists(path):
            from .train import train_and_save
            _model = train_and_save()
        else:
            _model = joblib.load(path)
    return _model


def predict_intent(text: str) -> str:
    model = load_model()
    return model.predict(text)


if __name__ == '__main__':
    import sys
    query = ' '.join(sys.argv[1:])
    print(predict_intent(query))
