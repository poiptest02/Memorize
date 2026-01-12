import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

# 스키마 임포트
from memory_schema import (
    MemoryObject,
    StructuredEntity,
    SemanticEntity,
    VisualEntity,
)


class MemoryManager:
    """
    Memory Single Source of Truth

    - RAM: 빠른 접근 (캐시)
    - SQLite: 영구 저장 (재시작 후 복원)

    ❌ 추론 없음
    ❌ 임베딩 생성 없음
    """

    # -------------------------------------------------
    # Init
    # -------------------------------------------------

    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path

        # entity_id -> MemoryObject
        self._memories: Dict[str, MemoryObject] = {}

        # 보조 인덱스 (RAM)
        self._name_index: Dict[str, List[str]] = {}

        self._init_db()
        self._load_from_db()

    # -------------------------------------------------
    # DB Connection
    # -------------------------------------------------

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")  # 성능 + 안정성
        return conn

    # -------------------------------------------------
    # Schema
    # -------------------------------------------------

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                entity_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                entity_type TEXT,
                device TEXT,
                updated_at TEXT,

                structured_payload TEXT,
                semantic_payload TEXT,
                visuals_payload TEXT,

                usage_count INTEGER,
                last_accessed_at TEXT
            )
            """)

            # 검색 최적화 인덱스
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_name ON memories(name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_device ON memories(device);")

    # -------------------------------------------------
    # Load (DB → RAM)
    # -------------------------------------------------

    def _load_from_db(self):
        """시스템 시작 시 모든 기억을 객체로 복원"""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM memories").fetchall()

        for row in rows:
            # JSON payload 로드
            s_dict = json.loads(row["structured_payload"])
            sem_dict = json.loads(row["semantic_payload"])
            vis_list = json.loads(row["visuals_payload"])

            # Structured 복원
            structured = StructuredEntity(**s_dict)
            structured.created_at = datetime.fromisoformat(structured.created_at)
            structured.updated_at = datetime.fromisoformat(structured.updated_at)

            # Semantic 복원
            semantic = SemanticEntity(**sem_dict)
            semantic.created_at = datetime.fromisoformat(semantic.created_at)
            semantic.updated_at = datetime.fromisoformat(semantic.updated_at)

            # Visual 복원
            visuals: List[VisualEntity] = []
            for v in vis_list:
                ve = VisualEntity(**v)
                ve.created_at = datetime.fromisoformat(ve.created_at)
                ve.updated_at = datetime.fromisoformat(ve.updated_at)
                visuals.append(ve)

            memory = MemoryObject(
                entity_id=row["entity_id"],
                structured=structured,
                semantic=semantic,
                visuals=visuals,
                usage_count=row["usage_count"],
                last_accessed_at=datetime.fromisoformat(row["last_accessed_at"])
            )

            self._register_to_cache(memory)

    # -------------------------------------------------
    # RAM Cache
    # -------------------------------------------------

    def _register_to_cache(self, memory: MemoryObject):
        self._memories[memory.entity_id] = memory
        name = memory.structured.name.lower()
        self._name_index.setdefault(name, []).append(memory.entity_id)

    # -------------------------------------------------
    # Save (RAM → DB)
    # -------------------------------------------------

    def save_memory(self, memory: MemoryObject):
        """MemoryObject를 SQLite에 영속 저장"""
        s = memory.structured

        with self._get_conn() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                memory.entity_id,
                s.name.lower(),
                s.entity_type,
                s.device,
                s.updated_at.isoformat(),

                json.dumps(s.__dict__, ensure_ascii=False, default=str),
                json.dumps(memory.semantic.__dict__, ensure_ascii=False, default=str),
                json.dumps([v.__dict__ for v in memory.visuals], ensure_ascii=False, default=str),

                memory.usage_count,
                memory.last_accessed_at.isoformat()
            ))

    # -------------------------------------------------
    # Interface
    # -------------------------------------------------

    def create_memory(
        self,
        name: str,
        entity_type: str,
        **kwargs
    ) -> MemoryObject:
        memory = MemoryObject.create(
            name=name,
            entity_type=entity_type,
            **kwargs
        )

        self._register_to_cache(memory)
        self.save_memory(memory)
        return memory

    def get(self, entity_id: str) -> Optional[MemoryObject]:
        memory = self._memories.get(entity_id)
        if memory:
            memory.touch()
            self.save_memory(memory)
        return memory

    def find_by_name(self, name: str) -> List[MemoryObject]:
        ids = self._name_index.get(name.lower(), [])
        return [self.get(i) for i in ids if i in self._memories]

    def delete(self, entity_id: str) -> bool:
        memory = self._memories.pop(entity_id, None)
        if not memory:
            return False

        with self._get_conn() as conn:
            conn.execute("DELETE FROM memories WHERE entity_id=?", (entity_id,))

        name = memory.structured.name.lower()
        if name in self._name_index:
            self._name_index[name].remove(entity_id)

        return True
