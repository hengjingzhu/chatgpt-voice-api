# Generated by Django 3.2 on 2023-04-21 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgptapiv1', '0023_alter_rolevoiceattribution_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolevoiceattribution',
            name='background_image',
            field=models.ImageField(default='images/adai.png', upload_to='backgroundimages/', verbose_name='角色背景'),
        ),
    ]
