import spacy
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent

class SMSParser:
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = SCRIPT_DIR / "models" / "model-best"
        model_dir = Path(model_path)
        if not model_dir.exists():
            raise RuntimeError(f"spaCy model not found at: {model_path}")
        # Load your trained NER model
        self.nlp = spacy.load(str(model_path))

    def parse_entities(self, doc):
        """Return entities as a dict with labels as keys"""
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
