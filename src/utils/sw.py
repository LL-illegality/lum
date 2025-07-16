#sw = Speech and Word
#https://ai.baidu.com/ai-doc/SPEECH/0lbxfnc9b
from aip import AipSpeech
from dotenv import load_dotenv
import pygame
import os
load_dotenv()
baidu_appid = os.getenv("baidu_appid")
baidu_api_key = os.getenv("baidu_api_key")
baidu_secret_key = os.getenv("baidu_secret_key")

client = AipSpeech(baidu_appid,baidu_api_key,baidu_secret_key)
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def s2t(filePath):
    re = client.asr(get_file_content(filePath), 'pcm', 16000, {
    'dev_pid': 1537,
})
    return re["result"]

def t2s(text):
    if len(text)<=500:
        result  = client.synthesis(text, 'zh', 1, {
        'vol': 5,
        #选择要音色 https://ai.baidu.com/ai-doc/SPEECH/Rluv3uq3d
        'per':4196,
        #1-15,15为中
        'spd':5
    })
    else:
        result  = client.synthesis("内容太长啦，请自己看文字吧！", 'zh', 1, {
        'vol': 5,
        #选择要音色 https://ai.baidu.com/ai-doc/SPEECH/Rluv3uq3d
        'per':4196,
        #1-15,15为中
        'spd':5
    })
    #如果错误的话会返回一个dict类型的result，这里检测如果不是错误的话就写入文件。
    if not isinstance(result, dict):
        # ！IMPORTANT！ 此处解除pygame播放器对output文件的锁定，防止出现[Errno 13] Permission denied: 'output.mp3'
        pygame.mixer.init()
        pygame.mixer.music.unload()
        with open(r"output.mp3", 'wb') as f:
            f.write(result)