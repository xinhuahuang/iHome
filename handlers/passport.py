# coding:utf-8
import hashlib
import logging
import re
import constants

from bases import BaseHandler
from utils.response_code import RET
from utils.session import Session
from utils.commons import required_login


class UserHandler(BaseHandler):
    """提供用户注册操作"""
    def put(self):
        mobile = self.json_args.get("mobile")
        password = self.json_args.get("password")
        sms_code = self.json_args.get("sms_code")

        # 判断请求参数是否为空，当为空时将错误信息返回
        if not all([mobile, password, sms_code]):
            resp_data = {
                "errno":RET.PARAMERR,
                "errmsg": "请求参数不完整"
            }
            return self.write(resp_data)

        # 验证手机号码是否正确
        if not re.match(r"1[34578]\d{9}", mobile):
            rep_data = {
                "errno": RET.PARAMERR,
                "errmsg": "手机号码格式不正确"
            }
            return self.write(rep_data)

        # 查询短信验证码
        try:
            real_sms_code = self.redis.get("sms_code_%s" % mobile)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno":RET.DBERR,
                "errmsg": "查询短信验证码失败"
            }
            return self.write(resp_data)

        # 如果real_sms_code为None时，表示短信验证码过期
        if real_sms_code is None:
            resp_data = {
                "errno":RET.NODATA,
                "errmsg": "短信验证码过期"
            }
            return self.write(resp_data)

        # 验证输入的短信验证码是否正确
        if real_sms_code != sms_code:
            resp_data = {
                "errno":RET.DATAERR,
                "errmsg": "输入的短信验证码不正确"
            }
            return self.write(resp_data)

        # 对密码进行加密
        encrypt_password = hashlib.sha256(password+constants.SECRET_KEY).hexdigest()

        # 将信息提交至数据库中
        sql = "insert into ih_user_profile (up_name, up_mobile, up_passwd) values(%(name)s, %(mobile)s, %(pwd)s)"
        try:
            user_id = self.db.execute(sql, name=mobile, mobile=mobile, pwd=encrypt_password)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno":RET.DBERR,
                "errmsg": "注册失败"
            }
            return self.write(resp_data)

        # 如果注册成功，则认为用户已登录
        try:
            session = Session(self)
            session.data["mobile"] = mobile
            session.data['name'] = mobile
            session.data["user_id"] = user_id
            session.save()
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno":RET.SERVERERR,
                "errmsg": "保存用户登录状态失败"
            }
            return self.write(resp_data)

        resp_data = {
            "errno":RET.OK,
            "errmsg":"登录成功"
        }
        self.write(resp_data)


class SessionHandler(BaseHandler):
    """进行用户登录、注销等操作"""
    def put(self):
        """用户登录"""
        mobile = self.json_args.get("mobile")
        password = self.json_args.get("password")

        # 判断请求参数是否为空，当为空时将错误信息返回
        if not all([mobile, password]):
            resp_data = {
                "errno":RET.PARAMERR,
                "errmsg": "请求参数不完整"
            }
            return self.write(resp_data)

        # 验证手机号码是否正确
        if not re.match(r"1[34578]\d{9}", mobile):
            rep_data = {
                "errno": RET.PARAMERR,
                "errmsg": "手机号码格式不正确"
            }
            return self.write(rep_data)

        # 对密码进行加密
        encrypt_password = hashlib.sha256(password + constants.SECRET_KEY).hexdigest()

        sql = "select up_user_id,up_name from ih_user_profile where up_mobile=%(mobile)s and up_passwd=%(passwd)s"
        try:
            resp = self.db.get(sql, mobile=mobile, passwd=encrypt_password)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "数据查询失败"
            }
            return self.write(resp_data)

        # 如果user_id为空时，表示该用户不存在
        if resp is None:
            resp_data = {
                "errno": RET.USERERR,
                "errmsg": "用户名或密码不正确"
            }
            return self.write(resp_data)

        # 登录成功后，修改session值
        try:
            session = Session(self)
            session.data["mobile"] = mobile
            session.data['name'] = resp["up_name"]
            session.data["user_id"] = resp["up_user_id"]
            session.save()
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno":RET.SERVERERR,
                "errmsg": "保存用户登录状态失败"
            }
            return self.write(resp_data)

        resp_data = {
            "errno":RET.OK,
            "errmsg":"登录成功"
        }
        self.write(resp_data)

    @required_login
    def delete(self):
        """用户退出操作"""
        self.session.clear()
        self.write({"errno": 0, "errmsg": "OK"})

    @required_login
    def get(self):
        """验证用户是否已登录"""
        resp_data = {
            "errno": RET.OK,
            "errmsg": "用户已登录",
            "data": self.session.data["name"]
        }
        return self.write(resp_data)