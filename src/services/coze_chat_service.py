from typing import List, Dict, Generator
import json
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL
from src.services.baseChatService import BaseChatService
from src.config import Config

class CozeChatService(BaseChatService):
    """基于Coze的聊天服务实现"""
    
    def __init__(self):
        self.config = Config()
        self.chat_history = []
        self.coze = Coze(
            auth=TokenAuth(token=self.config.coze_api_token),
            base_url=COZE_CN_BASE_URL
        )
    
    def process_stream_message(self, user_message: str) -> Generator:
        """处理流式消息"""
        if not user_message:
            yield {"type": "error", "message": "请输入有效的信息。"}
            return

        # 添加用户消息到历史记录
        self.chat_history.append({"role": "user", "content": user_message})

        # 准备上下文消息
        context_messages = self._prepare_context_messages()
        
        # 处理流式响应
        current = ''
        for event in self.coze.chat.stream(
            bot_id="7499749049093570598",
            user_id="random_string",
            additional_messages=context_messages
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                print(event.message.content, end="", flush=True)
                current += event.message.content
                yield {"type": "normal", "message": event.message.content}
        
        # 添加完整响应到历史记录
        self.chat_history.append({"role": "assistant", "content": current})

    def process_message(self, user_message: str) -> str:
        """处理单条消息"""
        m = self.process_stream_message(user_message)
        sum = ""
        for each in m:
            sum += each.get('message', '')
        print("\n历史记录:", self.chat_history, "\n")
        return sum

    def _prepare_context_messages(self) -> List[Message]:
        """准备上下文消息"""
        messages = []
        for msg in self.chat_history[-self.config.max_history_length:]:
            if msg["role"] == "user":
                messages.append(Message.build_user_question_text(msg["content"]))
            else:
                messages.append(Message.build_assistant_answer(msg["content"]))
        return messages

    def get_chat_history(self) -> List[Dict]:
        """获取聊天历史"""
        return self.chat_history

    def save_chat_history(self) -> None:
        """保存聊天历史到文件"""
        try:
            with open('chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存聊天历史时出错: {str(e)}")
            raise

    def load_chat_history(self) -> None:
        """从文件加载聊天历史"""
        try:
            with open('chat_history.json', 'r', encoding='utf-8') as f:
                self.chat_history = json.load(f)
        except FileNotFoundError:
            print("未找到聊天历史文件")
            self.chat_history = []
        except Exception as e:
            print(f"加载聊天历史时出错: {str(e)}")
            raise

    def delete_chat_history(self) -> None:
        """删除聊天历史"""
        self.chat_history = []
        
    def update_user_preferences(self, preferences: Dict) -> None:
        """更新用户喜好"""
        self.chat_history.append({
            "role": "user",
            "content": "当前最新的用户喜好:" + str(preferences)
        })
