from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - delimiter로 규칙/맥락을 분리해 전달한다.
# - 역할을 추가하면서 출력 형식을 점진적으로 제어한다.


def build_client_and_model() -> tuple[OpenAI, str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(client: OpenAI, model: str, input_data: str, instructions: str | None = None) -> str:
    payload: dict[str, Any] = {"model": model, "input": input_data}
    if instructions:
        payload["instructions"] = instructions

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


def main() -> None:
    client, model = build_client_and_model()

    rule_context = """
[답변 규칙]
1) 어려운 철학 용어는 쉽게 풀어 설명한다.
2) 실제 창작자 관련 사례를 1개 포함한다.
3) 6문장 이내로 답한다.
""".strip()

    prompt = (
        "다음 규칙을 참고해서 답변해.\n"
        "```rules\n"
        f"{rule_context}\n"
        "```\n"
        "질문: 창작자와 창작물은 분리해서 볼 수 있는가?"
    )

    scenarios: list[tuple[str, str | None]] = [
        ("역할 없음", None),
        ("역할 1개(Teacher)", "You are a teacher. Korean only. Explain in a beginner-friendly way."),
        (
            "역할 2개(Teacher + Formatter)",
            (
                "You are a teacher and formatter. Korean only. "
                "Return exactly 3 numbered lines: 핵심주장, 근거사례, 한줄요약."
            ),
        ),
    ]

    for title, role_instruction in scenarios:
        result = ask(client, model, prompt, role_instruction)
        print(f"\n=== Lesson 06 - {title} ===")
        print(result)


if __name__ == "__main__":
    main()
