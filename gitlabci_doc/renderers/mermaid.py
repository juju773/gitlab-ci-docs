from collections import defaultdict
from itertools import cycle
from typing import Dict, List

from gitlabci_doc.domain.Graph import (
    PipelineGraph,
    JobNode,
    Dependency,
)
from gitlabci_doc.renderers.base import GraphRenderer


class MermaidRenderer(GraphRenderer):
    """
    Renders a PipelineGraph into an enhanced Mermaid diagram.

    Features:
    - strict stage ordering (from stages:)
    - stage grouping using subgraphs
    - deterministic job ordering inside stages
    - implicit vs explicit (needs) dependencies
    - visual legend
    """

    STAGE_COLORS = [
        "#E3F2FD",  # blue
        "#E8F5E9",  # green
        "#FFFDE7",  # yellow
        "#FCE4EC",  # pink
        "#F3E5F5",  # purple
    ]

    def render(self, graph: PipelineGraph) -> str:
        lines: list[str] = ["graph LR"]

        jobs_by_stage = self._group_jobs_by_stage(graph.nodes)

        styles = self._render_stages(
            graph=graph,
            lines=lines,
            jobs_by_stage=jobs_by_stage,
        )

        lines.extend(self._render_dependencies(graph.dependencies))
        #lines.extend(self._render_legend())
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
        graph: PipelineGraph,
        lines: list[str],
        jobs_by_stage: Dict[str, List[JobNode]],
    ) -> list[str]:
        """
        Render stages as Mermaid subgraphs in strict order.
        Jobs inside a stage are rendered top-to-bottom and sorted
        according to their computed order (needs-aware).
        """
        styles: list[str] = []
        color_cycle = cycle(self.STAGE_COLORS)

        for stage in graph.stage_order:
            jobs = jobs_by_stage.get(stage, [])
            if not jobs:
                continue

            stage_class = f"stage_{stage}"
            color = next(color_cycle)

            lines.append(f"  subgraph {stage}")
            lines.append("    direction TB")

            for job in sorted(jobs, key=lambda j: j.order):
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
        Render dependencies using different arrow styles:
        - implicit stage dependency: solid arrow
        - explicit needs dependency: dotted arrow
        """
        lines: list[str] = []

        for dep in dependencies:
            if dep.kind == "needs":
                lines.append(f"  {dep.from_job} --> {dep.to_job}")
            #else:
            #    lines.append(f"  {dep.from_job} -.-> {dep.to_job}")

        return lines

    #@staticmethod
    #def _render_legend() -> list[str]:
    #    """
    #    Render a Mermaid legend explaining dependency types.
    #    """
    #    return [
    #        "",
    #        "  subgraph Legend",
    #        "    direction TB",
    #        "    I[Implicit dependency]",
    #        "    E[Explicit need]",
    #        "    I --> I",
    #        "    E -.-> E",
    #        "  end",
    #    ]
