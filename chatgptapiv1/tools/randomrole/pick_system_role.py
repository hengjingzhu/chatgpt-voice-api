import random
from django.core import serializers
from chatgptapiv1.models import RoleVoiceAttribution
import json
from django.db.models import Q

userinfotest = {'id':1,'username': 'admin', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'is_superuser':True,'creator':1}

class PickSystemRole():

    # {'id': 3,','username': 'admin3', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True},'blackbox': [], 'RoleVoiceAttribution': ''}
    def __init__(self,userinfo=userinfotest) -> None:
        self.userinfo=userinfo

    def datalist(self):
        
        # 如果是superuser 返回所有的 角色，如果不是只能返回公共角色以及创建用户的creator的角色
        if self.userinfo['is_superuser']:
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.all()
        elif not self.userinfo['is_superuser']:
            RoleVoiceAttribution_queryset = RoleVoiceAttribution.objects.filter(Q(shart_with_subadmin=True) | Q(creator_id=self.userinfo['id']) | Q(creator_id=self.userinfo['creator']))

        datalist = json.loads(serializers.serialize('json', RoleVoiceAttribution_queryset, fields=('system_role','system_role_random_weight')))
        return datalist

    def total_weight(self):
        #print(self.datalist())
        total_weight = 0
        for obj in self.datalist():
            total_weight += obj['fields']['system_role_random_weight']
        return total_weight

    def pick_random_role(self):

        random_number = random.randint(1,self.total_weight())
        sum = 0
        for obj in self.datalist():
            sum+=obj['fields']['system_role_random_weight']
            if sum >= random_number:
                return obj['fields']['system_role']


if __name__ == '__main__':

    # todo, 角色随机目录: 1. 公共角色，2. 二级管理员(判断是不是在sub-admin)登陆的时候所有角色 + 或者 访问用户的创建者的角色,
    userinfotest = {'id':1,'username': 'admin', 'customer_type': 'superuser', 'token_expired_time': None, 'api_request_left': 'unlimited', 'max_tokens': 1200, 'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluMyIsInR5cGUiOiJzdXBlcnVzZXIiLCJzdGF0dXMiOiJzdWNjZXNzIiwibWF4X3Rva2VucyI6MTIwMH0.7ZXYHn9s41qvorY_7cX0uudE6NwrwEwsrOmavdN43Vg', 'status': 'success', 'is_active': True,'is_superuser':False,'creator':1}

    # from chatgptapiv1.tools.randomrole.pick_system_role import PickSystemRole
    PickSystemRole(userinfo=userinfotest).pick_random_role()