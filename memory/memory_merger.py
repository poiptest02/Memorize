from typing import List, Optional, Dict, Tuple
from memory_schema import MemoryObject
from memory_manager import MemoryManager
from structured_memory import StructuredMemory
from semantic_memory import SemanticMemory
from visual_memory import VisualMemory

class MemoryMerger:
    """
    Memory Merger (Decision Core - Final)

    책임:
    - 독립된 각 레이어(Structured, Semantic, Visual)의 데이터를 종합.
    - 검색 쿼리에 가장 적합한 기억을 고르는 '최종 의사결정'.
    - 비즈니스 로직에 따른 가중치 기반 스코어링(Scoring).
    """

    # [보완] 가중치 수치를 상수로 관리하여 유지보수성을 높였습니다.
    WEIGHT_SEMANTIC = 1.0       # 의미 유사도 기본 가중치
    BONUS_WELL_DEFINED = 0.2    # 구조가 잘 정의된 경우 보너스
    PENALTY_INCOMPLETE = 0.3    # 정보가 부족한 경우 감점
    BONUS_VISUAL_MATCH = 0.2    # 시각 정보가 필요한 상황에서 존재할 때 보너스
    BONUS_USAGE_MAX = 0.1       # 사용 빈도에 따른 최대 가산점

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
    # 1. 통합 검색 및 랭킹 (Retrieve)
    # -------------------------------------------------

    def retrieve(
        self,
        query: str,
        *,
        require_visual: bool = False,
        top_k: int = 5,
    ) -> List[MemoryObject]:
        """자연어 질문을 분석하여 최적의 기억 후보를 반환합니다."""

        # 1-1. [보완] 의미 기반 후보 추출 시 범위를 유연하게 제한 (효율성)
        # 검색 대상이 너무 많아지지 않도록 top_k의 3배수 정도만 먼저 뽑습니다.
        semantic_candidates = self.semantic.naive_search(query) # (참고: 기존 코드명에 맞춰 호출)
        
        # 실제로는 (memory, score) 형태의 튜플 리스트를 다룬다고 가정합니다.
        # (만약 naive_search가 리스트만 반환한다면 기본 점수를 0.5로 세팅)
        scored: List[Tuple[MemoryObject, float]] = []

        # 1-2. 각 후보를 레이어별 지식으로 정밀 평가
        for memory in semantic_candidates:
            # 기본 점수 설정 (실제 임베딩 도입 시 이 점수가 유사도 값이 됨)
            current_score = 0.5 

            # [구조 레이어 평가] "정답으로 쓸만큼 정보가 충분한가?"
            if self.structured.is_well_defined(memory.entity_id):
                current_score += self.BONUS_WELL_DEFINED
            else:
                current_score -= self.PENALTY_INCOMPLETE

            # [시각 레이어 평가] "이미지 정보가 있는가?"
            has_visual = self.visual.has_visual(memory.entity_id)
            if require_visual:
                if not has_visual:
                    continue  # 시각 정보가 필수인데 없으면 탈락
                current_score += self.BONUS_VISUAL_MATCH
            elif has_visual:
                current_score += 0.05 # 필수는 아니지만 있으면 가산점

            # [경험 기반 보정] "자주 꺼내 본 기억인가?"
            # 익숙한 기억에 가산점을 주어 '기억의 고착화'를 유도합니다.
            current_score += min(memory.usage_count * 0.01, self.BONUS_USAGE_MAX)

            scored.append((memory, current_score))

        # 1-3. 최종 점수 기준 정렬 (내림차순)
        scored.sort(key=lambda x: x[1], reverse=True)

        # 1-4. [보완] 최종 선택된 기억들만 사용 이력 업데이트
        final_results = []
        for memory, score in scored[:top_k]:
            # 실제로 사용된 기억으로 간주하고 '터치'합니다.
            memory.usage_count += 1
            memory.touch()
            self.memory_manager.save_memory(memory)
            final_results.append(memory)

        return final_results

    # -------------------------------------------------
    # 2. 판단 근거 설명 (Explainability)
    # -------------------------------------------------

    def explain_logic(self, query: str) -> List[Dict]:
        """AI가 왜 이 기억을 골랐는지 점수 내역을 투명하게 보여줍니다."""
        # retrieve와 유사한 로직을 거치되, 딕셔너리 형태로 점수 원천을 기록
        candidates = self.semantic.naive_search(query)
        report = []

        for m in candidates:
            report.append({
                "name": m.structured.name,
                "total_usage": m.usage_count,
                "has_visual": self.visual.has_visual(m.entity_id),
                "is_complete": self.structured.is_well_defined(m.entity_id),
                "last_seen": m.updated_at.isoformat()
            })
        return report