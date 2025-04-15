from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_workflows():
    return {"message": "워크플로우 목록"}

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    return {"id": workflow_id, "name": f"워크플로우 {workflow_id}", "status": "active"}

@router.post("/")
async def create_workflow():
    return {"message": "워크플로우 생성됨", "id": "new-workflow-id"}

@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str):
    return {"message": f"워크플로우 {workflow_id} 업데이트됨"}

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    return {"message": f"워크플로우 {workflow_id} 삭제됨"} 