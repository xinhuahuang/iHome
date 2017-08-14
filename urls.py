# coding:utf-8

import os
from handlers import bases, xsrf_protect, verify_code, passport, profile, house


urls=[
    # 用户管理部分
    (r"/api/v1.0/imagecode", verify_code.ImageCodeHandler),
    (r"/api/v1.0/smscode", verify_code.SMSCodeHandler),
    (r"/api/v1.0/user", passport.UserHandler),  # 用户注册 （PUT）
    (r"/api/v1.0/session", passport.SessionHandler),  # 用户登录（PUT) 用户登出（DELETE） 判断用户是否处于登录状态 （GET）
    (r"/api/v1.0/avatar", profile.AvatarHandler),  # 处理用户头像
    (r"/api/v1.0/userinfo", profile.UserInfo),  # 显示用户信息

    # 房屋管理部分
    (r"/api/v1.0/areas", house.AreasHandler),  # 显示城区信息
    (r"/api/v1.0/facility", house.FacilityHandler),  # 显示房屋中的设施
    (r"/api/v1.0/house$", house.HouseHandler),   # 发布房源信息(PUT)   房东巨单(POST)   获取房屋信息(GET)
    (r"/api/v1.0/house/images", house.HouseImageHandler),  # 发布房屋图片信息(PUT)
    (r"/api/v1.0/house/(?P<house_id>\d+)", house.HouseDetailHandler),  # 获取房屋详细信息(GET)
    (r"/api/v1.0/houses/index", house.HousesIndexHandler),  # 查询主页房屋信息(GET)
    (r"/api/v1.0/houses", house.HousesSearchHandler),  # 房屋的查询信息

    (r"/api/xsrf_cookie", xsrf_protect.XSRFCookieHandler),   #用来让前端获取xsrf_coookie的值
    (r"/(.*)", bases.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "html"),
                                         "default_filename": "index.html"})  # 提供静态文件资源
]