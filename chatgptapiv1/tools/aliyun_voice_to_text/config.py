from django.conf import settings


# 长文本外网访问的 url,所有服务器均可使用外网访问URL。
HOSTS_EXTERNAL = "https://nls-gateway.cn-shanghai.aliyuncs.com/rest/v1/tts/async"
# 长文本内网访问的url,使用阿里云上海ECS（即ECS地域为华东2（上海）），可使用内网访问URL。
HOSTS_INTERNAL = "http://nls-gateway.cn-shanghai-internal.aliyuncs.com/rest/v1/tts/async"


# 短文本外网访问的 url,所有服务器均可使用外网访问URL。
SHORT_HOSTS_EXTERNAL = "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts"
# 短文本内网访问的url,使用阿里云上海ECS（即ECS地域为华东2（上海）），可使用内网访问URL。
SHORT_HOSTS_INTERNAL = "https://nls-gateway-cn-shanghai-internal.aliyuncs.com/stream/v1/tts"


# 文本语音合成的APP_KEY
APP_KEY_WOMAN = settings.ALIYUN_APP_KEY_WOMAN
# # 临时token
# ACCESS_TOKEN = "db69a8c400f746c58c168111b7b8a1a3"

# 阿里云的access_id
ALIYUN_ACCESS_ID=settings.ALIYUN_ACCESS_ID
# 阿里云的 accesskey_secret
ALIYUN_ACCESSKEY_SECRET=settings.ALIYUN_ACCESSKEY_SECRET
# 存储在 redis 的数据库token 的key的值
ACCESS_TOKEN_KEY_IN_REDIS = settings.ALIYUN_ACCESS_TOKEN_KEY_IN_REDIS
# token 的失效时间,默认是24小时
ACCESS_TOKEN_IN_REDIS_EXPIRED_TIME = 60*60