# VentureProcedure/settings_prod.py
from .settings import *

# 关闭调试模式
DEBUG = False

# 设置允许的主机（替换为您的服务器IP或域名）
#ALLOWED_HOSTS = ['your-domain.com', 'your-server-ip', '127.0.0.1']
ALLOWED_HOSTS = ['*']


# 生产环境使用更安全的SECRET_KEY
SECRET_KEY = 'django-insecure-m54%@$nwxx^y35&j8i0b*3@arz_q^ph=$h3@03au@nadc7_xc)'  # 使用更长更复杂的密钥

# 静态文件收集目录
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 数据库配置（根据生产环境调整）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vpbase',
        'USER': 'root',
        'PASSWORD': 'root_1234',
        'HOST': '192.168.1.3',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 生产环境日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
}

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True