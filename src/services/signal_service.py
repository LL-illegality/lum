from typing import List, Dict, Any
from datetime import datetime
import json,os

    

def add_signal(signal_data: Dict[str, Any]) -> None:
    global signal_list
    """
    添加新的信号
    """
    print("收到了新的危机信号")
    signal_list.append(signal_data)
    save_signals_to_file()

def get_signals() -> List[Dict]:
    """
    获取所有信号
    Return:
        信号列表（倒序）
    """
    load_signals_from_file()
    return signal_list[::-1]

def add_dangerous_chat( user_id: str, trigger_message: str, analyze: str) -> None:
    """
    添加危险聊天记录
    """
    signal_data = {
        'type': 'dangerous_chat',
        'user_id': user_id,
        'trigger_message': trigger_message,
        'analyze': analyze,
        'timestamp': datetime.now().isoformat()
    }
    add_signal(signal_data)

def save_signals_to_file(filename: str = 'signals.json') -> None:
    """
    将信号保存到文件
    """
    with open(filename,'w') as f:
        json.dump(signal_list, f, indent=4)

def load_signals_from_file(filename: str ='signals.json') -> None:
    """
    从文件加载信号
    """
    global signal_list
    if os.path.exists(filename):
        with open(filename) as f:
            signal_list = json.load(f)
    else:
        print("还没保存过危险信号记录")

# 初始化信号列表
signal_list = []
try:
    load_signals_from_file()
except Exception as e:
    print("还没保存过危险信号记录")
