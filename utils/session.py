# coding: utf-8

import uuid
import json
import logging
import constants

from utils.response_code import RET


class Session(object):
    """自定义session类，用来验证用户是否为合法用户"""
    def __init__(self, request_handler_obj):
        self.request_handler_obj = request_handler_obj

        # 先尝试获取cookie
        session_id = self.request_handler_obj.get_secure_cookie("session_id")

        if session_id is None:
            # 如果session_id为空时，代表用户是第一次访问，则通过uuid生成一个session_id
            self.sid = uuid.uuid4().get_hex()
            self.data ={}
        else:
            self.sid = session_id
            try:
                # 如果session_id不为空，则获取redis数据库中的session值
                json_str_data = self.request_handler_obj.redis.get("session_%s" % self.sid)
            except Exception as e:
                logging.error(e)
                raise e

            # 如果session过期
            if json_str_data is None:
                self.data = {}
            else:
                # 将json格式转化成字典格式
                self.data = json.loads(json_str_data)

    def save(self):
        """将session保存到redis数据库中"""
        # 将字典转化成json
        json_str_data = json.dumps(self.data)

        try:
            # 将session写入redis数据库中，并设置过期时间
            self.request_handler_obj.redis.setex("session_%s" % self.sid, constants.SESSION_DATA_REDIS_EXPIRES, json_str_data)
        except Exception as e:
            logging.error(e)
            raise e
        else:
            # 设置cookie
            self.request_handler_obj.set_secure_cookie("session_id", self.sid)

    def clear(self):
        """清除redis里面的session"""
        try:
            # 删除redis数据库中的cookie
            self.request_handler_obj.redis.delete("session_%s" % self.sid)
        except Exception as e:
            logging.error(e)
            raise e
        else:
            # 删除cookie
            self.request_handler_obj.clear_cookie("session_%s" % self.sid)

