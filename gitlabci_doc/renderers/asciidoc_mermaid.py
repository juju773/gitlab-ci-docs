from gitlabci_doc.domain.Graph import PipelineGraph
from gitlabci_doc.renderers.asciidoc import AsciiDocRenderer
from gitlabci_doc.renderers.mermaid import MermaidRenderer


class AsciiDocMermaidRenderer(AsciiDocRenderer):
    """
    Renders a PipelineGraph into AsciiDoc with an embedded Mermaid diagram.
    """

    def __init__(self, stage_order: list[str]) -> None:
        self._stage_order = stage_order
        self._mermaid = MermaidRenderer()

    def render(self, graph: PipelineGraph) -> str:
        mermaid_graph = self._mermaid.render(graph)

        return "\n".join(
            [
                "= GitLab CI Pipeline",
                "",
                "== Pipeline graph",
                "",
                "[mermaid]",
                "----",
                mermaid_graph,
                "----",
                "",
            ]
        )
