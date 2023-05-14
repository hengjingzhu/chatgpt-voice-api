from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse,StreamingHttpResponse
from django.conf import settings

from chatgptapiv1.tools.jwt_token.check_jwt_tokens import check_jwt
from chatgptapiv1.tools.chatgpt.openai_response_chatgpt import OpenAIModel
from chatgptapiv1.tools.chatgpt.config import *
from chatgptapiv1.tools.bilibili_bullet_redis import RedisConn

import traceback
import os
import json

from django.utils.decorators import method_decorator





# 弹幕样式视图函数
def bullet_font_view(request):
    if request.method == 'GET':
        room_id = request.GET.get('roomid','27716860')
        return render(request,'bilibili_live_stream/font_style.html',locals())
    
def bullet_font_streaming_response(request):
    
   
    
    if request.method == 'GET':
        
        
       
        room_id = request.GET.get('roomid','27716860')
        #text = RedisConn().get_bullet_response_from_list()
        r = RedisConn()
        text = r .get_bullet_response_from_dict('play_voice_bullet'+room_id)
        print('本次信息',text)
        response = StreamingHttpResponse(content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        # response['Connection'] = 'keep-alive'
        # response['Content-Encoding'] = 'identity'

        

        def event_stream():
            
            yield f'data: {json.dumps({"text": text})}\n\n'
        
        response.streaming_content = event_stream()
        return response
        # return HttpResponse(11111)
    
    else:
        return HttpResponse('not request method')