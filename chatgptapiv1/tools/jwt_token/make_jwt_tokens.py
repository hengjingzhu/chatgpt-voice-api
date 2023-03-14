
import jwt

from django.conf import settings


class JWTTokenMethod():

    # {'username': 'davidzhu', 'APIRequestLeft': 'unlimited', 'exp': 1678218776.8427725, 'type': 'LimitedTime_UnlimitedRequest', 'status': 'success'}

    def __init__(self,username,max_tokens) -> None:
        self.token_key = settings.JWT_TOKEN_KEY
        self.username = username
        self.max_tokens = max_tokens
        #self.APIRequestLeft = APIRequestLeft
       
    # 包月套餐无限制次数客户
    def maketoken_limitedtime_unlimitedrequest(self,expiredatetime):
        
        # expiredatetime传入的必须是 datetime 格式。
        # 计算出expireunixtime过期时间,转换成 unix 时间格式,比如 1678218776.8427725
        expireunixtime = expiredatetime.timestamp()

        payload = {'username':self.username,'APIRequestLeft':'unlimited','exp':expireunixtime,'type':'LimitedTime_UnlimitedRequest','status':'success','max_tokens':self.max_tokens}

        # jwt 加密
        token = jwt.encode(payload=payload,key=self.token_key, algorithm = 'HS256')
        #print(token,type(token),'maketoken_limitedtime_unlimitedrequest')

        return token
        
    # 限制次数,不限制时间客户
    def maketoken_unlimitedtime_limitedrequest(self,APIRequestLeft):
         # 设置明文信息，以及过期时间是在1秒以后
        payload = {'username':self.username,'APIRequestLeft':APIRequestLeft,'type':'UnlimitedTime_LimitedRequest','status':'success','max_tokens':self.max_tokens}

        # jwt 加密
        token = jwt.encode(payload=payload,key=self.token_key, algorithm = 'HS256')
        #print(token,type(token),'maketoken_unlimitedtime_limitedrequest')

        return token
    
    # 超级用户，无任何限制
    def maketoken_superuser(self):

         # 设置明文信息，以及过期时间是在1秒以后
        payload = {'username':self.username,'type':'superuser','status':'success','max_tokens':self.max_tokens}

        # jwt 加密
        token = jwt.encode(payload=payload,key=self.token_key, algorithm = 'HS256')
        #print(token,type(token),'maketoken_superuser')
        return token
        
    # 解码 jwt 客户
    def decode_token(self,token):
        try:
            # jwt 解密拿到信息,如果时间过期自动抛出ExpiredSignatureError
            info = jwt.decode(jwt=token,key=self.token_key,algorithms=['HS256'])
            print(info,type(info))
            return info
        except jwt.exceptions.ExpiredSignatureError as e:
            info = {'username':self.username,'type':'withlimitedtime','status':'tokenexpired'}
            return info
        




if __name__ =='__mian__':
    # from chatgptapiv1.tools.jwt_token.make_jwt_tokens import JWTTokenMethod
    JWTTokenMethod('davidzhu').maketoken_superuser()
    token = JWTTokenMethod('davidzhu').maketoken_unlimitedtime_limitedrequest(5)
    JWTTokenMethod('davidzhu').decode_token(token)
