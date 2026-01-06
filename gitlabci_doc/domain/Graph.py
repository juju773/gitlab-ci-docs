from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class JobNode:
    """
    Represents a job node in a pipeline graph.
    """

    name: str
    stage: str
    order: int


@dataclass(frozen=True)
class Dependency:
    """
    Represents a directed dependency between two jobs.
    """

    from_job: str
    to_job: str
    kind: str  # "implicit" | "needs"


@dataclass(frozen=True)
class PipelineGraph:
    """
    Directed acyclic graph representing a GitLab CI pipeline.
    """

    nodes: list[JobNode]
    dependencies: list[Dependency]
    stage_order: list[str]
