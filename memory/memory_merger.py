from typing import List, Optional, Dict, Tuple
from memory_schema import MemoryObject
from memory_manager import MemoryManager
from structured_memory import StructuredMemory
from semantic_memory import SemanticMemory
from visual_memory import VisualMemory

class MemoryMerger:
    """
    Memory Merger (Decision Core)
    
    책임:
    - 독립된 각 레이어의 데이터를 종합하여 최종 의사결정 수행.
    - 가중치 기반 스코어링을 통해 최적의 기억 후보 산출.
    """

    # 가중치 상수 설정 (수치 조절로 시스템 성격 변경 가능)
    BONUS_WELL_DEFINED = 0.2    # 구조가 완성된 기억 가산점
    PENALTY_INCOMPLETE = 0.3    # 정보가 부족한 기억 감점
    BONUS_VISUAL_MATCH = 0.2    # 시각 정보 존재 시 가산점
    BONUS_USAGE_MAX = 0.1       # 사용 빈도 가산점 상한선

    def __init__(
        self,
        memory_manager: MemoryManager,
        structured: StructuredMemory,
        semantic: SemanticMemory,
        visual: VisualMemory,
    ):
        self.memory_manager = memory_manager
        self.structured = structured
        self.semantic = semantic
        self.visual = visual

    # -------------------------------------------------
    # 1. 메인 검색 로직 (Retrieve)
    # -------------------------------------------------
    def retrieve(
        self,
        query: str,
        *,
        require_visual: bool = False,
        top_k: int = 5,
    ) -> List[MemoryObject]:
        """질문에 대해 가장 적합한 기억들을 순서대로 반환합니다."""

        # [1단계] 의미 기반 후보 추출
        semantic_candidates = self.semantic.naive_search(query)
        if not semantic_candidates:
            return []

        scored: List[Tuple[MemoryObject, float]] = []

        # [2단계] 정밀 스코어링
        for memory in semantic_candidates:
            # 기본 점수 (Semantic Search 결과 점수가 있다면 그것을 활용)
            score = 0.5 

            # 2-1. 구조 평가
            if self.structured.is_well_defined(memory.entity_id):
                score += self.BONUS_WELL_DEFINED
            else:
                score -= self.PENALTY_INCOMPLETE

            # 2-2. 시각 평가
            has_visual = self.visual.has_visual(memory.entity_id)
            if require_visual:
                if not has_visual:
                    continue  # 필수 조건 미달 시 제외
                score += self.BONUS_VISUAL_MATCH
            elif has_visual:
                score += 0.05

            # 2-3. 사용 이력 평가
            score += min(memory.usage_count * 0.01, self.BONUS_USAGE_MAX)

            scored.append((memory, score))

        # [3단계] 정렬 및 결과 반환
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for memory, _ in scored[:top_k]:
            memory.usage_count += 1
            memory.touch()
            self.memory_manager.save_memory(memory)
            results.append(memory)

        return results

    # -------------------------------------------------
    # 2. 판단 근거 설명 (Explainability)
    # -------------------------------------------------
    def explain_logic(self, query: str) -> List[Dict]:
        """AI가 왜 이 기억을 골랐는지 상세 점수 내역을 반환합니다."""
        
        candidates = self.semantic.naive_search(query)
        # 변수 이름을 'explanations'로 통일했습니다!
        explanations = []

        for m in candidates:
            explanations.append({
                "entity_id": m.entity_id,
                "name": m.structured.name,
                "total_usage": m.usage_count,
                "has_visual": self.visual.has_visual(m.entity_id),
                "is_complete": self.structured.is_well_defined(m.entity_id),
                "last_seen": m.updated_at.isoformat()
            })
            
        return explanations # 이제 밑줄 없이 깔끔하게 반환됩니다.