from fastapi import APIRouter

from app.view.gpt3_handler import gpt3
from app.view.join_handler import join
from app.view.login_handler import login
from app.view.auth_handler import auth


router = APIRouter()

router.add_api_route(
    path="/gpt3/",
    endpoint=gpt3,
    methods=["POST"],
    summary="GPT3 AI 对话",
    tags=["ai"],
)

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

router.add_api_route(
    path="/auth/",
    endpoint=auth,
    methods=["POST"],
    summary="Auth Token 签发/刷新",
    tags=["auth"],
)
