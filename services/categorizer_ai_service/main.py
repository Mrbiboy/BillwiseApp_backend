from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import hf_hub_download
import joblib

app = FastAPI(
    title="Transaction Category Classifier API",
    description="API for predicting transaction categories using a model stored on Hugging Face",
    version="1.0.0"
)

REPO_ID = "zzzzakaria/transaction-category-classifier"

tfidf_path = hf_hub_download(repo_id=REPO_ID, filename="tfidf_vectorizer.joblib")
label_path = hf_hub_download(repo_id=REPO_ID, filename="label_encoder.joblib")
model_path = hf_hub_download(repo_id=REPO_ID, filename="transaction_classifier_rf.joblib")

vectorizer = joblib.load(tfidf_path)
label_encoder = joblib.load(label_path)
model = joblib.load(model_path)


class TransactionRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Transaction Classifier API is running!"}


@app.post("/predict")
def predict_category(req: TransactionRequest):
    text = req.text

    vectorized = vectorizer.transform([text])
    pred = model.predict(vectorized)[0]
    category = label_encoder.inverse_transform([pred])[0]

    return {
        "input_text": text,
        "predicted_category": category
    }
