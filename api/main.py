from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.routes import router as api_router

app = FastAPI(
    title="Steganography AI API",
    description="API for embedding and extracting hidden messages in images using DCT and DWT-SVD algorithms.",
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6565)
