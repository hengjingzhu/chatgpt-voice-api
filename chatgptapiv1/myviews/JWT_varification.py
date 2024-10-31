from django.views import View
from django.http import JsonResponse,HttpResponse,StreamingHttpResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from chatgptapiv1.tools.jwt_token.check_jwt_tokens import check_jwt
from chatgptapiv1.tools.coordinate_converter.coordconvert_bd09_to_wgs84 import bd09_to_wgs84
import json


# api response
class GPS_location_JWT_Varification(View):
    
    # @method_decorator(check_jwt)
    def get(self,request):
        return HttpResponse('test gps location')
    
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        
        
        received_data = json.loads(request.body)
        userinfo_redis = kwargs['existed_userinfo_redis']
        print(userinfo_redis)
        response = {"code":200,"message":'success','status':'success','userinfo_redis':userinfo_redis}
        
        # print(received_data)
        bd09_coordinate = received_data.get('coordinate')
        if bd09_coordinate and bd09_coordinate['action'] == 'transfer_location':
            bd09_longitude = bd09_coordinate['longitude']
            bd09_latitude = bd09_coordinate['latitude']
            
            # 这里需要做坐标转换。然后把转换的坐标转给前端
            print('bd09_coordinates',bd09_longitude,bd09_latitude)
            wgs84_longitude, wgs84_latitude = bd09_to_wgs84(bd09_longitude, bd09_latitude)
            print('wgs_coordinates',wgs84_longitude,wgs84_latitude)
            response['wgs_coordinates'] = {
                'longitude':wgs84_longitude,
                'latitude':wgs84_latitude,
            }
        
        return JsonResponse(response)
        