from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트: Builder Pattern
# - 긴 프롬프트를 "역할/제약/예시/작업" 블록으로 조립한다.
# - 찬성/반대/중재자 역할을 builder로 일관되게 생성한다.


def build_client_and_model() -> tuple[OpenAI, str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(client: OpenAI, model: str, prompt: str, instructions: str) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "instructions": instructions,
        "input": prompt,
    }

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


@dataclass(frozen=True)
class PromptPayload:
    instructions: str
    prompt: str


class PromptBuilder:
    def __init__(self) -> None:
        self._role = ""
        self._tone = ""
        self._constraints: list[str] = []
        self._examples: list[str] = []
        self._context_blocks: list[str] = []
        self._task = ""

    def with_role(self, role_text: str) -> PromptBuilder:
        self._role = role_text
        return self

    def with_tone(self, tone_text: str) -> PromptBuilder:
        self._tone = tone_text
        return self

    def with_constraint(self, constraint: str) -> PromptBuilder:
        self._constraints.append(constraint)
        return self

    def with_example(self, user_example: str, assistant_example: str) -> PromptBuilder:
        self._examples.append(f"- 입력: {user_example}\n- 출력: {assistant_example}")
        return self

    def with_context_block(self, block: str) -> PromptBuilder:
        self._context_blocks.append(block)
        return self

    def with_task(self, task_text: str) -> PromptBuilder:
        self._task = task_text
        return self

    def build(self) -> PromptPayload:
        constraints = "\n".join(f"- {item}" for item in self._constraints)
        examples = "\n".join(self._examples)
        context = "\n\n".join(self._context_blocks)

        instructions = (
            f"{self._role}\n"
            f"Tone: {self._tone}\n"
            "Constraints:\n"
            f"{constraints}"
        )
        prompt = f"컨텍스트:\n{context}\n\n예시:\n{examples}\n\n실제 요청:\n{self._task}"
        return PromptPayload(instructions=instructions, prompt=prompt)


def main() -> None:
    client, model = build_client_and_model()

    shared_context = (
        "팀 상황: 학부 오픈소스 팀 프로젝트, 일정 6주, 팀원 4명, "
        "목표는 안정적인 첫 릴리스와 문서화 품질 확보"
    )

    pro_payload = (
        PromptBuilder()
        .with_role("You are an advocate mentor. Korean only.")
        .with_tone("assertive, practical")
        .with_constraint("Return exactly 4 bullet points.")
        .with_constraint("Each bullet must include one measurable action.")
        .with_example("코드 리뷰 문화 정착", "주 2회 리뷰 슬롯 운영")
        .with_context_block(shared_context)
        .with_task("오픈소스 팀에서 엄격한 코드리뷰 정책을 도입해야 하는 이유를 작성해줘.")
        .build()
    )

    con_payload = (
        PromptBuilder()
        .with_role("You are a skeptic mentor. Korean only.")
        .with_tone("critical, realistic")
        .with_constraint("Return exactly 4 bullet points.")
        .with_constraint("Each bullet must include one risk and one alternative.")
        .with_example("리뷰 강도 과도", "핵심 모듈 우선 리뷰로 완화")
        .with_context_block(shared_context)
        .with_task("오픈소스 팀에서 엄격한 코드리뷰 정책의 단점과 대안을 작성해줘.")
        .build()
    )

    pro_view = ask(client, model, pro_payload.prompt, pro_payload.instructions)
    con_view = ask(client, model, con_payload.prompt, con_payload.instructions)

    moderator_payload = (
        PromptBuilder()
        .with_role("You are a moderator PM. Korean only.")
        .with_tone("balanced, decision-oriented")
        .with_constraint("Return: 결론 1개 + 실행안 3개")
        .with_example("찬반 정리", "타협안 도출")
        .with_context_block(f"찬성 의견:\n{pro_view}")
        .with_context_block(f"반대 의견:\n{con_view}")
        .with_task("두 의견을 통합해 6주 운영 가능한 코드리뷰 정책을 제안해줘.")
        .build()
    )

    final_policy = ask(client, model, moderator_payload.prompt, moderator_payload.instructions)

    print("\n=== Lesson 13A - Builder (Advocate) ===")
    print(pro_view)
    print("\n=== Lesson 13B - Builder (Skeptic) ===")
    print(con_view)
    print("\n=== Lesson 13C - Builder (Moderator) ===")
    print(final_policy)


if __name__ == "__main__":
    main()
