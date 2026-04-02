import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - Teacher 역할은 개념의 '이유'를 초보자 눈높이에서 설명한다.
# - 분리론이 왜 중요한지, 인문학적 근거와 함께 설명한다.


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
    prompt = "창작자와 창작물을 분리해서 봐야 하는 이유를 설명해줘."

    no_role = ask(client, model, prompt)
    teacher_role = ask(
        client,
        model,
        prompt,
        (
            "You are a humanities professor. Answer in Korean for undergraduates. "
            "Explain why separating creator from work matters, and mention Roland Barthes' "
            "'Death of the Author' as supporting evidence."
        ),
    )

    print("\n=== Lesson 02A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 02B - 역할 부여(인문학 교수) ===")
    print(teacher_role)


if __name__ == "__main__":
    main()
