import jwt
import json
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
import traceback
from chatgptapiv1.models import BlackBox


# 这是一个检查 jwt token 的装饰器
def check_jwt(fn):
    def warp(request,*args,**kwargs):
        # 从请求体中获取 post 消息
        received_message_dict = json.loads(request.body)
        
        # print('received_message_dict',received_message_dict)

        # 开发环境不启动 nginx 配置
        #voice_url_base = settings.MY_HOST_NAME+settings.STATIC_URL

        #生产环境 启动 nginx 的时候配置
        voice_url_base = settings.NGINX_HOST_NAME+settings.STATIC_URL

        try:
            inputmessage = received_message_dict['inputmessage']
            if isinstance(inputmessage, str):
                inputmessage = inputmessage.strip()
            elif isinstance(inputmessage, list):
                inputmessage = inputmessage

            jwt_token = received_message_dict['authorization'].strip()
            
            # jwt 解密拿到信息
            userinfo_jwttoken = jwt.decode(jwt=jwt_token,key=settings.JWT_TOKEN_KEY,algorithms=['HS256'])
            #print(inputmessage,userinfo_jwttoken,type(userinfo_jwttoken))
            
            username_jwttoken = userinfo_jwttoken['username']
            #print(username_jwttoken)

            # 从缓存数据库中查找用户信息
            for i in range(10):
                userinfo_redis = cache.get(username_jwttoken)
                #print(userinfo_redis)
                if userinfo_redis:
                    break
                else:
                    #print(userinfo_redis)
                    voice_url = voice_url_base + 'voice/wronguser.wav'
                    result = {'code':200,'message':'您的用户名找不到,请联系老朱',"voice":voice_url}
                    return JsonResponse(result)

            #print(userinfo_redis,type(userinfo_redis))
            # 如果缓存数据库中的令牌和用户令牌不一致，告知您的令牌已经更新，请输入正确的令牌
            if jwt_token != userinfo_redis['userinfo']['jwt_token']:
                voice_url = voice_url_base + 'voice/neednewtoken.wav'
                result = {'code':200,'message':'您的令牌已经更新,请输入最新的令牌，或者请找老朱哦',"voice":voice_url}
                return JsonResponse(result)
        
            # 如果缓存数据库中的使用次数已经小于等于0了,并且用户是 UnlimitedTime_LimitedRequest,返回
            if userinfo_redis['userinfo']['customer_type'] == 'UnlimitedTime_LimitedRequest' and int(userinfo_redis['userinfo']['api_request_left'])<=0:
                voice_url = voice_url_base + 'voice/norquestquota.wav'
                result = {'code':200,'message':'对不起，您的次数已经用完, 或者请找老朱哦',"voice":voice_url}
                return JsonResponse(result)
            
            # 如果缓存数据库中的令牌和用户令牌不一致，告知您的令牌已经更新，请输入正确的令牌
            if not inputmessage:
                voice_url =voice_url_base + 'voice/nomessage.wav'
                result = {'code':200,'message':'你怎么不说话呢',"voice":voice_url}
                return JsonResponse(result)

            # 如果走到了这里，那说明是可以继续往下走的，把 userinfo_redis 信息和传输过来的 inputmessage 传给工作的函数
            kwargs['existed_userinfo_redis'] = userinfo_redis
            kwargs['inputmessage'] = inputmessage
            #print(kwargs)

        # 令牌过期客户,# jwt 解密拿到信息,如果时间过期自动抛出ExpiredSignatureError，如果解码失败就到解码失败的错误中
        except jwt.exceptions.ExpiredSignatureError as e:
            
            voice_url = voice_url_base + 'voice/token_expired.wav'
            result = {'code':200,'message':'您的令牌已经过期了,请找老朱续费哦',"voice":voice_url}
            return JsonResponse(result)

        # 令牌解码失败,令牌解码失败
        except Exception as e:
            voice_url = voice_url_base + 'voice/token_wrong.wav'
            
            print(traceback.format_exc())
            
            result = {'code':200,'message':'你的令牌不正确',"voice":voice_url}
            return JsonResponse(result)

        return fn(request,*args,**kwargs)
    return warp