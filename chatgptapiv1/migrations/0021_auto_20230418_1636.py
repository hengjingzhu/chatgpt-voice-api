# Generated by Django 3.2 on 2023-04-18 08:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgptapiv1', '0020_auto_20230318_0420'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolevoiceattribution',
            name='system_role_nickname',
            field=models.CharField(default='请设置', max_length=255, verbose_name='昵称'),
        ),
        migrations.AlterField(
            model_name='rolevoiceattribution',
            name='system_role_alivoice_pitchrate',
            field=models.IntegerField(default=0, help_text='-500到500', validators=[django.core.validators.MinValueValidator(-500, message='Value must be greater than or equal to -500'), django.core.validators.MaxValueValidator(500, message='Value must be less than or equal to 500')], verbose_name='语调'),
        ),
        migrations.AlterField(
            model_name='rolevoiceattribution',
            name='system_role_alivoice_speechrate',
            field=models.IntegerField(default=0, help_text='-500到500', validators=[django.core.validators.MinValueValidator(-500, message='Value must be greater than or equal to -500'), django.core.validators.MaxValueValidator(500, message='Value must be less than or equal to 500')], verbose_name='语速'),
        ),
    ]