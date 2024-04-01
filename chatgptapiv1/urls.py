
from django.urls import path
from chatgptapiv1.myviews.web_views import ResponseTextMessageOnly,ShortVoiceContent,IndexView,WebUIChat,WebUIChat_gpt4,WebUIClaude3_Haiku,WebUIClaude3_Sonnet
from chatgptapiv1.myviews.api_view import GPT_API,GPT_API_STREAM_V2,GPT_API_V2,CLAUDE_API_STREAM,CLAUDE_API
from chatgptapiv1.myviews.bilibili_bullet import bullet_font_view,bullet_font_streaming_response

urlpatterns = [
    # chatgpt文本回复
    path('textmessage',ResponseTextMessageOnly.as_view()),
    # chatgpt回复和 音频返回
    path('shortvoiceurl',ShortVoiceContent.as_view(),name='django_short_voice_url'),
    path('',IndexView.as_view()),
    path('webui',WebUIChat.as_view()),
    path('webuigpt4',WebUIChat_gpt4.as_view()),
    path('webuiclaude3haiku',WebUIClaude3_Haiku.as_view()),
    path('webuiclaude3sonnet',WebUIClaude3_Sonnet.as_view()),
    
    
    # 纯 chatgpt接口，供外部调用
    path('gptapi',GPT_API.as_view()),
    
    path('gptapiv2',GPT_API_V2.as_view()),
    path('gptapistreamv2',GPT_API_STREAM_V2.as_view()),
    
    # claude 接口，供外部调用
    path('claudeapi',CLAUDE_API.as_view()),
    path('claudeapistream',CLAUDE_API_STREAM.as_view()),
    
    # bilibili bullet comment style
    path('bilibili_bullet_page',bullet_font_view),
    path('bilibili_bullet_streaming_response',bullet_font_streaming_response),
]