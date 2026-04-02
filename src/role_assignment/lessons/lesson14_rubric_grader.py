from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트: Template Method Pattern
# - 실행 뼈대(run)는 고정하고, 역할/프롬프트 훅만 서브클래스에서 바꾼다.
# - 한 템플릿 안에서도 작성자/리뷰어/최종편집자 역할을 분리한다.


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
        "instructions": instructions,
        "input": prompt,
    }

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


class TeachingTemplate(ABC):
    def __init__(self, client: OpenAI, model: str) -> None:
        self.client = client
        self.model = model

    def run(self, topic: str) -> str:
        # 1) 초안 작성자 역할
        draft = ask(self.client, self.model, self.user_prompt(topic), self.author_role())

        # 2) 리뷰어 역할
        review = ask(
            self.client,
            self.model,
            f"초안:\n{draft}",
            self.reviewer_role(),
        )

        # 3) 최종 편집자 역할
        final = ask(
            self.client,
            self.model,
            f"초안:\n{draft}\n\n리뷰:\n{review}",
            self.finalizer_role(),
        )
        return self.post_process(final)

    @abstractmethod
    def author_role(self) -> str:
        ...

    @abstractmethod
    def reviewer_role(self) -> str:
        ...

    @abstractmethod
    def finalizer_role(self) -> str:
        ...

    @abstractmethod
    def user_prompt(self, topic: str) -> str:
        ...

    def post_process(self, text: str) -> str:
        return text.strip()


class BeginnerTeachingTemplate(TeachingTemplate):
    def author_role(self) -> str:
        return "You are a beginner tutor. Korean only. Keep it easy with one simple example."

    def reviewer_role(self) -> str:
        return "You are a readability reviewer. Korean only. Point out 2 confusing parts."

    def finalizer_role(self) -> str:
        return "You are an editor. Korean only. Finalize in 5 short sentences."

    def user_prompt(self, topic: str) -> str:
        return f"{topic}을 처음 배우는 학생에게 설명해줘."


class IntermediateTeachingTemplate(TeachingTemplate):
    def author_role(self) -> str:
        return "You are a practical mentor. Korean only. Include workflow-level guidance."

    def reviewer_role(self) -> str:
        return "You are a reviewer. Korean only. Check missing steps and unrealistic assumptions."

    def finalizer_role(self) -> str:
        return "You are a coach. Korean only. Final answer must include checklist 4개."

    def user_prompt(self, topic: str) -> str:
        return f"{topic}을 팀 프로젝트 경험이 있는 학생 기준으로 설명해줘."


class AdvancedTeachingTemplate(TeachingTemplate):
    def author_role(self) -> str:
        return "You are an advanced architect mentor. Korean only. Include trade-offs and scaling concerns."

    def reviewer_role(self) -> str:
        return "You are a risk reviewer. Korean only. Find top 3 risks with mitigation."

    def finalizer_role(self) -> str:
        return "You are a PM. Korean only. Summarize final strategy in 6 lines."

    def user_prompt(self, topic: str) -> str:
        return f"{topic}을 실제 운영 단계까지 고려해 설명해줘."


def main() -> None:
    client, model = build_client_and_model()
    topic = "오픈소스 기여 시작법"

    templates: tuple[tuple[str, TeachingTemplate], ...] = (
        ("Beginner", BeginnerTeachingTemplate(client, model)),
        ("Intermediate", IntermediateTeachingTemplate(client, model)),
        ("Advanced", AdvancedTeachingTemplate(client, model)),
    )

    for level_name, template in templates:
        result = template.run(topic)
        print(f"\n=== Lesson 14 - Template Method ({level_name}) ===")
        print(result)


if __name__ == "__main__":
    main()
