import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - Reviewer 역할은 "문제점 먼저" 같은 관점을 강제하기 좋다.


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
    prompt = "오픈소스 PR 리뷰 체크리스트를 알려줘."

    no_role = ask(client, model, prompt)
    reviewer_role = ask(
        client,
        model,
        prompt,
        "You are a strict reviewer. Answer in Korean. Show risks first, then fixes.",
    )

    print("\n=== Lesson 03A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 03B - 역할 부여(Reviewer) ===")
    print(reviewer_role)


if __name__ == "__main__":
    main()
