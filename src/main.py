from utils.record import *
from utils.sw import *
import services.chat_service as chat_service;
import services.signal_service as signal_service;
import utils.deepseek as deepseek
import json

print("====知微光年 Luminest v1.21====")
print("输入'Q'退出程序")
run = True
while run:
    user_input = input("\n欢迎使用>>")
    
    # 检查退出命令
    if user_input.upper() == 'Q':
        run = False
        continue

    record("record.wav")
    text = s2t("record.wav")[0]
    print("<<",text)
    result =json.loads(chat_service.process_message(text))
    if result["type"]=="dangerous":
        print("检测到危险信息,开始危险处理")
        #历史信息处理
        history_str = ""
        for i in chat_service.get_chat_history():
            history_str += i['role'] + ":" + i['content'] + "\n"

        signal_service.add_dangerous_chat("测试ID", text, deepseek.dangerAnayze(history_str))
    t2s(result["message"])
    print(">>",result["message"])
    play("output.mp3")