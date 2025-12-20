from collections import defaultdict
from itertools import cycle
from typing import List, Dict

from gitlabci_doc.domain.Graph import PipelineGraph, JobNode, Dependency
from gitlabci_doc.renderers.base import GraphRenderer


class MermaidRenderer(GraphRenderer):
    """
    Renders a PipelineGraph into an enhanced Mermaid diagram:
    - strict stage ordering
    - stage grouping (subgraph)
    - colors per stage
    - implicit vs needs dependencies
    - legend
    """

    STAGE_COLORS = [
        "#E3F2FD",  # blue
        "#E8F5E9",  # green
        "#FFFDE7",  # yellow
        "#FCE4EC",  # pink
        "#F3E5F5",  # purple
    ]

    def __init__(self, stage_order: List[str]) -> None:
        self._stage_order = stage_order

    def render(self, graph: PipelineGraph) -> str:
        lines: list[str] = ["graph LR"]

        jobs_by_stage = self._group_jobs_by_stage(graph.nodes)

        styles = self._render_stages(lines, jobs_by_stage)
        lines.extend(self._render_dependencies(graph.dependencies))
        lines.extend(styles)

        return "\n".join(lines)

    @staticmethod
    def _group_jobs_by_stage(
        nodes: List[JobNode],
    ) -> Dict[str, List[JobNode]]:
        grouped: Dict[str, List[JobNode]] = defaultdict(list)

        for node in nodes:
            grouped[node.stage].append(node)

        return dict(grouped)

    def _render_stages(
        self,
        lines: list[str],
        jobs_by_stage: Dict[str, List[JobNode]],
    ) -> list[str]:
        """
        Render stages as subgraphs in strict order.
        """
        styles: list[str] = []
        color_cycle = cycle(self.STAGE_COLORS)

        for stage in self._stage_order:
            jobs = jobs_by_stage.get(stage, [])
            if not jobs:
                continue

            stage_class = f"stage_{stage}"
            color = next(color_cycle)

            lines.append(f"  subgraph {stage}")
            lines.append("    direction TB")

            for job in jobs:
                lines.append(f'    {job.name}["{job.name}"]')

            lines.append("  end")

            styles.append(
                f"classDef {stage_class} fill:{color},stroke:#333,stroke-width:1px"
            )
            styles.append(
                f"class {','.join(job.name for job in jobs)} {stage_class}"
            )

        return styles

    @staticmethod
    def _render_dependencies(
        dependencies: List[Dependency],
    ) -> list[str]:
        """
        Render dependencies with different arrow styles.
        """
        lines: list[str] = []

        for dep in dependencies:
            if dep.kind == "needs":
                lines.append(
                    f"  {dep.from_job} --> {dep.to_job}"
                )
            # else:
            #     lines.append(
            #         f"  {dep.from_job} -.-> {dep.to_job}"
            #     )

        return lines

    # @staticmethod
    # def _render_legend() -> list[str]:
    #     """
    #     Render a Mermaid legend explaining arrows.
    #     """
    #     return [
    #         "",
    #         "  subgraph Legend",
    #         "    direction TB",
    #         '    A["Job A"] --> B["Job B"]',
    #         '    C["Job C"] -.->|needs| D["Job D"]',
    #         "  end",
    #         ]