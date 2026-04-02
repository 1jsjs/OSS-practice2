from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 하나의 답을 만들 때도 역할을 분리하면 품질 제어가 쉬워진다.
# - Student Draft -> Rubric Grader -> Learning Coach -> Final Teacher 단계.


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
    topic = "오픈소스는 무료 코드다. 마음대로 쓰면 된다."

    student_draft = ask(
        client,
        model,
        topic,
        "You are a freshman student. Korean only. Write a short answer in 3 lines.",
    )

    rubric = ask(
        client,
        model,
        f"학생 답변:\n{student_draft}",
        (
            "You are a rubric grader for OSS class. Korean only. "
            "Grade clarity, accuracy, actionability from 1 to 5, "
            "and provide one-line improvement per item."
        ),
    )

    coaching = ask(
        client,
        model,
        f"학생 답변:\n{student_draft}\n\n채점 결과:\n{rubric}",
        "You are a learning coach. Korean only. Give 3 revision tips the student can apply now.",
    )

    final_answer = ask(
        client,
        model,
        f"학생 답변:\n{student_draft}\n\n채점:\n{rubric}\n\n코칭:\n{coaching}",
        "You are a teacher. Korean only. Produce improved final answer in 4 lines.",
    )

    print("\n=== Lesson 10A - Student Draft ===")
    print(student_draft)
    print("\n=== Lesson 10B - Rubric Grader ===")
    print(rubric)
    print("\n=== Lesson 10C - Learning Coach ===")
    print(coaching)
    print("\n=== Lesson 10D - Final Teacher Version ===")
    print(final_answer)


if __name__ == "__main__":
    main()
