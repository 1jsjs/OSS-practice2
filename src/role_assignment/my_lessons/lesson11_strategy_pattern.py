from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from dotenv import load_dotenv
from openai import OpenAI

MessageInput = list[dict[str, str]]


# 수업 포인트: Strategy Pattern
# - 역할별 프롬프트 생성 방식 자체를 전략 객체로 분리한다.
# - 철학자/법학자/심리학자/윤리학자 전략으로 같은 주제를 다각도로 탐구한다.


def build_client_and_model() -> tuple[OpenAI, str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set in src/.env", file=sys.stderr)
        raise SystemExit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return OpenAI(api_key=api_key), model


def ask(
    client: OpenAI,
    model: str,
    input_data: str | MessageInput,
    instructions: str | None = None,
) -> str:
    payload: dict[str, Any] = {"model": model, "input": input_data}
    if instructions is not None:
        payload["instructions"] = instructions

    try:
        response = client.responses.create(**payload)
    except Exception as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return (response.output_text or "").strip()


@dataclass(frozen=True)
class StrategyRequest:
    instructions: str | None
    input_data: str | MessageInput


class PromptStrategy(Protocol):
    name: str

    def build(self, topic: str) -> StrategyRequest:
        ...


@dataclass(frozen=True)
class PhilosopherStrategy:
    name: str = "PhilosopherStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions=(
                "You are a philosopher. Korean only. "
                "Argue that artwork is an autonomous text independent of its creator, "
                "referencing Barthes' Death of the Author."
            ),
            input_data=topic,
        )


@dataclass(frozen=True)
class LawyerStrategy:
    name: str = "LawyerStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions=(
                "You are a legal scholar. Korean only. "
                "Explain how copyright and moral rights law treats creator and work separately."
            ),
            input_data=topic,
        )


@dataclass(frozen=True)
class PsychologistStrategy:
    name: str = "PsychologistStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions=None,
            input_data=[
                {
                    "role": "developer",
                    "content": "You are a psychologist. Korean only. Analyze how prior knowledge of a creator influences audience perception of their work.",
                },
                {"role": "user", "content": topic},
            ],
        )


@dataclass(frozen=True)
class EthicistStrategy:
    name: str = "EthicistStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions=(
                "You are an ethicist. Korean only. "
                "Distinguish between aesthetic value (separable) and the ethics of consumption (personal choice). "
                "Return top 3 key ethical considerations."
            ),
            input_data=topic,
        )


class StrategyRunner:
    def __init__(self, client: OpenAI, model: str) -> None:
        self.client = client
        self.model = model

    def run(self, strategy: PromptStrategy, topic: str) -> str:
        request = strategy.build(topic)
        return ask(self.client, self.model, request.input_data, request.instructions)


def main() -> None:
    client, model = build_client_and_model()
    runner = StrategyRunner(client, model)

    topic = "창작자와 창작물은 분리해서 볼 수 있는가? 각자의 관점에서 입장을 정리해줘."
    strategies: tuple[PromptStrategy, ...] = (
        PhilosopherStrategy(),
        LawyerStrategy(),
        PsychologistStrategy(),
        EthicistStrategy(),
    )

    for strategy in strategies:
        result = runner.run(strategy, topic)
        print(f"\n=== Lesson 11 - Strategy Pattern ({strategy.name}) ===")
        print(result)


if __name__ == "__main__":
    main()
