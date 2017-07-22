# coding:utf-8

# 调用获取xsrf_cookie接口的时候，进行身份验证的口令，防止黑客调用
API_XSRF_TOKEN = "hfdsofhsdofhsdofhdsofhsofhsof"

# 图片验证码文本redis保存时间, 单位秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码文本redis保存时间, 单位秒
SMS_CODE_REDIS_EXPIRES = 180

# session数据的redis保存有效期, 单位秒
SESSION_DATA_REDIS_EXPIRES = 86400

