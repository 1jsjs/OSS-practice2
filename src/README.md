# GPT Role Assignment Teaching Pack

학생들이 수업 시간에 파일 하나를 열고 라인 단위로 설명하기 쉽게,
각 레슨은 **파일 1개 완결형**으로 구성되어 있습니다.

- 실행 진입점이 곧 예제 코드 본문: `role_assignment/lessons/lessonXX_*.py`
- 예제별 관련 함수/클래스는 해당 파일 안에만 배치
- 모든 코드와 `.env`는 `src/` 아래에만 존재

## 1) 환경 준비

```bash
cd src
uv venv .venv
uv sync
```

`src/.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o
```

## 2) 실행 방법

전체 단계 목록:

```bash
cd src
uv run role-assignment
```

개별 레슨:

```bash
cd src
uv run role-lesson-01
...
uv run role-lesson-15
```

## 3) 난이도 구성 (요청 반영)

### 1~5: 초급 (문법 단순 + 역할 유무 비교 중심)

1. 기본 비교: 역할 없음 vs 교수자
2. Teacher 역할
3. Reviewer 역할
4. Planner 역할
5. Mentor 톤 제어

특징:
- 문법을 단순하게 유지
- 대부분 `ask(..., role_text=None)` 형태
- 모든 레슨에서 `역할 없음`과 `역할 있음` 비교 가능

### 6~10: 중급 (문법 확장 + 다중 역할)

6. Delimiter + 역할/형식 제어
7. `instructions` + `messages` + Audience 역할 비교
8. Writer/Reviewer/Fact Checker/Editor 파이프라인
9. 동일 프롬프트 다중 역할 비교(Teacher/Planner/Reviewer/Maintainer)
10. Student/Rubric Grader/Coach/Teacher 단계형 개선

특징:
- `dataclass`, `tuple/list 반복`, 메시지 배열 사용
- 한 문제를 여러 역할로 분해하는 흐름

### 11~15: 고급 (복합 구조 + 역할 다수)

11. Strategy Pattern + 4개 역할 전략
12. Factory Pattern + 역할 프로필 파이프라인
13. Builder Pattern + 찬성/반대/중재 역할 조립
14. Template Method + 작성/리뷰/최종 역할 훅
15. Chain of Responsibility + 6단계 워크플로우

특징:
- 역할뿐 아니라 "구조(패턴)"까지 설계
- 역할 수 증가 + 단계별 상태 전달

## 4) 코드 읽기 포인트 (설명)

1. `setup/build_client_and_model`: API 키와 모델 설정
2. `ask`: OpenAI Responses API 호출 래퍼
3. `main`: 수업에서 보여줄 핵심 실험 시나리오
4. (중/고급) `dataclass`, 패턴 클래스: 역할과 실행 흐름의 분리

각 파일 상단에는 해당 레슨의 학습 목적을 주석으로 추가해두었습니다.
