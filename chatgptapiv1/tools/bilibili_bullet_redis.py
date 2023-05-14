
#from chatgptapiv1.tools.bilibili_bullet_redis import RedisConn

import redis
import json

from django.conf import settings

class RedisConn():

    def __init__(self,REDIS_HOST=settings.ALIYUN_REDIS_HOST,REDIS_PORT=settings.ALIYUN_REDIS_PORT,REDIS_DATABASE=3,REDIS_PASSWORD=settings.ALIYUN_REDIS_PASSWORD) -> None:
        self.redis_host = REDIS_HOST
        self.redis_port = REDIS_PORT
        self.redis_password = REDIS_PASSWORD
        self.redis_db = REDIS_DATABASE
        self.r = redis.Redis(host = REDIS_HOST,port =REDIS_PORT,db = REDIS_DATABASE, password = REDIS_PASSWORD,decode_responses=True)
        
    def get_bullet_response_from_list(self,listkey='processed_bullet_list23141761'):
        bullet_response = self.r.rpop(listkey)
        
        if bullet_response:
            return json.loads(bullet_response)
        
    
    def get_bullet_response_from_dict(self,dickkey='play_voice_bullet23141761'):
        bullet_response = self.r.get(dickkey)
        print(bullet_response,'get_bullet_response_from_dict')
        if bullet_response:
            return json.loads(bullet_response)
        
    def reset_bullet_response_from_dict(self,dickkey='play_voice_bullet23141761'):
        
        message = json.dumps({'text':'没人互动了','response':'胡言乱语中。。。。','nickname':'本小姐'})
        bullet_response = self.r.set(dickkey,message)
        if bullet_response:
            return True

if __name__ == '__main__':
    # RedisConn().get_bullet_response_from_list('processed_bullet_list23141761')
    RedisConn().get_bullet_response_from_dict('play_voice_bullet23141761')
    # RedisConn().reset_bullet_response_from_dict('play_voice_bullet23141761')