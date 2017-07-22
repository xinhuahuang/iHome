# coding: utf-8
import constants
import logging
import re
import random

from handlers.bases import BaseHandler
from utils.captcha.captcha import captcha
from utils.response_code import RET
from lib.yuntongxun.sendsms import ccp


class ImageCodeHandler(BaseHandler):
    """用来生成验证码，并将验证码的信息写入redis数据库"""
    def get(self):
        # 接收前端传递过来的id，用来作为redis的key
        image_code_id = self.get_argument("id")

        # 调用第三方接口，用来生成验证码
        # name: 表示验证码名称
        # text: 表示验证码的内容
        # image: 验证码图片，该值是一个二进制数据
        name, text, image = captcha.generate_captcha()

        try:
            # 写入redis，并设置过期时间
            self.redis.setex("image_code_%s" %image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        except Exception as e:
            # 将错误信息写入日志，并通过json将错误信息返回
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "插入redis失败"
            }
            self.write(resp_data)
        else:
            # 将验证码返回，并设置响应头
            self.write(image)
            self.set_header("Content-Type", "image/jpg")


class SMSCodeHandler(BaseHandler):
    """
        1. 验证图片验证码是否正确
        2. 发送短信验证码，并将短信验证码信息写入redis数据库
    """
    def get(self):
        mobile = self.get_argument("mobile")
        image_code_text = self.get_argument("code")
        image_code_id = self.get_argument("codeId")

        # 验证手机号码格式是否正确
        if not re.match(r"1[34578]\d{9}", mobile):
            rep_data = {
                "errno": RET.PARAMERR,
                "errmsg": "手机号码格式不正确"
            }
            return self.write(rep_data)

        try:
            # 从redis数据库里面获取验证码信息
            real_image_code_text = self.redis.get("image_code_%s" %image_code_id)
        except Exception as e:
            # 将错误信息写入日志，并通过json将错误信息返回
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "从redis数据库中读取信息失败"
            }
            return self.write(resp_data)

        # 判断用户输入的验证码与redis数据库中的验证码信息是否一致
        if image_code_text.lower() != real_image_code_text.lower():
            resp_data = {
                "errno": RET.DATAERR,
                "errmsg": "输入的验证码信息错误"
            }
            return self.write(resp_data)

        # 删除redis中保存的验证码信息
        try:
            self.redis.delete("image_code_%s" %image_code_id)
        except Exception as e:
            # 将错误信息写入日志，并通过json将错误信息返回
            logging.error(e)

        # 生成6位的短信验证码
        sms_code = "%6d" %(random.randint(0, 999999))

        # 将生成的短信验证码写入redis数据库
        try:
            self.redis.setex("sms_code_%s" %image_code_id, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        except Exception as e:
            # 将错误信息写入日志，并通过json将错误信息返回
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "插入redis信息失败"
            }
            return self.write(resp_data)

        # 调用第三方接口发送短信
        try:
            ccp.send_template_sms(mobile, [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
        except Exception as e:
            resp_data = {
                "errno": RET.THIRDERR,
                "errmsg": "调用短信接口失败"
            }
            return self.write(resp_data)
        else:
            resp_data = {
                "errno": RET.OK,
                "errmsg": "发送短信成功"
            }
            return self.write(resp_data)




