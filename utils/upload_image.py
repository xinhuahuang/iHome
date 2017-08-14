# -*- coding: utf-8 -*-

from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'EYUpE8ZvIygRkDYaQsWPuBgZvr9xG__lgRp5OI5S'

secret_key = 'WvXiTJHB7FKGshTp52WAvUI18YM0ZDxq3L_OTbZ4'


# file_data 要上传的文件数据
def upload_qiniu(file_data):
    """上传到七牛的辅助函数"""
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome'

    # 上传到七牛后保存的文件名
    # key = 'my-python-logo.png';

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # 要上传文件的本地路径
    # localfile = './home02.jpg'

    ret, info = put_data(token, None, file_data)
    if info.status_code != 200:
        # 表示上传到七牛出现异常
        raise Exception("上传到七牛出现异常")
    else:
        # 表示上传成功
        return ret["key"]