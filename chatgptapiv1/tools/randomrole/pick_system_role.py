import random
from django.core import serializers
from chatgptapiv1.models import RoleVoiceAttribution
import json



class PickSystemRole():

    def __init__(self) -> None:
        self.datalist = json.loads(serializers.serialize('json', RoleVoiceAttribution.objects.all(), fields=('system_role','system_role_random_weight')))

    def total_weight(self):

        total_weight = 0
        for obj in self.datalist:
            total_weight += obj['fields']['system_role_random_weight']
        return total_weight

    def pick_random_role(self):

        random_number = random.randint(1,self.total_weight())
        sum = 0
        for obj in self.datalist:
            sum+=obj['fields']['system_role_random_weight']
            if sum >= random_number:
                return obj['fields']['system_role']


if __name__ == '__main__':
    # from chatgptapiv1.tools.randomrole.pick_system_role import PickSystemRole
    PickSystemRole().pick_random_role()