from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 학생 초안 → 채점 → 코칭 → 최종 교사 버전의 품질 향상 파이프라인.
# - "나쁜 창작자의 작품이 좋을 수도 있다"는 주장을 단계적으로 다듬는다.


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
    topic = "나쁜 창작자의 작품이 좋을 수도 있다."

    student_draft = ask(
        client,
        model,
        topic,
        "You are a freshman student. Korean only. Write a short answer in 3 lines supporting this claim.",
    )

    rubric = ask(
        client,
        model,
        f"학생 답변:\n{student_draft}",
        (
            "You are a rubric grader for a humanities class. Korean only. "
            "Grade clarity, logical consistency, and supporting evidence from 1 to 5, "
            "and provide one-line improvement per item."
        ),
    )

    coaching = ask(
        client,
        model,
        f"학생 답변:\n{student_draft}\n\n채점 결과:\n{rubric}",
        "You are a learning coach. Korean only. Give 3 revision tips the student can apply to better argue the separation of creator and work.",
    )

    final_answer = ask(
        client,
        model,
        f"학생 답변:\n{student_draft}\n\n채점:\n{rubric}\n\n코칭:\n{coaching}",
        "You are a teacher. Korean only. Produce an improved final answer in 4 lines that clearly argues a bad creator's work can still be good.",
    )

    print("\n=== Lesson 10A - 학생 초안 ===")
    print(student_draft)
    print("\n=== Lesson 10B - 루브릭 채점 ===")
    print(rubric)
    print("\n=== Lesson 10C - 코칭 ===")
    print(coaching)
    print("\n=== Lesson 10D - 최종 교사 버전 ===")
    print(final_answer)


if __name__ == "__main__":
    main()
