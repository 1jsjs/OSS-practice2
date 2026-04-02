from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트: Builder Pattern
# - 긴 프롬프트를 역할/제약/예시/작업 블록으로 조립한다.
# - 팬(찬성) vs 피해자 지지자(반대) vs 문화평론가(중재) 구조로 토론한다.
# - 중재자는 "예술 가치는 분리 가능, 소비는 개인 선택"으로 결론 낸다.


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
        "토론 주제: 창작자와 창작물은 분리해서 볼 수 있는가? "
        "논란이 있는 창작자(범죄, 성범죄, 사회적 물의 등)의 작품을 어떻게 볼 것인가."
    )

    pro_payload = (
        PromptBuilder()
        .with_role("You are a fan and art advocate. Korean only.")
        .with_tone("passionate, art-first")
        .with_constraint("Return exactly 4 bullet points.")
        .with_constraint("Each bullet must include one concrete reason why artwork stands independently.")
        .with_example("작품의 가치는?", "창작 당시의 예술적 완성도로 평가해야 한다")
        .with_context_block(shared_context)
        .with_task("창작자와 창작물을 분리해서 볼 수 있다는 찬성 입장을 작성해줘.")
        .build()
    )

    con_payload = (
        PromptBuilder()
        .with_role("You are a victims' rights advocate. Korean only.")
        .with_tone("critical, empathetic to victims")
        .with_constraint("Return exactly 4 bullet points.")
        .with_constraint("Each bullet must include one risk and one alternative perspective.")
        .with_example("소비의 의미는?", "소비는 창작자에 대한 경제적 지지로 이어진다")
        .with_context_block(shared_context)
        .with_task("창작자와 창작물을 분리할 수 없다는 반대 입장을 작성해줘.")
        .build()
    )

    pro_view = ask(client, model, pro_payload.prompt, pro_payload.instructions)
    con_view = ask(client, model, con_payload.prompt, con_payload.instructions)

    moderator_payload = (
        PromptBuilder()
        .with_role("You are a cultural critic and moderator. Korean only.")
        .with_tone("balanced, nuanced, decision-oriented")
        .with_constraint("결론 1개: 예술적 가치는 분리 가능하다는 방향으로 결론 낼 것.")
        .with_constraint("실행안 3개: 개인이 실천할 수 있는 구체적 방안 제시.")
        .with_example("찬반 통합", "예술 가치는 분리 가능하나 소비는 개인 윤리적 판단")
        .with_context_block(f"찬성 의견:\n{pro_view}")
        .with_context_block(f"반대 의견:\n{con_view}")
        .with_task("두 의견을 통합해 창작자-창작물 분리 문제에 대한 균형 잡힌 결론을 제시해줘.")
        .build()
    )

    final_view = ask(client, model, moderator_payload.prompt, moderator_payload.instructions)

    print("\n=== Lesson 13A - Builder (팬/찬성) ===")
    print(pro_view)
    print("\n=== Lesson 13B - Builder (피해자 지지자/반대) ===")
    print(con_view)
    print("\n=== Lesson 13C - Builder (문화평론가/중재) ===")
    print(final_view)


if __name__ == "__main__":
    main()
