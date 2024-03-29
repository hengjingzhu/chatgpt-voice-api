
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
from django.contrib.admin import SimpleListFilter
from django.core import serializers

from django.utils.html import format_html
from PIL import Image



import json

# 我在左上角
admin.site.site_header = 'AI 智慧平台'
# 我在浏览器标签
admin.site.site_title = 'AI 智慧平台'
# 我在后台首页
admin.site.index_title = 'AI'

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
 
        (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
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

        # print(frontend_formdata,'customer_type')
        # 无限制超级用户客户，只有超级管理员才能创建超级用户
        if max_tokens and frontend_formdata['customer_type'] == 'superuser' and request.user.is_superuser:
            obj.api_request_left = 'unlimited'
            obj.token_expired_time = None
        
            # 制作 jwt_token
            jwt_token = JWTTokenMethod(username,max_tokens).maketoken_superuser()
            obj.jwt_token = jwt_token
            # print(jwt_token,'无限制超级用户客户，只有超级管理员才能创建超级用户')
        
        # 不是超级管理员的话，创建不了超级用户，数据会被清空
        elif max_tokens and frontend_formdata['customer_type'] == 'superuser' and not request.user.is_superuser:
            obj.api_request_left = None
            obj.token_expired_time = None
            obj.jwt_token = ''
            obj.customer_type = None
            # print(jwt_token,'不是超级管理员的话，创建不了超级用户，数据会被清空')

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
            # print(jwt_token,'无限制时间，限制次数用户')
        
        # 无限制次数，限制时间用户
        elif max_tokens and frontend_formdata['customer_type'] == 'LimitedTime_UnlimitedRequest':
            obj.api_request_left = 'unlimited'
            #obj.token_expired_time = None

            # 制作 jwt_token
            jwt_token = JWTTokenMethod(username,max_tokens).maketoken_limitedtime_unlimitedrequest(frontend_formdata['token_expired_time'])
            obj.jwt_token = jwt_token
            # print(jwt_token,'无限制次数，限制时间用户')
        
        obj.status = 'success'
        obj.creator = request.user
        # print(jwt_token,'jwt_token')
        # 如果 jwt_token有值的话，把 redis 缓存数据中更新 
        if jwt_token:
            
            # 把 obj 转换成字典传输进去
            # {'username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True}
            userinfo_dict = model_to_dict(obj, fields=['id','username', 'jwt_token','GPT_4_8K','customer_type','token_expired_time','api_request_left','max_tokens','status','is_active','creator','is_superuser'])
            
            print('admin中存储前 userinfo_dict',userinfo_dict)
            for i in range(0,10):

                # 先从 redis 中取出 原有的用户信息
                userinfo_redis = cache.get(username)
                print("旧的用户信息",userinfo_redis)
                if userinfo_redis:
                    userinfo_redis['userinfo'] = userinfo_dict
                    print('新用户信息token已更新完毕',userinfo_redis)
                else:
                    userinfo_redis = {'userinfo':userinfo_dict,"blackbox":[],'RoleVoiceAttribution':{},'webuidata':{}}

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
    
            (gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','GPT_4_8K','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
        # 二级管理员查看其他用户的字段
        elif not request.user.is_superuser and user_in_view_form_OBJ != request.user:
            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            (gettext_lazy('Permissions'), {'fields': ('is_staff','GPT_4_8K')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
        # 二级管理员看自己的字段
        elif not request.user.is_superuser and user_in_view_form_OBJ == request.user:

            self.readonly_fields = ['jwt_token','status','creator','customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status']

            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            (gettext_lazy('Permissions'), {'fields': ('is_staff','GPT_4_8K')}),
    
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
    
            (gettext_lazy('Permissions'), {'fields': ('is_superuser','is_staff','GPT_4_8K','is_active','groups', 'user_permissions')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
            
        else:
            self.fieldsets = (
            (None,{'fields':('username','password','first_name','last_name','email')}),
            # 自定义字段显示
            (gettext_lazy('User Information'),{'fields':('customer_type','token_expired_time','api_request_left','max_tokens','jwt_token','status')}),
    
            (gettext_lazy('Permissions'), {'fields': ('is_staff','GPT_4_8K')}),
    
            (gettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined','creator')}),
        )
        
        return super().add_view(
            request, form_url, extra_context=extra_context,
        )



# 自定义 user 过滤器，超级用户看到所有，其他用户只能看到自己和自己创建的用户
class CustomUserFilter(SimpleListFilter):
    title = '用户'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded
        value for the option that will appear in the URL query. The second
        element is the human-readable name for the option that will appear in
        the right sidebar.
        """
        if request.user.is_superuser:
            qs = UserInfo.objects.all()
        elif not request.user.is_superuser:
            qs = UserInfo.objects.filter(Q(username=request.user) | ~Q(is_superuser=True) & ~Q(groups__name='sub-admin') &Q(creator=request.user))

        return qs.values_list('id', 'username')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the
        query string and retrievable via `self.value()`.
        """
        value = self.value()

        if value:
            return queryset.filter(user_id=value)
        return queryset


# 自定义 user 过滤器，超级用户看到所有，其他用户只能看到自己和自己创建的用户
class CustomRoleVoiceAttributionFilter(SimpleListFilter):
    title = '角色属性'
    parameter_name = 'RoleVoiceAttribution'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded
        value for the option that will appear in the URL query. The second
        element is the human-readable name for the option that will appear in
        the right sidebar.
        """
        if request.user.is_superuser:
            qs = RoleVoiceAttribution.objects.all()
        elif not request.user.is_superuser:
            qs = RoleVoiceAttribution.objects.filter(Q(shart_with_subadmin=True) | Q(creator=request.user))

        return qs.values_list('id','system_role')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the
        query string and retrievable via `self.value()`.
        """
        value = self.value()

        if value:
            return queryset.filter(RoleVoiceAttribution_id=value)
        return queryset




# 压缩图片的函数，默认图片不压缩, 并且大于 1M 的时候才会压缩
def compress_image(image, quality=100, size_limit=1 * 1024 * 1024):
    if image and '\\default\\adai.png' not in image.path:
        # 检查图片文件大小是否大于 size_limit（1M）
        if image.size > size_limit:
            img = Image.open(image.path)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.save(image.path, 'JPEG', quality=quality)
    return image


# 角色声音属性表
@admin.register(RoleVoiceAttribution)
class RoleVoiceAttributionAdmin(admin.ModelAdmin):
    list_display = ('display_image','system_role','system_role_random_weight','system_role_nickname','display_background_image','system_role_alivoice_role','shart_with_subadmin','creator')
    list_per_page = 20
    list_editable =('system_role_random_weight',)

    readonly_fields = ('creator',)
    

    def display_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
    display_image.short_description = '角色头像'

    def display_background_image(self, obj):
        return format_html('<img src="{}" width="50" height="" />', obj.background_image.url)
    display_background_image.short_description = '角色背景'


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
        
        # 如果 creator 是 admin,那就说明这个不是其他角色创建的，登录名就是创建名
        # 如果 creator 不是 admin,那就说明这个角色是其他人创建的，不要修改.因为数据库默认创建就是 admin
        if obj.creator.username == 'admin' and obj.shart_with_subadmin==True or obj.creator.username != 'admin' and request.user.is_superuser:
            pass
        else :
            obj.creator = request.user

        # 如果有图片更新的话，就删除老图片，在 model中写好
        obj.delete_old_image()

        # 只有超级用户可以修改，或者不是超级用户的话只能修改自己的角色
        if request.user.is_superuser or not request.user.is_superuser and obj.creator == request.user:
            super().save_model(request, obj, frontend_formdata, change)
            # 压缩头像和背景图片
            compress_image(obj.avatar)
            compress_image(obj.background_image)


    def save_related(self,request, form, formsets, change):
        #print(form.cleaned_data,type(form.cleaned_data),change)
        
        # 点击保存之后，把 pg 的数据库更新完毕之后，把所有的属性角色放到 redis 数据库中， key 名 "allRoleVoiceAttribution"
        RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.all()

        # 返回列表格式的字符串  [{"model": "chatgptapiv1.rolevoiceattribution", "pk": 27, "fields": {"system_role": "general-admin", "system_role_description": "you are a helpful ai", "system_role_random_weight": 1, "chatgpt_model_temperature": "0.80", "chatgpt_model_p": "1.00", "chatgpt_frequency_penalty": "1.00", "chatgpt_presence_penalty": "0.60", "chatgpt_max_reponse_tokens": 250, "system_role_alivoice_role": "zhimiao_emo", "system_role_alivoice_samplerate": 16000, "system_role_alivoice_speechrate": 0, "system_role_alivoice_pitchrate": 0, "system_role_aivoice_speak_effect": "", "system_role_alivoice_speak_emotion": "gentle", "system_role_alivoice_speak_intensity": "1.00", "creator": 1, "shart_with_subadmin": true, "created_time": "2023-03-17T19:09:56.208Z", "updated_time": "2023-03-19T12:27:35.696Z", "is_active": true}},{....},....]
        allRoleVoiceAttribution_str = serializers.serialize('json', RoleVoiceAttribution_queryset)
        # print(allRoleVoiceAttribution_str,type(allRoleVoiceAttribution_str))

        cache.set('allRoleVoiceAttribution',allRoleVoiceAttribution_str,timeout=None)
        super().save_related(request, form, formsets, change)


    # superuser 权限返回所有，其他用户只能返回 superuser创建的角色以及自己创建的角色
    def get_queryset(self, request):

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            self.list_editable =('system_role_random_weight',)
            self.readonly_fields = ('creator',)
            return qs

        # 其他后台管理人员登陆只能看到公共角色，或者是二级管理员自己创建的角色
        return qs.filter(Q(shart_with_subadmin=True) | Q(creator=request.user))


    def delete_model(self,request, obj):

        # 如果是超级用户可以删除
        if request.user.is_superuser:
            obj.delete()

        # 如果不是superuser的话,删除的obj创建者是自己的话，可以删除
        elif not request.user.is_superuser and obj.creator == request.user:
            obj.delete()

        # 如果不是删除，删除的obj不是自己的话，删除不了
        elif not request.user.is_superuser and not obj.creator == request.user:
            pass

    def delete_queryset(self,request, queryset):
        # 如果是超级用户可以删除
        if request.user.is_superuser:
            queryset.delete()
        
        # 如果不是superuser的话,只能删除自己创建的角色
        elif not request.user.is_superuser:

            for obj in queryset:
                if obj.creator == request.user:
                    obj.delete()
                elif obj.creator != request.user:
                    pass


    

    # 管理员返回所有，其他管理员只能看到部分字段
    def change_view(self, request, object_id, form_url='', extra_context=None):
        
        if request.user.is_superuser:
            self.readonly_fields = ('creator',)
            
        elif not request.user.is_superuser:
            self.readonly_fields = ('creator','shart_with_subadmin')
            
            # 获取当前查看的对象,如果查看的对象的创建者是 superuser的话，不能看角色描述信息
            obj = self.get_object(request, object_id)
            if obj.creator.is_superuser:
                # 所有字段设置为只读
                self.exclude = ('system_role_description',)
                self.readonly_fields = [field.name for field in self.model._meta.fields if field.name!= 'system_role_description']
                
            else:
                 self.exclude = ('',)


        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
    
    # 管理员返回所有，其他管理员只能看到部分字段
    def add_view(self, request, form_url='', extra_context=None):

        if request.user.is_superuser:
           self.readonly_fields = ('creator',)
        else:
            self.readonly_fields = ('creator','shart_with_subadmin')
        
        return super().add_view(
            request, form_url, extra_context=extra_context,
        )





# blackbox 表
@admin.register(BlackBox)
class BlackBoxAdmin(admin.ModelAdmin):
    list_display = ('user','RoleVoiceAttribution','get_creator','updated_time','GPT_model_name')
    list_per_page = 30
    list_filter = (CustomRoleVoiceAttributionFilter,CustomUserFilter,'GPT_model_name')
    search_fields = ['user__username']

    readonly_fields = ['user','RoleVoiceAttribution','updated_time','created_time']

    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'cols': 200, 'rows': 50})},
    }

    # 增加一个自定义字段
    def get_creator(self, obj):
        return obj.user.creator
    get_creator.short_description = '用户创建者'
    get_creator.admin_order_field = 'user__creator'

    # superuser 权限返回所有，其他用户返回非superuser 用户
    def get_queryset(self, request):

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # 其他后台管理人员登陆只能看到自己创建的用户，但是不包含 superuser以及不包含sub-admin组的其他成员,以及只能看到自己创建的成员
        return qs.filter(Q(user__creator=request.user) | Q(user=request.user))
