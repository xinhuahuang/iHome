# coding=utf-8

from CCPRestSDK import REST
from tornado.ioloop import IOLoop


# 主帐号
accountSid = '8a216da85d158d1b015d6970c4002384'

# 主帐号Token
accountToken = '811f710ca4264310ba77c56f4e30e930'

# 应用Id
appId = '8a216da85d158d1b015d6970c4382388'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


class CCP(object):
    """发送短信的辅助类，做成了单例模式"""

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "__instance"):
            return cls.__instance
        else:
            # 创建一个CCP类的对象，并保存到类属性__instance中
            cls.__instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            # 初始化REST SDK
            cls.__instance.rest = REST(serverIP, serverPort, softVersion)
            cls.__instance.rest.setAccount(accountSid, accountToken)
            cls.__instance.rest.setAppId(appId)
            return cls.__instance

    def send_template_sms(self, to, datas, temp_id):
        # 发送模板短信
        # @param to 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param temp_d 模板Id

        # 通过调用云通讯SDK对象的方法发送短信
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        #result = IOLoop.current().spawn_callback(self.rest.sendTemplateSMS(to, datas, temp_id))


        if result.get("statusCode") != "000000":
            # 表示云通讯发送短信失败
            reason = u"云通讯发送短信失败: %s" % result.get("statusMsg")
            raise Exception(reason)

ccp = CCP()

if __name__ == '__main__':
    ccp.send_template_sms("18616707532", ["1234", "5"], 1)
