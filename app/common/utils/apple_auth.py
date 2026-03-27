import jwt
import aiohttp
import asyncio


async def get_apple_public_key(kid):
    """异步获取苹果的公钥"""
    url = "https://appleid.apple.com/auth/keys"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            jwk_set = await response.json()
            for key in jwk_set['keys']:
                if key['kid'] == kid:
                    return key
    raise ValueError("Key ID not found in JWK set")


async def verify_and_decode_token(id_token):
    """异步验证并解析苹果的身份令牌，返回sub"""
    header = jwt.get_unverified_header(id_token)
    apple_public_key = await get_apple_public_key(header['kid'])
    # 从苹果公钥构建一个RSA公钥
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(apple_public_key)

    # 验证JWT令牌
    payload = jwt.decode(
        id_token,
        public_key,
        algorithms=["RS256"],
        audience="com.palmzen.NebulaBuds",  # 请根据实际情况填写你的客户端ID
        issuer="https://appleid.apple.com"
    )
    return payload.get('sub')  # 返回用户的唯一标识符sub
