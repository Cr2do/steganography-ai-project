from fastapi import FastAPI
from routes import dct, dwt, unified

app = FastAPI()

# Routes spécifiques (si besoin de forcer un algo)
app.include_router(dct.router, prefix="/dct", tags=["DCT"])
app.include_router(dwt.router, prefix="/dwt_svd", tags=["DWT-SVD"])

# Routes unifiées (recommandées)
app.include_router(unified.router, prefix="/api", tags=["Unified"])
