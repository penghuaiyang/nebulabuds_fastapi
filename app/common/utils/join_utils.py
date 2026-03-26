"""Join handler 工具函数"""
import hashlib


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
