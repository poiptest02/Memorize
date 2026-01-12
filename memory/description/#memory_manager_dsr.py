import sqlite3  # 가벼운 데이터베이스(서랍)를 쓰기 위한 도구
import json     # 파이썬 데이터를 글자 형태로 바꿔서 저장하기 위한 도구
from datetime import datetime  # 시간을 기록하기 위한 도구
from typing import Dict, List, Optional  # 코드의 가독성을 높여주는 도우미

# 미리 만들어둔 기억의 틀(설계도)을 가져옵니다.
from memory_schema import (
    MemoryObject,
    StructuredEntity,
    SemanticEntity,
    VisualEntity,
)

class MemoryManager:
    """
    기억 관리자: 모든 기억이 생성되고, 저장되고, 사라지는 통로입니다.
    """

    # -------------------------------------------------
    # 1. 초기화 (설치 및 준비)
    # -------------------------------------------------
    def __init__(self, db_path: str = "memory.db"):
        # 저장될 데이터베이스 파일 이름을 정합니다 (기본: memory.db)
        self.db_path = db_path

        # [_memories] 책상 위 공간입니다. 지금 바로 쓰고 있는 기억들을 담아둡니다.
        self._memories: Dict[str, MemoryObject] = {}

        # [_name_index] 이름표 모음입니다. 이름만 보고 빠르게 기억을 찾기 위해 만듭니다.
        self._name_index: Dict[str, List[str]] = {}

        # 프로그램을 켜자마자 실행될 작업들
        self._init_db()       # 1. 서랍(DB)이 없으면 만듭니다.
        self._load_from_db()   # 2. 서랍에 들어있던 예전 기억을 책상(RAM)으로 꺼냅니다.

    # -------------------------------------------------
    # 2. 서랍(DB) 연결 통로 만들기
    # -------------------------------------------------
    def _get_conn(self) -> sqlite3.Connection:
        # 데이터베이스 파일에 접속합니다.
        conn = sqlite3.connect(self.db_path)
        # 데이터를 가져올 때 이름으로 편하게 가져오게 설정합니다.
        conn.row_factory = sqlite3.Row
        # 데이터의 안전과 성능을 위한 특수 설정들입니다.
        conn.execute("PRAGMA foreign_keys = ON;") # 관계 연결 활성화
        conn.execute("PRAGMA journal_mode = WAL;") # 동시에 읽고 쓰기 성능 향상
        return conn

    # -------------------------------------------------
    # 3. 서랍(DB)의 구조 짜기
    # -------------------------------------------------
    def _init_db(self):
        with self._get_conn() as conn:
            # 'memories'라는 이름의 표(Table)를 만듭니다. 각 칸에는 정해진 데이터가 들어갑니다.
            conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                entity_id TEXT PRIMARY KEY,  -- 기억의 고유 번호 (중복 안됨)
                name TEXT NOT NULL,          -- 기억의 이름
                entity_type TEXT,            -- 기억의 종류 (개념, 장치 등)
                device TEXT,                 -- 관련 장치 이름
                updated_at TEXT,             -- 마지막으로 수정된 시간

                structured_payload TEXT,     -- 상세 정보들을 글자로 뭉쳐서 저장 (JSON)
                semantic_payload TEXT,       -- 의미 정보들을 글자로 뭉쳐서 저장 (JSON)
                visuals_payload TEXT,        -- 시각 정보들을 글자로 뭉쳐서 저장 (JSON)

                usage_count INTEGER,         -- 얼마나 자주 사용했나
                last_accessed_at TEXT        -- 마지막으로 꺼내본 시간
            )
            """)

            # 이름과 장치로 검색할 때 0.001초만에 찾을 수 있게 '인덱스(색인)'를 만듭니다.
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_name ON memories(name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_device ON memories(device);")

    # -------------------------------------------------
    # 4. 기억 복원하기 (서랍 → 책상)
    # -------------------------------------------------
    def _load_from_db(self):
        """프로그램을 켰을 때, 예전 기억을 DB에서 꺼내 파이썬 객체로 만듭니다."""
        with self._get_conn() as conn:
            # 서랍에 있는 모든 기억을 한 줄씩 가져옵니다.
            rows = conn.execute("SELECT * FROM memories").fetchall()

        for row in rows:
            # 뭉쳐서 저장된 글자(JSON)를 다시 파이썬 딕셔너리(데이터 묶음)로 풉니다.
            s_dict = json.loads(row["structured_payload"])
            sem_dict = json.loads(row["semantic_payload"])
            vis_list = json.loads(row["visuals_payload"])

            # 딕셔너리 데이터를 설계도(StructuredEntity 등)에 부어 실제 객체로 만듭니다.
            # 이 과정에서 '글자'였던 시간을 다시 '진짜 시간 객체'로 바꿉니다.
            structured = StructuredEntity(**s_dict)
            structured.created_at = datetime.fromisoformat(structured.created_at)
            structured.updated_at = datetime.fromisoformat(structured.updated_at)

            semantic = SemanticEntity(**sem_dict)
            semantic.created_at = datetime.fromisoformat(semantic.created_at)
            semantic.updated_at = datetime.fromisoformat(semantic.updated_at)

            # 시각 정보는 여러 개일 수 있으니 하나씩 복구합니다.
            visuals: List[VisualEntity] = []
            for v in vis_list:
                ve = VisualEntity(**v)
                ve.created_at = datetime.fromisoformat(ve.created_at)
                ve.updated_at = datetime.fromisoformat(ve.updated_at)
                visuals.append(ve)

            # 최종적으로 하나의 '통합 기억 객체'를 조립합니다.
            memory = MemoryObject(
                entity_id=row["entity_id"],
                structured=structured,
                semantic=semantic,
                visuals=visuals,
                usage_count=row["usage_count"],
                last_accessed_at=datetime.fromisoformat(row["last_accessed_at"])
            )

            # 조립된 기억을 책상(캐시) 위에 올립니다.
            self._register_to_cache(memory)

    # -------------------------------------------------
    # 5. 책상 정리하기
    # -------------------------------------------------
    def _register_to_cache(self, memory: MemoryObject):
        # 고유 번호로 기억을 저장합니다.
        self._memories[memory.entity_id] = memory
        # 이름으로도 찾을 수 있게 이름표를 달아둡니다 (소문자로 통일해서 검색 편하게).
        name = memory.structured.name.lower()
        self._name_index.setdefault(name, []).append(memory.entity_id)

    # -------------------------------------------------
    # 6. 기억 저장하기 (책상 → 서랍)
    # -------------------------------------------------
    def save_memory(self, memory: MemoryObject):
        """기억이 변할 때마다 서랍(DB)에 안전하게 기록합니다."""
        s = memory.structured

        with self._get_conn() as conn:
            # INSERT OR REPLACE: 이미 있으면 업데이트하고, 없으면 새로 만듭니다.
            conn.execute("""
            INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                memory.entity_id,
                s.name.lower(),
                s.entity_type,
                s.device,
                s.updated_at.isoformat(), # 시간을 글자 형태로 바꿔서 저장

                # 복잡한 데이터들은 json.dumps를 써서 '글자' 하나로 뭉칩니다.
                json.dumps(s.__dict__, ensure_ascii=False, default=str),
                json.dumps(memory.semantic.__dict__, ensure_ascii=False, default=str),
                json.dumps([v.__dict__ for v in memory.visuals], ensure_ascii=False, default=str),

                memory.usage_count,
                memory.last_accessed_at.isoformat()
            ))

    # -------------------------------------------------
    # 7. 실제 사용자가 쓰는 기능들 (API)
    # -------------------------------------------------
    def create_memory(self, name: str, entity_type: str, **kwargs) -> MemoryObject:
        """[새 기억 만들기] 사용자가 이름을 말하면 기억을 생성하고 저장합니다."""
        # 설계도에 따라 새 기억을 찍어냅니다.
        memory = MemoryObject.create(name=name, entity_type=entity_type, **kwargs)

        # 책상에 올리고 서랍에도 저장합니다.
        self._register_to_cache(memory)
        self.save_memory(memory)
        return memory

    def get(self, entity_id: str) -> Optional[MemoryObject]:
        """[기억 꺼내기] ID를 주면 기억을 찾아줍니다. 찾을 때마다 사용 횟수가 늘어납니다."""
        memory = self._memories.get(entity_id)
        if memory:
            memory.touch()       # 사용 시간과 횟수 업데이트
            self.save_memory(memory) # 변한 내용을 서랍에 반영
        return memory

    def find_by_name(self, name: str) -> List[MemoryObject]:
        """[이름으로 찾기] 이름표를 보고 관련된 모든 기억을 리스트로 돌려줍니다."""
        ids = self._name_index.get(name.lower(), [])
        return [self.get(i) for i in ids if i in self._memories]

    def delete(self, entity_id: str) -> bool:
        """[기억 지우기] 책상과 서랍에서 해당 기억을 영구히 삭제합니다."""
        # 책상에서 먼저 지웁니다.
        memory = self._memories.pop(entity_id, None)
        if not memory:
            return False

        # 서랍(DB)에서도 지웁니다.
        with self._get_conn() as conn:
            conn.execute("DELETE FROM memories WHERE entity_id=?", (entity_id,))

        # 이름표 모음에서도 삭제합니다.
        name = memory.structured.name.lower()
        if name in self._name_index:
            self._name_index[name].remove(entity_id)

        return True