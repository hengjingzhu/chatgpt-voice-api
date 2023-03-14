# from chatgptapiv1.tools.chatgpt.config import REDIS_HOST,REDIS_PORT,REDIS_PASSWORD,REDIS_EXPIRY_TIME,REDIS_DATABASE
# import redis


# class RedisConn():

#     def __init__(self) -> None:
#         self.redis_host = REDIS_HOST
#         self.redis_port = REDIS_PORT
#         self.redis_password = REDIS_PASSWORD
#         self.redis_expiry_time = REDIS_EXPIRY_TIME
#         self.redis_db = REDIS_DATABASE
#         self.r = redis.Redis(host = REDIS_HOST,port =REDIS_PORT,db = REDIS_DATABASE, password = REDIS_PASSWORD,decode_responses=True)


#     # def redis_conn(self):
#     #     r = redis.Redis(host = self.redis_host,port =self.redis_port,db = self.redis_db, password = self.redis_password)
#     #     return r

#     def save_message(self,key,value):
#         result = self.r.setex(key,self.redis_expiry_time,value)
#         return result

#     def get_message(self,key):
#         result = self.r.get(key)
#         return result
    
#     def delete_message(self,key):
#         self.r.delete(key)

#     def clean_database(self):
#         self.r.flushdb()    

# if __name__ == '__main__':
#     redis_conn = RedisConn()
#     print(redis_conn.save_message('david','zhu'))
#     print(redis_conn.get_message('david'))
#     # print(redis_conn.delete_message('david'))
#     print(redis_conn.clean_database())
#     print(redis_conn.get_message('david'))
    