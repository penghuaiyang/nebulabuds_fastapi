from fastapi import APIRouter

from app.view_admin.login_handler import admin_login

router_admin = APIRouter()

router_admin.add_api_route(path="/adminLogin/", endpoint=admin_login, methods=["POST"], summary="Admin 登录")
