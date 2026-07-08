from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": "AI BI Copilot",
        "version": "1.0.0"
    }