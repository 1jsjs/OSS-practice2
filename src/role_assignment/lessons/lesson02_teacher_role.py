import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - Teacher 역할을 주면 초보자 대상 설명 방식으로 바뀌는지 확인한다.
# - lesson02도 문법은 단순하게 유지한다.


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
    prompt = "오픈소스 라이선스가 왜 필요한지 설명해줘."

    no_role = ask(client, model, prompt)
    teacher_role = ask(
        client,
        model,
        prompt,
        "You are a university instructor. Answer in Korean for beginners.",
    )

    print("\n=== Lesson 02A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 02B - 역할 부여(Teacher) ===")
    print(teacher_role)


if __name__ == "__main__":
    main()
