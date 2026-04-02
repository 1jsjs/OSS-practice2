import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트:
# - 같은 질문이라도 '역할(role)'을 주면 답변 톤/구조가 달라진다.
# - 역할 없음 vs 철학 교수 비교로 분리론 개념을 소개한다.


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
    prompt = "창작자와 창작물을 분리해서 볼 수 있는지 3문장으로 설명해줘."

    no_role = ask(client, model, prompt)

    with_role = ask(
        client,
        model,
        prompt,
        (
            "You are a philosophy professor who believes artwork has independent value "
            "separate from its creator. Answer in Korean for undergraduates. "
            "Reference Roland Barthes' 'Death of the Author' naturally."
        ),
    )

    print("\n=== Lesson 01A - 역할 없음 ===")
    print(no_role)
    print("\n=== Lesson 01B - 역할 부여(철학 교수) ===")
    print(with_role)


if __name__ == "__main__":
    main()
