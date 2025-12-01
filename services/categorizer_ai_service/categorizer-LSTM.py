from fastapi import FastAPI
from pydantic import BaseModel
import tensorflow as tf
from keras.layers import TFSMLayer
from tensorflow.keras import Input, Model
import pickle
import numpy as np
import json

MODEL_DIR = r"D:\Billwise\models_production\models\production"

# ---- Load SavedModel (expects string input) ----
input_x = Input(shape=(1,), dtype=tf.string)   # <--- IMPORTANT
tfsml = TFSMLayer(f"{MODEL_DIR}/saved_model", call_endpoint="serving_default")
output = tfsml(input_x)
model = Model(inputs=input_x, outputs=output)

# ---- Load Label Encoder ----
with open(f"{MODEL_DIR}/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)


# ---- Prediction ----
def run_prediction(text: str):
    X = tf.constant([[text]])   # <---- string input, shape (1,1)

    raw = model.predict(X, verbose=0)

    if isinstance(raw, dict):
        y = list(raw.values())[0][0]
    else:
        y = raw[0]

    idx = int(np.argmax(y))
    return label_encoder.inverse_transform([idx])[0]


# ---- FastAPI ----
app = FastAPI()

class Request(BaseModel):
    description: str

@app.post("/predict")
def predict(req: Request):
    return {
        "input_text": req.description,
        "predicted_category": run_prediction(req.description)
    }
