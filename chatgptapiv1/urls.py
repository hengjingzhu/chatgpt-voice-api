
from django.urls import path
from chatgptapiv1.views import ChatGPTResponseMessage,ShortVoiceContent,IndexView

urlpatterns = [
    # chatgpt回复和 音频返回
    path('responsemessage',ChatGPTResponseMessage.as_view()),
    # 短文本返回
    path('shortvoiceurl',ShortVoiceContent.as_view(),name='django_short_voice_url'),
    path('',IndexView.as_view())
]