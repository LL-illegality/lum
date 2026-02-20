from typing import List, Dict, Any
import os
import json
from datetime import datetime
from .dataService import DataService
from .analysisService import DeepseekAnalysisService


class DiaryService:
    """管理光喵日记：生成、列出、删除、读取。"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.diary_dir = os.path.join(self.data_dir, "diaries")
        os.makedirs(self.diary_dir, exist_ok=True)
        self.data_service = DataService(self.data_dir)
        self.analysis_service = DeepseekAnalysisService()

    def _diary_path(self, date_str: str) -> str:
        safe = date_str.replace('/', '-').replace(' ', '_')
        return os.path.join(self.diary_dir, f"diary_{safe}.md")

    def list_diaries(self) -> List[str]:
        files = []
        try:
            for name in os.listdir(self.diary_dir):
                if name.startswith('diary_'):
                    files.append(name[len('diary_'):-3])
        except Exception:
            pass
        return sorted(files)

    def read_diary(self, date_str: str) -> str:
        path = self._diary_path(date_str)
        if not os.path.exists(path):
            return ""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def delete_diary(self, date_str: str) -> bool:
        path = self._diary_path(date_str)
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception:
            pass
        return False

    def generate_diary(self, date_str: str) -> str:
        """基于给定日期的聊天记录与长期记忆生成日记并保存，返回日记文本。"""
        # 收集当天聊天记录
        chats = []
        try:
            all_chats = self.data_service.get_chats()
            for c in all_chats:
                ts = c.get('timestamp','')
                if ts and ts.startswith(date_str):
                    chats.append(c)
        except Exception as e:
            print(f"读取聊天记录失败: {e}")
            chats = []

        memories = []
        try:
            # 读取长期记忆文件（memories.json）
            mem_file = os.path.join(self.data_dir, 'memories.json')
            if os.path.exists(mem_file):
                with open(mem_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
        except Exception as e:
            print(f"读取记忆失败: {e}")
            memories = []

        # 调用分析服务生成日记
        try:
            diary_text = self.analysis_service.generate_diary(chats, memories, date_str)
        except Exception as e:
            print(f"生成日记失败: {e}")
            diary_text = ""

        if diary_text:
            path = self._diary_path(date_str)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(diary_text)
            except Exception as e:
                print(f"写入日记失败: {e}")

        return diary_text
