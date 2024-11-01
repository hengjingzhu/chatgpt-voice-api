"""
Django settings for chatgptapi project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatgptapiv1',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chatgptapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',

            ],
        },
    },
]

WSGI_APPLICATION = 'chatgptapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRESQL_INTERNAL_DBNAME'),
        'USER': os.environ.get('POSTGRESQL_INTERNAL_USERNAME'),
        'PASSWORD': os.environ.get('POSTGRESQL_INTERNAL_PASSWORD'),
        'HOST': os.environ.get('AWS_EC2_INERNAL_HOST'),
        'PORT': os.environ.get('POSTGRESQL_INTERNAL_PORT'),
        'client_encoding':'UTF8',
        'default_transaction_isolation':'read committed',
        'OPTIONS': {
            'options': '-c search_path="chatgptapi"'   # 指定PostgreSQL 的 Schema,如果是大写要加上双引号
        }
    }
}

CACHES = {
    "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://{}/1".format(os.environ.get('AWS_EC2_INERNAL_HOST')),		#数字代表使用redis哪个数据库
                            "OPTIONS": 
                            {
                                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                                "PASSWORD": os.environ.get('REDIS_INTERNAL_PASSWORD'),         
                            }
                },

    "ali_voice_token": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://{}/2".format(os.environ.get('AWS_EC2_INERNAL_HOST')),		#数字代表使用redis哪个数据库
                            "OPTIONS": 
                            {
                                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                                "PASSWORD": os.environ.get('REDIS_INTERNAL_PASSWORD'),
                            }
                },


}




# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# 指定用户表
AUTH_USER_MODEL = 'chatgptapiv1.UserInfo'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL  = True       								#如果添加这一行为True,就允许所有origin都来访问,不会启用白名单

#CORS_ORIGIN_WHITELIST = ['https://www.example.com']      		#添加允许来访问的白名单,必须是https

CORS_ALLOW_METHODS=('DELETE','GET','OPTIONS','PATCH','POST','PUT')	#添加cors允许使用的访问方法

CORS_ALLOW_HEADERS = ('accept-encoding','authorization','content-type','dnt','origin','user-agent','x-csrftoken','x-requested-with')												#预检查请求中,cors允许的头的配置项

CORS_PREFLIGHT_MAX_AGE = 86400 														#默认是86400秒,首次options会话状态后，保持时间，可选项

CORS_EXPOSE_HEADERS =[]       													# 特俗的响应头配置，需要ajax得到，可选项

#CORS_ALLOW_CREDENTIALS =True/False 									#需不需要接受跨域请求的cookie，默认是false，可选项




# simple ui config

SIMPLEUI_HOME_PAGE = '/chatgptapi'
# 首页配置
SIMPLEUI_HOME_TITLE = '首页'
# 设置simpleui 点击首页图标跳转的地址
SIMPLEUI_INDEX = '/chatgptapi'
SIMPLEUI_ANALYSIS = False
SIMPLEUI_HOME_INFO = False

SIMPLEUI_DEFAULT_THEME = 'e-black-pro.css'

# logo
SIMPLEUI_LOGO = '/static/image/adai.png'

# character reset commamd
RESET_CHARACTER_COMMAMD = ['重置角色','角色重置','reset the character','reset character','reset your character','character reset']




STATICFILES_DIRS = ['chatgptapiv1/static/']

# 静态文件在容器内的目录
STATIC_ROOT = '/djangostatic'


MEDIA_URL = '/media/'   #配置上传文件相关的url路由 http://127.0.0.1/media/xxxx
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')   #配置上传文件的存储本地路径,通知Django,media root在哪里


# 当前主机ip
MY_HOST_NAME = "https://{}:8000".format(os.environ.get('GPT_DOMAIN_NAME'))
NGINX_HOST_NAME = "https://{}".format(os.environ.get('GPT_DOMAIN_NAME'))


# jwt token key 
JWT_TOKEN_KEY = os.environ.get('JWT_TOKEN_KEY')

# openai 配置
OPENAI_SECRETKEY = os.environ.get('OPENAI_SECRETKEY')
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')

# claude 配置
ANTHROPIC_SECRETKEY = os.environ.get('ANTHROPIC_SECRETKEY')

ALIYUN_REDIS_HOST = os.environ.get('ALIYUN_REDIS_HOST')
ALIYUN_REDIS_PORT = os.environ.get('ALIYUN_REDIS_PORT')
ALIYUN_REDIS_PASSWORD = os.environ.get('ALIYUN_REDIS_PASSWORD')

# 阿里云文本合成配置
ALIYUN_APP_KEY_WOMAN = os.environ.get('ALIYUN_APP_KEY_WOMAN')
# 阿里云的access_id
ALIYUN_ACCESS_ID = os.environ.get('ALIYUN_ACCESS_ID')
# 阿里云的 accesskey_secret
ALIYUN_ACCESSKEY_SECRET = os.environ.get('ALIYUN_ACCESSKEY_SECRET')
# 存储在 redis 的数据库token 的key的值
ALIYUN_ACCESS_TOKEN_KEY_IN_REDIS = os.environ.get('ALIYUN_ACCESS_TOKEN_KEY_IN_REDIS')

SIMPLEUI_CONFIG = {
    'system_keep': True,
    #'menu_display': ['Simpleui', '测试', '权限认证', '动态菜单测试'],      # 开启排序和过滤功能, 不填此字段为默认排序和全部显示, 空列表[] 为全部不显示.
    'dynamic': True,    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [

                {
                    'app': 'auth',
                    'name': '对话聊天',
                    'icon': 'fas fa-user-shield',
                    'models': [{
                        'name': 'GPT-4o-mini',
                        'icon': 'fa fa-user',
                        'url': '/chatgptapi/webui'
                    },
                    {
                        'name': 'GPT-4o',
                        'icon': 'fa fa-user-plus',
                        'url': '/chatgptapi/webuigpt4'
                    },
                    {
                        'name':'Claude-3-Haiku',
                        'icon': 'fa fa-user-pen',
                        'url':'/chatgptapi/webuiclaude3haiku'
                    },
                    {
                        'name':'Claude-3.5-Sonnet',
                        'icon': 'fa fa-user-check',
                        'url':'/chatgptapi/webuiclaude3sonnet'
                    }
                    
                    ]
                }, 
]
}