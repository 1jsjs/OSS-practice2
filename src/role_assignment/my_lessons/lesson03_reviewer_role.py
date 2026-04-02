import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - Reviewer 역할은 반대 주장의 약점을 먼저 드러낸다.
# - 분리 불가론의 논리적 허점을 비판하여 분리 가능론을 간접 강화한다.


def setup():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(client, model, prompt, role_text=None):
    payload = {"model": model, "input": prompt}
    if role_text:
        payload["instructions"] = role_text

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


def main():
    client, model = setup()
    prompt = "창작자와 창작물을 분리할 수 없다는 주장의 문제점을 알려줘."

    no_role = ask(client, model, prompt)
    reviewer_role = ask(
        client,
        model,
        prompt,
        (
            "You are a strict ethics reviewer. Answer in Korean. "
            "Show the logical weaknesses of the anti-separation argument first, "
            "then suggest counterpoints that support separation."
        ),
    )

    print("\n=== Lesson 03A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 03B - 역할 부여(윤리학자 Reviewer) ===")
    print(reviewer_role)


if __name__ == "__main__":
    main()
