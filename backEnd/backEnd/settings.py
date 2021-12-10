"""
Django settings for backEnd project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from base64 import b64decode, b16decode

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i)*55-ep)i&50syq_k^&6qxeh7z*p$e4=7d11&vm7)_eyl=%+8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    'django.contrib.staticfiles',
    'sslserver',
    'djangosecure',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'xMiddleware.logger.RequestLogMiddleware',
]

ROOT_URLCONF = 'backEnd.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'backEnd.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440000  #上传文件大小，改成25M
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440000  #上传数据大小，也改成了25M

# 为了防止cookie被阻止，这里要设置这两行，因为新的浏览器设置
SESSION_COOKIE_SAMESITE = 'none'
CSRF_COOKIE_SAMESITE = 'none'
# 以下两行为是否为https链接，在标准配置中，如果前后台地址不同，则设置跨域必须加上这行
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True # 将所有非SSL请求永久重定向到SSL
SESSION_COOKIE_SECURE = True # 仅通过https传输cookie
CSRF_COOKIE_SECURE = True # 仅通过https传输cookie
SECURE_HSTS_INCLUDE_SUBDOMAINS = True # 严格要求使用https协议传输
SECURE_HSTS_PRELOAD = True # HSTS为
SECURE_HSTS_SECONDS = 60
SECURE_CONTENT_TYPE_NOSNIFF = True # 防止浏览器猜测资产的内容类型


CORS_ORIGIN_WHITELIST = ()
 
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
 
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

RSA_PRIVATE_KEY = RSA.import_key(open('rsa_1024_priv.pem').read())
# 实例化加密套件
CIPHER = PKCS1_v1_5.new(RSA_PRIVATE_KEY)

# 日志信息相关

LOGGING = {
    # 版本
    'version': 1,
    # 是否禁止默认配置的记录器
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "method": "%(method)s", "username": "%(username)s", "role": "%(role)s","sip": "%(sip)s", "dip": "%(dip)s", "path": "%(path)s", "status_code": "%(status_code)s", "reason_phrase": "%(reason_phrase)s", "func": "%(module)s.%(funcName)s:%(lineno)d",  "message": "%(message)s", "body": "%(body)s","response":"%(response)s"}',
            'datefmt': '%Y-%m-%d %H:%M:%S'
# { "_id" : ObjectId("60aa656bca4210950a41fa52"), "body" : { "id" : [ "15" ] }, "path" : "/modelmarket_backend/queryModel", "method" : "GET", "username" : "provider", "role" : "user", "nickname" : "Model Provider", "sip" : "127.0.0.1", "dip" : "127.0.1.1", "response" : { "status" : 200, "data" : { "id" : 15, "modelName" : "test", "modelDescription" : "test2sdf", "howToRunAndDetails" : "adgs\nadsf1`23213\n\n## sadf\n\n11`1sd\n\n", "modelFramework" : "sklearn", "tags" : [ "asd" ], "filename" : "provider_model_9_2021-05-23-18-49-57.onnx", "price" : 0, "structurePic" : "provider_model_9_2021-05-23-18-49-57.onnx.svg", "status" : true, "created_time" : "2021-05-23 18:51:25", "updated_time" : "2021-05-23 20:13:23", "author" : "provider" } }, "status_code" : 200, "reason_phrase" : "OK" }
        }
    },
    # 过滤器
    'filters': {
        'request_info': {'()': 'xMiddleware.logger.RequestLogFilter'},
    },
    'handlers': {
        # 标准输出
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        # 自定义 handlers，输出到文件
        'restful_api': {
            'level': 'DEBUG',
            # 时间滚动切分
            'class': 'logging.StreamHandler',
            # 'filename': os.path.join(os.getcwd(), 'logs/web-log.log'),
            # 'formatter': 'standard',
            # # 调用过滤器
            # 'filters': ['request_info'],
            # # 每天凌晨切分
            # 'when': 'MIDNIGHT',
            # # 保存 30 天
            # 'backupCount': 30,
        },
    },
    'loggers': {
        # 'django': {
        #     'handlers': ['console'],
        #     'level': 'INFO', #
        #     'propagate': False
        # },
        'web.log': {
            'handlers': ['restful_api'],
            'level': 'INFO',
            # 此记录器处理过的消息就不再让 django 记录器再次处理了
            'propagate': False
        },
    }
}
