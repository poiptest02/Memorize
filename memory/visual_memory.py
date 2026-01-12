from typing import List, Optional, Dict

from memory_schema import MemoryObject, VisualEntity
from memory_manager import MemoryManager

class VisualMemory:
    """
    Visual Memory Layer (Architectural Final)

    책임:
    - 기억(MemoryObject)에 시각적 좌표(Bounding Box) 정보를 연결.
    - '어디에 있는가'를 데이터화하여 저장.
    - 사람이 지정한 위치 정보를 훼손 없이 보관.
    """

    def __init__(self, memory_manager: MemoryManager):
        # 데이터 통로인 매니저를 연결합니다.
        self.memory_manager = memory_manager

    # -------------------------------------------------
    # 1. 시각적 정보 추가 (개선: 중복 추가 방지)
    # -------------------------------------------------

    def add_visual(
        self,
        memory_id: str,
        *,
        image_id: str,
        bbox: List[float],
        view_angle: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """기존 기억에 새로운 시각적 위치 정보를 달아줍니다."""
        
        # 1. 매니저를 통해 기억 객체를 안전하게 가져옵니다.
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        # [개선] 이미 동일한 이미지의 동일한 좌표가 저장되어 있는지 확인 (중복 방지)
        for v in memory.visuals:
            if v.image_id == image_id and v.bbox == bbox:
                return False

        # 2. 새로운 시각 엔티티를 생성합니다. (ID는 기억의 ID를 공유)
        visual = VisualEntity(
            entity_id=memory.entity_id,
            image_id=image_id,
            bbox=bbox,
            view_angle=view_angle,
            confidence=confidence,
            source="image",
        )

        # 3. 추가적인 정보(메타데이터)가 있다면 합쳐줍니다.
        if metadata:
            visual.metadata.update(metadata)

        # 4. 기억 객체의 리스트에 추가하고 수정 시간을 기록합니다.
        memory.visuals.append(visual)
        memory.touch()

        # 5. 서랍(DB)에 최종 저장합니다.
        self.memory_manager.save_memory(memory)
        return True

    # -------------------------------------------------
    # 2. 정보 조회
    # -------------------------------------------------

    def get_visuals(
        self,
        memory_id: str,
        *,
        image_id: Optional[str] = None,
    ) -> List[VisualEntity]:
        """특정 기억의 시각 정보를 가져옵니다. (이미지별 필터 가능)"""
        
        # 1. 기억을 가져옵니다.
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return []

        # 2. 특정 이미지만 찾는 게 아니라면 전체 시각 리스트를 줍니다.
        if image_id is None:
            return memory.visuals

        # 3. 특정 이미지 ID와 일치하는 시각 정보만 걸러서 줍니다.
        return [
            v for v in memory.visuals
            if v.image_id == image_id
        ]

    # -------------------------------------------------
    # 3. 신뢰도 관리 (개선: 인덱스 대신 객체 속성 기반)
    # -------------------------------------------------

    def update_confidence(
        self,
        memory_id: str,
        image_id: str, # [개선] 인덱스 번호는 위험하므로 이미지 ID로 식별
        confidence: float,
    ) -> bool:
        """시각 정보가 얼마나 정확한지 신뢰도를 수정합니다."""
        
        memory = self.memory_manager.get(memory_id)
        if not memory:
            return False

        changed = False
        # 0.0 ~ 1.0 사이로 숫자를 강제 고정(clamping)합니다.
        safe_conf = max(0.0, min(confidence, 1.0))

        # 해당 이미지와 관련된 모든 시각 정보의 신뢰도를 바꿉니다.
        for v in memory.visuals:
            if v.image_id == image_id:
                v.confidence = safe_conf
                changed = True

        if changed:
            memory.touch()
            self.memory_manager.save_memory(memory)
        
        return changed

    # -------------------------------------------------
    # 4. 상태 판단 (Validation)
    # -------------------------------------------------

    def has_visual(self, memory_id: str) -> bool:
        """이 기억에 그림(위치 정보)이 하나라도 달려있는지 확인합니다."""
        memory = self.memory_manager.get(memory_id)
        # 기억이 존재하고, 시각 정보 리스트가 비어있지 않으면 True입니다.
        return bool(memory and memory.visuals)