from typing import Dict
import os
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载环境变量和配置"""
        load_dotenv()
        
        # API Keys
        self.coze_api_token = os.getenv("COZE_API_TOKEN")
        self.deepseek_api_key = os.getenv("DEEP_SEEK_API_KEY")
        self.baidu_appid = os.getenv("baidu_appid")
        self.baidu_api_key = os.getenv("baidu_api_key")
        self.baidu_secret_key = os.getenv("baidu_secret_key")
        
        # 聊天相关配置
        self.max_history_length = 50
        self.coze_cn_base_url = "https://www.coze.cn"
