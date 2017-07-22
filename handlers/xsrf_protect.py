# coding:utf-8

import constants

from handlers.bases import BaseHandler


class XSRFCookieHandler(BaseHandler):
    """用来提供xsrf_cookie"""
    def get(self):
        # 提取身份口令参数，进行身份校验
        token = self.get_argument("token")   # 用户发送过来的请求中携带的token参数的值，应该和 API_XSRF_TOKEN是一样
        if token == constants.API_XSRF_TOKEN:
            # 表示调用这个接口的是自己人
            # 通过获取xsrf_token值，tornado会自动帮助我们完成xsrf_cookie的设置操作
            self.xsrf_token
            self.write("OK")
        else:
            # 表示不是自己人，可能是黑客, 不会设置xsrf_cookie，并返回403禁止操作
            self.send_error(403)
