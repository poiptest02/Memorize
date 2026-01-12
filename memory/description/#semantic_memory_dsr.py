from typing import List, Optional
from memory_schema import MemoryObject
from memory_manager import MemoryManager

class SemanticMemory:
    """
    의미 기억 레이어: 기억에 '말뜻'을 더해주는 역할을 합니다.
    책임:
    - 기억에 "이건 소리 켜는 버튼이야" 같은 설명을 추가합니다.
    - 사람마다 다르게 말하는 표현(말투 차이)을 하나로 묶어줍니다.
    """

    def __init__(self, memory_manager: MemoryManager):
        # 이미 만들어진 '기억 관리자'를 전달받아서 사용합니다. (협업 관계)
        self.memory_manager = memory_manager

    # -------------------------------------------------
    # 1. 의미 정보 추가하기 (Add)
    # -------------------------------------------------
    def add_text(
        self,
        memory_id: str,
        text: str,
        language_hint: Optional[str] = None,
    ) -> bool:
        """기존 기억에 새로운 설명(텍스트)을 하나 추가합니다."""

        # 1. 관리자에게 "그 번호의 기억 좀 꺼내줘"라고 요청합니다.
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False # 기억이 없으면 실패!

        # 2. [중복 방지] 똑같은 설명이 이미 들어있는지 확인하고 없으면 넣습니다.
        if text not in memory.semantic.texts:
            memory.semantic.texts.append(text)

        # 3. 언어 정보(예: 'ko', 'en')가 있다면 기록해둡니다.
        if language_hint and language_hint not in memory.semantic.language_hints:
            memory.semantic.language_hints.append(language_hint)

        # 4. 기억을 수정했으니 '수정 시간'을 찍고 관리자에게 "서랍(DB)에 다시 넣어줘"라고 합니다.
        memory.semantic.touch()
        self.memory_manager.save_memory(memory)
        return True

    # -------------------------------------------------
    # 2. 한꺼번에 여러 설명 추가하기 (Batch Add)
    # -------------------------------------------------
    def add_texts(
        self,
        memory_id: str,
        texts: List[str],
        language_hint: Optional[str] = None,
    ) -> bool:
        """여러 개의 표현을 한 번에 추가할 때 씁니다. (효율적!)"""
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        changed = False # 실제로 바뀐 게 있는지 체크하는 스위치
        for text in texts:
            if text not in memory.semantic.texts:
                memory.semantic.texts.append(text)
                changed = True

        if language_hint and language_hint not in memory.semantic.language_hints:
            memory.semantic.language_hints.append(language_hint)
            changed = True

        # 바뀐 게 있을 때만 서랍(DB)에 저장해서 낭비를 줄입니다.
        if changed:
            memory.semantic.touch()
            self.memory_manager.save_memory(memory)

        return changed

    # -------------------------------------------------
    # 3. 저장된 설명들 읽어오기 (Read)
    # -------------------------------------------------
    def get_texts(self, memory_id: str) -> List[str]:
        """특정 기억에 어떤 설명들이 달려있는지 리스트로 가져옵니다."""
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return []
        return memory.semantic.texts

    # -------------------------------------------------
    # 4. 비슷한 글자로 찾기 (Search)
    # -------------------------------------------------
    def naive_search(self, query: str) -> List[MemoryObject]:
        """
        검색어가 설명에 포함되어 있는지 하나하나 찾아봅니다. (가장 기초적인 검색)
        """
        query = query.lower() # 검색어를 소문자로 바꿔서 대소문자 무시
        results: List[MemoryObject] = []

        # 모든 기억을 하나씩 꺼내서 확인합니다.
        # (주의: memory_manager에 list_all() 메서드가 구현되어 있어야 합니다.)
        for memory in self.memory_manager.list_all():
            for text in memory.semantic.texts:
                # 검색어가 설명글 안에 쏙 들어가 있나요?
                if query in text.lower():
                    results.append(memory)
                    break # 하나라도 찾았으면 다음 기억으로 넘어감

        return results