# coding:utf-8

import os

# tornado应用程序Application的构造参数
settings = dict(
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    debug=True,
    xsrf_cookies=True,
    cookie_secret="eGpgcCeJRm2aAivkyMSX6SGKwY0jUkNRnO5WUqOL9xs="
)

# mysql参数
mysql_options = dict(
    host="127.0.0.1",
    database="ihome",
    user="root",
    password="12345678"
)

# redic参数
redis_options = dict(
    host="127.0.0.1",
    port=6379
)

# 日志的保存文件
log_files_path = "./logs/log"

# 日志的等级
log_level = "debug"