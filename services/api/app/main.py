import io
from typing import Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from app.schemas import TryOnRequest
from app.services.virtual_tryon import generate_virtual_tryon, image_to_base64

app = FastAPI(
    title="AI Virtual Try-On API",
    version="0.1.0",
    description="A starter backend for a realistic virtual try-on system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "virtual-try-on"}


@app.post("/api/v1/tryon")
async def try_on(
    user_image: UploadFile = File(..., description="User portrait or full-body image."),
    garment_image: UploadFile = File(..., description="Garment image to overlay."),
    request: TryOnRequest = None,
):
    try:
        person_bytes = await user_image.read()
        garment_bytes = await garment_image.read()

        person_image = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        garment_image_obj = Image.open(io.BytesIO(garment_bytes)).convert("RGBA")

        try_on_result = generate_virtual_tryon(person_image, garment_image_obj)
        return {
            "status": "success",
            "image": image_to_base64(try_on_result),
            "prompt": request.prompt if request else None,
        }
    except Exception as exc:  # noqa: BLE001 - simple API error handling for MVP
        raise HTTPException(status_code=400, detail=f"Failed to generate try-on preview: {exc}") from exc

