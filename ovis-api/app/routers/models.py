from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_models():
    return {"message": "모델 목록", "status": "ok"}

@router.get("/{model_id}")
async def get_model(model_id: str):
    return {
        "id": model_id,
        "name": f"모델 {model_id}",
        "status": "active",
        "type": "language_model",
        "version": "1.0"
    }

@router.post("/")
async def create_model():
    return {"message": "모델 생성됨", "id": "new-model-id"}

@router.put("/{model_id}")
async def update_model(model_id: str):
    return {"message": f"모델 {model_id} 업데이트됨"}

@router.delete("/{model_id}")
async def delete_model(model_id: str):
    return {"message": f"모델 {model_id} 삭제됨"} 