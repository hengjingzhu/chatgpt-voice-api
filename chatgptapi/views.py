from django.http import JsonResponse,HttpResponse
from django.views import View

class IndexView(View):
    def get(self,request):
        return HttpResponse("testview")