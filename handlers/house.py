# coding:utf-8

import logging

import math

import constants
import json

from handlers.bases import BaseHandler
from utils.response_code import RET
from utils.commons import required_login
from utils.upload_image import upload_qiniu
from utils.session import Session


class AreasHandler(BaseHandler):
    """获取城区信息"""
    def get(self):
        # 如果redis中有城区信息，则直接读取redis中的数据
        try:
            res = self.redis.get("areas_id")
            if res :
                resp_str_data = '{"errno": "0", "errmsg": "OK", "data": %s}' % res
                return self.write(resp_str_data)
        except Exception as e:
            logging.error(e)

        # 从mysql中取出所有的城区信息
        sql = "select ai_area_id, ai_name from ih_area_info"
        try:
            res = self.db.query(sql)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DATAERR,
                "errmsg": "数据查询失败"
            }
            return self.write(resp_data)
        # 将城区信息写入redis数据库
        try:
            areas_redis_data = json.dumps(res)
            self.redis.setex("areas_id", constants.AREA_REDIS_EXPIRES, areas_redis_data)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DATAERR,
                "errmsg": "写redis失败"
            }
            return self.write(resp_data)
        else:
            resp_data = {
                "errno": RET.OK,
                "errmsg": "OK",
                "data": res
            }
            return self.write(resp_data)


class FacilityHandler(BaseHandler):
    """获取房间内设施"""
    def get(self):
        # 如果redis中有城区信息，则直接读取redis中的数据
        try:
            res = self.redis.get("facility_id")
            if res:
                resp_str_data = '{"errno": "0", "errmsg": "OK", "data": %s}' % res
                return self.write(resp_str_data)
        except Exception as e:
            logging.error(e)

        # 从mysql中取出所有的城区信息
        sql = "select fc_id, fc_name from ih_facility_catelog"
        try:
            res = self.db.query(sql)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DATAERR,
                "errmsg": "数据查询失败"
            }
            return self.write(resp_data)
        # 将城区信息写入redis数据库
        try:
            facility_redis_data = json.dumps(res)
            self.redis.setex("facility_id", constants.FACILITY_REDIS_EXPIRES, facility_redis_data)
        except Exception as e:
            logging.error(e)
            resp_data = {
                "errno": RET.DATAERR,
                "errmsg": "写redis失败"
            }
            return self.write(resp_data)
        else:
            resp_data = {
                "errno": RET.OK,
                "errmsg": "OK",
                "data": res
            }
            return self.write(resp_data)


class HouseHandler(BaseHandler):
    """发布房源信息"""
    @required_login
    def put(self):
        """用户发布房源信息"""
        user_id = self.session.data["user_id"]
        title = self.json_args.get("title")
        price = self.json_args.get("price")
        area_id = self.json_args.get("area_id")
        address = self.json_args.get("address")
        room_count = self.json_args.get("room_count")
        acreage = self.json_args.get("acreage")
        unit = self.json_args.get("unit")
        capacity = self.json_args.get("capacity")
        beds = self.json_args.get("beds")
        deposit = self.json_args.get("deposit")
        min_days = self.json_args.get("min_days")
        max_days = self.json_args.get("max_days")

        # 标题不能为空
        if not title:
            return self.write({"errno":RET.PARAMERR, "errmsg": "房屋标题不能为空"})

        # 添加新的房屋信息
        sql = "insert into ih_house_info (hi_user_id, hi_title, hi_price, hi_area_id, hi_address, hi_room_count, " \
              "hi_acreage, hi_house_unit, hi_capacity, hi_beds, hi_deposit, hi_min_days, hi_max_days) values (%(user_id)s," \
              " %(title)s, %(price)s, %(area_id)s, %(address)s, %(room_count)s, %(acreage)s, %(unit)s, %(capacity)s, " \
              "%(beds)s, %(deposit)s, %(min_days)s, %(max_days)s)"
        try:
            house_id = self.db.execute(sql, user_id=user_id, title=title, price=price, area_id=area_id, address=address,
                            room_count=room_count, acreage=acreage, unit=unit, capacity=capacity, beds=beds,
                            deposit=deposit, min_days=min_days, max_days=max_days)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "房屋信息添加失败"})

        # 添加房屋的设施
        facility = self.json_args.get("facility",[])

        if facility:
            sql = "insert into ih_house_facility (hf_house_id, hf_facility_id) values"
            # 保存sql语句中的占位符
            sql_str_list = []
            # 保存sql语句中的动态参数
            sql_val_list = []

            for facility_id in facility:
                sql_str_list.append("(%s, %s)")
                sql_val_list.append(house_id)
                sql_val_list.append(facility_id)

            sql += ",".join(sql_str_list)

            try:
                self.db.execute(sql, *tuple(sql_val_list))
            except Exception as e:
                logging.error(e)
                # 房屋设施添加失败，进行手动事务回滚
                sql = "delete from ih_house_info where hi_house_id=%s"
                try:
                    self.db.execute(sql, house_id)
                except Exception as e:
                    logging.error(e)
                    return self.write({"errno":RET.DBERR, "errmsg":"删除房屋基本信息失败"})
                else:
                    return self.write({"errno": RET.DBERR, "errmsg": "保存房屋设施失败，房屋信息已删除"})

            return self.write({"errno": RET.OK, "errmsg": "OK", "house_id": house_id})

    @required_login
    def get(self):
        """展示用户发布的房屋信息"""
        # 获取房屋基本信息
        user_id = self.session.data["user_id"]

        sql = "select h.hi_house_id, h.hi_title, h.hi_price, a.ai_name, hi_utime, hi_index_image_url from " \
              "ih_house_info as h, ih_area_info as a " \
              "where h.hi_area_id = a.ai_area_id and h.hi_user_id=%s order by hi_utime DESC"
        try:
            houses_info = self.db.query(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":RET.DBERR, "errmsg":"获取房屋基本信息失败"})

        if houses_info:
            for house in houses_info:
                house["hi_utime"] = str(house["hi_utime"])
                house["hi_index_image_url"] = constants.QINIU_DOMAIN_PREFIX + house["hi_index_image_url"]

            return self.write({"errno":RET.OK, "errmsg":"OK", "data":houses_info})
        else:
            return self.write({"errno":RET.OK, "errmsg":"OK", "data":{}})


class HouseImageHandler(BaseHandler):
    """发布房源的图片"""
    @required_login
    def put(self):
        house_id = self.get_argument("house_id")
        house_image_list = self.request.files.get("house_image")

        # 检查上传的图片是否为空
        if house_image_list is None:
            return self.write({"errno":RET.PARAMERR, "errmsg":"图片不能为空"})

        # 获取图片的二进制内容
        house_image_data = house_image_list[0].body
        try:
            filename = upload_qiniu(house_image_data)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":RET.THIRDERR, "errmsg": "上传图片失败"})

        # 将图片信息写入数据库
        sql = "insert into ih_house_image (hi_house_id, hi_url) values(%(house_id)s, %(image_url)s)"
        try:
            self.db.execute(sql, house_id=house_id, image_url=filename)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":RET.DBERR, "errmsg":"图片写入数据库失败"})

        # 当房屋信息表中的图片为空时，更新房屋信息表中的图片
        sql = "select hi_index_image_url from ih_house_info where hi_house_id=%(house_id)s"
        try:
            ret = self.db.get(sql, house_id=house_id)
        except Exception as e:
            logging.error(e)

        if ret["hi_index_image_url"] is None:
            sql = "update ih_house_info set hi_index_image_url=%(image_url)s where hi_house_id=%(house_id)s"
            try:
                self.db.execute(sql, image_url=filename, house_id=house_id)
            except Exception as e:
                logging.error(e)
                return self.write({"errno":RET.DBERR, "errmsg":"数据库更新失败"})

        self.write({"errno": RET.OK, "errmsg": "OK", "image_url": constants.QINIU_DOMAIN_PREFIX + filename})


class HouseDetailHandler(BaseHandler):
    """获取房屋的详细信息"""
    def get(self, house_id):
        session = Session(self)
        user_id = session.data.get("user_id", "-1")

        # 如果house_id为空，则直接抛出错误
        if not house_id:
            return self.write({"errno":RET.PARAMERR, "errmsg":"缺少参数"})

        # 先尝试去redis中取房屋信息，如果没有再从数据库取
        try:
            house = self.redis.get("house_info_%s" % house_id)
        except Exception as e:
            logging.error(e)
        else:
            if house:
                resp = '{"errno": 0, "errmsg": "OK", "user_id":%s, "house":%s}' % (user_id, house)
                return self.write(resp)

        # 获取房屋的基本信息
        sql = "select h.hi_title, hi_user_id, h.hi_price, h.hi_address, h.hi_room_count, h.hi_acreage, h.hi_house_unit, " \
              "h.hi_capacity,h.hi_beds,h.hi_deposit,h.hi_min_days,h.hi_max_days, a.ai_name, us.up_name, us.up_avatar " \
              "from ih_house_info as h " \
              "inner join ih_user_profile as us " \
              "inner join ih_area_info as a " \
              "on h.hi_area_id = a.ai_area_id and us.up_user_id = h.hi_user_id " \
              "where h.hi_house_id=%s"
        try:
            house_info = self.db.get(sql, house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg":"获取房屋基本信息失败"})

        if not house_info:
            return self.write({"errno": RET.NODATA, "errmsg":"房屋信息不存在"})

        # 构造返回报文
        house = {
            "hid": house_id,
            "user_id": house_info["hi_user_id"],
            "title": house_info["hi_title"],
            "price": house_info["hi_price"],
            "address": house_info["hi_address"],
            "room_count": house_info["hi_room_count"],
            "acreage": house_info["hi_acreage"],
            "house_unit": house_info["hi_house_unit"],
            "capacity": house_info["hi_capacity"],
            "beds": house_info["hi_beds"],
            "deposit": house_info["hi_deposit"],
            "min_days": house_info["hi_min_days"],
            "max_days": house_info["hi_max_days"],
            "area": house_info["ai_name"],
            "name": house_info["up_name"],
            "avatar": constants.QINIU_DOMAIN_PREFIX + house_info["up_avatar"] if house_info["up_avatar"] else ""
        }

        # 查询图片信息
        sql = "select hi_url from ih_house_image where hi_house_id=%s"
        try:
            images_info = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            # return self.write({"errno": RET.DBERR, "errmsg": "获取图片信息失败"})

        house["img_urls"] = []
        if images_info:
            for img in images_info:
                house["img_urls"].append(constants.QINIU_DOMAIN_PREFIX + img["hi_url"])

        # 查询房屋设施信息
        sql = "select cate.fc_name, cate.fc_id from ih_house_facility as fa inner join ih_facility_catelog as cate " \
              "on fa.hf_id = cate.fc_id where fa.hf_house_id = %s"
        try:
            facility_info = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            # return self.write({"errno": RET.DBERR, "errmsg": "获取房屋设施失败"})

        house["facility"] = []
        if facility_info:
            for fa in facility_info:
                house["facility"].append(fa["fc_id"])
                house["facility"].append(fa["fc_name"])

        # 存入redis中
        json_house = json.dumps(house)
        try:
            self.redis.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRES, json_house)
        except Exception as e:
            logging.error(e)

        resp = '{"errno": 0, "errmsg": "OK", "user_id":%s, "house":%s}' %(user_id, json_house)
        return self.write(resp)


class HousesIndexHandler(BaseHandler):
    """获取房屋主页图片信息"""
    def get(self):
        # 从redis中读取数据
        try:
            ret = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
        else:
            if ret:
                resp = '{"errno": "0", "errmsg": "数据返回成功", "houses": %s}' %ret
                return self.write(resp)

        if not ret:
            sql = "select hi_house_id, hi_title, hi_index_image_url from ih_house_info order by hi_ctime DESC LIMIT %s"
            try:
                resp = self.db.query(sql, constants.HOUSE_INDEX_SHOW_COUNTS)
            except Exception as e:
                logging.error(e)
                return self.write({"errno": RET.DBERR, "errmsg": "数据库读取失败"})

            # 构建返回报文
            houses = []
            if resp:
                for l in resp:
                    if l["hi_index_image_url"]:
                        house = {
                            "house_id": l["hi_house_id"],
                            "title": l["hi_title"],
                            "image_url": constants.QINIU_DOMAIN_PREFIX + l["hi_index_image_url"]
                        }
                    houses.append(house)

            # 将首页的信息写入redis
            json_houses = json.dumps(houses)
            try:
                self.redis.setex("home_page_data", constants.HOUSE_INDEX_REDIS_EXPIRES, json_houses)
            except Exception as e:
                logging.error(e)

            # 将值返回给前端
            resp = '{"errno": 0, "errmsg": "OK", "houses": %s}' % json_houses
            return self.write(resp)


class HousesSearchHandler(BaseHandler):
    """获取房屋搜索结果信息"""
    def get(self):
        start_date = self.get_argument("sd")  # 用户的开始入住日期
        end_date = self.get_argument("ed")    # 用户的离开日期
        area_id = self.get_argument("aid")    # 区域id
        sort_key = self.get_argument("sk", "new")  # 用户想要的排序顺序 new   booking   price-inc price-des
        page = self.get_argument("p", "1")    # 分页信息

        sql = "select a.hi_user_id, a.hi_house_id, a.hi_index_image_url, a.hi_title, a.hi_price, a.hi_room_count, a.hi_address, " \
              "a.hi_order_count, b.up_avatar from ih_house_info a inner join ih_user_profile b " \
              "on a.hi_user_id = b.up_user_id left join ih_order_info c on a.hi_house_id = c.oi_house_id"

        total_page_sql = "select count(*) as counts from ih_house_info a inner join ih_user_profile b " \
              "on a.hi_user_id = b.up_user_id left join ih_order_info c on a.hi_house_id = c.oi_house_id"

        sql_where_str = []
        sql_where_val = {}
        # 用户的入住时间和离店时间
        if start_date and end_date:
            sql_where_str.append(" (a.hi_house_id not in (select oi_house_id from ih_order_info where "
                                 "oi_begin_date<=%(end_date)s and oi_end_date>=%(start_date)s))")
            sql_where_val["end_date"] = end_date
            sql_where_val["start_date"] = start_date
        elif start_date:
            sql_where_str.append(" (a.hi_house_id not in (select oi_house_id from ih_order_info where "
                                 "oi_end_date>=%(start_date)s))")
            sql_where_val["start_date"] = start_date
        elif end_date:
            sql_where_str.append(" (a.hi_house_id not in (select oi_house_id from ih_order_info where "
                                 "oi_end_date>=%(end_date)s))")
            sql_where_val["end_date"] = end_date

        # 房屋的区域
        if area_id:
            area_id = int(area_id)
            sql_where_str.append(" (a.hi_area_id=%(area_id)s) ")
            sql_where_val["area_id"] = area_id

        # 拼接where语句
        if sql_where_str:
            sql += " where " + " and ".join(sql_where_str)
            total_page_sql += " where " + " and ".join(sql_where_str)

        # 查询总页数
        try:
            ret = self.db.get(total_page_sql, **sql_where_val)
        except Exception as e:
            logging.error(e)
            total_page_index = -1
        else:
            counts = int(ret["counts"])
            total_page_index = int(math.ceil(counts/float(constants.HOUSE_LIST_PAGE_CAPACITY)))

        # 如果查询的页数>总页数，则查询结果中的houses为空
        page = int(page)
        if page > total_page_index:
            return self.write({"errno":RET.OK, "errmsg":"Ok", "houses":[], "total_page_index":total_page_index})

        # 房屋的排序规则
        if "new" == sort_key:
            sql += " order by a.hi_ctime desc "
        elif "booking" == sort_key:
            sql += " order by a.hi_order_count desc "
        elif "price-inc" == sort_key:
            sql += " order by a.hi_price asc "
        elif "price-des" == sort_key:
            sql += " order by a.hi_price desc "

        # 分页
        if 1 == page:
            sql += " limit %d " %constants.HOUSE_LIST_PAGE_CAPACITY
        else:
            sql += " limit %d,%d " %((page-1)*constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY)

        # 查询数据库信息，并将最终结果返回
        try:
            ret = self.db.query(sql, **sql_where_val)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":RET.DBERR, "errmsg":"数据查询失败"})

        houses = []
        if not ret:
            return self.write({"errno":RET.NODATA, "errmsg":"未查询到记录"})
        else:
            for l in ret:
                data = {
                    "user_id":l["hi_user_id"],
                    "house_id":l["hi_house_id"],
                    "house_image_url":constants.QINIU_DOMAIN_PREFIX + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                    "title":l["hi_title"],
                    "price":l["hi_price"],
                    "room_count":l["hi_room_count"],
                    "address":l["hi_address"],
                    "order_count":l["hi_order_count"],
                    "avatar":constants.QINIU_DOMAIN_PREFIX + l["up_avatar"] if l["up_avatar"] else ""
                }
                houses.append(data)

            resp = '{"errno": 0, "errmsg": "OK", "houses":%s, "total_page_index":%s}' % (json.dumps(houses),total_page_index)
            return self.write(resp)