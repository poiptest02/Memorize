# 1. 도구 상자에서 필요한 연장들을 꺼내오는 거야.
from dataclasses import dataclass, field # 데이터 바구니를 쉽게 만들어주는 도구
from typing import List, Dict, Optional, Literal # 바구니 안에 뭐가 들어갈지 미리 정해주는 도구
from datetime import datetime # '지금 몇 시지?'를 알려주는 도구
import uuid # 세상에 하나뿐인 '번호표'를 만들어주는 도구


# ---------------------------
# 유틸리티 (비서 같은 함수들)
# ---------------------------

# 새로운 기억이 생길 때마다 고유한 번호표(ID)를 만들어주는 기능이야.
def generate_id(prefix: str) -> str:
    # 예: "mem_123456789abc" 처럼 겹치지 않는 이름을 지어줘.
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# 현재 시간을 알려주는 기능이야.
def utcnow() -> datetime:
    return datetime.utcnow()


# ---------------------------
# Base Entity (모든 기억의 공통 기초)
# ---------------------------

# 이건 모든 기억들이 기본적으로 가져야 할 '공통 양식'이야.
@dataclass
class BaseEntity:
    entity_id: str # 기억의 고유 번호 (이게 있어야 안 헷갈려!)
    created_at: datetime = field(default_factory=utcnow) # 이 기억이 언제 생겼는지 기록해.
    updated_at: datetime = field(default_factory=utcnow) # 마지막으로 언제 수정했는지 기록해.

    confidence: float = 1.0 # 이 기억이 얼마나 정확한지 점수를 매겨 (1.0은 100점!)
    source: Literal["text", "image", "mixed"] = "text" # 이 기억을 어디서 얻었어? (글? 사진?) / 기본 초기화 상태 'text' 로 설정

    # 기억이 수정되면 시간을 새로 고치는 기능이야.
    def touch(self):
        self.updated_at = utcnow()


# ---------------------------
# Structured Memory (사전적인 정의)
# ---------------------------

# 이건 '이 물건이 공식적으로 뭐냐?'를 적는 칸이야.
@dataclass
class StructuredEntity(BaseEntity):
    entity_type: Literal[
        "concept",          # 그냥 생각 (예: 사랑, 민주주의)
        "device_component", # 기계 부품 (예: 핸드폰 액정)
        "software_spec",    # 프로그램 설명
        "rule"              # 규칙 (예: 여기서 담배 금지)
    ] = "concept"

    name: str = "" # 이름이 뭐야?
    function: str = "" # 무슨 기능을 해?
    description: str = "" # 자세하게 설명해봐.

    device: Optional[str] = None # 연관된 기계가 있어?
    domain: Optional[str] = None # 어떤 분야야? (요리? 코딩?)

    aliases: List[str] = field(default_factory=list) # 다른 이름이 있어? (별명)
    constraints: List[str] = field(default_factory=list) # 하면 안 되는 행동이나 제약 조건이 있어?

    metadata: Dict = field(default_factory=dict) # 그 외에 더 적고 싶은 잡다한 것들.


# ---------------------------
# Semantic Memory (의미와 느낌)
# ---------------------------

# 이건 컴퓨터가 그 말의 '뜻'을 수학적으로 이해하기 위해 쓰는 칸이야.
@dataclass
class SemanticEntity(BaseEntity):
    texts: List[str] = field(default_factory=list) # 관련 있는 문장들을 모아둬.
    embedding: Optional[List[float]] = None # 문장을 숫자로 바꿔서 저장해 (AI가 이해하는 방식이야)

    language_hints: List[str] = field(default_factory=list) # 이게 한국어인지 영어인지 적어줘.


# ---------------------------
# Visual Memory (눈으로 본 것)
# ---------------------------

# 이건 사진 속에서 '어디에 있는지'를 기억하는 칸이야.
@dataclass
class VisualEntity(BaseEntity):
    image_id: str = "" # 어떤 사진 파일인지 적어.

    # [x좌표, y좌표, 가로길이, 세로길이]로 사진 속 위치를 네모칸 쳐서 저장해.
    bbox: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])

    view_angle: Optional[str] = None  # 정면에서 본 건지, 위에서 본 건지 적어.
    visual_embedding: Optional[List[float]] = None # 이미지의 특징을 숫자로 저장해.


# ---------------------------
# Unified Memory Object (종합 선물 세트)
# ---------------------------

# 이게 진짜 '기억 보따리'야! 위에 적은 모든 정보를 이 하나에 다 담아.
@dataclass
class MemoryObject:
    entity_id: str # 보따리 번호

    structured: StructuredEntity # 사전적 정의 상자
    semantic: SemanticEntity # 의미 상자
    visuals: List[VisualEntity] = field(default_factory=list) # 사진들 상자

    usage_count: int = 0 # 이 기억을 몇 번이나 꺼내 봤어?
    last_accessed_at: datetime = field(default_factory=utcnow) # 마지막으로 언제 꺼냈어?

    # 새로운 기억 보따리를 처음 만들 때 쓰는 기능이야.
    @classmethod
    def create(
        cls,
        name: str,
        entity_type: str,
        source: Literal["text", "image", "mixed"] = "text",
        device: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> "MemoryObject":
        
        new_id = generate_id("mem") # 고유 번호표를 뽑고,

        # 사전 정의 상자를 만들고,
        structured = StructuredEntity(
            entity_id=new_id,
            entity_type=entity_type,
            name=name,
            device=device,
            domain=domain,
            source=source,
        )

        # 의미 상자도 만들어서,
        semantic = SemanticEntity(
            entity_id=new_id,
            source=source,
        )

        # 보따리에 쏙 집어넣어서 돌려줘!
        return cls(
            entity_id=new_id,
            structured=structured,
            semantic=semantic,
        )

    # 이 기억에 사진 정보를 추가하고 싶을 때 쓰는 기능이야.
    def add_visual(
        self,
        image_id: str,
        bbox: List[float],
        view_angle: Optional[str] = None,
        confidence: float = 1.0,
    ):
        v = VisualEntity(
            entity_id=self.entity_id,
            image_id=image_id,
            bbox=bbox,
            view_angle=view_angle,
            confidence=confidence,
            source="image",
        )
        self.visuals.append(v) # 사진 목록에 추가!

    # 기억을 사용하면 "조회수"를 올리고 시간을 업데이트해.
    def touch(self):
        self.usage_count += 1
        self.last_accessed_at = utcnow()