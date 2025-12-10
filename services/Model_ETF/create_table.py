# create_table.py  (run once)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from database.database import engine
from models import Base

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Table 'recommendations' created!")