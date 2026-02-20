from typing import List, Dict, Any
import os
import json
from typing import Optional
from datetime import datetime
from .dataService import DataService
from .analysisService import DeepseekAnalysisService


class MemoryService:
    """长期记忆服务：管理、生成并持久化长期记忆"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.memories_file = os.path.join(self.data_dir, "memories.json")
        self.data_service = DataService(self.data_dir)
        self.analysis_service = DeepseekAnalysisService()

    def _read_memories(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.memories_file):
            return []
        try:
            with open(self.memories_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_memories(self, memories: List[Dict[str, Any]]) -> None:
        with open(self.memories_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=4)

    def get_memories(self) -> List[Dict[str, Any]]:
        return self._read_memories()

    def add_memory(self, summary: str) -> Dict[str, Any]:
        entry = {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        mems = self._read_memories()
        mems.append(entry)
        try:
            self._write_memories(mems)
        except Exception:
            pass
        return entry

    def generate_long_term_memory(self, history_messages: List[Dict[str, Any]], event_timestamp: Optional[str] = None) -> List[Dict[str, Any]]:
        """基于当前聊天历史与已有记忆，生成若干长期记忆条目并替换以前的记忆。

        参数:
            history_messages: 聊天历史列表
            event_timestamp: 可选，关联的聊天事件时间（ISO 字符串），用于设置记忆条目的时间戳

        返回写入到记忆文件的条目列表（每项为 dict，包含 summary 和 timestamp）。
        若 AI 未配置或生成失败，返回空列表。
        """
        # 读取已有记忆并把它们作为历史的一部分传给分析器
        existing = self._read_memories()
        combined = []
        # 将已有记忆作为 assistant 的历史条目（用于迭代总结）
        for m in existing:
            combined.append({"role": "assistant", "message": m.get("summary", "")})
        # 将聊天历史追加（DataService 的条目格式为含 message 字段）
        for h in history_messages:
            if isinstance(h, dict):
                combined.append({"role": h.get("role", "user"), "message": h.get("message") or h.get("content", "")})

        # 调用新的分析服务接口以生成多条长期记忆
        try:
            mem_texts = self.analysis_service.generate_long_term_memories(combined)
        except Exception as e:
            print(f"生成长期记忆时 AI 分析失败: {e}")
            mem_texts = []

        # mem_texts 应为字符串列表
        mem_texts = mem_texts or []
        entries: List[Dict[str, Any]] = []
        for t in mem_texts:
            s = (t or "").strip()
            if not s:
                continue
            ts = event_timestamp if event_timestamp else datetime.now().isoformat()
            entries.append({"summary": s, "timestamp": ts})

        if entries:
            # 覆盖写入（迭代压缩：删除以前所有记忆，替换为新生成条目）
            try:
                self._write_memories(entries)
            except Exception as e:
                print(f"写入长期记忆失败: {e}")

        return entries

    def clear_memories(self) -> None:
        """清空所有长期记忆文件内容。"""
        try:
            self._write_memories([])
        except Exception:
            pass
