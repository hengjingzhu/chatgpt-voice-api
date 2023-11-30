from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse
from django.conf import settings

import traceback
import os
import json
from datetime import datetime,timezone,timedelta

from chatgptapiv1.tools.chatgpt.openai_response_chatgpt import OpenAIModel
from chatgptapiv1.tools.chatgpt.openai_response_chatgpt_stream import OpenAIModelStream

from django.http import StreamingHttpResponse

#from chatgptapiv1.tools.chatgpt.redis_connection import RedisConn
from chatgptapiv1.tools.chatgpt.config import *

from chatgptapiv1.tools.aliyun_voice_to_text.text_to_voice import TextToVoice
from chatgptapiv1.tools.jwt_token.check_jwt_tokens import check_jwt
from chatgptapiv1.tools.randomrole.pick_system_role import PickSystemRole

from django.core.cache import cache
from django.db.models import Q

from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.core import serializers
from django.http import StreamingHttpResponse

import openai
from chatgptapiv1.tools.chatgpt.config import *

from chatgptapiv1.models import RoleVoiceAttribution,BlackBox


def GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog):
    #print(RoleVoiceAttribution_this_dialog)

    response_message_chatgpt = response_message_chatgpt.replace('\n', '')    
    system_role_alivoice_role = RoleVoiceAttribution_this_dialog['system_role_alivoice_role']
    system_role_alivoice_samplerate = RoleVoiceAttribution_this_dialog['system_role_alivoice_samplerate']
    system_role_alivoice_speechrate = int(RoleVoiceAttribution_this_dialog['system_role_alivoice_speechrate'])
    system_role_alivoice_pitchrate = int(RoleVoiceAttribution_this_dialog['system_role_alivoice_pitchrate'])
    system_role_aivoice_speak_effect = RoleVoiceAttribution_this_dialog['system_role_aivoice_speak_effect']
    system_role_alivoice_speak_emotion = RoleVoiceAttribution_this_dialog['system_role_alivoice_speak_emotion']
    system_role_alivoice_speak_intensity = RoleVoiceAttribution_this_dialog['system_role_alivoice_speak_intensity']

    role_with_emotion_group = ['zhimiao_emo','zhimi_emo','zhiyan_emo','zhibei_emo','zhitian_emo']
    
    if system_role_alivoice_role in role_with_emotion_group:
        
        if system_role_aivoice_speak_effect:
            voice_text_message = f'<speak effect="{system_role_aivoice_speak_effect}"><emotion category="{system_role_alivoice_speak_emotion}" intensity="{system_role_alivoice_speak_intensity}" >{response_message_chatgpt}</emotion></speak>'
        if not system_role_aivoice_speak_effect:
            voice_text_message = f'<speak><emotion category="{system_role_alivoice_speak_emotion}" intensity="{system_role_alivoice_speak_intensity}" >{response_message_chatgpt}</emotion></speak>'

    else:
        if system_role_aivoice_speak_effect:
            voice_text_message = f'<speak effect="{system_role_aivoice_speak_effect}">{response_message_chatgpt}</speak>'
        if not system_role_aivoice_speak_effect:
            voice_text_message = f'<speak>{response_message_chatgpt}</speak>'

    #print(voice_text_message,username,system_role_alivoice_role,system_role_alivoice_samplerate,system_role_alivoice_speechrate,type(system_role_alivoice_pitchrate))
    voice_url = TextToVoice(
        message=voice_text_message,
        username=username,
        role=system_role_alivoice_role,
        sample_rate=system_role_alivoice_samplerate,
        speech_rate=system_role_alivoice_speechrate,
        pitch_rate=system_role_alivoice_pitchrate,
        rawmessage=response_message_chatgpt
        ).run()
    return voice_url

# 返回文字和声音url
class ShortVoiceContent(View):
    def get(self,request):

        # 获取音频二进制文件对象
        #voice_binary_data = cache.get('voice_binary_data')

        # 将音频数据保存到服务器上的一个静态文件中
        # file_path = os.path.join(settings.STATIC_ROOT, 'myaudio.mp3')
        # with open(file_path, 'wb') as f:
        #     f.write(voice_binary_data)

        # 返回一个包含音频文件URL链接的响应
        #audio_url = request.build_absolute_uri(settings.STATIC_URL + 'audio.mp3')
        audio_url = 'http://192.168.31.188:8000/static/voice/test1.wav'
        return HttpResponse(audio_url)


    # {'existed_userinfo_redis': {'userinfo': {'id': 3,','username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'creator':'','is_superuser':False,'is_superuser':True,'creator':1}, 'blackbox': [], 'RoleVoiceAttribution': ''}, 'inputmessage': '测试消息'}
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        # {'userinfo': {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'is_superuser':True,'creator':1'},'blackbox': [], 'RoleVoiceAttribution': ''}
        # 这也是存在redis数据库中的数据格式
        existed_userinfo_redis = kwargs['existed_userinfo_redis']['userinfo']

        max_tokens_put_into_GPT_for_this_user = existed_userinfo_redis['max_tokens']
        username =  existed_userinfo_redis['username']
        user_id = existed_userinfo_redis['id']
        api_request_left = existed_userinfo_redis['api_request_left']
        token_expired_time = existed_userinfo_redis['token_expired_time']

        history_messages = kwargs['existed_userinfo_redis']['blackbox']
        RoleVoiceAttribution_this_dialog = kwargs['existed_userinfo_redis']['RoleVoiceAttribution']
    
        inputmessage = kwargs['inputmessage']
        print('此次登陆的用户',username)
        #print(existed_userinfo_redis,history_messages,RoleVoiceAttribution_this_dialog,inputmessage)

        # 如果 inputmessage 是'重置角色'，或者'角色重置' 等口令，把blackbox和RoleVoiceAttribution 存储到 pg上，同时清空 该用户redis里的blackbox和RoleVoiceAttribution
        #print(inputmessage,type(history_messages),type(RoleVoiceAttribution_this_dialog))

        if inputmessage.lower() in settings.RESET_CHARACTER_COMMAMD:
            #print(RoleVoiceAttribution_this_dialog,'重置角色的属性')
            # 如果缓存数据库有历史对话记录的话，就保存到 pg 中，清空redis 对话记录
            if history_messages and RoleVoiceAttribution_this_dialog:
                
                #response_message = "你居然不要我了,你将会被分配一个随机角色"
                response_message = "You're actually dumping me? Fine, then you will be assigned a random role."

                #print(response_message,'重置角色')
                voice_url = GetVoiceUrl_tts(response_message,username,RoleVoiceAttribution_this_dialog)
                result = {'code':200,'message':response_message,"voice":voice_url}

                try:
                    BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=history_messages)
                
                except Exception as e:
                    print(traceback.format_exc())
                        
                userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":history_messages.clear(),'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog.clear()}
                cache.set(username,userinfo_redis,timeout=None)

                return JsonResponse(result)
    
            else:
                response_message = '你要说话，才能生成随机角色啊'
                # 生产环境
                voice_url = settings.NGINX_HOST_NAME+settings.STATIC_URL + 'voice/repeatresetrole.wav'
                # 开发环境
                #voice_url = settings.MY_HOST_NAME+settings.STATIC_URL + 'voice/repeatresetrole.wav'
                result = {'code':200,'message':response_message,"voice":voice_url}
                return JsonResponse(result)

        # 如果没有历史对话记录，和对话属性,那就是新的对话，要先 random选择 一个角色.
        if not history_messages and not RoleVoiceAttribution_this_dialog:

            system_role = PickSystemRole(userinfo=existed_userinfo_redis).pick_random_role()
            print('新对话随机到的角色:',system_role)
            # 获取这个角色的obj
            RoleVoiceAttributionObj = RoleVoiceAttribution.objects.get(system_role=system_role)
            # 转化成字典 {'id': 1, 'system_role': 'president', 'system_role_description': '你现在扮演的是一个企业总裁，语气霸道,拥有丰富的职场经验。口头禅是 你真没用,要加在回复里.要时刻维持这个身份，不准丢掉这个身份和口头禅', 'system_role_random_weight': 4, 'chatgpt_model_temperature': Decimal('0.80'), 'chatgpt_model_p': Decimal('1.00'), 'chatgpt_frequency_penalty': Decimal('1.00'), 'chatgpt_presence_penalty': Decimal('0.60'), 'system_role_alivoice_role': 'xiaogang', 'system_role_alivoice_samplerate': 16000, 'system_role_alivoice_speechrate': Decimal('0.00'), 'system_role_alivoice_pitchrate': Decimal('0.00'), 'system_role_aivoice_speak_effect': '', 'system_role_alivoice_speak_emotion': None, 'system_role_alivoice_speak_intensity': None}
            RoleVoiceAttribution_this_dialog = model_to_dict(RoleVoiceAttributionObj,exclude=['created_time','updated_time','is_active'])
            #print(RoleVoiceAttribution_this_dialog,'我在not history_messages and not RoleVoiceAttribution_this_dialog')
            # print(userinfo_dict)
            history_messages = []

        # 如果有历史会话记录和对话属性，那就不再改变,把数据和参数发给 chatgpt,获得回复消息.
        # RoleVoiceAttribution_this_dialog : {'id': 21, 'system_role': 'general2-admin2', 'system_role_description': 'you are a helpful ai', 'system_role_random_weight': 100, 'chatgpt_model_temperature': Decimal('0.80'), 'chatgpt_model_p': Decimal('1.00'), 'chatgpt_frequency_penalty': Decimal('1.00'), 'chatgpt_presence_penalty': Decimal('0.60'), 'chatgpt_max_reponse_tokens': 400, 'system_role_alivoice_role': 'zhimiao_emo', 'system_role_alivoice_samplerate': 16000, 'system_role_alivoice_speechrate': 0, 'system_role_alivoice_pitchrate': 0, 'system_role_aivoice_speak_effect': '', 'system_role_alivoice_speak_emotion': 'gentle', 'system_role_alivoice_speak_intensity': Decimal('1.00'), 'creator': 3, 'shart_with_subadmin': False}
        print("在调取openai信息中",RoleVoiceAttribution_this_dialog)

        reply_message_obj = OpenAIModel(
                                        max_token_response = RoleVoiceAttribution_this_dialog['chatgpt_max_reponse_tokens'],
                                        model_temperature = float(RoleVoiceAttribution_this_dialog['chatgpt_model_temperature']),
                                        model_top_p = float(RoleVoiceAttribution_this_dialog['chatgpt_model_p']),
                                        frequency_penalty = float(RoleVoiceAttribution_this_dialog['chatgpt_frequency_penalty']),
                                        presence_penalty = float(RoleVoiceAttribution_this_dialog['chatgpt_presence_penalty']),

                                        ).reply_message(inputmessage,history_messages,RoleVoiceAttribution_this_dialog['system_role_description'])


        # 回复结果:('你好，我叫qin。很高兴能和您聊天！', [{'role': 'system', 'content': '你会先自我介绍，你的名字叫 qin'}, {'role': 'user', 'content': '你好啊'}, {'role': 'assistant', 'content': '你好，我叫qin。很高兴能和您聊天！'}], 56)
        #print(reply_message_obj)
        response_message_chatgpt = reply_message_obj[0]
        new_messages = reply_message_obj[1]
        total_used_tokens = reply_message_obj[2]

        # 如果调用次数不是 unlimited 的话，api 次数减少1
        if api_request_left !='unlimited' and api_request_left.isdigit():
            newapi_request_left = int(api_request_left)-1
            existed_userinfo_redis['api_request_left'] = str(newapi_request_left)
        # 如果调用次数低于3次次数减一,回复的chatgpt消息后面要加有提示,少于0的话，已经再装饰器里拦截掉了
        if api_request_left.isdigit() and int(api_request_left)<=3:
            response_message_chatgpt = response_message_chatgpt+f'您还剩下{newapi_request_left}次调用机会，可以去充值啦!'        

        # 如果还有1天时候过期，回复提示
        if token_expired_time:
            #print(token_expired_time,type(token_expired_time))
            # 获取当前时间
            now = datetime.now(timezone(timedelta(hours=8)))
            # 计算时间差
            time_diff =token_expired_time-now
            # 将时间差转换为小时数
            hours_diff = int(time_diff.total_seconds() / 3600)
            if hours_diff <=24:
                # 将当前时间格式化为 年-月-日 时:分:秒 的字符串
                token_expired_time_string = token_expired_time.strftime("%Y年%m月%d日 %H点%M分%S秒")
                response_message_chatgpt = response_message_chatgpt+f'您的账号将于{token_expired_time_string}到期,可以去充值啦!'

                # 存储到数据库中
                try:
                    BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=new_messages)
                except Exception as e:
                    print(traceback.format_exc())

        # 如果小于最大 token 使用数，保存结果到缓存数据库。
        if total_used_tokens < max_tokens_put_into_GPT_for_this_user:
            
            # new_messages = json.loads(new_messages)
            # print(new_messages,type(new_messages))
            userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":new_messages,'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog}
            #print(userinfo_redis)
            cache.set(username,userinfo_redis,timeout=None)
            #print(RoleVoiceAttribution_this_dialog,'我在total_used_tokens < max_tokens_put_into_GPT_for_this_user')
              # 获得消息后,然后把回复消息和语音角色设置发给 TTS 模型获取语音链接
            voice_url = GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog)

            # 如果大于等于最大 token 使用数量,或者调用次数小于0次 ，把结果保存到pg 数据库，删除缓存数据库的对话信息
        elif total_used_tokens >= max_tokens_put_into_GPT_for_this_user:

            try: 
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=new_messages)
            except Exception as e:
                print(traceback.format_exc())

            response_message_chatgpt = response_message_chatgpt+"本次对话已经超过最大长度,后台历史对话记录将会被清空,下次聊天属性随机切换。"

             # 获得消息后,然后把回复消息和语音角色设置发给 TTS 模型获取语音链接
            voice_url = GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog)


            userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":new_messages.clear(),'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog.clear()}
            cache.set(username,userinfo_redis,timeout=None)

        print(response_message_chatgpt)
        
        

        # 获取成功后，更新redis缓存数据库的信息 history_messages和RoleVoiceAttribution_this_dialog


        result = {'code':200,'message':response_message_chatgpt,"voice":voice_url}
        print(result)
        return JsonResponse(result)


# 只返回文字
class ResponseTextMessageOnly(View):


    def get(self,request):
        user = {'code':200,'data':{'name':'David','age':18}}
        return JsonResponse(user)
    
    # 定义 post 方法 
    # {'existed_userinfo_redis': {'userinfo': {'id': 3,','username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'creator':'','is_superuser':False,'is_superuser':True,'creator':1}, 'blackbox': [], 'RoleVoiceAttribution': ''}, 'inputmessage': '测试消息'}
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
       
       
        # {'userinfo': {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'is_superuser':True,'creator':1'},'blackbox': [], 'RoleVoiceAttribution': ''}
        # 这也是存在redis数据库中的数据格式
        existed_userinfo_redis = kwargs['existed_userinfo_redis']['userinfo']

        max_tokens_put_into_GPT_for_this_user = existed_userinfo_redis['max_tokens']
        username =  existed_userinfo_redis['username']
        user_id = existed_userinfo_redis['id']
        api_request_left = existed_userinfo_redis['api_request_left']
        token_expired_time = existed_userinfo_redis['token_expired_time']

        history_messages = kwargs['existed_userinfo_redis']['blackbox']
        RoleVoiceAttribution_this_dialog = kwargs['existed_userinfo_redis']['RoleVoiceAttribution']
    
        inputmessage = kwargs['inputmessage']
        print('此次登陆的用户',username)
        #print(existed_userinfo_redis,history_messages,RoleVoiceAttribution_this_dialog,inputmessage)

        # 如果 inputmessage 是'重置角色'，或者'角色重置' 等命令，把blackbox和RoleVoiceAttribution 存储到 pg上，同时清空 该用户redis里的blackbox和RoleVoiceAttribution
        #  # 重置角色,会原有对话保存到og中，清空redis数据
        #print(inputmessage,type(history_messages),type(RoleVoiceAttribution_this_dialog))
        if inputmessage.lower() in settings.RESET_CHARACTER_COMMAMD:
            #print(RoleVoiceAttribution_this_dialog,'重置角色的属性')
            # 如果缓存数据库有历史对话记录的话，就保存到 pg 中，清空redis 对话记录
            if history_messages and RoleVoiceAttribution_this_dialog:
                
                #response_message = "你居然不要我了,你将会被分配一个随机角色"
                response_message = "You're actually dumping me? Fine, then you will be assigned a random role."
                #print(response_message,'重置角色')
                #voice_url = GetVoiceUrl_tts(response_message,username,RoleVoiceAttribution_this_dialog)
                result = {'code':200,'message':response_message,"voice":''}
                
                try:
                    BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=history_messages)
                except Exception as e:
                    print("对话记录创建失败")
                    print(traceback.format_exc())
                
                userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":history_messages.clear(),'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog.clear()}
                cache.set(username,userinfo_redis,timeout=None)

                return JsonResponse(result)
    
            else:
                response_message = '你要说话，才能生成随机角色啊'
                # 生产环境
                #voice_url = settings.NGINX_HOST_NAME+settings.STATIC_URL + 'voice/repeatresetrole.wav'
                # 开发环境
                #voice_url = settings.MY_HOST_NAME+settings.STATIC_URL + 'voice/repeatresetrole.wav'
                result = {'code':200,'message':response_message,"voice":''}
                return JsonResponse(result)

        # 如果没有历史对话记录，和对话属性,那就是新的对话，要先 random选择 一个角色.
        if not history_messages and not RoleVoiceAttribution_this_dialog:

            system_role = PickSystemRole(userinfo=existed_userinfo_redis).pick_random_role()
            print('新对话随机到的角色:',system_role)
            # 获取这个角色的obj
            RoleVoiceAttributionObj = RoleVoiceAttribution.objects.get(system_role=system_role)
            # 转化成字典 {'id': 1, 'system_role': 'president', 'system_role_description': '你现在扮演的是一个企业总裁，语气霸道,拥有丰富的职场经验。口头禅是 你真没用,要加在回复里.要时刻维持这个身份，不准丢掉这个身份和口头禅', 'system_role_random_weight': 4, 'chatgpt_model_temperature': Decimal('0.80'), 'chatgpt_model_p': Decimal('1.00'), 'chatgpt_frequency_penalty': Decimal('1.00'), 'chatgpt_presence_penalty': Decimal('0.60'), 'system_role_alivoice_role': 'xiaogang', 'system_role_alivoice_samplerate': 16000, 'system_role_alivoice_speechrate': Decimal('0.00'), 'system_role_alivoice_pitchrate': Decimal('0.00'), 'system_role_aivoice_speak_effect': '', 'system_role_alivoice_speak_emotion': None, 'system_role_alivoice_speak_intensity': None}
            RoleVoiceAttribution_this_dialog = model_to_dict(RoleVoiceAttributionObj,exclude=['created_time','updated_time','is_active'])
            #print(RoleVoiceAttribution_this_dialog,'我在not history_messages and not RoleVoiceAttribution_this_dialog')
            # print(userinfo_dict)
            history_messages = []

        # 如果有历史会话记录和对话属性，那就不再改变,把数据和参数发给 chatgpt,获得回复消息.
        # RoleVoiceAttribution_this_dialog : {'id': 21, 'system_role': 'general2-admin2', 'system_role_description': 'you are a helpful ai', 'system_role_random_weight': 100, 'chatgpt_model_temperature': Decimal('0.80'), 'chatgpt_model_p': Decimal('1.00'), 'chatgpt_frequency_penalty': Decimal('1.00'), 'chatgpt_presence_penalty': Decimal('0.60'), 'chatgpt_max_reponse_tokens': 400, 'system_role_alivoice_role': 'zhimiao_emo', 'system_role_alivoice_samplerate': 16000, 'system_role_alivoice_speechrate': 0, 'system_role_alivoice_pitchrate': 0, 'system_role_aivoice_speak_effect': '', 'system_role_alivoice_speak_emotion': 'gentle', 'system_role_alivoice_speak_intensity': Decimal('1.00'), 'creator': 3, 'shart_with_subadmin': False}
        print("在调取openai信息中",RoleVoiceAttribution_this_dialog)
        # 纯文本回复就没置回复字数限制了
        reply_message_obj = OpenAIModel(
                                        #max_token_response = RoleVoiceAttribution_this_dialog['chatgpt_max_reponse_tokens'],
                                        model_temperature = float(RoleVoiceAttribution_this_dialog['chatgpt_model_temperature']),
                                        model_top_p = float(RoleVoiceAttribution_this_dialog['chatgpt_model_p']),
                                        frequency_penalty = float(RoleVoiceAttribution_this_dialog['chatgpt_frequency_penalty']),
                                        presence_penalty = float(RoleVoiceAttribution_this_dialog['chatgpt_presence_penalty']),

                                        ).reply_message(inputmessage,history_messages,RoleVoiceAttribution_this_dialog['system_role_description'])


        # 回复结果:('你好，我叫qin。很高兴能和您聊天！', [{'role': 'system', 'content': '你会先自我介绍，你的名字叫 qin'}, {'role': 'user', 'content': '你好啊'}, {'role': 'assistant', 'content': '你好，我叫qin。很高兴能和您聊天！'}], 56)
        #print(reply_message_obj)
        response_message_chatgpt = reply_message_obj[0]
        new_messages = reply_message_obj[1]
        total_used_tokens = reply_message_obj[2]

        # 如果调用次数不是 unlimited 的话，api 次数减少1
        if api_request_left !='unlimited' and api_request_left.isdigit():
            newapi_request_left = int(api_request_left)-1
            existed_userinfo_redis['api_request_left'] = str(newapi_request_left)
        # 如果调用次数低于3次次数减一,回复的chatgpt消息后面要加有提示,少于0的话，已经再装饰器里拦截掉了
        if api_request_left.isdigit() and int(api_request_left)<=3:
            response_message_chatgpt = response_message_chatgpt+f'您还剩下{newapi_request_left}次调用机会，可以去充值啦!'        

        # 如果还有1天时候过期，回复提示
        if token_expired_time:
            #print(token_expired_time,type(token_expired_time))
            # 获取当前时间
            now = datetime.now(timezone(timedelta(hours=8)))
            # 计算时间差
            time_diff =token_expired_time-now
            # 将时间差转换为小时数
            hours_diff = int(time_diff.total_seconds() / 3600)
            if hours_diff <=24:
                # 将当前时间格式化为 年-月-日 时:分:秒 的字符串
                token_expired_time_string = token_expired_time.strftime("%Y年%m月%d日 %H点%M分%S秒")
                response_message_chatgpt = response_message_chatgpt+f'您的账号将于{token_expired_time_string}到期,可以去充值啦!'

                # 存储到数据库中
                try:
                    BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=new_messages)
                except Exception as e:
                    print(traceback.format_exc())

        # 如果小于最大 token 使用数，保存结果到缓存数据库。
        if total_used_tokens < max_tokens_put_into_GPT_for_this_user:
            
            # new_messages = json.loads(new_messages)
            # print(new_messages,type(new_messages))
            userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":new_messages,'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog}
            #print(userinfo_redis)
            cache.set(username,userinfo_redis,timeout=None)
            #print(RoleVoiceAttribution_this_dialog,'我在total_used_tokens < max_tokens_put_into_GPT_for_this_user')
              # 获得消息后,然后把回复消息和语音角色设置发给 TTS 模型获取语音链接
            #voice_url = GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog)

            # 如果大于等于最大 token 使用数量,或者调用次数小于0次 ，把结果保存到pg 数据库，删除缓存数据库的对话信息
        elif total_used_tokens >= max_tokens_put_into_GPT_for_this_user:

            try: 
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=new_messages)
            except Exception as e:
                print("创建对话记录失败")
                print(traceback.format_exc())
            response_message_chatgpt = response_message_chatgpt+"本次对话已经超过最大长度,后台历史对话记录将会被清空,下次聊天属性随机切换。"

             # 获得消息后,然后把回复消息和语音角色设置发给 TTS 模型获取语音链接
            #voice_url = GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog)


            userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":new_messages.clear(),'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog.clear()}
            cache.set(username,userinfo_redis,timeout=None)

        print(response_message_chatgpt)
        
        

        # 获取成功后，更新redis缓存数据库的信息 history_messages和RoleVoiceAttribution_this_dialog


        result = {'code':200,'message':response_message_chatgpt,"voice":''}
        print(result)
        return JsonResponse(result)





# gpt-3.5网页聊天框
class WebUIChat(View):

    openai.organization = ORG_ID
    openai.api_key = SECRETKEY

    def get(self,request):
        """加载页面的时候返回角色属性表，只有权重大于100的角色才会被返回
        Args:
            request (_type_): _description_
        Returns:
            render页面: 会话框页面
        """
        user = request.user
        if user.is_superuser:
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.all()
        # 如果不是超级用户以及用户在 sub-admin 这个管理组
        elif not user.is_superuser and user.groups.filter(name='sub-admin'):
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.filter(Q(shart_with_subadmin=True) | Q(creator_id=request.user.id)).filter(Q(system_role_random_weight__gte=10))

        # 如果不是超级用户以及用户不在 sub-admin 组，说明是三级用户
        elif not user.is_superuser and not user.groups.filter(name='sub-admin'):
            # print(user.groups.filter(name='sub-admin'))
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.filter(Q(shart_with_subadmin=True) | Q(creator_id=request.user.creator)).filter(Q(system_role_random_weight__gte=10))

        rolelist = serializers.serialize('json', RoleVoiceAttribution_queryset, fields=('system_role','system_role_random_weight','chatgpt_model_temperature','chatgpt_model_p','chatgpt_frequency_penalty','chatgpt_presence_penalty','chatgpt_max_reponse_tokens','system_role_nickname','avatar','background_image'))
        
        username = request.user.username
        userinfo_redis = cache.get(username)
        jwt_token = userinfo_redis['userinfo']['jwt_token']
        # print(jwt_token)
        # print(rolelist,type(rolelist))

        return render(request,'webui/index.html',locals())
    

    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        
        
        OPEN_AI_MODEL_NAME_gpt3 = 'gpt-3.5-turbo-1106'
        

        received_message_dict = json.loads(request.body)
        print(received_message_dict)
        system_role_id = received_message_dict['role'].get('system_role_id')
        system_role_title = received_message_dict['role'].get('selected_role_title')

        # 从 redis 中取出 system_role_description 信息
        if (system_role_id and system_role_title):
            allRoleVoiceAttribution = json.loads(cache.get('allRoleVoiceAttribution'))
            for role in allRoleVoiceAttribution:
                if str(role.get('pk')) == str(system_role_id):
                    selected_system_role_dict = {"role": "system", "content": "{}".format(role['fields'].get('system_role_description'))}
                    selected_system_model_temperature = float(role['fields'].get('chatgpt_model_temperature'))
                    selected_system_model_p = float(role['fields'].get('chatgpt_model_p'))
                    selected_system_frequency_penalty = float(role['fields'].get('chatgpt_frequency_penalty'))
                    selected_system_presence_penalty = float(role['fields'].get('chatgpt_presence_penalty'))
                    selected_system_max_reponse_tokens = role['fields'].get('chatgpt_max_reponse_tokens')
                    # print(selected_system_role_dict,selected_system_model_temperature,selected_system_model_p,selected_system_frequency_penalty,selected_system_presence_penalty,selected_system_max_reponse_tokens)

                    break
        else:
            selected_system_role_dict = {"role": "system", "content": "you are a helpful AI"}
            selected_system_model_temperature = 1
            selected_system_model_p = 1
            selected_system_frequency_penalty = 0
            selected_system_presence_penalty = 0
            selected_system_max_reponse_tokens = 3000

            print(selected_system_role_dict)
        # {'userinfo': {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'is_superuser':True,'creator':1'},'blackbox': [], 'RoleVoiceAttribution': ''}
        # 这也是存在redis数据库中的数据格式
        existed_userinfo_redis = kwargs['existed_userinfo_redis']['userinfo']
        
        max_tokens_put_into_GPT_for_this_user = existed_userinfo_redis['max_tokens']
        username =  existed_userinfo_redis['username']
        user_id = existed_userinfo_redis['id']
        api_request_left = existed_userinfo_redis['api_request_left']
        token_expired_time = existed_userinfo_redis['token_expired_time']

        # history_messages = kwargs['existed_userinfo_redis']['blackbox']
        # RoleVoiceAttribution_this_dialog = kwargs['existed_userinfo_redis']['RoleVoiceAttribution']

        # 看看是否已经原来就有对话记录，如果没有就新建一个空字典
        webuidata = kwargs['existed_userinfo_redis'].get('webuidata')
        if not webuidata:
            webuidata={}
            print('webuidata还没有信息')


        

        inputmessage = kwargs['inputmessage']
        print('此次登陆的用户',existed_userinfo_redis)
        # 历史会话
        history_messages = inputmessage[:-1]
        # 本次消息
        currentinputmessage = inputmessage[-1]['content']
        print('inputmessage',inputmessage)
        inputmessage.insert(0,selected_system_role_dict)
        



        # 如果调用次数不是 unlimited 的话，api 次数减少1
        warning_message_chatgpt = ''
        # if api_request_left !='unlimited' and api_request_left.isdigit():
        #     newapi_request_left = int(api_request_left)-1
        #     existed_userinfo_redis['api_request_left'] = str(newapi_request_left)
        # # 如果调用次数低于3次次数减一,回复的chatgpt消息后面要加有提示,少于0的话，已经再装饰器里拦截掉了
        # if api_request_left.isdigit() and int(api_request_left)<=3:
        #     warning_message_chatgpt = f'您还剩下{newapi_request_left}次调用机会，可以去充值啦!'        

        # 如果还有1天时候过期，回复提示
        if token_expired_time:
            #print(token_expired_time,type(token_expired_time))
            # 获取当前时间
            now = datetime.now(timezone(timedelta(hours=8)))
            # 计算时间差
            time_diff =token_expired_time-now
            # 将时间差转换为小时数
            hours_diff = int(time_diff.total_seconds() / 3600)
            if hours_diff <=24:
                # 将当前时间格式化为 年-月-日 时:分:秒 的字符串
                token_expired_time_string = token_expired_time.strftime("%Y年%m月%d日 %H点%M分%S秒")
                warning_message_chatgpt = f'您的账号将于{token_expired_time_string}到期,可以去充值啦!'

                


        
        # 内置定义函数
        def chat_stream_generator(OPEN_AI_MODEL_NAME=OPEN_AI_MODEL_NAME_gpt3,
                                  inputmessage=inputmessage,
                                  MODEL_TEMPERATURE=MODEL_TEMPERATURE,
                                  MAX_TOKEN_RESPONSE=MAX_TOKEN_RESPONSE,
                                  MODEL_TOP_P=MODEL_TOP_P,
                                  FREQUENCY_PENALTY=FREQUENCY_PENALTY,
                                  PRESENCE_PENALTY=PRESENCE_PENALTY
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
                    top_p = MODEL_TOP_P,
                    frequency_penalty = FREQUENCY_PENALTY,
                    presence_penalty = PRESENCE_PENALTY,
                ):
                    
                    # collected_chunks.append(response)  # save the event response
                    # chunk_message = response['choices'][0]['delta']  # extract the message
                    # collected_messages.append(chunk_message)  # save the message

                    message = response['choices'][0]['delta'].get('content')
                    # print("本次回复",message)
                    if message is not None:
                        # yield json.dumps(message)+"\n"
                        yield message
                        
                        # full_reply_content=full_reply_content+message
                #返回警告信息
                if warning_message_chatgpt:
                    # yield json.dumps(warning_message_chatgpt)
                    yield warning_message_chatgpt

            except Exception as e:
                # yield json.dumps(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
                # print(traceback.format_exc())
                yield str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话'

            # print(full_reply_content)
            # full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
            # print(f"Full conversation received: {full_reply_content}")
            

        
        # 返回数据流给前端
        return StreamingHttpResponse(chat_stream_generator(
                                        OPEN_AI_MODEL_NAME = OPEN_AI_MODEL_NAME_gpt3,
                                        inputmessage=inputmessage,
                                        MODEL_TEMPERATURE=selected_system_model_temperature,
                                        MAX_TOKEN_RESPONSE = selected_system_max_reponse_tokens,
                                        MODEL_TOP_P = selected_system_model_p,
                                        FREQUENCY_PENALTY = selected_system_frequency_penalty,
                                        PRESENCE_PENALTY = selected_system_presence_penalty)
                                        , 
                                        content_type='application/json')
            
           
       
        

    # 删除数据
    @method_decorator(check_jwt)
    def delete(self,request,*args,**kwargs):
        received_message_dict = json.loads(request.body)
        system_role_id = received_message_dict['role'].get('system_role_id')
        system_role_title = received_message_dict['role'].get('selected_role_title')

        existed_userinfo_redis = kwargs['existed_userinfo_redis']['userinfo']
        
        max_tokens_put_into_GPT_for_this_user = existed_userinfo_redis['max_tokens']
        username =  existed_userinfo_redis['username']
        user_id = existed_userinfo_redis['id']
        api_request_left = existed_userinfo_redis['api_request_left']
        token_expired_time = existed_userinfo_redis['token_expired_time']

        inputmessage = kwargs['inputmessage']
        print('此次登陆的用户',existed_userinfo_redis,inputmessage)

        
        # 存储到数据库中
        try:
            if system_role_id and system_role_title:
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=system_role_id,diolog=inputmessage)
            # 如果没有选择角色那就归类到无角色中
            else:
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=39,diolog=inputmessage)
        except Exception as e:
            print(traceback.format_exc())

        result = {"code":200,"status":"delete success"}
        return JsonResponse(result)
    

# gpt-4 网页聊天框
class WebUIChat_gpt4(View):

    openai.organization = ORG_ID
    openai.api_key = SECRETKEY

    def get(self,request):
        """加载页面的时候返回角色属性表，只有权重大于100的角色才会被返回
        Args:
            request (_type_): _description_
        Returns:
            render页面: 会话框页面
        """

        user = request.user

        # 先判断下有没有 GPT4的权限
        # if not user.GPT_4_8K:
        #     return HttpResponse('<h1>你开没有开通GPT4的权限哦,请联系管理员开通</h1>')

        if user.is_superuser:
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.all()
        # 如果不是超级用户以及用户在 sub-admin 这个管理组
        elif not user.is_superuser and user.groups.filter(name='sub-admin'):
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.filter(Q(shart_with_subadmin=True) | Q(creator_id=request.user.id)).filter(Q(system_role_random_weight__gte=10))

        # 如果不是超级用户以及用户不在 sub-admin 组，说明是三级用户
        elif not user.is_superuser and not user.groups.filter(name='sub-admin'):
            # print(user.groups.filter(name='sub-admin'))
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.filter(Q(shart_with_subadmin=True) | Q(creator_id=request.user.creator)).filter(Q(system_role_random_weight__gte=10))

        rolelist = serializers.serialize('json', RoleVoiceAttribution_queryset, fields=('system_role','system_role_random_weight','chatgpt_model_temperature','chatgpt_model_p','chatgpt_frequency_penalty','chatgpt_presence_penalty','chatgpt_max_reponse_tokens','system_role_nickname','avatar','background_image'))
        
        username = request.user.username
        userinfo_redis = cache.get(username)
        jwt_token = userinfo_redis['userinfo']['jwt_token']
        # print(jwt_token)
        # print(rolelist,type(rolelist))

        return render(request,'webui/index_gpt4.html',locals())
    

    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):

        OPEN_AI_MODEL_NAME_gpt4_8k = 'gpt-4-1106-preview'    

        received_message_dict = json.loads(request.body)
        
        system_role_id = received_message_dict['role'].get('system_role_id')
        system_role_title = received_message_dict['role'].get('selected_role_title')

        # 从 redis 中取出 system_role_description 信息
        if (system_role_id and system_role_title):
            allRoleVoiceAttribution = json.loads(cache.get('allRoleVoiceAttribution'))
            for role in allRoleVoiceAttribution:
                if str(role.get('pk')) == str(system_role_id):
                    selected_system_role_dict = {"role": "system", "content": "{}".format(role['fields'].get('system_role_description'))}
                    selected_system_model_temperature = float(role['fields'].get('chatgpt_model_temperature'))
                    selected_system_model_p = float(role['fields'].get('chatgpt_model_p'))
                    selected_system_frequency_penalty = float(role['fields'].get('chatgpt_frequency_penalty'))
                    selected_system_presence_penalty = float(role['fields'].get('chatgpt_presence_penalty'))
                    selected_system_max_reponse_tokens = role['fields'].get('chatgpt_max_reponse_tokens')
                    # print(selected_system_role_dict,selected_system_model_temperature,selected_system_model_p,selected_system_frequency_penalty,selected_system_presence_penalty,selected_system_max_reponse_tokens)

                    break
        else:
            selected_system_role_dict = {"role": "system", "content": "you are a helpful AI"}
            selected_system_model_temperature = 0
            selected_system_model_p = 1
            selected_system_frequency_penalty = 0
            selected_system_presence_penalty = 0
            selected_system_max_reponse_tokens = 3000

            print(selected_system_role_dict)
        # {'userinfo': {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'is_superuser':True,'creator':1'},'blackbox': [], 'RoleVoiceAttribution': ''}
        # 这也是存在redis数据库中的数据格式
        existed_userinfo_redis = kwargs['existed_userinfo_redis']['userinfo']
        
        GPT_4_8K_enable = existed_userinfo_redis.get('GPT_4_8K')

        max_tokens_put_into_GPT_for_this_user = existed_userinfo_redis['max_tokens']
        username =  existed_userinfo_redis['username']
        user_id = existed_userinfo_redis['id']
        api_request_left = existed_userinfo_redis['api_request_left']
        token_expired_time = existed_userinfo_redis['token_expired_time']

        GPT_4_8K_enable = existed_userinfo_redis.get('GPT_4_8K')

        # 判断下有没有 gpt4的权限，如果没有
        if not GPT_4_8K_enable:
            return StreamingHttpResponse("你没有GPT4的访问权限")


    


        # history_messages = kwargs['existed_userinfo_redis']['blackbox']
        # RoleVoiceAttribution_this_dialog = kwargs['existed_userinfo_redis']['RoleVoiceAttribution']

        # 看看是否已经原来就有对话记录，如果没有就新建一个空字典
        webuidata = kwargs['existed_userinfo_redis'].get('webuidata')
        if not webuidata:
            webuidata={}
            print('webuidata还没有信息')


        

        inputmessage = kwargs['inputmessage']
        print('此次登陆的用户',existed_userinfo_redis)
        # 历史会话
        history_messages = inputmessage[:-1]
        # 本次消息
        currentinputmessage = inputmessage[-1]['content']
        print('inputmessage',inputmessage)
        inputmessage.insert(0,selected_system_role_dict)
        



        # 如果调用次数不是 unlimited 的话，api 次数减少1
        warning_message_chatgpt = ''
        # if api_request_left !='unlimited' and api_request_left.isdigit():
        #     newapi_request_left = int(api_request_left)-1
        #     existed_userinfo_redis['api_request_left'] = str(newapi_request_left)
        # # 如果调用次数低于3次次数减一,回复的chatgpt消息后面要加有提示,少于0的话，已经再装饰器里拦截掉了
        # if api_request_left.isdigit() and int(api_request_left)<=3:
        #     warning_message_chatgpt = f'您还剩下{newapi_request_left}次调用机会，可以去充值啦!'        

        # 如果还有1天时候过期，回复提示
        if token_expired_time:
            #print(token_expired_time,type(token_expired_time))
            # 获取当前时间
            now = datetime.now(timezone(timedelta(hours=8)))
            # 计算时间差
            time_diff =token_expired_time-now
            # 将时间差转换为小时数
            hours_diff = int(time_diff.total_seconds() / 3600)
            if hours_diff <=24:
                # 将当前时间格式化为 年-月-日 时:分:秒 的字符串
                token_expired_time_string = token_expired_time.strftime("%Y年%m月%d日 %H点%M分%S秒")
                warning_message_chatgpt = f'您的账号将于{token_expired_time_string}到期,可以去充值啦!'

                

        # 内置定义函数
        def chat_stream_generator(OPEN_AI_MODEL_NAME=OPEN_AI_MODEL_NAME_gpt4_8k,inputmessage=inputmessage,MODEL_TEMPERATURE=MODEL_TEMPERATURE,MAX_TOKEN_RESPONSE=MAX_TOKEN_RESPONSE,MODEL_TOP_P=MODEL_TOP_P,FREQUENCY_PENALTY=FREQUENCY_PENALTY,PRESENCE_PENALTY=PRESENCE_PENALTY):
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
                    top_p = MODEL_TOP_P,
                    frequency_penalty = FREQUENCY_PENALTY,
                    presence_penalty = PRESENCE_PENALTY,
                ):
                    
                    # collected_chunks.append(response)  # save the event response
                    # chunk_message = response['choices'][0]['delta']  # extract the message
                    # collected_messages.append(chunk_message)  # save the message

                    message = response['choices'][0]['delta'].get('content')
                    if message is not None:
                        # yield json.dumps(message)+"\n"
                        yield message
                        
                        # full_reply_content=full_reply_content+message
                #返回警告信息
                if warning_message_chatgpt:
                    # yield json.dumps(warning_message_chatgpt)
                    yield warning_message_chatgpt

            except Exception as e:
                # yield json.dumps(str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话')
                # print(traceback.format_exc())
                yield str(e)+' 会话可能已经达到最大长度,可清空此次会话 或开始新的会话'



            # print(full_reply_content)
            # full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
            # print(f"Full conversation received: {full_reply_content}")
            

        
        # 返回数据流给前端
        return StreamingHttpResponse(chat_stream_generator(
                                        OPEN_AI_MODEL_NAME = OPEN_AI_MODEL_NAME_gpt4_8k,
                                        inputmessage=inputmessage,
                                        MODEL_TEMPERATURE=selected_system_model_temperature,
                                        MAX_TOKEN_RESPONSE = selected_system_max_reponse_tokens,
                                        MODEL_TOP_P = selected_system_model_p,
                                        FREQUENCY_PENALTY = selected_system_frequency_penalty,
                                        PRESENCE_PENALTY = selected_system_presence_penalty)
                                        , 
                                        content_type='application/json')
            
           
       
        

    # 删除数据
    @method_decorator(check_jwt)
    def delete(self,request,*args,**kwargs):
        received_message_dict = json.loads(request.body)
        system_role_id = received_message_dict['role'].get('system_role_id')
        system_role_title = received_message_dict['role'].get('selected_role_title')

        existed_userinfo_redis = kwargs['existed_userinfo_redis']['userinfo']
        
        max_tokens_put_into_GPT_for_this_user = existed_userinfo_redis['max_tokens']
        username =  existed_userinfo_redis['username']
        user_id = existed_userinfo_redis['id']
        api_request_left = existed_userinfo_redis['api_request_left']
        token_expired_time = existed_userinfo_redis['token_expired_time']

        inputmessage = kwargs['inputmessage']
        print('此次登陆的用户',existed_userinfo_redis,inputmessage)

        
        # 存储到数据库中
        try:
            if system_role_id and system_role_title:
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=system_role_id,diolog=inputmessage,GPT_model_name='gpt-4')
            # 如果没有选择角色那就归类到无角色中
            else:
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=39,diolog=inputmessage,GPT_model_name='gpt-4')
        except Exception as e:
            print(traceback.format_exc())

        result = {"code":200,"status":"delete success"}
        return JsonResponse(result)

# 数据分析页面
class IndexView(View):

    def get(self,request):
        
        return render(request,'keynote.html',locals())
    


