from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse
from django.conf import settings

from chatgptapiv1.tools.jwt_token.check_jwt_tokens import check_jwt
from chatgptapiv1.tools.chatgpt.openai_response_chatgpt import OpenAIModel
from chatgptapiv1.tools.chatgpt.config import *

import traceback
import os
import json

from django.utils.decorators import method_decorator
from datetime import datetime,timezone,timedelta


# api response
class GPT_API(View):
    
    
    
    def get(self,request):
        return HttpResponse('gpt test view')
    
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        
        # print(request.body)
        received_message_dict = json.loads(request.body)
        
        # print(received_message_dict)
        
        inputmessage = kwargs.get('inputmessage') or '你好啊'
        # print(kwargs.get('inputmessage'))
        # print('此次请求的信息',inputmessage)
        
        max_token_response = received_message_dict.get('max_token_response') or 3000
        model_temperature = received_message_dict.get('model_temperature') or 1
        model_top_p = received_message_dict.get('model_top_p') or 1
        frequency_penalty = received_message_dict.get('frequency_penalty') or 0
        presence_penalty = received_message_dict.get('presence_penalty') or 0
        open_ai_model_name = received_message_dict.get('open_ai_model_name') or 'gpt-3.5-turbo'
        systme_role_description =  received_message_dict.get('systme_role_description') or 'you are a helpful ai'
        # print(systme_role_description)
        start_messages = []
        OpenAIObj = OpenAIModel(
            max_token_response=max_token_response,
            model_temperature=model_temperature,
            model_top_p=model_top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            open_ai_model_name=open_ai_model_name
            )
        try:
            response = OpenAIObj.reply_message(inputmessage,start_messages,systme_role_description)
        except Exception as e:
            response = [str(e)]
        
        reuslt = {'code':200,'result':response}
        
        return JsonResponse(reuslt)