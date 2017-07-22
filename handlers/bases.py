# coding:utf-8
import json
import tornado.web

from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    """自定义的请求处理基类，实现一些能用的被调用的方法"""
    def prepare(self):
        """预处理方法，主要实现对于前端发送过来json数据的解析操作"""
        # 如果发送过来的数据是json格式，才进行解析
        if self.request.headers.get("Content-Type", "").startswith("Applications/json"):
            req_json_data = self.request.body
            self.json_args = json.loads(req_json_data)
        else:
            self.json_args = {}

    def set_default_headers(self):
        """用来设置默认的响应头信息"""
        self.set_header("Content-Type", "Application/json; charset=utf-8")

    @property
    def db(self):
        """将self.application.db的使用方式简化为直接操作属性db，即self.db"""
        return self.application.db

    @property
    def redis(self):
        """将self.application.redis的使用方式简化为直接操作属性redis，即self.redis"""
        return self.application.redis


class StaticFileHandler(tornado.web.StaticFileHandler):
    """自定义静态文件处理类，让用户在第一次获取前端页面的同时，就能设置上xsrf_cookie"""
    def __init__(self, *args, **kwargs):
        super(StaticFileHandler, self).__init__(*args, **kwargs)
        self.xsrf_token