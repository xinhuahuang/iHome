# coding:utf-8

import functools

from utils.response_code import RET


def required_login(fun):
    @functools.wraps(fun)
    def wrapper(request_handler_obj, *args, **kwargs):

        if not request_handler_obj.get_current_user():
            # 如果用户未登录
            resp_data = {
                "errno": RET.SESSIONERR,
                "errmsg": "用户未登录"
            }
            # 返回一个json数据
            request_handler_obj.write(resp_data)
        else:
            # 如果用户已登录
            fun(request_handler_obj, *args, **kwargs)
    return wrapper