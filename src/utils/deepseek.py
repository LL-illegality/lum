import openai
import os
import json
from dotenv import load_dotenv
load_dotenv()

dskey = os.getenv("DEEP_SEEK_API_KEY")
client = openai.OpenAI(api_key=dskey, base_url="https://api.deepseek.com")
msglist = []

def dangerAnayze(history_messages:list)->list:
    msglist.append({"role": "system", "content": """
    现有一个心理分析项目，目前检测到了用户存在心理危机,你需要分析用户和机器人的对话，为"介入的专业人士"给出总结和处理建议。
    要求: 1.结合专业心理学知识回答 
          2.字数控制在200字左右（历史总结占100字左右），适度分行便于阅读
          3.你应该返回给我一个字符串
    """})
    msglist.append({"role": "user", "content": history_messages})
    print("Deepseek危机分析中...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=msglist,
        stream=False,
        temperature=1.0 # 1.0适于语言分析
    ) 
    print("分析结果：",response.choices[0].message.content)
    return response.choices[0].message.content

def preferenceAnayze(history_messages:list)->str:
    msglist.append({"role": "system", "content": """
    现有一个心理机器人项目，用户已完成聊天，请你在本次聊天内容中汇总用户感兴趣的话题。
    你需要返回给我一个字符串，格式示例: {"<话题1>":"<对话题1的详细汇总>"，"<话题2>":"<对话题2的详细汇总>"}
    PS. 1.不能加入会导致json解析失败的内容
        2.话题数量可以为1-20个，应基于事实列举，不能够为提高量而重复话题。
    
    """})
    msglist.append({"role": "user", "content": history_messages})
    print("Deepseek话题分析中...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=msglist,
        stream=False,
        temperature=1.0 # 1.0适于语言分析
    )
    print("本次总结：",response.choices[0].message.content)
    return response.choices[0].message.content


def test():
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False)

    print(response.choices[0].message.content)

if __name__ == "__main__":
    test()