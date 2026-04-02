from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from dotenv import load_dotenv
from openai import OpenAI

MessageInput = list[dict[str, str]]


# 수업 포인트(고급 시작): Strategy Pattern
# - "역할별 프롬프트 생성 방식" 자체를 전략 객체로 분리한다.
# - 전략만 바꿔서 같은 질문을 다양한 역할 관점으로 실행할 수 있다.


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
class TeacherStrategy:
    name: str = "TeacherStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions="You are a teacher. Korean only. Beginner-friendly with one easy example.",
            input_data=topic,
        )


@dataclass(frozen=True)
class PlannerStrategy:
    name: str = "PlannerStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions="You are a planner. Korean only. Return 5 actionable numbered steps.",
            input_data=topic,
        )


@dataclass(frozen=True)
class ReviewerStrategy:
    name: str = "ReviewerStrategy"

    def build(self, topic: str) -> StrategyRequest:
        # messages 입력 형식 전략(고급 문법)
        return StrategyRequest(
            instructions=None,
            input_data=[
                {
                    "role": "developer",
                    "content": "You are a reviewer. Korean only. Show risks first and fixes next.",
                },
                {"role": "user", "content": topic},
            ],
        )


@dataclass(frozen=True)
class RiskManagerStrategy:
    name: str = "RiskManagerStrategy"

    def build(self, topic: str) -> StrategyRequest:
        return StrategyRequest(
            instructions=(
                "You are a risk manager for OSS team. Korean only. "
                "Return top 3 risks with mitigation and owner role."
            ),
            input_data=topic,
        )


class StrategyRunner:
    """전략 객체를 받아 실제 API 호출까지 수행하는 실행기."""

    def __init__(self, client: OpenAI, model: str) -> None:
        self.client = client
        self.model = model

    def run(self, strategy: PromptStrategy, topic: str) -> str:
        request = strategy.build(topic)
        return ask(self.client, self.model, request.input_data, request.instructions)


def main() -> None:
    client, model = build_client_and_model()
    runner = StrategyRunner(client, model)

    topic = "오픈소스 팀 프로젝트 시작 전 체크포인트를 정리해줘."
    strategies: tuple[PromptStrategy, ...] = (
        TeacherStrategy(),
        PlannerStrategy(),
        ReviewerStrategy(),
        RiskManagerStrategy(),
    )

    for strategy in strategies:
        result = runner.run(strategy, topic)
        print(f"\n=== Lesson 11 - Strategy Pattern ({strategy.name}) ===")
        print(result)


if __name__ == "__main__":
    main()
