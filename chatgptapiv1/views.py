from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse
from django.conf import settings

import os
import json
from datetime import datetime,timezone,timedelta

from chatgptapiv1.tools.chatgpt.openai_response_chatgpt import OpenAIModel
#from chatgptapiv1.tools.chatgpt.redis_connection import RedisConn
from chatgptapiv1.tools.chatgpt.config import *

from chatgptapiv1.tools.aliyun_voice_to_text.text_to_voice import TextToVoice
from chatgptapiv1.tools.jwt_token.check_jwt_tokens import check_jwt
from chatgptapiv1.tools.randomrole.pick_system_role import PickSystemRole

from django.core.cache import cache

from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator

from chatgptapiv1.models import RoleVoiceAttribution,BlackBox


def GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog):
    print(RoleVoiceAttribution_this_dialog)

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

    print(voice_text_message,username,system_role_alivoice_role,system_role_alivoice_samplerate,system_role_alivoice_speechrate,type(system_role_alivoice_pitchrate))
    voice_url = TextToVoice(message=voice_text_message,username=username,role=system_role_alivoice_role,sample_rate=system_role_alivoice_samplerate,speech_rate=system_role_alivoice_speechrate,pitch_rate=system_role_alivoice_pitchrate).run()
    return voice_url
    

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


    # {'existed_userinfo_redis': {'userinfo': {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True}, 'blackbox': [], 'RoleVoiceAttribution': ''}, 'inputmessage': '测试消息'}
    @method_decorator(check_jwt)
    def post(self,request,*args,**kwargs):
        # {'userinfo': {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True},'blackbox': [], 'RoleVoiceAttribution': ''}
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

        print(existed_userinfo_redis,history_messages,RoleVoiceAttribution_this_dialog,inputmessage)

        # 如果 inputmessage 是'重置角色'，或者'角色重置'，把blackbox和RoleVoiceAttribution 存储到 pg上，同时清空 该用户redis里的blackbox和RoleVoiceAttribution
        #  # 重置角色,会原有对话保存到og中，清空redis数据
        print(inputmessage,type(history_messages),type(RoleVoiceAttribution_this_dialog))
        if "重置角色" in inputmessage or "角色重置" in inputmessage:
            print(RoleVoiceAttribution_this_dialog,'重置角色的属性')
            # 如果缓存数据库有历史对话记录的话，就保存到 pg 中，清空redis 对话记录
            if history_messages and RoleVoiceAttribution_this_dialog:
                
                    
                response_message = "你居然不要我了,你将会被分配一个随机角色"
                print(response_message,'重置角色')
                voice_url = GetVoiceUrl_tts(response_message,username,RoleVoiceAttribution_this_dialog)
                result = {'code':200,'message':response_message,"voice":voice_url}

                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=history_messages)
                userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":history_messages.clear(),'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog.clear()}
                cache.set(username,userinfo_redis,timeout=None)

                return JsonResponse(result)
    
            else:
                response_message = '你要说话，才能生成随机角色啊'
                # 生产环境
                voice_url = settings.NGINX_HOST_NAME+settings.STATIC_URL + 'voice/repeatresetrole.wav'
                # 开发环境
                #voice_url = settings.MY_HOST_NAME+settings.STATIC_URL + 'voice/repeatresetrole.wav'
                result = {'code':200,'message':'你要说话，才能生成随机角色啊',"voice":voice_url}
                return JsonResponse(result)

        # 如果没有历史对话记录，和对话属性,那就是新的对话，要先 random选择 一个角色.
        if not history_messages and not RoleVoiceAttribution_this_dialog:

            system_role = PickSystemRole().pick_random_role()
            print('新对话随机到的角色:',system_role)
            # 获取这个角色的obj
            RoleVoiceAttributionObj = RoleVoiceAttribution.objects.get(system_role=system_role)
            # 转化成字典 {'id': 1, 'system_role': 'president', 'system_role_description': '你现在扮演的是一个企业总裁，语气霸道,拥有丰富的职场经验。口头禅是 你真没用,要加在回复里.要时刻维持这个身份，不准丢掉这个身份和口头禅', 'system_role_random_weight': 4, 'chatgpt_model_temperature': Decimal('0.80'), 'chatgpt_model_p': Decimal('1.00'), 'chatgpt_frequency_penalty': Decimal('1.00'), 'chatgpt_presence_penalty': Decimal('0.60'), 'system_role_alivoice_role': 'xiaogang', 'system_role_alivoice_samplerate': 16000, 'system_role_alivoice_speechrate': Decimal('0.00'), 'system_role_alivoice_pitchrate': Decimal('0.00'), 'system_role_aivoice_speak_effect': '', 'system_role_alivoice_speak_emotion': None, 'system_role_alivoice_speak_intensity': None}
            RoleVoiceAttribution_this_dialog = model_to_dict(RoleVoiceAttributionObj,exclude=['created_time','updated_time','is_active'])
            print(RoleVoiceAttribution_this_dialog,'我在not history_messages and not RoleVoiceAttribution_this_dialog')
            # print(userinfo_dict)
            history_messages = []

        # 如果有历史会话记录和对话属性，那就不再改变,把数据和参数发给 chatgpt,获得回复消息.
        # 回复结果:('你好，我叫qin。很高兴能和您聊天！', [{'role': 'system', 'content': '你会先自我介绍，你的名字叫 qin'}, {'role': 'user', 'content': '你好啊'}, {'role': 'assistant', 'content': '你好，我叫qin。很高兴能和您聊天！'}], 56)
        print("在调取openai信息中")
        reply_message_obj = OpenAIModel().reply_message(inputmessage,history_messages,RoleVoiceAttribution_this_dialog['system_role_description'])
        print(reply_message_obj)
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
                BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=new_messages)


        # 如果小于最大 token 使用数，保存结果到缓存数据库。
        if total_used_tokens < max_tokens_put_into_GPT_for_this_user:
            
            # new_messages = json.loads(new_messages)
            # print(new_messages,type(new_messages))
            userinfo_redis = {'userinfo':existed_userinfo_redis,"blackbox":new_messages,'RoleVoiceAttribution':RoleVoiceAttribution_this_dialog}
            #print(userinfo_redis)
            cache.set(username,userinfo_redis,timeout=None)
            print(RoleVoiceAttribution_this_dialog,'我在total_used_tokens < max_tokens_put_into_GPT_for_this_user')
              # 获得消息后,然后把回复消息和语音角色设置发给 TTS 模型获取语音链接
            voice_url = GetVoiceUrl_tts(response_message_chatgpt,username,RoleVoiceAttribution_this_dialog)

            # 如果大于等于最大 token 使用数量,或者调用次数小于0次 ，把结果保存到pg 数据库，删除缓存数据库的对话信息
        elif total_used_tokens >= max_tokens_put_into_GPT_for_this_user:

             
            BlackBox.objects.create(user_id=user_id,RoleVoiceAttribution_id=RoleVoiceAttribution_this_dialog['id'],diolog=new_messages)
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


# 继承 View
class ChatGPTResponseMessage(View):

    OpenAIObj = OpenAIModel()
    start_messages = []
    # redis_conn = RedisConn()

    def get(self,request):
        user = {'code':200,'data':{'name':'David','age':18}}
        return JsonResponse(user)
    
    # 定义 post 方法 
    def post(self,request):
       
        received_message_dict = json.loads(request.body)
        
        received_message_str = received_message_dict.get('inputmessage')
        username = received_message_dict.get('username')

        existed_dialog = cache.get(username)
        
        # 重置角色,会清空数据库
        if "重置角色" in received_message_str:
            cache.delete(username)
            response_message_chatgpt = "你居然不要我了,我会立场,你会得到一个随机角色"

            # 转陈域名
            # f'<speak><emotion category="gentle" intensity="1.0" >{response_message_chatgpt}</emotion></speak>'
            voice_url = TextToVoice(f'<speak effect="lolita"><emotion category="angry" intensity="1.0" >{response_message_chatgpt}</emotion></speak>').run()
            result = {'code':200,'message':response_message_chatgpt,"voice":voice_url}
            return JsonResponse(result)




        if existed_dialog:
            # print("我在这里 existed_dialog")
            existed_dialog = json.loads(existed_dialog)
            
            reply_message_obj = self.OpenAIObj.reply_message(received_message_str.strip(),existed_dialog,username)


        elif not existed_dialog:
            # print("我在这里 not existed_dialog")
            # print(username)
            start_messages = []
            reply_message_obj = self.OpenAIObj.reply_message(received_message_str.strip(),start_messages,username)


        # ('嘿！你好啊，有什么我可以帮助你的吗？', [{'role': 'system', 'content': ', 257)
        #response_contents_chatgpt = self.OpenAIObj.reply_message(received_message_str,self.start_messages,'myself')
        response_message_chatgpt = reply_message_obj[0]
        new_messages = json.dumps(reply_message_obj[1])
        total_used_tokens = reply_message_obj[2]
        


        # 如果小于最大 token 使用数，保存结果返回结果数据。
        if total_used_tokens < MAX_TOKEN_INMESSAGE:

            cache.set(username,new_messages)

            # 如果大于等于最大 token 使用数量，删除数据库的对话信息
        else:
            cache.delete(username)
            #response_message_chatgpt = response_message_chatgpt+"\n===========================================\n本次对话已经超过最大长度,后台数据库中的历史对话记录将会被清空,聊天属性会被随机切换"
            response_message_chatgpt = response_message_chatgpt+"本次对话已经超过最大长度,后台数据库中的历史对话记录将会被清空,聊天属性会被随机切换"

        # <speak><emotion category="gentle" intensity="1.0" >{response_message_chatgpt}</emotion></speak>
        voice_url = TextToVoice(f'<speak><emotion category="gentle" intensity="1.0" >{response_message_chatgpt}</emotion></speak>').run()
        print(voice_url)
        result = {'code':200,'message':response_message_chatgpt,"voice":voice_url}
        return JsonResponse(result)


class IndexView(View):

    def get(self,request):
        
        return render(request,'keynote.html',locals())