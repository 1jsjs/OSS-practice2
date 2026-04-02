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
# - 입문자/중급자/심화 수준별로 분리론을 다르게 설명한다.


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
        draft = ask(self.client, self.model, self.user_prompt(topic), self.author_role())
        review = ask(self.client, self.model, f"초안:\n{draft}", self.reviewer_role())
        final = ask(
            self.client,
            self.model,
            f"초안:\n{draft}\n\n리뷰:\n{review}",
            self.finalizer_role(),
        )
        return self.post_process(final)

    @abstractmethod
    def author_role(self) -> str: ...

    @abstractmethod
    def reviewer_role(self) -> str: ...

    @abstractmethod
    def finalizer_role(self) -> str: ...

    @abstractmethod
    def user_prompt(self, topic: str) -> str: ...

    def post_process(self, text: str) -> str:
        return text.strip()


class BeginnerTeachingTemplate(TeachingTemplate):
    def author_role(self) -> str:
        return "You are a beginner tutor. Korean only. Use simple words and one pop culture example."

    def reviewer_role(self) -> str:
        return "You are a readability reviewer. Korean only. Point out 2 parts that might confuse a beginner."

    def finalizer_role(self) -> str:
        return "You are an editor. Korean only. Finalize in 5 short sentences a beginner can understand."

    def user_prompt(self, topic: str) -> str:
        return f"{topic}을 처음 접하는 중학생에게 설명해줘."


class IntermediateTeachingTemplate(TeachingTemplate):
    def author_role(self) -> str:
        return "You are a practical mentor. Korean only. Include real cases of controversial creators and their works."

    def reviewer_role(self) -> str:
        return "You are a reviewer. Korean only. Check for missing counterarguments and oversimplified claims."

    def finalizer_role(self) -> str:
        return "You are a coach. Korean only. Final answer must include a checklist of 4 points for evaluating creator-work separation."

    def user_prompt(self, topic: str) -> str:
        return f"{topic}을 인문학 수업을 들은 대학생 기준으로 설명해줘."


class AdvancedTeachingTemplate(TeachingTemplate):
    def author_role(self) -> str:
        return "You are an advanced cultural theorist. Korean only. Include Barthes, Foucault, and the intentional fallacy."

    def reviewer_role(self) -> str:
        return "You are a critical reviewer. Korean only. Find top 3 theoretical weaknesses with suggested rebuttals."

    def finalizer_role(self) -> str:
        return "You are a philosopher-editor. Korean only. Summarize the final position in 6 lines with a clear thesis."

    def user_prompt(self, topic: str) -> str:
        return f"{topic}을 철학적 이론까지 포함하여 심화 수준으로 설명해줘."


def main() -> None:
    client, model = build_client_and_model()
    topic = "창작자와 창작물 분리론"

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
