# coding:utf-8

import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop
import torndb
import redis
import config


from tornado.options import options
from urls import urls


tornado.options.define("port", default=8000, type=int, help="在指定端口运行服务器")


class Application(tornado.web.Application):
    """用于添加url、数据库连接对象"""
    def __init__(self, *args, **kwargs):
        # 继承父类的tornado.web.Application的初始化方法，主要用于接收url
        super(Application, self).__init__(*args, **kwargs)

        # 向self对象中补充数据库的连接对象
        self.db = torndb.Connection(**config.mysql_options)

        # 向self对象中补充redis的连接对象
        self.redis = redis.StrictRedis(**config.redis_options)


def main():
    # 设置日志的保存目录
    options.log_file_prefix = config.log_files_path
    # 设置日志输出的等级
    options.logging = config.log_level

    options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(urls, **config.settings))
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()