
from django.urls import path
from chatgptapiv1.myviews.web_views import ResponseTextMessageOnly,ShortVoiceContent,IndexView,WebUIChat,WebUIChat_gpt4
from chatgptapiv1.myviews.api_view import GPT_API
from chatgptapiv1.myviews.bilibili_bullet import bullet_font_view,bullet_font_streaming_response

urlpatterns = [
    # chatgpt文本回复
    path('textmessage',ResponseTextMessageOnly.as_view()),
    # chatgpt回复和 音频返回
    path('shortvoiceurl',ShortVoiceContent.as_view(),name='django_short_voice_url'),
    path('',IndexView.as_view()),
    path('webui',WebUIChat.as_view()),
    path('webuigpt4',WebUIChat_gpt4.as_view()),
    
    # 纯 chatgpt接口，供外部调用
    path('gptapi',GPT_API.as_view()),
    
    # bilibili bullet comment style
    path('bilibili_bullet_page',bullet_font_view),
    path('bilibili_bullet_streaming_response',bullet_font_streaming_response),
]