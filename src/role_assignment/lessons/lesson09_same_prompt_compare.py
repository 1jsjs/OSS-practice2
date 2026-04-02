from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 동일한 사용자 질문을 여러 역할로 동시에 비교한다.
# - 역할별 관점 차이를 빠르게 관찰할 수 있다.


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
    prompt = "오픈소스 프로젝트 온보딩 문서를 어떻게 구성하면 좋을까?"

    cases: tuple[RoleCase, ...] = (
        RoleCase("Teacher", "You are a teacher. Korean. Beginner-friendly."),
        RoleCase("Planner", "You are a planner. Korean. Return actionable steps."),
        RoleCase("Reviewer", "You are a reviewer. Korean. Show risks and mitigations."),
        RoleCase("Maintainer", "You are a maintainer. Korean. Focus on long-term 운영 규칙."),
    )

    for case in cases:
        result = ask(client, model, prompt, case.instruction)
        print(f"\n=== Lesson 09 - {case.name} Role ===")
        print(result)


if __name__ == "__main__":
    main()
