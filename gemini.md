PROJECT: Personal Career Statement Generator (CLI)

LANGUAGE / RUNTIME
- Python 3.10+
- CLI only
- File-based I/O (TXT / JSON / MD)

PYTHON CODING RULES (MANDATORY)
- Follow PEP8 strictly
- Max line length: 88 chars
- Use type hints for all functions
- No global mutable state
- No deep nesting (max 3 levels)
- Functions must be small (≤40 lines)
- Explicit variable names (no single-letter vars except i/j)
- Use dataclasses for structured data
- All file I/O must be UTF-8
- Exceptions must be explicit (no bare except)
- Print/log only via a single output utility
- No “quick hack” or inline scripts in main.py

LLM ARCHITECTURE
- LLM must be swappable
- Core logic must not depend on vendor SDK
- All LLM calls go through llm/base.py interface

LLM INTERFACE
- generate(prompt: str, context: dict) -> str
- No side effects
- Stateless per call

GOAL
- 실제 제출 가능한 경력기술서(final.md) 생성
- 사용자 회고 기반 사실 중심
- 기억 희미 시 조건부 추론 허용 (승인 필수)
- 최종 문서에는 승인된 사실만 포함

DIRECTORY
career_writer/
- main.py
- cli/
  - menu.py
  - prompts.py
- llm/
  - base.py
  - openai_client.py
  - local_client.py
- models/
  - memory.py
  - config.py
- prompts/
  - interview_fact.txt
  - interview_infer.txt
  - draft.txt
  - revise.txt
- data/
  - resume.txt
  - references/        # 추가 참고자료
    - *.txt
  - memory.json
  - config.json
- output/
  - draft.md
  - final.md

INPUT SOURCES (UPDATED)
- resume.txt: 기존 이력서
- references/*.txt:
  - 프로젝트 문서
  - 회고 메모
  - 메신저 로그 발췌
  - 설계 문서 일부
- 모든 입력은 사실 참고용 컨텍스트로만 사용

EXEC FLOW
1. 모든 입력 소스 로드 (resume + references)
2. 사용자에게 인식된 컨텍스트 요약 출력
3. 회사/프로젝트 선택
4. FACT MODE 인터뷰
5. 기억 부족 시 INFERENCE MODE 진입 여부 확인
6. 인터뷰 결과를 memory.json에 저장 (fact / inferred 구분)
7. fact 기준 draft.md 생성
8. inferred 승인 인터랙션
9. final.md 생성

USER INTERACTION RULES
- 모든 질문은 목적 명시
- 한 질문 = 한 정보 슬롯
- 자유 회고 금지
- 수정/승인은 y/n 기반
- AI는 판단하지 않고 제안만 수행

MEMORY SCHEMA
{
  "CompanyName": {
    "period": "YYYY.MM~YYYY.MM",
    "projects": [
      {
        "name": "ProjectName",
        "problem": { "text": "", "source": "fact | inferred" },
        "action":  { "text": "", "source": "fact | inferred" },
        "tech":    { "text": [], "source": "fact | inferred" },
        "result":  { "text": "", "source": "fact | inferred" },
        "difficulty": { "text": "", "source": "fact | inferred" }
      }
    ]
  }
}

DRAFT GENERATION RULES
- source == fact only
- 프로젝트당 최대 5줄
- 문장당 단일 사실
- 추상어/감정 표현 금지
- 수치 생성 금지

INFERENCE RULES
- 일반적인 직무 관행 범위만 허용
- 성과/수치/리더십 추론 금지
- inferred 자동 승격 금지

FINAL OUTPUT RULE
- final.md는 fact만 포함
- inferred 데이터는 내부 보관만

FORBIDDEN
- AI 추측 기반 문장 확정
- 이력서에 없는 기술 추가
- 엄격하지 않은 코드 작성
- main.py에 비즈니스 로직 집중

SUCCESS CRITERIA
- 결과물 그대로 제출 가능
- 사용자 체감: 사실 왜곡 없음
- LLM 교체 시 코드 수정 최소화

IMPLEMENTATION PRIORITY
1. 데이터 모델 + 파일 로딩
2. LLM 인터페이스 추상화
3. CLI 메뉴 / 인터랙션
4. 인터뷰 로직
5. draft / final 생성
