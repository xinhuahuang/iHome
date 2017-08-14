# coding:utf-8

# 调用获取xsrf_cookie接口的时候，进行身份验证的口令，防止黑客调用
API_XSRF_TOKEN = "hfdsofhsdofhsdofhdsofhsofhsof"

# 图片验证码文本redis保存时间, 单位秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码文本redis保存时间, 单位秒
SMS_CODE_REDIS_EXPIRES = 180

# session数据的redis保存有效期, 单位秒
SESSION_DATA_REDIS_EXPIRES = 86400

# 处理用户密码加密时的附加字符串，盐值， 用来混淆使用
SECRET_KEY = "Y3EpEGh6Sj2VJxpU76CNRDdFOviK30SmpR2RXzHnE60="

# 七牛图片地址的前缀，即域名信息
QINIU_DOMAIN_PREFIX = "http://otmykwcsc.bkt.clouddn.com/"

# 城区信息redis保存时间，单位秒
AREA_REDIS_EXPIRES = 3600

# 房屋设施redis保存时间，单位秒
FACILITY_REDIS_EXPIRES = 3600

# 房屋详细信息redis保存有效期， 单位秒
HOUSE_DETAIL_REDIS_EXPIRES = 7200

# 房屋首页信息展示，默认展示3条
HOUSE_INDEX_SHOW_COUNTS = 5

# 房屋首页信息redis保存时间，单位秒
HOUSE_INDEX_REDIS_EXPIRES = 300

# 房屋搜索页面每页显示房屋的记录条数
HOUSE_LIST_PAGE_CAPACITY = 2