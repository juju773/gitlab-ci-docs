from abc import ABC, abstractmethod

from gitlabci_doc.domain.Graph import PipelineGraph


class AsciiDocRenderer(ABC):
    """
    Base interface for AsciiDoc renderers.
    """

    @abstractmethod
    def render(self, graph: PipelineGraph) -> str:
        """
        Render a PipelineGraph into AsciiDoc.
        """
        raise NotImplementedError
