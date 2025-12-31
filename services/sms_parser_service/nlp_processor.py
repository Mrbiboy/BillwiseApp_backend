import spacy
from huggingface_hub import snapshot_download
from pathlib import Path
import os

class SMSParser:
    _nlp = None  # cache model (singleton)

    def __init__(self, model_path: str = None):
        if SMSParser._nlp is None:
            if model_path is None:
                model_path = snapshot_download(
                    repo_id="elam0222/sms-parser-spacy",
                    revision="main",              # optional
                    cache_dir="/tmp/hf_models"    # Railway-friendly
                )

            model_dir = Path(model_path)
            if not model_dir.exists():
                raise RuntimeError(f"spaCy model not found at: {model_dir}")

            SMSParser._nlp = spacy.load(str(model_dir))

        self.nlp = SMSParser._nlp

    def parse_entities(self, doc):
        entities = {}
        for ent in doc.ents:
            entities[ent.label_] = ent.text
        return entities

    def parse(self, text: str):
        doc = self.nlp(text)
        ents = self.parse_entities(doc)
        return {
            "provider": ents.get("PROVIDER"),
            "service": ents.get("SERVICE"),
            "account": ents.get("ACCOUNT"),
            "bill_month": ents.get("BILL_MONTH"),
            "amount": ents.get("AMOUNT"),
            "due_date": ents.get("DUE_DATE"),
            "url": ents.get("URL"),
            "raw_text": text,
        }
