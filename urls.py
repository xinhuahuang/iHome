# coding:utf-8

import os
from handlers import bases, xsrf_protect, verify_code


urls=[
    (r"/api/v1.0/imagecode", verify_code.ImageCodeHandler),
    (r"/api/v1.0/smscode", verify_code.SMSCodeHandler),


    (r"/api/xsrf_cookie", xsrf_protect.XSRFCookieHandler),   #用来让前端获取xsrf_coookie的值
    (r"/(.*)", bases.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "html"),
                                         "default_filename": "index.html"})  # 提供静态文件资源
]