from fastapi import APIRouter

from app.view.join_handler import join
from app.view.login_handler import login


router = APIRouter()

router.add_api_route(
    path="/join/",
    endpoint=join,
    methods=["POST"],
    summary="Join 用户登录/注册",
    tags=["auth"],
)

router.add_api_route(
    path="/login/",
    endpoint=login,
    methods=["POST"],
    summary="Login 用户登录",
    tags=["auth"],
)
