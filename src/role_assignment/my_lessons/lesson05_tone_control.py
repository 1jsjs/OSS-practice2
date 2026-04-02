import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 역할은 내용뿐 아니라 '말투'도 제어한다.
# - Mentor는 판단을 강요하지 않고, 분리해서 보는 것이 하나의 유효한 선택임을 전달한다.


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
    prompt = "논란이 있는 창작자의 작품을 어떻게 대하면 좋을지 알려줘."

    no_role = ask(client, model, prompt)
    mentor_role = ask(
        client,
        model,
        prompt,
        (
            "You are a calm mentor. Answer in Korean with a kind and open-minded tone. "
            "Acknowledge that separating the work from the creator is a valid and thoughtful approach, "
            "while respecting the reader's autonomy to decide for themselves."
        ),
    )

    print("\n=== Lesson 05A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 05B - 역할 부여(Mentor) ===")
    print(mentor_role)


if __name__ == "__main__":
    main()
