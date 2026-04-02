import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 같은 질문이라도 '역할(role)'을 주면 답변 톤/구조가 달라진다.
# - lesson01은 가장 기본 비교(역할 없음 vs 역할 있음)만 다룬다.


def setup():
    """.env에서 API 키와 모델명을 읽고 클라이언트를 만든다."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(client, model, prompt, role_text=None):
    """role_text가 있으면 instructions로 전달하고, 없으면 일반 호출한다."""
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
    prompt = "오픈소스가 무엇인지 3문장으로 설명해줘."

    # 1) 역할 없음
    no_role = ask(client, model, prompt)

    # 2) 역할 있음(친절한 교수자)
    with_role = ask(
        client,
        model,
        prompt,
        "You are a friendly professor. Answer in Korean for complete beginners.",
    )

    print("\n=== Lesson 01A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 01B - 역할 부여(교수자) ===")
    print(with_role)


if __name__ == "__main__":
    main()
