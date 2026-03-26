from fastapi import APIRouter
from app.view.join_handler import JOIN_ROUTE_OPENAPI_EXTRA, JOIN_ROUTE_RESPONSES, join


router = APIRouter()

router.add_api_route(
    path="/join/",
    endpoint=join,
    methods=["POST"],
    summary="Join 用户登录/注册",
    tags=["auth"],
    responses=JOIN_ROUTE_RESPONSES,
    openapi_extra=JOIN_ROUTE_OPENAPI_EXTRA,
)

