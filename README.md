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
└── tests/                # 품질 검증 (의도 분류 정확도 및 기억 복원 재현율 테스트)