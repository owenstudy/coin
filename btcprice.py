import requests
import json
import urlaccess

class JSONObject:
    def __init__(self, d):
        self.__dict__ = d

#url='http://api.btc38.com/v1/ticker.php?c=btc&mk_type=cny'
url='http://api.btc38.com/v1/ticker.php?c=all&mk_type=cny'

r=urlaccess.get_content(url)

#r=b'{"ticker":{"high":19850,"low":19001.5,"last":19602,"vol":1723.108035,"buy":19640,"sell":19602}}'
#返回的字节转换成字符串
price=r.decode('utf8')
#转换为json格式的字符串
str=json.dumps(price)
print(price)

#把json字符串转换成为python对象
data = json.loads(price, object_hook=JSONObject)
print(data.btc.ticker.buy)
