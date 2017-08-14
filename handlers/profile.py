# coding: utf-8
import logging
import re

import constants

from handlers.bases import BaseHandler
from utils.upload_image import upload_qiniu
from utils.commons import required_login
from utils.response_code import RET


class AvatarHandler(BaseHandler):
    """上传用户头像"""
    @required_login
    def put(self):
        user_id = self.session.data["user_id"]

        avatar_files_data = self.request.files.get("avatar")

        # 判断上传的文件是否为空
        if avatar_files_data is None:
            resp_data = {
                "errno": RET.NODATA,
                "errmsg": "未上传文件"
            }
            return self.write(resp_data)

        # 获取头像的二进制文件内容
        avatar_file_data = avatar_files_data[0].body

        try:
            file_name = upload_qiniu(avatar_file_data)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.THIRDERR,
                "errmsg": "上传到七牛失败"
            }
            return self.write(resp_data)

        # 对应的七牛的文件路径 http://o91qujnqh.bkt.clouddn.com/Fg3g-QPWYps9lNfB0yOmhUb-FRH7

        # 操作数据库，保存头像图片的七牛地址
        sql = "update ih_user_profile set up_avatar=%(avatar)s where up_user_id=%(user_id)s"
        try:
            self.db.execute_rowcount(sql, user_id=user_id, avatar=file_name)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "保存图片信息失败"
            }
            return self.write(resp_data)

        # 表示上传头像的整个流程执行成功
        resp_data = {
            "errno": RET.OK,
            "errmsg": "OK",
            "avatar_url": constants.QINIU_DOMAIN_PREFIX + file_name
        }
        self.write(resp_data)

    @required_login
    def get(self):
        """显示用户的头像、昵称"""
        user_id = self.session.data["user_id"]

        sql = "select up_avatar,up_name from ih_user_profile where up_user_id=%(user_id)s"
        try:
            res = self.db.get(sql, user_id=user_id)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "图片查询失败"
            }
            return self.write(resp_data)
        else:
            resp_data = {
                "errno": RET.OK,
                "errmsg": "查询成功",
                "avatar_url": constants.QINIU_DOMAIN_PREFIX + res["up_avatar"],
                "name": res["up_name"]
            }
            return self.write(resp_data)

    @required_login
    def post(self):
        """修改用户昵称"""
        user_id = self.session.data["user_id"]
        name = self.json_args.get("name")

        # 判断用户名不能为空
        if name is None:
            resp_data = {
                "errno": RET.PARAMERR,
                "errmsg": "用户名不能为空"
            }
            return self.write(resp_data)

        # 检查用户名是否存在，如果存在提示：用户名已存在；否则，更新用户名
        try:
            sql = "select count(*) as counts from ih_user_profile where up_user_id=%(user_id)s and up_name=%(name)s"
            counts = self.db.get(sql, user_id=user_id, name=name)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno":RET.DBERR,
                "errmsg":"查询用户失败"
            }
            return self.write(resp_data)
        else:
            if counts["counts"] > "0":
                resp_data = {
                    "errno": RET.DATAEXIST,
                    "errmsg": "用户名已存在"
                }
                return self.write(resp_data)
            else:
                # 更新用户名
                sql = "update ih_user_profile set up_name=%(name)s where up_user_id=%(user_id)s"
                try:
                    self.db.execute(sql, name=name, user_id=user_id)
                except Exception as e:
                    logging.error(e)
                    resp_data = {
                        "errno":RET.DBERR,
                        "errmsg":"数据更新失败"
                    }
                    return self.write(resp_data)
                else:
                    resp_data = {
                        "errno":RET.OK,
                        "errmsg":"更新成功",
                        "name":name
                    }
                    self.write(resp_data)


class UserInfo(BaseHandler):
    """用户信息相关操作"""
    @required_login
    def get(self):
        """显示用户基本信息"""
        user_id = self.session.data["user_id"]
        try:
            sql = "select up_name, up_mobile, up_avatar, up_real_name, up_id_card from ih_user_profile where up_user_id=%(user_id)s"
            res = self.db.get(sql, user_id=user_id)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DBERR,
                "errmsg": "查询数据失败"
            }
            return self.write(resp_data)
        else:
            resp_data = {
                "errno": RET.OK,
                "errmsg": "OK",
                "data": {
                    "name":res['up_name'],
                    "mobile":res['up_mobile'],
                    "avatar":constants.QINIU_DOMAIN_PREFIX + res['up_avatar'],
                    "real_name": res["up_real_name"],
                    "id_card": res["up_id_card"]
                }
            }
            self.write(resp_data)

    @required_login
    def post(self):
        """用户实名制认证"""
        user_id = self.session.data["user_id"]

        real_user_name = self.json_args.get("real_name")
        real_id_card = self.json_args.get("id_card")

        # 判断请求参数是否为空，当为空时将错误信息返回
        if not all([real_user_name, real_id_card]):
            resp_data = {
                "errno": RET.PARAMERR,
                "errmsg": "请求参数不完整"
            }
            return self.write(resp_data)

        # 验证身份证号码是否正确
        if not re.match(r"\d{18}|\d{17}x", real_id_card):
            resp_data = {
                "errno":RET.PARAMERR,
                "errmsg": "省份证号码不正确"
            }
            return self.write(resp_data)

        # 更新用户信息
        sql = "update ih_user_profile set up_real_name=%(name)s,up_id_card=%(card)s where up_user_id=%(uid)s"
        try:
            self.db.execute(sql, name=real_user_name, card=real_id_card, uid=user_id)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno":RET.DBERR,
                "errmsg": "更新数据库失败"
            }
            return self.write(resp_data)
        else:
            resp_data = {
                "errno":RET.OK,
                "errmsg": "OK",
                "data": {"user_name": real_user_name, "id_card": real_id_card}
            }
            self.write(resp_data)
