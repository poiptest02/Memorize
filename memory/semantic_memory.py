from typing import List, Optional

from memory_schema import MemoryObject
from memory_manager import MemoryManager


class SemanticMemory:
    """
    Semantic Memory Layer

    책임:
    - 기억에 '의미적 표현'을 추가
    - 말투/언어/표현 차이를 흡수
    - MemoryManager 위에서만 동작

    ❌ DB 직접 접근 금지
    ❌ 임베딩 생성 금지 (추후 확장)
    """

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    # -------------------------------------------------
    # Add semantic knowledge
    # -------------------------------------------------

    def add_text(
        self,
        memory_id: str,
        text: str,
        language_hint: Optional[str] = None,
    ) -> bool:
        """
        기존 기억에 의미 텍스트 추가

        예:
        - "스피커 버튼"
        - "speaker on/off"
        - "이 장비 소리 켜는 곳"
        """

        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        # 중복 방지 (완전 일치 기준)
        if text not in memory.semantic.texts:
            memory.semantic.texts.append(text)

        if language_hint and language_hint not in memory.semantic.language_hints:
            memory.semantic.language_hints.append(language_hint)

        memory.semantic.touch()
        self.memory_manager.save_memory(memory)
        return True

    # -------------------------------------------------
    # Batch add (권장)
    # -------------------------------------------------

    def add_texts(
        self,
        memory_id: str,
        texts: List[str],
        language_hint: Optional[str] = None,
    ) -> bool:
        """
        여러 표현을 한 번에 추가
        """
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        changed = False
        for text in texts:
            if text not in memory.semantic.texts:
                memory.semantic.texts.append(text)
                changed = True

        if language_hint and language_hint not in memory.semantic.language_hints:
            memory.semantic.language_hints.append(language_hint)
            changed = True

        if changed:
            memory.semantic.touch()
            self.memory_manager.save_memory(memory)

        return changed

    # -------------------------------------------------
    # Read
    # -------------------------------------------------

    def get_texts(self, memory_id: str) -> List[str]:
        """
        특정 기억에 저장된 모든 의미 표현 반환
        """
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return []
        return memory.semantic.texts

    # -------------------------------------------------
    # Search (Rule-based, embedding 이전 단계)
    # -------------------------------------------------

    def naive_search(self, query: str) -> List[MemoryObject]:
        """
        임베딩 없는 1차 의미 검색 (baseline)

        - substring
        - 소문자 기준
        - 추후 embedding search로 대체 예정
        """

        query = query.lower()
        results: List[MemoryObject] = []

        for memory in self.memory_manager.list_all():
            for text in memory.semantic.texts:
                if query in text.lower():
                    results.append(memory)
                    break

        return results
