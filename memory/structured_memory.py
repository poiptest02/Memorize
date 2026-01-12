from typing import Optional, List, Dict
from memory_schema import MemoryObject
from memory_manager import MemoryManager

class StructuredMemory:
    """
    Structured Memory Layer (Architectural Final)

    책임:
    - MemoryObject의 '정체성(무엇인가)'과 '사용법(어떻게 쓰는가)'을 명격히 정의.
    - 별명(Aliases) 및 제약사항(Constraints)의 중복 없는 확장 관리.
    - 기억의 완성도(is_well_defined)를 판단하는 순수 비즈니스 로직 수행.

    ❌ 직접적인 리스트 순회 및 검색 기능 삭제 (Merger/Manager에게 위임)
    ❌ MemoryManager 내부 변수(_memories) 접근 금지 (캡슐화 준수)
    """

    def __init__(self, memory_manager: MemoryManager):
        # 유일한 통로인 MemoryManager만 의존성 주입으로 받습니다.
        self.memory_manager = memory_manager

    # -------------------------------------------------
    # 1. 속성 정의 및 업데이트 (Define)
    # -------------------------------------------------

    def define(
        self,
        memory_id: str,
        *,
        function: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        confidence: Optional[float] = None,
    ) -> bool:
        """기억의 핵심 정의를 갱신합니다."""
        memory = self.memory_manager.get(memory_id) # 공식 Interface만 사용
        if not memory:
            return False

        s = memory.structured
        changed = False

        if function is not None:
            s.function = function
            changed = True
        if description is not None:
            s.description = description
            changed = True
        if confidence is not None:
            s.confidence = confidence
            changed = True
        if metadata:
            s.metadata.update(metadata)
            changed = True

        if changed:
            s.touch()
            self.memory_manager.save_memory(memory)
        return changed

    # -------------------------------------------------
    # 2. 리스트형 데이터 점진적 추가 (Append-only)
    # -------------------------------------------------

    def add_requirements(
        self,
        memory_id: str,
        *,
        aliases: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> bool:
        """기존 데이터를 덮어쓰지 않고 새로운 별명이나 제약을 안전하게 추가합니다."""
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        s = memory.structured
        changed = False

        # 별명 추가 (중복 체크 로직 포함)
        if aliases:
            for a in aliases:
                if a not in s.aliases:
                    s.aliases.append(a)
                    changed = True

        # 제약 사항 추가 (중복 체크 로직 포함)
        if constraints:
            for c in constraints:
                if c not in s.constraints:
                    s.constraints.append(c)
                    changed = True

        if changed:
            s.touch()
            self.memory_manager.save_memory(memory)
        return changed

    # -------------------------------------------------
    # 3. 데이터 조회 (Read-only Accessor)
    # -------------------------------------------------

    def get_definition(self, memory_id: str) -> Optional[Dict]:
        """기억의 구조화된 정의를 딕셔너리 형태로 반환합니다."""
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return None

        s = memory.structured
        return {
            "entity_id": memory.entity_id,
            "name": s.name,
            "entity_type": s.entity_type,
            "function": s.function,
            "description": s.description,
            "aliases": s.aliases,
            "constraints": s.constraints,
            "device": s.device,
            "domain": s.domain,
            "metadata": s.metadata,
            "confidence": s.confidence,
        }

    # -------------------------------------------------
    # 4. 정합성 판단 (Validation)
    # -------------------------------------------------

    def is_well_defined(self, memory_id: str) -> bool:
        """이 기억이 후보로 쓰기에 충분한 정보를 가졌는지 판단합니다."""
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        s = memory.structured
        # 최소 기준: 이름과 기능 정의가 반드시 있어야 함
        return bool(s.name and s.function)

    # -------------------------------------------------
    # 5. 필터링 로직 (Merger/Manager 보조)
    # -------------------------------------------------

    def filter_well_defined(self, memories: List[MemoryObject]) -> List[MemoryObject]:
        """주어진 리스트에서 구조적으로 완성된 기억들만 걸러냅니다."""
        return [m for m in memories if self.is_well_defined(m.entity_id)]