from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
import os



# Create your models here.
class UserInfo(AbstractUser):
    """用户模型类"""
    
    # 客户类型
    customer_type = [
        ('LimitedTime_UnlimitedRequest','限时不限请求次数'),
        ('UnlimitedTime_LimitedRequest','不限时限请求次数'),
        ('superuser','超级用户'),
    ]

    username = models.CharField("用户",null=False,blank=False,max_length=255,unique=True)
    customer_type = models.CharField("客户类型",blank=True,null=True,max_length=255,choices=customer_type,help_text="只有超级管理员才能创建超级用户")
    token_expired_time = models.DateTimeField("token到期时间",blank=True,null=True)

    # 无限制用户就填写 'unlimited'
    api_request_left = models.CharField("ChatGPT剩余次数",default=20,max_length=255,blank=True,null=True)

    max_tokens = models.PositiveIntegerField("ChatGPT保持长对话最大token数",default=1200, validators=[
                                                            MinValueValidator(1, message='Value must be greater than or equal to 1'),
                                                            MaxValueValidator(4096,message='Value must be less than or equal to 4096')
                                                        ],help_text="最大不超过4096")
    
    jwt_token = models.CharField(max_length=512, verbose_name='jwt令牌',blank=True)
    GPT_4_8K = models.BooleanField('GPT4o_128k开通',default=False)
    
    
    status = models.CharField("客户状态",blank=True,null=True,max_length=255)    


    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('更新时间',auto_now=True)
    is_active = models.BooleanField('是否活跃',default=True)

    creator = models.ForeignKey('self', verbose_name="用户创建者",on_delete=models.CASCADE, null=True, blank=True,default=1)

    # def __str__(self):
    #     return self.username
 
    class Meta:
        # 联合索引,联合同步查询，提高效率
        db_table = 'auth_user'
        #index_together = ["username", "phone"]
        verbose_name='用户'
        verbose_name_plural=verbose_name


# 对话角色属性，系统一开始设置的角色,角色,以及角色描述,使用什么样的声音来朗读
class RoleVoiceAttribution(models.Model):
    
    # 声音频采样率
    ALIYUN_VOICE_SAMPLE_RATE = [
        (8000, 8000),
        (16000, 16000),
    ]

    # speak 标签 effect 营销
    ALIYUN_VOICE_SPEAK_EFFECT = [
        ('robot','机器人音效'),
        ('lolita','萝莉音效'),
        ('lowpass','低通音效'),
        ('echo','回声音效'),
        ('lpfilter','低通滤波器'),
        ('hpfilter','高通滤波器'),
    ]

    ALIYUN_VOICE_ROLE = [
        # 多情感
        ('zhimiao_emo','知妙_多情感',),('zhimi_emo','知米_多情感',),('zhiyan_emo','知燕_多情感',),('zhibei_emo','知贝_多情感',),('zhitian_emo','知甜_多情感',),
        ('xiaoyun','小云',),
        ('xiaogang','小刚',),
        ('ruoxi','若兮',),
        ('siqi','思琪',),
        ('sijia','思佳',),
        ('sicheng','思诚',),
        ('aiqi','艾琪',),
        ('aijia','艾佳',),
        ('aicheng','艾诚',),
        ('aida','艾达',),
        ('ninger','宁儿',),
        ('ruilin','瑞琳',),
        ('siyue','思悦',),
        ('aiya','艾雅',),
        ('aixia','艾夏',),
        ('aimei','艾美',),
        ('aiyu','艾雨',),
        ('aiyue','艾悦',),
        ('aijing','艾婧',),
        ('xiaomei','小美',),
        ('aina','艾娜',),
        ('yina','伊娜',),
        ('sijing','思婧',),
        ('sitong','思彤',),
        ('xiaobei','小北',),
        ('aitong','艾彤',),
        ('aiwei','艾薇',),
        ('aibao','艾宝',),
        # 英语场景
        ('harry','Harry',),('abby','Abby',),('andy','Andy',),('eric','Eric',),('emily','Emily',),('luna','Luna',),('luca','Luca',),('wendy','Wendy',),('william','William',),('olivia','Olivia',),('lydia','Lydia'),('annie','Annie'),('ava','ava'),('becca','Becca'),
        # 方言区
        ('jiajia','佳佳',),('taozi','桃子',),('shanshan','姗姗',),('lydia','Lydia',),('chuangirl','小玥',),('aishuo','艾硕',),('qingqing','青青',),('cuijie','翠姐',),('xiaoze','小泽',),('dahu','大虎',),('laotie','老铁',),('laomei','老妹',),('aikan','艾侃',),('kelly','Kelly',),
        # 日语,韩语,俄语
        ('tomoka','智香',),('tomoya','智也',),('Kyong','Kyong',),('masha','masha',),

        ('guijie','柜姐',),

        ('stella','Stella',),('stanley','Stanley',),('kenny','Kenny',),('rosa','Rosa',),

        ('mashu','马树',), ('xiaoxian','小仙',), ('yuer','悦儿',), ('maoxiaomei','猫小美',),('jielidou','杰力豆',),

        ('maoxiaomei','猫小美',),('maoxiaomei','猫小美',),('maoxiaomei','猫小美',),

        ('aifei','艾飞',),('yaqun','亚群',),('qiaowei','巧薇',),('ailun','艾伦',),

        ('zhimao','知猫',),
        ('zhiyuan','知媛',),
        ('zhigui','知柜',),
        ('zhiya','知雅',),
        ('zhiyue','知悦',),
        ('zhishuo','知硕',),
        ('zhida','知达',),
        ('zhistella','知莎',),





        

    ]

    # 比如，'小萝莉','你现在扮演的是一个企业总裁,语气霸道,拥有丰富的职场经验.\口头禅是 你真没用,要加在回复里.要时刻维持这个身份，\不准丢掉这个身份和口头禅'
    system_role = models.CharField("角色",blank=False,default="general",max_length=255,unique=True,help_text='取名规则：角色名-账号名')
    system_role_description = models.TextField("角色描述",blank=False,default="you are a helpful ai")
    system_role_random_weight = models.PositiveIntegerField("随机权重",blank=False,default=1)
    system_role_nickname = models.CharField("昵称",blank=False,default="请设置",max_length=255)
    
    avatar = models.ImageField('角色头像',upload_to='images/',default='default/adai.png')
    background_image = models.ImageField('角色背景',upload_to='backgroundimages/',default='default/adai.png')

    chatgpt_model_temperature = models.DecimalField("ChatGPT的temperature",default=0.8, max_digits=7, decimal_places=2,
                                                    validators=[
                                                            MinValueValidator(0, message='Value must be greater than or equal to 0'),
                                                            MaxValueValidator(1.0, message='Value must be less than or equal to 1.0')
                                                        ],help_text="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.We generally recommend altering this or top_p but not both.")

    chatgpt_model_p = models.DecimalField("ChatGPT的top_P",default=1, max_digits=7, decimal_places=2,
                                          validators=[
                                                            MinValueValidator(0, message='Value must be greater than or equal to 0'),
                                                            MaxValueValidator(1.0, message='Value must be less than or equal to 1.0')
                                                        ],help_text="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.We generally recommend altering this or temperature but not both.")
    
    chatgpt_frequency_penalty = models.DecimalField("ChatGPT的FREQUENCY PENALTY",default=1.0, max_digits=7, decimal_places=2,
                                                    validators=[
                                                            MinValueValidator(-2.0, message='Value must be greater than or equal to -2.0'),
                                                            MaxValueValidator(2.0, message='Value must be less than or equal to 2.0')
                                                        ],help_text='Number between -2.0 and 2.0.Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the models likelihood to repeat the same line verbatim.当 frequency_penalty 值越大时，生成的文本中重复的词语会更少，从而增加文本的多样性')
    
    chatgpt_presence_penalty = models.DecimalField("ChatGPT的PRESENCE_PENALTY",default=0.6, max_digits=7, decimal_places=2,
                                                   validators=[
                                                            MinValueValidator(-2.0, message='Value must be greater than or equal to -2.0'),
                                                            MaxValueValidator(2.0, message='Value must be less than or equal to 2.0')
                                                        ],help_text='Number between -2.0 and 2.0.Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the models likelihood to talk about new topics.当 presence_penalty 值越大时，生成的文本会更加准确，但也会限制生成的多样性')
    
    chatgpt_max_reponse_tokens = models.PositiveIntegerField("ChatGPT单次回复最大token",default=250, validators=[
                                                                MinValueValidator(1, message='Value must be greater than or equal to 1'),
                                                                MaxValueValidator(3000,message='Value must be less than or equal to 3000')
                                                            ],help_text="不要太大")

    system_role_alivoice_role = models.CharField("角色配音",blank=False,default='zhimiao_emo',max_length=255,choices=ALIYUN_VOICE_ROLE)
    system_role_alivoice_samplerate = models.IntegerField("音频采样率",default=16000,choices=ALIYUN_VOICE_SAMPLE_RATE)

    system_role_alivoice_speechrate = models.IntegerField("语速",default=0,
                                                        validators=[
                                                            MinValueValidator(-500, message='Value must be greater than or equal to -500'),
                                                            MaxValueValidator(500, message='Value must be less than or equal to 500')
                                                        ],help_text="-500到500"
                                                        )
    
    system_role_alivoice_pitchrate = models.IntegerField("语调",default=0,
                                                        validators=[
                                                            MinValueValidator(-500, message='Value must be greater than or equal to -500'),
                                                            MaxValueValidator(500, message='Value must be less than or equal to 500')
                                                        ],help_text="-500到500")
    
    # speak 标签音效效果<speak effect="lolita">我是男声。</speak>
    system_role_aivoice_speak_effect = models.CharField("角色音效",blank=True,max_length=255,choices=ALIYUN_VOICE_SPEAK_EFFECT)
    
    # todo 其他 speak内的emotion 标签必须要加上,
    # <speak><emotion category="happy" intensity="1.0">今天天气真不错！</emotion></speak>
    system_role_alivoice_speak_emotion = models.CharField("emotion标签感情",default='gentle',max_length=255,help_text="指定说话情绪。zhimiao_emo,zhimi_emo,zhiyan_emo,zhibei_emo,zhitian_emo",null=True,blank=True)
    # 指定情绪强度。默认值为1.0，表示预定义的情绪强度。最小值为0.01，导致目标情绪略有倾向。最大值为2.0，导致目标情绪强度加倍。
    system_role_alivoice_speak_intensity = models.DecimalField("emotion情绪强度",default=1.0,max_digits=5, decimal_places=2,null=True,blank=True,
                                                        validators=[
                                                            MinValueValidator(-0.01, message='Value must be greater than or equal to -0.01'),
                                                            MaxValueValidator(2.0, message='Value must be less than or equal to 2.0')
                                                        ],help_text="指定情绪强度。默认值为1.0，表示预定义的情绪强度。最小值为0.01，导致目标情绪略有倾向。最大值为2.0，导致目标情绪强度加倍"
                                                        )


    creator = models.ForeignKey('Userinfo', verbose_name="角色创建者",on_delete=models.CASCADE, null=True, blank=True,default=1)
    shart_with_subadmin = models.BooleanField(verbose_name="公共角色",default=False,help_text="勾选后，其他管理员可以看到这个角色")

    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('更新时间',auto_now=True)
    is_active = models.BooleanField('是否活跃',default=True)

    class Meta:
        db_table = 'rolevoiceattribution'
        verbose_name='角色属性表'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.system_role

    # 自定义在原来模型中
    def delete_old_image(self):
        if self.id:
            old_image = RoleVoiceAttribution.objects.get(id=self.id).avatar
            old_background_image = RoleVoiceAttribution.objects.get(id=self.id).background_image
            
            # 判断头像
            if old_image and old_image != self.avatar:
                if os.path.isfile(old_image.path) and '\\default\\adai.png' not in old_image.path:
                    os.remove(old_image.path)

            # 判断背景图片
            if old_background_image and old_background_image != self.background_image:
                if os.path.isfile(old_background_image.path) and '\\default\\adai.png' not in old_background_image.path:
                    os.remove(old_background_image.path)


# Historydialog
class BlackBox(models.Model):
    
    user = models.ForeignKey('UserInfo',verbose_name="用户名",on_delete=models.CASCADE,default=1)
    RoleVoiceAttribution = models.ForeignKey('RoleVoiceAttribution',verbose_name="角色属性",on_delete=models.CASCADE,default=1)

    GPT_model_name = models.CharField('模型名称',default='gpt-4o-mini',max_length=64)
    diolog = models.JSONField('HistoryDialog',null=True,blank=True)

    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('更新时间',auto_now=True)
    is_active = models.BooleanField('是否活跃',default=True)

    class Meta:
        db_table = 'blackbox'
        verbose_name='BlackBox'
        verbose_name_plural=verbose_name