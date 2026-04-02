from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 동일한 질문을 여러 전문가 역할로 동시에 비교한다.
# - 철학자/법학자/심리학자/문화평론가의 관점 차이를 관찰한다.


def build_client_and_model() -> tuple[OpenAI, str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(client: OpenAI, model: str, prompt: str, role_instruction: str) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "input": prompt,
        "instructions": role_instruction,
    }

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


@dataclass(frozen=True)
class RoleCase:
    name: str
    instruction: str


def main() -> None:
    client, model = build_client_and_model()
    prompt = "창작자와 창작물은 분리해서 볼 수 있는가?"

    cases: tuple[RoleCase, ...] = (
        RoleCase("철학자", "You are a philosopher. Korean. Discuss the ontological independence of artwork from its creator."),
        RoleCase("법학자", "You are a legal scholar. Korean. Explain how copyright law treats creator and work as separate entities."),
        RoleCase("심리학자", "You are a psychologist. Korean. Analyze how audience perception is affected by knowledge of the creator."),
        RoleCase("문화평론가", "You are a cultural critic. Korean. Evaluate how separation theory plays out in real cultural consumption."),
    )

    for case in cases:
        result = ask(client, model, prompt, case.instruction)
        print(f"\n=== Lesson 09 - {case.name} ===")
        print(result)


if __name__ == "__main__":
    main()
