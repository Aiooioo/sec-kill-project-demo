import os
from typing import Optional

class AppConfig:
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")

    REDIS_DB = os.getenv("REDIS_DB", 0)
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # 日志配置
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
    LOG_DIR: str = os.getenv('LOG_DIR', 'logs')
    LOG_FILE: str = os.getenv('LOG_FILE', 'app.log')

    # 服务器配置
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))

    @classmethod
    def get_redis_config(cls) -> dict:
        config = {
            "host": cls.REDIS_HOST,
            "port": cls.REDIS_PORT,
            "db": cls.REDIS_DB,
            'decode_responses': True
        }

        if cls.REDIS_PASSWORD:
            config['username'] = 'default'  # Redis 6+ 需要指定用户名
            config['password'] = cls.REDIS_PASSWORD

        return config

    @classmethod
    def get_log_file_path(cls) -> str:
        return os.path.join(cls.LOG_DIR, cls.LOG_FILE)
