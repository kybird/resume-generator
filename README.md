# 개인 경력 기술서 생성기 (AI 기반)

다양한 LLM(OpenAI, Groq, Google Gemini, Anthropic/Antigravity, Local LLM)을 활용하여 전문적이고 사실에 입각한 경력 기술서 및 이력서를 생성해주는 대화형 CLI 도구입니다.

## 🚀 주요 기능

-   **대화형 인터뷰**: 현재 이력서를 분석하고 부족한 세부 사항(Problem, Action, Result 등)을 파악하기 위해 사실 확인 인터뷰를 진행합니다.
-   **다양한 모델 지원**: OpenAI (GPT-4), Groq (Llama 3), Google (Gemini), Antigravity(Google 내부 샌드박스) 간 전환이 자유롭습니다.
-   **사실 vs 추론 분리**: 사용자가 확인한 '사실'과 AI가 제안한 '추론' 정보를 엄격하게 구분하여 데이터의 정확성을 보장합니다.
-   **스마트 컨텍스트 관리**: Map-Reduce 요약 방식과 슬라이딩 윈도우 기법을 사용하여 대용량 참고 문서도 문제없이 처리합니다.
-   **안정적인 아키텍처**: Regex 기반 JSON 파싱, 자동 API 재시도(Retry), 모듈화된 설계를 적용했습니다.

## 📦 설치 방법

1.  **프로젝트 클론** 또는 다운로드 후 해당 디렉토리로 이동합니다.

2.  **의존성 패키지 설치**:
    ```bash
    pip install python-dotenv openai groq google-generativeai requests fastmcp
    ```

3.  **환경 설정**:
    -   `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.
        ```bash
        copy .env.example .env
        ```
    -   `.env` 파일을 열어 `LLM_PROVIDER`와 해당 API 키를 설정합니다.
        ```ini
        LLM_PROVIDER=openai
        OPENAI_API_KEY=sk-your-key-here
        ```

## 🛠️ 사용 방법

1.  **데이터 준비**:
    -   기존 이력서 텍스트를 `career_writer/data/resume.txt` 또는 `career_writer/data/resume.md`에 저장합니다.
    -   (선택 사항) 프로젝트 노트, 로그 등 참고 자료가 있다면 `career_writer/data/references/` 경로에 `.txt` 또는 `.md` 파일로 넣어줍니다.

2.  **프로그램 실행**:
    -   프로젝트 루트에서 제공되는 배치 파일을 실행하거나:
        ```cmd
        .\run.bat
        ```
    -   또는 직접 파이썬 스크립트를 실행합니다:
        ```bash
        cd career_writer
        python main.py
        ```

3.  **작업 흐름 (v2 아키텍처)**:
    -   **[1] 초기화 (Init Baseline)**:
        -   최초 실행 시 `resume.md`를 분석하여 `Baseline Information` (기본 정보, 경력 목록)을 추출하고 `data/baseline.json`에 동결(Frozen)합니다.
        -   이 정보는 이후 절대 변경되지 않는 뼈대 역할을 합니다.
    -   **[2] 인터뷰 (Start Interview)**:
        -   사용자가 특정 경력(Experience)을 선택하면, 6가지 핵심 질문(What, Directness, Problem, Action, Tech, Result)을 던집니다.
        -   답변은 `Fact` 객체로 변환되어 해당 경력 ID에 연결 저장됩니다 (`data/facts.json`).
        -   *날짜나 직함을 묻는 불필요한 질문은 제거되었습니다.*
    -   **[3] 이력서 생성 (Generate Resume)**:
        -   Baseline(뼈대)와 Facts(살)를 병합하여 최종 이력서 섹션을 생성합니다.
        -   결과는 `output/v2_resume.md`에 저장됩니다.

## 📂 폴더 구조

```
career_writer/
├── main.py                 # 시작점 (v2 Menu)
├── cli/                    # CLI 로직 (Init, Interviewer)
├── llm/                    # LLM 클라이언트 (OpenAI, Groq, Antigravity 등)
├── models/                 # 데이터 모델
│   ├── schema.py           # Baseline, Fact, Experience 정의
│   └── store.py            # JSON 저장소 관리자
├── processing/             # 데이터 처리
│   └── baseline_extractor.py # 이력서 파싱 요원
├── prompts/                # LLM 프롬프트
│   ├── extract_baseline.txt # 메타데이터 추출용
│   ├── v2_fact_parser.txt   # 인터뷰 답변 구조화용
│   └── v2_resume_writer.txt # 불렛포인트 작성용
├── data/                   # 데이터 저장소
│   ├── resume.txt/md       # 원본 이력서
│   ├── baseline.json       # 추출된 메타데이터 (Frozen)
│   └── facts.json          # 인터뷰로 수집된 사실들
└── output/                 # 결과물 저장소
```

## 🔌 MCP 서버 (Model Context Protocol)

이 프로젝트는 **MCP 서버**로도 동작하며, 외부 에이전트(Claude 등)가 로컬 데이터에 접근할 수 있게 합니다.

**제공 도구 (Tools v2)**:
-   `get_baseline_info()`: 동결된 경력 메타데이터(Baseline) 조회.
-   `get_linked_facts(experience_id)`: 특정 경력에 연결된 사실(Fact) 조회.
-   `add_linked_fact(...)`: 특정 경력에 새로운 사실 추가.
-   `generate_resume_v2()`: v2 생성기를 통한 문서 작성.

**실행 방법**:
1.  `run.bat` 실행 후 **2. Run MCP Server** 선택
2.  또는 직접 실행: `fastmcp run mcp_server.py`

### 🔗 Claude Desktop 등 에이전트 연결 설정

Claude Desktop 앱의 설정 파일(`config.json`)에 아래 내용을 추가하면, Claude가 직접 이 프로젝트의 도구들을 사용할 수 있습니다.

**설정 파일 경로**: 
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

**추가할 JSON**:
```json
{
  "mcpServers": {
    "resume-ai": {
      "command": "python",
      "args": ["C:\\path\\to\\your\\resume-ai\\mcp_server.py"]
    }
  }
}
```
> **Note**: `C:\\path\\to\\your\\resume-ai` 부분은 실제 프로젝트가 설치된 절대 경로로 변경해주세요. Python 가상환경을 사용 중이라면 `python` 대신 가상환경의 python 실행 파일 경로(예: `.venv\\Scripts\\python.exe`)를 입력해야 합니다.
