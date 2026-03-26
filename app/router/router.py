from fastapi import APIRouter

from app.view.join_handler import join


router = APIRouter()

router.add_api_route(
    path="/join/",
    endpoint=join,
    methods=["POST"],
    summary="Join 用户登录/注册",
    tags=["auth"],
)
