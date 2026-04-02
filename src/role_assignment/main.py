from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Lesson:
    number: int
    title: str
    command: str


LESSONS: tuple[Lesson, ...] = (
    Lesson(1, "기본 비교: 역할 없음 vs 교수자", "uv run role-lesson-01"),
    Lesson(2, "Teacher 역할", "uv run role-lesson-02"),
    Lesson(3, "Reviewer 역할", "uv run role-lesson-03"),
    Lesson(4, "Planner 역할", "uv run role-lesson-04"),
    Lesson(5, "Mentor 톤 제어", "uv run role-lesson-05"),
    Lesson(6, "Delimiter + 역할/형식 제어", "uv run role-lesson-06"),
    Lesson(7, "messages + Audience 역할", "uv run role-lesson-07"),
    Lesson(8, "다중 역할 Self-Refine 파이프라인", "uv run role-lesson-08"),
    Lesson(9, "동일 프롬프트 다중 역할 비교", "uv run role-lesson-09"),
    Lesson(10, "학생/채점/코칭/교수 역할 체인", "uv run role-lesson-10"),
    Lesson(11, "Strategy Pattern + 4개 역할", "uv run role-lesson-11"),
    Lesson(12, "Factory Pattern + 역할 파이프라인", "uv run role-lesson-12"),
    Lesson(13, "Builder Pattern + 찬반/중재 역할", "uv run role-lesson-13"),
    Lesson(14, "Template Method + 작성/리뷰/최종", "uv run role-lesson-14"),
    Lesson(15, "Chain of Responsibility + 6단계", "uv run role-lesson-15"),
)


def main() -> None:
    print("GPT Role Assignment - 15단계 수업 예제")
    print("아래 명령을 순서대로 실행하세요:\n")
    for lesson in LESSONS:
        print(f"{lesson.number:02d}. {lesson.title}")
        print(f"    {lesson.command}")
