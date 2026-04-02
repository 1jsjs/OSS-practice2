from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

MessageInput = list[dict[str, str]]


# 수업 포인트:
# - instructions + messages(input 배열)를 함께 사용한다.
# - 같은 질문을 대상(audience)에 따라 다르게 설명하는 역할 비교.


def build_client_and_model() -> tuple[OpenAI, str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(
    client: OpenAI,
    model: str,
    input_data: MessageInput,
    instructions: str,
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "input": input_data,
        "instructions": instructions,
    }

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


@dataclass(frozen=True)
class AudienceCase:
    title: str
    instruction: str


def main() -> None:
    client, model = build_client_and_model()

    input_data: MessageInput = [
        {
            "role": "developer",
            "content": "한국어로 답하고, 창작자와 창작물 분리론의 맥락에서 설명해.",
        },
        {
            "role": "user",
            "content": "창작자와 창작물을 분리해서 보는 것이 왜 의미 있을까?",
        },
    ]

    cases: tuple[AudienceCase, ...] = (
        AudienceCase(
            title="중학생 대상 Teacher",
            instruction="You are a teacher. Use simple words and one relatable example like a famous singer or director.",
        ),
        AudienceCase(
            title="철학과 대학원생 대상 Mentor",
            instruction="You are a mentor. Include philosophical trade-offs, reference Barthes and Foucault, and discuss practical implications.",
        ),
        AudienceCase(
            title="문화정책가 대상 Coach",
            instruction="You are a policy coach. Focus on how separation theory affects cultural policy, funding, and public consumption decisions.",
        ),
    )

    for case in cases:
        result = ask(client, model, input_data, case.instruction)
        print(f"\n=== Lesson 07 - {case.title} ===")
        print(result)


if __name__ == "__main__":
    main()
