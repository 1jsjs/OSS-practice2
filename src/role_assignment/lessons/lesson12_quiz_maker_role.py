from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트: Factory Pattern
# - 역할 프로필 생성 책임을 Factory에 모은다.
# - 파이프라인은 "어떤 역할을 쓸지"만 선언하면 된다.


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


@dataclass(frozen=True)
class RoleProfile:
    name: str
    instructions: str


class RoleProfileFactory:
    def __init__(self) -> None:
        self._profiles: dict[str, RoleProfile] = {
            "researcher": RoleProfile(
                name="researcher",
                instructions="You are a researcher. Korean only. Extract 5 핵심 사실.",
            ),
            "architect": RoleProfile(
                name="architect",
                instructions="You are a software architect. Korean only. Propose module-level structure.",
            ),
            "reviewer": RoleProfile(
                name="reviewer",
                instructions="You are a reviewer. Korean only. Point out risks and mitigation.",
            ),
            "coach": RoleProfile(
                name="coach",
                instructions="You are a learning coach. Korean only. Give beginner-friendly study plan.",
            ),
            "quiz_maker": RoleProfile(
                name="quiz_maker",
                instructions=(
                    "You are a quiz maker for OSS class. Korean only. "
                    "Produce 3 multiple-choice questions with answers and explanations."
                ),
            ),
        }

    def create(self, role_name: str) -> RoleProfile:
        profile = self._profiles.get(role_name)
        if profile is None:
            raise ValueError(f"Unknown role profile: {role_name}")
        return profile


class RolePipeline:
    """Factory가 만든 역할을 순서대로 실행해 누적 결과를 만든다."""

    def __init__(self, client: OpenAI, model: str, factory: RoleProfileFactory) -> None:
        self.client = client
        self.model = model
        self.factory = factory

    def run(self, topic: str, role_order: tuple[str, ...]) -> dict[str, str]:
        outputs: dict[str, str] = {}
        context = f"주제:\n{topic}"

        for role_name in role_order:
            profile = self.factory.create(role_name)
            result = ask(self.client, self.model, context, profile.instructions)
            outputs[role_name] = result

            # 다음 단계가 이전 결과를 참고하도록 context를 누적한다.
            context = f"{context}\n\n[{profile.name} 출력]\n{result}"

        return outputs


def main() -> None:
    client, model = build_client_and_model()
    factory = RoleProfileFactory()
    pipeline = RolePipeline(client, model, factory)

    topic = "오픈소스 협업, 라이선스, 코드리뷰 관점에서 수업 핵심 학습 포인트를 정리해줘."
    role_order = ("researcher", "architect", "reviewer", "coach", "quiz_maker")

    outputs = pipeline.run(topic, role_order)

    for role_name in role_order:
        print(f"\n=== Lesson 12 - Factory Pattern ({role_name}) ===")
        print(outputs[role_name])


if __name__ == "__main__":
    main()
