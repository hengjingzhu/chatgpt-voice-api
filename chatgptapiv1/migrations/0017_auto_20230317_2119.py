# Generated by Django 3.2 on 2023-03-17 13:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatgptapiv1', '0016_auto_20230317_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blackbox',
            name='RoleVoiceAttribution',
            field=models.ForeignKey(default='角色已被删除', on_delete=django.db.models.deletion.SET_DEFAULT, to='chatgptapiv1.rolevoiceattribution', verbose_name='角色属性'),
        ),
        migrations.AlterField(
            model_name='blackbox',
            name='user',
            field=models.ForeignKey(default='此用户已被删除', on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL, verbose_name='用户名'),
        ),
        migrations.AlterField(
            model_name='rolevoiceattribution',
            name='chatgpt_max_reponse_tokens',
            field=models.PositiveIntegerField(default=250, help_text='不要太大', validators=[django.core.validators.MinValueValidator(1, message='Value must be greater than or equal to 1'), django.core.validators.MaxValueValidator(3000, message='Value must be less than or equal to 3000')], verbose_name='ChatGPT单次回复最大token'),
        ),
    ]