from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from datetime import datetime
import uuid


# ---------------------------
# 유틸리티
# ---------------------------

def generate_id(prefix: str) -> str:
    """
    충돌 가능성 낮고, 로그/디버깅에 적당한 길이의 ID 생성
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def utcnow() -> datetime:
    return datetime.utcnow()


# ---------------------------
# Base Entity
# ---------------------------

@dataclass
class BaseEntity:
    """
    모든 기억 엔티티의 공통 베이스.
    - LLM 비의존
    - DB/파일 저장에 안전
    """
    entity_id: str
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    confidence: float = 1.0
    source: Literal["text", "image", "mixed"] = "text"

    def touch(self):
        """엔티티가 수정되었을 때 호출"""
        self.updated_at = utcnow()


# ---------------------------
# Structured Memory
# ---------------------------

@dataclass
class StructuredEntity(BaseEntity):
    """
    '이게 무엇인가'를 정의하는 정형 기억
    """
    entity_type: Literal[
        "concept",
        "device_component",
        "software_spec",
        "rule"
    ] = "concept"

    name: str = ""
    function: str = ""
    description: str = ""

    device: Optional[str] = None
    domain: Optional[str] = None

    aliases: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)


# ---------------------------
# Semantic Memory
# ---------------------------

@dataclass
class SemanticEntity(BaseEntity):
    """
    의미 검색 전용 메모리
    - 말투/언어 변화 대응
    """
    texts: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    language_hints: List[str] = field(default_factory=list)


# ---------------------------
# Visual Memory
# ---------------------------

@dataclass
class VisualEntity(BaseEntity):
    """
    사람이 의미를 부여한 이미지 내 영역
    """
    image_id: str = ""

    # [x, y, w, h] (0~1 normalized)
    bbox: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])

    view_angle: Optional[str] = None  # front, side, top 등
    visual_embedding: Optional[List[float]] = None


# ---------------------------
# Unified Memory Object
# ---------------------------

@dataclass
class MemoryObject:
    """
    시스템이 실제로 다루는 '완전한 기억 단위'
    모든 모달리티는 동일한 entity_id를 공유한다.
    """

    entity_id: str

    structured: StructuredEntity
    semantic: SemanticEntity
    visuals: List[VisualEntity] = field(default_factory=list)

    usage_count: int = 0
    last_accessed_at: datetime = field(default_factory=utcnow)

    # ---------- Factory ----------

    @classmethod
    def create(
        cls,
        name: str,
        entity_type: str,
        source: Literal["text", "image", "mixed"] = "text",
        device: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> "MemoryObject":
        """
        ID 정합성을 강제하는 유일한 생성 루트
        """
        new_id = generate_id("mem")

        structured = StructuredEntity(
            entity_id=new_id,
            entity_type=entity_type,
            name=name,
            device=device,
            domain=domain,
            source=source,
        )

        semantic = SemanticEntity(
            entity_id=new_id,
            source=source,
        )

        return cls(
            entity_id=new_id,
            structured=structured,
            semantic=semantic,
        )

    # ---------- Helpers ----------

    def add_visual(
        self,
        image_id: str,
        bbox: List[float],
        view_angle: Optional[str] = None,
        confidence: float = 1.0,
    ):
        """
        시각적 참조 정보 추가
        """
        v = VisualEntity(
            entity_id=self.entity_id,
            image_id=image_id,
            bbox=bbox,
            view_angle=view_angle,
            confidence=confidence,
            source="image",
        )
        self.visuals.append(v)

    def touch(self):
        """조회 또는 사용 시 호출"""
        self.usage_count += 1
        self.last_accessed_at = utcnow()
