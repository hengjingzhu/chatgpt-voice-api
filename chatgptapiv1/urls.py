
from django.urls import path
from chatgptapiv1.views import ResponseTextMessageOnly,ShortVoiceContent,IndexView,WebUIChat,WebUIChat_gpt4


urlpatterns = [
    # chatgpt文本回复
    path('textmessage',ResponseTextMessageOnly.as_view()),
    # chatgpt回复和 音频返回
    path('shortvoiceurl',ShortVoiceContent.as_view(),name='django_short_voice_url'),
    path('',IndexView.as_view()),
    path('webui',WebUIChat.as_view()),
    path('webuigpt4',WebUIChat_gpt4.as_view())
]