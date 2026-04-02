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
# - 개념정의 → 찬반논거 → 사례분석 → 리스크 → 시사점 → 최종브리프


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
    concept: str = ""
    arguments: str = ""
    case_study: str = ""
    risks: str = ""
    implications: str = ""
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
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None: ...


class ConceptHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.concept = ask(
            client,
            model,
            f"주제: {state.topic}",
            "You are a philosophy teacher. Korean only. Define the concept of creator-work separation in 3 clear sentences.",
        )


class ArgumentHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.arguments = ask(
            client,
            model,
            f"개념 정의:\n{state.concept}",
            (
                "You are a debate coach. Korean only. "
                "List 3 arguments FOR separation and 3 arguments AGAINST, one line each. "
                "Lean toward separation being the more defensible position."
            ),
        )


class CaseStudyHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.case_study = ask(
            client,
            model,
            f"찬반 논거:\n{state.arguments}",
            "You are a cultural analyst. Korean only. Provide 2 real-world cases where creator-work separation was debated, and how it was resolved.",
        )


class RiskHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.risks = ask(
            client,
            model,
            f"사례 분석:\n{state.case_study}",
            "You are a risk reviewer. Korean only. List top 3 risks of blindly applying separation theory, with mitigations.",
        )


class ImplicationHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.implications = ask(
            client,
            model,
            f"찬반논거:\n{state.arguments}\n\n리스크:\n{state.risks}",
            "You are a cultural critic. Korean only. Suggest 4 practical implications for how society should handle controversial creators' works.",
        )


class FinalBriefHandler(WorkflowHandler):
    def process(self, state: WorkflowState, client: OpenAI, model: str) -> None:
        state.final_brief = ask(
            client,
            model,
            (
                f"개념:\n{state.concept}\n\n"
                f"찬반논거:\n{state.arguments}\n\n"
                f"사례:\n{state.case_study}\n\n"
                f"리스크:\n{state.risks}\n\n"
                f"시사점:\n{state.implications}"
            ),
            (
                "You are a philosopher-editor. Korean only. "
                "Summarize the final brief in 7 lines. "
                "Conclude that artwork has independent aesthetic value from its creator, "
                "but the act of consumption remains each individual's ethical choice."
            ),
        )


def main() -> None:
    client, model = build_client_and_model()

    state = WorkflowState(topic="창작자와 창작물은 분리해서 볼 수 있는가?")

    chain = ConceptHandler()
    chain.set_next(ArgumentHandler()).set_next(CaseStudyHandler()).set_next(RiskHandler()).set_next(
        ImplicationHandler()
    ).set_next(FinalBriefHandler())

    chain.handle(state, client, model)

    print("\n=== Lesson 15A - 개념 정의 ===")
    print(state.concept)
    print("\n=== Lesson 15B - 찬반 논거 ===")
    print(state.arguments)
    print("\n=== Lesson 15C - 사례 분석 ===")
    print(state.case_study)
    print("\n=== Lesson 15D - 리스크 ===")
    print(state.risks)
    print("\n=== Lesson 15E - 시사점 ===")
    print(state.implications)
    print("\n=== Lesson 15F - 최종 브리프 ===")
    print(state.final_brief)


if __name__ == "__main__":
    main()
