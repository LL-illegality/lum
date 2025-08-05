from abc import ABC, abstractmethod
from typing import List, Dict, Generator

class BaseChatService(ABC):
    """聊天服务基类"""
    
    @abstractmethod
    def process_message(self, message: str) -> str:
        """处理用户消息"""
        pass
        
    @abstractmethod
    def process_stream_message(self, message: str) -> Generator:
        """流式处理用户消息"""
        pass
        
    @abstractmethod
    def get_chat_history(self) -> List[Dict]:
        """获取聊天历史"""
        pass
        
    @abstractmethod
    def save_chat_history(self) -> None:
        """保存聊天历史"""
        pass
        
    @abstractmethod
    def load_chat_history(self) -> None:
        """加载聊天历史"""
        pass
        
    @abstractmethod
    def delete_chat_history(self) -> None:
        """删除聊天历史"""
        pass
        
    @abstractmethod
    def update_user_preferences(self, preferences: Dict) -> None:
        """更新用户偏好"""
        pass
