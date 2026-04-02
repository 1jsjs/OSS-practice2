from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# 수업 포인트: Chain of Responsibility Pattern
# - 단계별 처리자를 체인으로 연결한다.
# - 각 처리자는 자기 역할만 수행하고, 다음 처리자로 상태를 넘긴다.


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


@dataclass
class WorkflowState:
    topic: str
    idea: str = ""
    scope: str = ""
    plan: str = ""
    risks: str = ""
    metrics: str = ""
    final_brief: str = ""


class WorkflowHandler(ABC):
    def __init__(self) -> None:
        self._next: WorkflowHandler | None = None

    def set_next(self, nxt: WorkflowHandler) -> WorkflowHandler:
        self._next = nxt
        return nxt

    def handle(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        self.process(state, client, model)
        if self._next is not None:
            self._next.handle(state, client, model)

    @abstractmethod
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        ...


class IdeaHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.idea = ask(
            client,
            model,
            f"주제: {state.topic}",
            "You are a creative teacher. Korean only. Propose one concrete OSS team project idea.",
        )


class ScopeHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.scope = ask(
            client,
            model,
            f"아이디어:\n{state.idea}",
            "You are a product owner. Korean only. Define scope: must-have 3개, out-of-scope 2개.",
        )


class PlanHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.plan = ask(
            client,
            model,
            f"아이디어:\n{state.idea}\n\n범위:\n{state.scope}",
            "You are a planner. Korean only. Produce a 5-step execution plan.",
        )


class RiskReviewHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.risks = ask(
            client,
            model,
            f"실행 계획:\n{state.plan}",
            "You are a reviewer. Korean only. List top 3 risks and mitigations.",
        )


class MetricsHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.metrics = ask(
            client,
            model,
            f"실행 계획:\n{state.plan}\n\n리스크:\n{state.risks}",
            "You are a data analyst. Korean only. Suggest 4 measurable success metrics.",
        )


class FinalBriefHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.final_brief = ask(
            client,
            model,
            (
                f"아이디어:\n{state.idea}\n\n"
                f"범위:\n{state.scope}\n\n"
                f"계획:\n{state.plan}\n\n"
                f"리스크:\n{state.risks}\n\n"
                f"지표:\n{state.metrics}"
            ),
            "You are a PM. Korean only. Summarize final brief in 7 lines.",
        )


def main() -> None:
    client, model = build_client_and_model()

    state = WorkflowState(topic="학부 오픈소스 수업 팀프로젝트 주제 선정")

    # 체인 구성: 아이디어 -> 범위 -> 계획 -> 리스크 -> 지표 -> 최종 브리프
    chain = IdeaHandler()
    chain.set_next(ScopeHandler()).set_next(PlanHandler()).set_next(RiskReviewHandler()).set_next(
        MetricsHandler()
    ).set_next(FinalBriefHandler())

    chain.handle(state, client, model)

    print("\n=== Lesson 15A - Idea ===")
    print(state.idea)
    print("\n=== Lesson 15B - Scope ===")
    print(state.scope)
    print("\n=== Lesson 15C - Plan ===")
    print(state.plan)
    print("\n=== Lesson 15D - Risks ===")
    print(state.risks)
    print("\n=== Lesson 15E - Metrics ===")
    print(state.metrics)
    print("\n=== Lesson 15F - Final Brief ===")
    print(state.final_brief)


if __name__ == "__main__":
    main()
