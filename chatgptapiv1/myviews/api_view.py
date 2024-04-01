from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse,StreamingHttpResponse
from django.conf import settings

from chatgptapiv1.tools.jwt_token.check_jwt_tokens import check_jwt
from chatgptapiv1.tools.chatgpt.openai_response_chatgpt import OpenAIModel
from chatgptapiv1.tools.chatgpt.config import *

import traceback
import os
import json

from django.utils.decorators import method_decorator
from datetime import datetime,timezone,timedelta
import openai
import anthropic

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
        model_temperature = received_message_dict.get('model_temperature') or 0
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
    

class GPT_API_V2(View):
    
    def get(self,request):
        print(11111111)
        return HttpResponse('gpt stream test view v1')
    
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        received_message_dict = json.loads(request.body)
        
        # print(received_message_dict)
        
        inputmessage = kwargs.get('inputmessage')
        # print('inputmessage',inputmessage[0],type(inputmessage[0]))
        # print(kwargs.get('inputmessage'))
        # print('此次请求的信息',inputmessage)
        
        max_token_response = received_message_dict.get('max_token_response') or 3000
        model_temperature = received_message_dict.get('model_temperature') or 0
        open_ai_model_name = received_message_dict.get('open_ai_model_name') or 'gpt-3.5-turbo'
        systme_role_description =  received_message_dict.get('systme_role_description') or 'you are a helpful ai'
        
            
        try:
            response = openai.ChatCompletion.create(
                model=open_ai_model_name,
                messages=inputmessage,
                temperature=model_temperature,
                max_tokens=max_token_response,
            )
            return JsonResponse(response)

        except Exception as e:
            # yield json.dumps(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
            # print(traceback.format_exc())
            return JsonResponse(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
                
            

        

    
class GPT_API_STREAM_V2(View):
    
    def get(self,request):
        print(11111111111)
        return HttpResponse('gpt stream test view v2')
    
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        received_message_dict = json.loads(request.body)
        
        # print(received_message_dict)
        
        inputmessage = kwargs.get('inputmessage')
        # print('inputmessage',inputmessage[0],type(inputmessage[0]))
        # print(kwargs.get('inputmessage'))
        # print('此次请求的信息',inputmessage)
        
        max_token_response = received_message_dict.get('max_token_response') or 3000
        model_temperature = received_message_dict.get('model_temperature') or 0
        open_ai_model_name = received_message_dict.get('open_ai_model_name') or 'gpt-3.5-turbo'
        systme_role_description =  received_message_dict.get('systme_role_description') or 'you are a helpful ai'
        
        
        
        # 内置定义函数
        def chat_stream_generator(OPEN_AI_MODEL_NAME=open_ai_model_name,
                                  inputmessage=inputmessage,
                                  MODEL_TEMPERATURE=model_temperature,
                                  MAX_TOKEN_RESPONSE=max_token_response,

                                  ):
            # full_reply_content = ''
            # collected_chunks = []
            # collected_messages = []
            
            try:
                for response in openai.ChatCompletion.create(
                    model = OPEN_AI_MODEL_NAME,
                    messages = inputmessage,
                    temperature = MODEL_TEMPERATURE,
                    stream = True,
                    max_tokens = MAX_TOKEN_RESPONSE,
                ):
                    
                    # collected_chunks.append(response)  # save the event response
                    # chunk_message = response['choices'][0]['delta']  # extract the message
                    # collected_messages.append(chunk_message)  # save the message

                    
                    # print(response)
                    message = response['choices'][0]['delta'].get('content')
                    
                    if message is not None:
                        # print(message)
                        # yield json.dumps(message)+"\n"
                        yield message
                        
                        # full_reply_content=full_reply_content+message
                

            except Exception as e:
                # yield json.dumps(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
                # print(traceback.format_exc())
                yield str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话'

            # print(full_reply_content)
            # full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
            # print(f"Full conversation received: {full_reply_content}")
            

        
        # 返回数据流给前端
        return StreamingHttpResponse(chat_stream_generator(
                                        OPEN_AI_MODEL_NAME = open_ai_model_name,
                                        inputmessage=inputmessage,
                                        MODEL_TEMPERATURE=model_temperature,
                                        MAX_TOKEN_RESPONSE = max_token_response,
                                        )
                                        , 
                                        content_type='application/json')
        
        

class CLAUDE_API(View):
    
    def get(self,request):
        print(11111111)
        return HttpResponse('claude test view v1')
    
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        received_message_dict = json.loads(request.body)
        
        # print(received_message_dict)
        
        inputmessage = kwargs.get('inputmessage')
        # print(inputmessage)
        # print('inputmessage',inputmessage[0],type(inputmessage[0]))
        # print(kwargs.get('inputmessage'))
        # print('此次请求的信息',inputmessage)
        
        max_token_response = received_message_dict.get('max_token_response') or 3000
        model_temperature = received_message_dict.get('model_temperature') or 0
        claude_model_name = received_message_dict.get('claude_model_name') or 'claude-3-haiku-20240307'
        systme_role_description =  received_message_dict.get('systme_role_description') or 'you are a helpful ai'
        
        
        try:
            client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_SECRETKEY,
            )
            response = client.messages.create(
                    model=claude_model_name,
                    max_tokens=max_token_response,
                    messages=inputmessage,
                    temperature = model_temperature,
                    system = systme_role_description,
                    
                )
            data = {
                'id':response.id,
                'content':[
                        {
                        'text':response.content[0].text,
                        'type':response.content[0].type
                        }
                ],
                'model':response.model,
                'role':response.role,
                'stop_reason':response.stop_reason,
                'stop_sequence':response.stop_sequence,
                'type':response.type,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
            }
            # print('response',response,type(response))
            return JsonResponse(data)

        except Exception as e:
            # yield json.dumps(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
            # print(traceback.format_exc())
            # print(e)
            return HttpResponse(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
        
        
class CLAUDE_API_STREAM(View):
    
    def get(self,request):
        print(11111111111)
        return HttpResponse('claude stream test view v2')
    
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        received_message_dict = json.loads(request.body)
        
        # print(received_message_dict)
        
        inputmessage = kwargs.get('inputmessage')
        # print('inputmessage',inputmessage[0],type(inputmessage[0]))
        # print(kwargs.get('inputmessage'))
        # print('此次请求的信息',inputmessage)
        
        max_token_response = received_message_dict.get('max_token_response') or 3000
        model_temperature = received_message_dict.get('model_temperature') or 0
        claude_model_name = received_message_dict.get('claude_model_name') or 'claude-3-haiku-20240307'
        system_role_description =  received_message_dict.get('systme_role_description') or 'you are a helpful ai'
        
        client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_SECRETKEY,
        )
        
        # 内置定义函数
        def chat_stream_generator():
           
            
            try:
                with client.messages.stream(
                    system = system_role_description,
                    max_tokens=max_token_response,
                    messages=inputmessage,
                    model=claude_model_name,
                    temperature = model_temperature
                ) as stream:
                    for text in stream.text_stream:
                        if text is not None:
                            # print(text)
                            # yield json.dumps(message)+"\n"
                            yield text
                        
                        # full_reply_content=full_reply_content+message
                

            except Exception as e:
                # yield json.dumps(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
                # print(traceback.format_exc())
                yield str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话'

           
            

        
        # 返回数据流给前端
        return StreamingHttpResponse(chat_stream_generator(), content_type='application/json')