# -*- coding: utf-8 -*-
import os
import time
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from chatgptapiv1.tools.aliyun_voice_to_text.config import *
from django.core.cache import caches


class GETACCESSTOKEN():

    def __init__(self) -> None:
        self.total_retry = 0
        self.max_retry = 10
        self.ALIYUN_ACCESS_ID = ALIYUN_ACCESS_ID
        self.ALIYUN_ACCESSKEY_SECRET = ALIYUN_ACCESSKEY_SECRET
        self.ACCESS_TOKEN_KEY_IN_REDIS = ACCESS_TOKEN_KEY_IN_REDIS
        self.ACCESS_TOKEN_IN_REDIS_EXPIRED_TIME = ACCESS_TOKEN_IN_REDIS_EXPIRED_TIME

    def GetAccessToken(self):
        # 创建AcsClient实例
        client = AcsClient(
            self.ALIYUN_ACCESS_ID,
            self.ALIYUN_ACCESSKEY_SECRET,
            "cn-shanghai"
        )

        # 创建request，并设置参数。
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')

        try : 
            response = client.do_action_with_exception(request)
            # print(response)

            jss = json.loads(response)
            # print(jss)
            if jss.get('Token') and jss['Token'].get('Id'):
                token = jss['Token']['Id']
                expireTime = jss['Token']['ExpireTime']
                #print("token = " + token)
                #print("expireTime = " + str(expireTime))

                return token

        except Exception as e:
            print(e)
            
    def run(self):

        # use cache database ali_voice_token
        ali_voice_token_redis = caches['ali_voice_token']

        # check the existed token in database, if existed return exited token
        existed_ali_voice_token_in_redis = ali_voice_token_redis.get(self.ACCESS_TOKEN_KEY_IN_REDIS)
        if existed_ali_voice_token_in_redis:
            return existed_ali_voice_token_in_redis

        # if not existed,get new token
        token = self.GetAccessToken()
        if token:
            # set the token to redis cache
            ali_voice_token_redis.set(self.ACCESS_TOKEN_KEY_IN_REDIS, token,self.ACCESS_TOKEN_IN_REDIS_EXPIRED_TIME)

            return token

        # if failed get new token,retry until max number reached    
        if self.total_retry <= self.max_retry:
            self.total_retry += 1
            return self.run()



# from chatgptapiv1.tools.aliyun_voice_to_text.get_access_token import GETACCESSTOKEN
if __name__ =='__main__':
    GETACCESSTOKEN().run()