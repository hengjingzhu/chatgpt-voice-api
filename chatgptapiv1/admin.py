
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy
from chatgptapiv1.models import *
from chatgptapiv1.tools.jwt_token.make_jwt_tokens import JWTTokenMethod
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.db import models
from django.forms import Textarea
from django.db.models import Q

# 我在左上角
admin.site.site_header = '智慧语音管理平台'
# 我在浏览器标签
admin.site.site_title = '智慧语音管理平台'
# 我在后台首页
admin.site.index_title = '智慧语音'

# 用户表
@admin.register(UserInfo)
class UserInfoAdmin(UserAdmin):

    list_display = ('username','customer_type','token_expired_time','api_request_left','is_active','date_joined','jwt_token')
    list_filter = ('customer_type', 'is_active')
    search_fields = ['username']

    readonly_fields = ['jwt_token','status','creator']
    list_per_page =30

    fieldsets = (
        (None,{'fields':('username','password','first_name','last_name','email')}),
 		# 自定义字段显示
        (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
 
        (gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','is_active','groups', 'user_permissions')}),
 
        (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


    
    # superuser 权限返回所有，其他用户返回非superuser 用户
    def get_queryset(self, request):

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # 其他后台管理人员登陆只能看到自己，但是不包含 superuser以及不包含sub-admin组的其他成员,以及只能看到自己创建的成员
        return qs.filter(Q(username=request.user) | ~Q(is_superuser=True) & ~Q(groups__name='sub-admin') &Q(creator=request.user))

    def save_model(self, request, obj, form, change):
        
        # {'username': 'admin', 'customer_type': None, 'token_expired_time': None, 'api_request_left': '2', 'is_superuser': True, 'is_staff': True, 'is_active': True, 'groups': <QuerySet []>, 'user_permissions': <QuerySet []>, 'last_login': datetime.datetime(2023, 3, 8, 16, 58, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>), 'date_joined': datetime.datetime(2023, 3, 8, 16, 53, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>)}
        # <class 'dict'>
        frontend_formdata = form.cleaned_data
        username = frontend_formdata['username']
        max_tokens = frontend_formdata.get('max_tokens')
        jwt_token = ''

        # 无限制超级用户客户，只有超级管理员才能创建超级用户
        if max_tokens and frontend_formdata['customer_type'] == 'superuser' and request.user.is_superuser:
            obj.api_request_left = 'unlimited'
            obj.token_expired_time = None
        
            # 制作 jwt_token
            jwt_token = JWTTokenMethod(username,max_tokens).maketoken_superuser()
            obj.jwt_token = jwt_token
        
        # 不是超级管理员的话，创建不了超级用户，数据会被清空
        elif max_tokens and frontend_formdata['customer_type'] == 'superuser' and not request.user.is_superuser:
            obj.api_request_left = None
            obj.token_expired_time = None
            obj.jwt_token = ''
            obj.customer_type = None

        # 无限制时间，限制次数用户
        elif max_tokens and frontend_formdata['customer_type'] == 'UnlimitedTime_LimitedRequest':
            # 如果是数字就按照数字
            api_request_left = frontend_formdata['api_request_left']
            if api_request_left.isdigit():
                obj.api_request_left = api_request_left
            else:
                obj.api_request_left = 30
            obj.token_expired_time = None
            
            # 制作 jwt_token
            jwt_token = JWTTokenMethod(username,max_tokens).maketoken_unlimitedtime_limitedrequest(api_request_left)
            obj.jwt_token = jwt_token
        
        # 无限制次数，限制时间用户
        elif max_tokens and frontend_formdata['customer_type'] == 'LimitedTime_UnlimitedRequest':
            obj.api_request_left = 'unlimited'
            #obj.token_expired_time = None

            # 制作 jwt_token
            jwt_token = JWTTokenMethod(username,max_tokens).maketoken_limitedtime_unlimitedrequest(frontend_formdata['token_expired_time'])
            obj.jwt_token = jwt_token
        
        obj.status = 'success'
        obj.creator = request.user

        # 如果 jwt_token有值的话，把 redis 缓存数据中更新 
        if jwt_token:
            
            # 把 obj 转换成字典传输进去
            # {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True}
            userinfo_dict = model_to_dict(obj, fields=['id','username', 'jwt_token','customer_type','token_expired_time','api_request_left','max_tokens','status','is_active'])
            
            #print('admin中存储前 userinfo_dict',userinfo_dict)
            for i in range(0,10):

                # 先从 redis 中取出 原有的用户信息
                userinfo_redis = cache.get(username)
                print("旧的用户信息",userinfo_redis)
                if userinfo_redis:
                    userinfo_redis['userinfo'] = userinfo_dict
                    print('新用户信息token已更新完毕',userinfo_redis)
                else:
                    userinfo_redis = {'userinfo':userinfo_dict,"blackbox":[],'RoleVoiceAttribution':{}}

                saving_result = cache.set(username,userinfo_redis,timeout=None)
                print(saving_result)
                if saving_result:
                    break
        super().save_model(request, obj, frontend_formdata, change)

    def save_related(self,request, form, formsets, change):
        #print(form.cleaned_data,type(form.cleaned_data),change)
        super().save_related(request, form, formsets, change)

    # 管理员返回所有，其他管理员只能看到部分字段
    def change_view(self, request, object_id, form_url='', extra_context=None):
        
        user_in_view_form_OBJ = UserInfo.objects.get(id=object_id)
        self.readonly_fields = ['jwt_token','status','creator']

        if request.user.is_superuser:
            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            (gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
            
        elif not request.user.is_superuser and user_in_view_form_OBJ != request.user:
            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            #(gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
            
        elif not request.user.is_superuser and user_in_view_form_OBJ == request.user:

            self.readonly_fields = ['jwt_token','status','creator','customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status']

            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            #(gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
          
        
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
    
    # 管理员返回所有，其他管理员只能看到部分字段
    def add_view(self, request, form_url='', extra_context=None):
        if request.user.is_superuser:
            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            (gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
            
        else:
            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            #(gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
        
        return super().add_view(
            request, form_url, extra_context=extra_context,
        )



# 角色声音属性表
@admin.register(RoleVoiceAttribution)
class RoleVoiceAttributionAdmin(admin.ModelAdmin):
    list_display = ('system_role','system_role_random_weight','system_role_alivoice_role','is_active')
    list_per_page = 30
    list_editable =('system_role_random_weight',)

    def save_model(self, request, obj, form, change):
        
        # {'username': 'admin', 'customer_type': None, 'token_expired_time': None, 'api_request_left': '2', 'is_superuser': True, 'is_staff': True, 'is_active': True, 'groups': <QuerySet []>, 'user_permissions': <QuerySet []>, 'last_login': datetime.datetime(2023, 3, 8, 16, 58, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>), 'date_joined': datetime.datetime(2023, 3, 8, 16, 53, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>)}
        # <class 'dict'>
        frontend_formdata = form.cleaned_data
        system_role_alivoice_role = frontend_formdata.get('system_role_alivoice_role')
        role_with_emotion = ['zhimiao_emo','zhimi_emo','zhiyan_emo','zhibei_emo','zhitian_emo']
        
        # 如果角色不是多感性声音的话,speak_emotion和intensiy都是为0
        if system_role_alivoice_role and system_role_alivoice_role not in role_with_emotion:
            obj.system_role_alivoice_speak_emotion = None
            obj.system_role_alivoice_speak_intensity = None
        

        super().save_model(request, obj, frontend_formdata, change)



# blackbox 表
@admin.register(BlackBox)
class BlackBoxAdmin(admin.ModelAdmin):
    list_display = ('user','RoleVoiceAttribution','get_creator','updated_time')
    list_per_page = 30
    list_filter = ('user', 'RoleVoiceAttribution')
    search_fields = ['user__username']

    readonly_fields = ['user','RoleVoiceAttribution','updated_time','created_time']

    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'cols': 200, 'rows': 50})},
    }

    # 增加一个自定义字段
    def get_creator(self, obj):
        return obj.user.creator
    get_creator.short_description = 'creator'
    get_creator.admin_order_field = 'user__creator'

    # superuser 权限返回所有，其他用户返回非superuser 用户
    def get_queryset(self, request):

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # 其他后台管理人员登陆只能看到自己创建的用户，但是不包含 superuser以及不包含sub-admin组的其他成员,以及只能看到自己创建的成员
        return qs.filter(Q(user__creator=request.user) | Q(user=request.user))
