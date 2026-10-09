"""
Semantic Chunk Manager for Voice Service (First-Chunk Streaming TTS).
Splits real-time token stream into natural, expressive, Korean semantic chunks
for low-latency First-Chunk Audio Synthesis.
"""

from typing import List, Optional


class SemanticChunkManager:
    """
    Buffers streaming LLM tokens and emits natural semantic chunks for TTS processing.
    """

    DEFAULT_SENTENCE_DELIMITERS = {".", "!", "?", "\n", "…", "。", "！", "？"}
    DEFAULT_CLAUSE_DELIMITERS = {",", ";", ":", "·", " - "}

    def __init__(
        self,
        min_chunk_length: int = 5,
        max_chunk_length: int = 60,
        clause_break_threshold: int = 15,
    ):
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
        self.clause_break_threshold = clause_break_threshold
        self._buffer = ""
        self._emitted_chunks: List[str] = []

    @property
    def buffer(self) -> str:
        return self._buffer

    @property
    def emitted_chunks(self) -> List[str]:
        return self._emitted_chunks

    def reset(self) -> None:
        self._buffer = ""
        self._emitted_chunks.clear()

    def push(self, token: str) -> List[str]:
        if not token:
            return []

        self._buffer += token
        emitted = []

        while True:
            chunk = self._try_extract_chunk()
            if chunk:
                emitted.append(chunk)
                self._emitted_chunks.append(chunk)
            else:
                break

        return emitted

    def flush(self) -> List[str]:
        remaining = self._buffer.strip()
        self._buffer = ""
        if remaining:
            self._emitted_chunks.append(remaining)
            return [remaining]
        return []

    def _try_extract_chunk(self) -> Optional[str]:
        if not self._buffer:
            return None

        buf_len = len(self._buffer)

        # 1. Check for Sentence Delimiters (. ! ? \n)
        for i, char in enumerate(self._buffer):
            if char in self.DEFAULT_SENTENCE_DELIMITERS:
                candidate = self._buffer[: i + 1].strip()
                if len(candidate) >= 4:
                    self._buffer = self._buffer[i + 1 :].lstrip()
                    return candidate

        # 2. Check for Clause Delimiters (,)
        if buf_len >= self.clause_break_threshold:
            for i, char in enumerate(self._buffer):
                if char in self.DEFAULT_CLAUSE_DELIMITERS:
                    candidate = self._buffer[: i + 1].strip()
                    if len(candidate) >= self.min_chunk_length:
                        self._buffer = self._buffer[i + 1 :].lstrip()
                        return candidate

        # 3. Handle Max Length Overflow
        if buf_len >= self.max_chunk_length:
            split_idx = self._buffer.rfind(" ", self.min_chunk_length, self.max_chunk_length)
            if split_idx != -1:
                candidate = self._buffer[:split_idx].strip()
                self._buffer = self._buffer[split_idx + 1 :].lstrip()
                return candidate
            else:
                candidate = self._buffer[: self.max_chunk_length].strip()
                self._buffer = self._buffer[self.max_chunk_length :].lstrip()
                return candidate

        return None
