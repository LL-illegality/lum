import pyaudio, wave, pygame
import numpy as np
import sys, os

if os.name == 'nt':
    import msvcrt
else:
    import select

def record(file: str):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    print('开始录音...（按回车键停止）')
    frames = []
    while True:
        data = stream.read(1024)
        frames.append(data)
        # Windows
        if os.name == 'nt':
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\r':
                    break
        # Linux/Mac
        else:
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                c = sys.stdin.read(1)
                if c == '\n':
                    break
    print('录音结束')
    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))


def play(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def oldrecord(file: str, t: int):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    print('Recording...')
    frames = [stream.read(1024) for _ in range(int(16000 / 1024 * t))]
    print('Recording finished.')
    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))


def oldplay(file: str):
    print('Started Playing...')
    with wave.open(file, 'rb') as wf:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
    print('Playing finished.')