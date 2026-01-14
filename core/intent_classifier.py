# core/intent_classifier.py

class IntentClassifier:
    """
    Brumby-14b-base 모델의 성능을 극대화하기 위해 
    한글 설명과 영어 지시어를 전략적으로 혼합한 의도 분류기 클래스입니다.
    """

    def __init__(self, llm_client):
        """
        클래스가 처음 생성될 때 실행되는 초기화 함수입니다.
        :param llm_client: Brumby 14 모델과 통신하기 위한 AI 클라이언트 객체입니다.
        """
        self.llm = llm_client  # 외부에서 만든 AI 클라이언트를 클래스 내부 변수에 저장합니다.
        
        # [중요] AI에게 줄 '지시문(Prompt)'입니다. 
        # Base 모델의 논리 사고력을 높이기 위해 구조(Task, Rules)는 영어로, 
        # 한국어 말투의 예시는 한글로 작성하여 인식률을 높였습니다.
        self.system_prompt = (
            "### Task: Classify the user's intent into exactly one of these tags.\n"
            "### Rules:\n"
            "1. [SAVE_SPEC]: 사용자가 새로운 사양, 규칙, 정보 등을 '기억'이나 '저장'하라고 할 때\n"
            "   (예: '이거 기억해둬', '사양 등록해줘', '메모해', '기록 시작')\n"
            "2. [SEARCH_MEMORY]: 과거에 저장했던 정보를 '검색'하거나 '질문'할 때\n"
            "   (예: '아까 그게 뭐야?', '데이터 찾아봐', '저번에 말한 사양 알려줘')\n"
            "3. [GENERAL_TALK]: 인사, 잡담, 시스템 사용법 등 위 항목에 해당하지 않는 일반 대화\n"
            "   (예: '안녕', '너는 누구니?', '반가워', '도움말 보여줘')\n\n"
            "### Constraint: Respond with ONLY the tag name in brackets (e.g., [SAVE_SPEC])."
        )

    def classify(self, user_input):
        """
        사용자의 입력 문장을 받아서 어떤 의도인지 분석하고 태그를 반환합니다.
        """
        
        # 1. 사용자의 입력값이 비어있는지 먼저 확인합니다. (값이 없으면 에러가 날 수 있기 때문입니다.)
        if not user_input or len(user_input.strip()) == 0:
            return "GENERAL_TALK"  # 입력이 없으면 일반 대화로 처리합니다.

        # 2. 모델에게 보낼 최종 질문(프롬프트)을 조립합니다.
        # 지시사항(system_prompt) 뒤에 사용자의 실제 말(user_input)을 따옴표로 감싸서 붙입니다.
        prompt = (
            f"{self.system_prompt}\n\n"
            f"User Input: \"{user_input}\"\n"
            f"Result (Tag Only):"
        )

        try:
            # 3. Brumby-14b AI 모델에게 조립된 질문을 던지고 답변을 기다립니다.
            raw_response = self.llm.generate(prompt)

            # 4. 모델이 준 답변의 양끝 공백을 제거하고 모두 대문자로 바꿉니다. 
            # (예: " [save_spec] " -> "[SAVE_SPEC]")
            result = raw_response.strip().upper()

            # 5. 최종 결과가 우리가 정한 3가지 태그 중 어디에 속하는지 검사합니다.
            # 'in'을 사용하는 이유는 AI가 "[SAVE_SPEC]입니다"라고 대답해도 'SAVE_SPEC'만 있으면 인식하기 위해서입니다.
            if "SAVE_SPEC" in result:
                return "SAVE_SPEC"  # '저장' 의도로 최종 판정
            elif "SEARCH_MEMORY" in result:
                return "SEARCH_MEMORY"  # '검색' 의도로 최종 판정
            else:
                return "GENERAL_TALK"  # 그 외에는 모두 '일반 대화'로 판정

        except Exception as e:
            # 6. AI 모델 호출 중에 인터넷 끊김 등의 문제가 발생하면 프로그램이 꺼지지 않게 처리합니다.
            print(f"[오류 발생] 의도 분류를 실패했습니다: {e}")
            return "GENERAL_TALK"  # 에러가 나면 안전하게 일반 대화로 넘깁니다.