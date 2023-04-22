import requests
from chatgptapiv1.tools.aliyun_voice_to_text.config import *
from chatgptapiv1.tools.aliyun_voice_to_text.get_access_token import GETACCESSTOKEN
import json
import time
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
import os

class TextToVoice():

    def __init__(self,message,username='myaudio',role='zhimiao_emo',sample_rate=16000,speech_rate=-100,pitch_rate=0,rawmessage='你好啊') -> None:
        
        self.retry_time = 0
        self.max_retry = 10
        self.message = message
        self.access_token = GETACCESSTOKEN().run()
        self.long_voice_get_task_id_host = HOSTS_EXTERNAL
        self.short_voice_host = SHORT_HOSTS_EXTERNAL
        self.app_key = APP_KEY_WOMAN
        
        self.username = username
        self.role = role
        self.sample_rate = sample_rate
        self.speech_rate = speech_rate
        self.pitch_rate = pitch_rate

        self.rawmessage = rawmessage
        self.payload={
            "payload":{
                "tts_request":{
                    "voice":self.role,
                    "sample_rate":self.sample_rate,
                    "format":"wav",
                    "text":self.message,
                    #"text":f'<speak><emotion category="gentle" intensity="1.0" >{message}</emotion></speak>',
                    "enable_subtitle": False,
                    "speech_rate": self.speech_rate,
                    "pitch_rate":self.pitch_rate,
                },
                "enable_notify":False
            },
            "context":{
                "device_id":"my_device_id"
            },
            "header":{
                "appkey":self.app_key,
                "token":self.access_token
            }
        }

        self.headers = {
            "Content-Type":"application/json"
        }


        self.short_voice_url_params = {
                "voice":self.role,
                "sample_rate":self.sample_rate,
                "format":"wav",
                "text":self.message,
                #"text":f'<speak><emotion category="gentle" intensity="1.0" >{message}</emotion></speak>',
                "speech_rate": self.speech_rate,
                "token":self.access_token,
                "appkey":self.app_key,
                "pitch_rate":self.pitch_rate,
        }


    def get_task_id(self):
        # 重写 考虑延时见，超时过程
        
        response_get_taskid = requests.post(url=self.long_voice_get_task_id_host,headers=self.headers,data=json.dumps(self.payload))

        if response_get_taskid: #and response_get_taskid.json()['error_code']=='20000000':
            response_obj = response_get_taskid.json()
            task_id = response_obj['data']['task_id']
            return task_id

    def get_voice_url(self,taskid):
        # https://nls-gateway.cn-shanghai.aliyuncs.com/rest/v1/tts/async?appkey={Appkey}&task_id={task_id}&token={Token}
        get_voice_url = f'https://nls-gateway.cn-shanghai.aliyuncs.com/rest/v1/tts/async?appkey={self.app_key}&task_id={taskid}&token={self.access_token}'
        response_voice_url = requests.get(url=get_voice_url).json()

        #print(response_voice_url)
        if response_voice_url['error_message'] == 'SUCCESS':
            voice_url = response_voice_url['data']['audio_address']
            return voice_url
        else:
            print('长音频制作中,在工作')
            time.sleep(1)
            return self.get_voice_url(taskid)


    # 文字300字以内的短文本合成,
    def run_short(self):
        
        
        # 成功的话响应内容为合成音频的二进制数据.失败的话响应体内容为错误信息，以JSON格式的字符串表示
        response_voice_data_short = requests.get(url=self.short_voice_host,params=self.short_voice_url_params)
        
        try:
            error_response_voice_data_short = response_voice_data_short.json()
            print(error_response_voice_data_short)

            if self.retry_time < self.max_retry:
                time.sleep(1)
                self.retry_time +=1
                return self.run_short()
            else:
                self.retry_time=0
                return "no short voice url"
            
        except Exception:
            voice_binary_data = response_voice_data_short.content
            
            # 然后把数据存到数据库里, 把页面返回给客户
            # cache_result=cache.set('voice_binary_data',voice_binary_data,60*60)
            if voice_binary_data:
                # 将音频数据保存到服务器上的一个静态文件中,dev 环境中 STATIC_ROOT 包括了voice,所以这里不用写
                
                # 生产环境
                file_path = os.path.join(settings.STATIC_ROOT, 'voice/{}.wav'.format(self.username))
                
                # 开发环境
                #file_path = os.path.join(settings.STATIC_ROOT, '{}.wav'.format(self.username))

                with open(file_path, 'wb') as f:
                    f.write(voice_binary_data)

                # 开发环境返回一个包含音频文件URL链接的响应
                #audio_url = settings.MY_HOST_NAME+settings.STATIC_URL + 'voice/{}.wav'.format(self.username)
                # 生产环境配置nginx后的返回路由，nginx监听的是本机80版本
                audio_url = settings.NGINX_HOST_NAME+settings.STATIC_URL + 'voice/{}.wav'.format(self.username)

                print(audio_url,'本次产生的音频地址')
                #audio_url = 'http://192.168.31.188:8000/static/voice/test1.wav'
                return audio_url
            
            
            
            



    # 如果 message 长度超过300就同长文本,低于300就用短文本, 返回 voice url, 都是一个链接地址
    def run(self):

        if len(self.rawmessage)<=300:
            voice_url = self.run_short()

        else:
            #长文本合成
            task_id = self.get_task_id()
            print(task_id)
            if task_id:
                voice_url = self.get_voice_url(task_id)
        return voice_url




if __name__ == '__main__':


    # from chatgptapiv1.tools.aliyun_voice_to_text.text_to_voice import TextToVoice

    TextToVoice('<speak effect="lolita"><emotion category="angry" intensity="1.0" >对不起,您的令牌已经过期,请输入正确的令牌</emotion></speak>').run()
    TextToVoice('<speak voice="sitong">你怎么不说话呢?</speak>','davidzhu').run()