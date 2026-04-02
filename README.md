# GPT 역할 부여 실험 — 창작자와 창작물 분리론

오픈소스소프트웨어개발 과제 2  
**주제**: 창작자와 창작물은 분리해서 볼 수 있는가?

---

## 개요

GPT에 역할(Role)을 부여하면 동일한 질문에 대한 응답의 톤, 구조, 관점이 어떻게 달라지는지 실험한 프로젝트입니다.  
기존 예제(`lessons/`)의 주제와 역할을 **창작자-창작물 분리론** 주제로 새롭게 재구성하여 `my_lessons/`에 구현했습니다.

---

## 레포 구조

```
src/
├── role_assignment/
│   ├── lessons/          # 원본 예제 코드 (lesson01~15)
│   └── my_lessons/       # 새 주제로 재구성한 코드 (lesson01~15)
├── pyproject.toml
└── uv.lock
```

---

## Lesson 구성

| Lesson | 주제 | 핵심 역할 | 패턴 |
|--------|------|-----------|------|
| 01 | 분리론이란? | 역할 없음 vs 철학 교수 | 기본 비교 |
| 02 | 분리론이 왜 중요한가? | Teacher (인문학 교수) | 단일 역할 |
| 03 | 분리론의 문제점 | Reviewer (윤리학자) | 단일 역할 |
| 04 | 논란 창작물 소비 체크리스트 | Planner | 단일 역할 |
| 05 | 논란 창작자 작품 대처법 | Mentor | 톤 제어 |
| 06 | 분리 가능한가? | 없음 / Teacher / Teacher+Formatter | 포맷 제어 |
| 07 | 대상별 설명 | 중학생 / 대학원생 / 문화정책가 | 다중 역할 |
| 08 | 분리론 에세이 | Writer→Reviewer→FactChecker→Editor | 파이프라인 |
| 09 | 동일 프롬프트 비교 | 철학자 / 법학자 / 심리학자 / 문화평론가 | 다역할 비교 |
| 10 | 학생 초안 첨삭 | Student→Grader→Coach→Teacher | 단계형 개선 |
| 11 | 입장 정리 | 철학자 / 법학자 / 심리학자 / 윤리학자 | Strategy |
| 12 | 핵심 탐구 | researcher / critic / coach / ethicist / quiz_maker | Factory |
| 13 | 찬반 토론 | 팬(찬성) / 피해자 지지자(반대) / 문화평론가(중재) | Builder |
| 14 | 수준별 설명 | Beginner / Intermediate / Advanced | Template Method |
| 15 | 심층 워크플로우 | 개념→찬반→사례→리스크→시사점→브리프 | Chain of Responsibility |

---

## 환경 설정

```bash
cd src
uv venv .venv
uv sync
```

`src/.env` 파일 생성:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o
```

---

## 실행 방법

```bash
cd src
uv run python -m role_assignment.my_lessons.lesson01_baseline
uv run python -m role_assignment.my_lessons.lesson02_teacher_role
uv run python -m role_assignment.my_lessons.lesson03_reviewer_role
uv run python -m role_assignment.my_lessons.lesson04_planner_role
uv run python -m role_assignment.my_lessons.lesson05_tone_control
uv run python -m role_assignment.my_lessons.lesson06_format_control
uv run python -m role_assignment.my_lessons.lesson07_messages_teacher
uv run python -m role_assignment.my_lessons.lesson08_messages_reviewer
uv run python -m role_assignment.my_lessons.lesson09_same_prompt_compare
uv run python -m role_assignment.my_lessons.lesson10_audience_role
uv run python -m role_assignment.my_lessons.lesson11_strategy_pattern
uv run python -m role_assignment.my_lessons.lesson12_factory_pattern
uv run python -m role_assignment.my_lessons.lesson13_debate_roles
uv run python -m role_assignment.my_lessons.lesson14_rubric_grader
uv run python -m role_assignment.my_lessons.lesson15_mini_workflow
```
