import redis.asyncio as redis

from fastapi import APIRouter
from app.view.join_handler import join


router = APIRouter()

router.add_api_route(path="/join/", endpoint=join, methods=["POST"])

