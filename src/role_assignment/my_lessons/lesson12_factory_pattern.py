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
# - researcher → critic → coach → ethicist → quiz_maker 순서로 누적 탐구한다.


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
                instructions="You are a researcher. Korean only. Extract 5 key facts about creator-work separation theory.",
            ),
            "critic": RoleProfile(
                name="critic",
                instructions="You are a cultural critic. Korean only. Point out risks and limitations of the separation argument.",
            ),
            "coach": RoleProfile(
                name="coach",
                instructions="You are a learning coach. Korean only. Give a beginner-friendly summary of why separation theory matters.",
            ),
            "ethicist": RoleProfile(
                name="ethicist",
                instructions=(
                    "You are an ethicist. Korean only. "
                    "Clarify that aesthetic value is separable from creator morality, "
                    "but consumption is a personal ethical choice."
                ),
            ),
            "quiz_maker": RoleProfile(
                name="quiz_maker",
                instructions=(
                    "You are a quiz maker for a humanities class. Korean only. "
                    "Produce 3 multiple-choice questions about creator-work separation with answers and explanations."
                ),
            ),
        }

    def create(self, role_name: str) -> RoleProfile:
        profile = self._profiles.get(role_name)
        if profile is None:
            raise ValueError(f"Unknown role profile: {role_name}")
        return profile


class RolePipeline:
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
            context = f"{context}\n\n[{profile.name} 출력]\n{result}"

        return outputs


def main() -> None:
    client, model = build_client_and_model()
    factory = RoleProfileFactory()
    pipeline = RolePipeline(client, model, factory)

    topic = "창작자와 창작물은 분리해서 볼 수 있다는 주제의 핵심을 탐구해줘."
    role_order = ("researcher", "critic", "coach", "ethicist", "quiz_maker")

    outputs = pipeline.run(topic, role_order)

    for role_name in role_order:
        print(f"\n=== Lesson 12 - Factory Pattern ({role_name}) ===")
        print(outputs[role_name])


if __name__ == "__main__":
    main()
