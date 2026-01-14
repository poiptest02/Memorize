# 🧠 Dual Memory System with Brumby 14

> **"LLM은 사고(Reasoning)하고, 시스템은 기억(Memory)한다."** > Brumby 14 base의 강력한 추론 능력과 정형/비정형 메모리 구조를 결합한 차세대 사양 관리 시스템입니다.

---

## 🚀 프로젝트 비전
단순한 대화 로그 저장을 넘어, 사용자의 의도를 파악하고 지식을 **구조화(Canonical Form)**하여 저장합니다. 사용자가 사양을 부정확하게 말하거나 다른 언어로 질문하더라도 의미 기반 검색(Semantic Search)을 통해 정확한 정보를 복원하는 것이 핵심입니다.

### 핵심 기능
1. **📌 명령형 기억**: "이 사양 기억해둬"와 같은 명령을 감지하여 지식 베이스화.
2. **🧠 의미 기반 기억 (Semantic Memory)**: 말투, 언어, 표현이 달라도 의미가 비슷하면 같은 사양을 검색.
3. **🔎 망각 보완 및 복원**: 사용자가 틀리게 말해도 "아, 이 사양 말씀하시죠?"라며 정정 및 정보 제공.
4. **📸 시각적 개념 기억 (Visual Memory)**: 장비 이미지의 특정 위치와 기능 개념을 연결하여 저장.

---

## 🏗 시스템 아키텍처

### 1. 처리 파이프라인
1. **Input**: 사용자 발화 진입
2. **Intent Classifier (Brumby 14)**: 기억 저장 / 기억 조회 / 일반 대화 목적 분류
3. **Memory Manager**: 발화 성격에 따라 Semantic / Structured / Visual 메모리 분기 처리
4. **Context Builder**: 검색된 기억 조각들을 LLM이 이해하기 쉽게 재구성
5. **Response Generator**: Brumby 14 base를 통해 최종 답변 생성

### 2. 기억 저장 방식 (Core Algorithm)
* **Canonical Form 변환**: 원문을 그대로 저장하지 않고, LLM을 통해 도메인, 핵심 규칙, 제약 조건이 포함된 JSON 형태로 구조화하여 저장.
* **벡터 임베딩**: 구조화된 데이터의 핵심 규칙과 키워드를 벡터화하여 검색 효율 극대화.

---

## 📂 폴더 구조 및 역할

```text
ai_memory_chatbot/
├── app.py                # 엔트리 포인트 (전체 파이프라인 조립 및 실행)
├── config/               # 설정 (LLM 모델 경로, DB 연결, 로깅 레벨 등)
├── core/                 # 시스템 뇌 (의도 분류기, 컨텍스트 빌더, 오케스트레이터)
├── memory/               # 🔥 핵심 메모리 (벡터 DB 연동, JSON 구조화 저장, 시각 기억 관리)
├── agents/               # 서브 AI (사양 추출 에이전트, 답변 검증 에이전트)
├── prompts/              # 프롬프트 관리 (의도 분류, 사양 추출, 답변 생성 템플릿)
├── models/               # 모델 래퍼 (Brumby 14 클라이언트, 임베딩 모델 인터페이스)
├── services/             # 외부 서비스 (Vector DB, File Storage, Cache 서비스)
├── utils/                # 공통 유틸리티 (텍스트 정규화, 유사도 계산, 언어 감지)
├── data/                 # 물리적 데이터 저장소 (Vector Index, Structured JSON)
└── tests/                # 품질 검증 (의도 분류 정확도 및 기억 복원 재현율 테스트)'

## 세부구조
project-root/
├── 📄 app.py                # [Main] 엔트리 포인트, 파이프라인 조립 및 실행
├── 📁 config/               # [Configuration] 설정 전용 폴더
│   ├── settings.py          # 공통 설정 (ENV, 경로, 모드)
│   ├── llm_config.py        # Brumby 14 모델 로딩 옵션
│   ├── memory_config.py     # 벡터 DB 및 저장소 설정
│   └── logging_config.py    # 로그 포맷 및 레벨 설정
├── 📁 core/                 # [Core] 시스템의 뇌, 흐름 제어
│   ├── orchestrator.py      # 전체 워크플로우 제어 (Intent-Agent-Memory 연결)
│   ├── intent_classifier.py # 사용자 입력 의도 분류
│   ├── context_builder.py   # 검색된 기억의 재구성 (LLM 주입용)
│   └── response_generator.py # 최종 프롬프트 구성 및 응답 생성
├── 📁 memory/               # [Memory] 기억 저장 및 관리 (시스템 핵심)
│   ├── memory_manager.py    # 메모리 통합 인터페이스 (CRUD)
│   ├── semantic_memory.py   # 벡터 DB 연동 및 임베딩 검색
│   ├── structured_memory.py # JSON 기반 사양 및 메타정보 저장
│   ├── memory_schema.py     # Canonical Spec 포맷 정의 (JSON Schema)
│   ├── visual_memory.py     # 시각적 정보 처리 및 저장
│   └── memory_merger.py     # 중복 기억 병합 및 유사 사양 정리
├── 📁 agents/               # [Agents] 특정 태스크 수행 서브 AI
│   ├── base_agent.py        # 공통 LLM 호출 인터페이스
│   ├── spec_extraction_agent.py # 사양 구조화 추출 에이전트
│   ├── memory_query_agent.py    # 검색 쿼리 최적화 에이전트
│   └── verification_agent.py    # 정보 검증 및 확신도 계산
├── 📁 prompts/              # [Prompts] 프롬프트 관리 (독립적 로직)
│   ├── intent_prompt.txt
│   ├── spec_extraction_prompt.txt
│   ├── memory_query_prompt.txt
│   ├── response_prompt.txt
│   └── verification_prompt.txt
├── 📁 models/               # [Models] 모델 호출 래퍼
│   ├── llm_client.py        # Brumby 14 호출 클라이언트
│   ├── embedding_model.py   # 문장 벡터화 모델
│   └── tokenizer.py         # 토큰 계산 및 제한 관리
├── 📁 services/             # [Services] 외부 인프라 연결
│   ├── vector_db_service.py # FAISS / Qdrant 연동
│   ├── storage_service.py   # 로컬 파일 / DB 저장 서비스
│   └── cache_service.py     # Redis 등 캐시 관리
├── 📁 utils/                # [Utils] 공통 유틸리티
│   ├── logger.py            # 시스템 로깅 통일
│   ├── text_normalizer.py   # 텍스트 전처리 및 정규화
│   ├── similarity.py        # 유사도 계산 알고리즘
│   └── language_detector.py # 언어 감지 (한/영 혼용 대응)
├── 📁 data/                 # [Data] 실제 데이터 저장소
│   ├── semantic_index/      # 벡터 DB 인덱스 파일
│   ├── structured_memory/   # 저장된 JSON 사양서들
│   └── backups/             # 메모리 스냅샷 및 백업
├── 📁 tests/                # [Tests] 테스트 코드
│   ├── test_intent.py       # 의도 분류 테스트
│   ├── test_memory_recall.py # 기억 소환 정확도 테스트
│   └── test_spec_storage.py  # 사양 저장 로직 테스트
├── 📄 README.md             # 아키텍처 다이어그램 및 설계 철학 문서
└── 📄 requirements.txt      # 의존성 라이브러리 목록

---

## 🛠 기술 스택

| 구분 | 기술 스택 | 비고 |
| :--- | :--- | :--- |
| **LLM** | Brumby 14 base | 추론, 구조화 요약, 의도 파악 전담 |
| **Embedding** | Korean/Tech optimized Model | 의미 기반 검색을 위한 벡터 변환 |
| **Vector DB** | FAISS / Qdrant | Semantic Memory 저장소 |
| **Structured DB** | JSON + SQLite / MongoDB | 정형 사양(Spec) 및 메타데이터 저장 |
| **Framework** | Python 3.10+ | 시스템 통합 및 백엔드 로직 |

---

## 💡 설계 철학 (Core Principles)

1. **LLM은 생각만 한다**
   - LLM에게 장기 기억을 맡기지 않습니다. 기억은 시스템(Vector/DB)이 보존하며, LLM은 이를 활용해 추론만 수행합니다.
2. **구조화는 필수다**
   - 대화 로그를 통째로 저장하면 검색 정확도가 떨어집니다. 반드시 **Canonical Form**으로 요약 및 구조화하여 저장합니다.
3. **의도(Intent) 우선 처리**
   - 모든 요청의 시작은 "이게 저장인가, 조회인가, 일반 대화인가"를 판단하는 것부터 시작합니다.
4. **불확실성 대응**
   - 검색 결과의 확신도(Confidence Score)를 계산하여, 정보가 모호할 경우 사용자에게 되묻거나 잘못된 정보를 정정합니다.

---

## 🧪 주요 테스트 시나리오

* **유사도 테스트**: "AAOS 차량 속성 접근법" 저장 후, "차에서 데이터 읽는 법"과 같은 일상어로 질문 시 올바른 검색 성공 여부 확인.
* **복원 테스트**: 존재하지 않는 용어나 틀린 명칭(예: 잘못된 프로토콜 이름)으로 질문 시, 저장된 지식을 바탕으로 정정 답변을 생성하는지 검증.
* **다국어 테스트**: 영어로 작성된 기술 사양을 저장한 뒤, 한국어 질문에 대해 의미적으로 정확하게 대응하는지 확인.

---

**최종 수정일: 2026-01-12**