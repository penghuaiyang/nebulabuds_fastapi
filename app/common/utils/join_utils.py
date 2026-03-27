"""Join handler 工具函数"""
import hashlib
from functools import wraps

from app.common.base.base_reponse import api_write


def check(params: dict) -> bool:
    """MD5签名校验

    校验逻辑：排除pass字段后拼接所有参数值，计算MD5并取[2:9]位与pass比对
    """
    tmp_str = ''.join(str(v) for k, v in params.items() if k != 'pass')
    str_md5 = hashlib.md5(tmp_str.encode('utf-8')).hexdigest()[2:9]
    return str_md5 == params.get('pass')


def create_pass(params: dict) -> dict:
    """生成签名pass字段

    校验逻辑：排除pass字段后拼接所有参数值，计算MD5并取[2:9]位
    """
    combined_str = ''.join(str(v) for k, v in params.items() if k != 'pass')
    encrypted_str = hashlib.md5(combined_str.encode('utf-8')).hexdigest()
    pass_str = encrypted_str[2:9]
    params['pass'] = pass_str
    return params


def check_params(func):
    @wraps(func)
    async def wrapper(data, request, *args, **kwargs):
        params = data.model_dump(by_alias=True)
        # 如果有字段为 admin 且值为 hqq，则跳过校验
        if params.get("admin") == "hqq":
            return await func(data, request, *args, **kwargs)

        # 否则正常校验参数
        if not check(params):
            return await api_write(request=request, code=0, message="params error")

        return await func(data, request, *args, **kwargs)

    return wrapper
