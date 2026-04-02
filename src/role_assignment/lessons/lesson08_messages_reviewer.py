from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 역할을 단계별로 바꿔가며 품질을 높인다.
# - Writer -> Reviewer -> Fact Checker -> Editor 순서의 중간 난이도 파이프라인.


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
        "input": prompt,
        "instructions": instructions,
    }

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


def main() -> None:
    client, model = build_client_and_model()

    draft = ask(
        client,
        model,
        "오픈소스 첫 기여 가이드를 짧게 작성해줘.",
        "You are a writer. Korean only. Keep it concise.",
    )

    feedback = ask(
        client,
        model,
        f"초안:\n{draft}",
        "You are a reviewer. Korean only. Return exactly 3 concrete improvements.",
    )

    fact_check = ask(
        client,
        model,
        f"초안:\n{draft}\n\n리뷰:\n{feedback}",
        "You are a fact checker. Korean only. Point out 2 ambiguity risks.",
    )

    revised = ask(
        client,
        model,
        f"초안:\n{draft}\n\n리뷰:\n{feedback}\n\n팩트체크:\n{fact_check}",
        "You are an editor. Korean only. Apply feedback and produce improved final version.",
    )

    print("\n=== Lesson 08A - Draft(Writer) ===")
    print(draft)
    print("\n=== Lesson 08B - Feedback(Reviewer) ===")
    print(feedback)
    print("\n=== Lesson 08C - Fact Check ===")
    print(fact_check)
    print("\n=== Lesson 08D - Revised(Editor) ===")
    print(revised)


if __name__ == "__main__":
    main()
