from typing import List, Dict, Any
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL
from dotenv import load_dotenv
import os
load_dotenv()
#初始化
cozekey = os.getenv("COZE_API_TOKEN")
#上下文长度
MAX_HISTORY_LENGTH = 50
coze = Coze(
auth=TokenAuth(token=cozekey),
base_url=COZE_CN_BASE_URL)
chat_history = []

def process_stream_message(user_message: str):
    if not user_message:
        yield {"type": "error", "message": "请输入有效的信息。"}
        return

    # 添加用户消息到历史记录
    chat_history.append({"role": "user", "content": user_message})

    # 准备上下文消息
    context_messages = _prepare_context_messages()
    
    # 处理流式响应
    current = ''
    for event in coze.chat.stream(
        bot_id="7499749049093570598",
        user_id="random_string",
        additional_messages=context_messages
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)
            current += event.message.content
            # 返回带有message字段的字典
            yield {"type": "normal", "message": event.message.content}
    
    # 添加完整响应到历史记录
    chat_history.append({"role": "assistant", "content": current})

def process_message(user_message: str) -> str:
    m = process_stream_message(user_message)
    sum = ""
    for each in m:
        sum += each.get('message', '')
    print("\n历史记录:",chat_history,"\n")
    return sum

def _prepare_context_messages() -> List[Message]:
    """准备上下文消息"""
    messages = []
    for msg in chat_history[-MAX_HISTORY_LENGTH:]:
        if msg["role"] == "user":
            messages.append(Message.build_user_question_text(msg["content"]))
        else:
            messages.append(Message.build_assistant_answer(msg["content"]))
    return messages

def get_chat_history():
    return chat_history

def write_chat_history(history_list:list,favor:dict):
    """
    将文件中读取的聊天记录写入到记录列表
    并将喜好添加到列表
    """
    global chat_history
    chat_history = history_list
    history_list.append({"role":"user","content":"当前最新的用户喜好:"+str(favor)})
def delete_chat_history():
    global chat_history
    chat_history = []
    
if __name__ == "__main__":
    print(process_message("你好"))