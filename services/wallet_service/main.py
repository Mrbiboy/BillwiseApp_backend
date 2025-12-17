import sys
from pathlib import Path

# Add project root to path to enable imports like `database.database`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from router import router as wallet_router


app = FastAPI()

app.include_router(wallet_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8086)
