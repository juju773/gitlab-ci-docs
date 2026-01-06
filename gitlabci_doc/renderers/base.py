from abc import ABC, abstractmethod

from gitlabci_doc.domain.Graph import PipelineGraph


class GraphRenderer(ABC):
    """
    Base interface for all pipeline graph renderers.
    """

    @abstractmethod
    def render(self, graph: PipelineGraph) -> str:
        """
        Render a PipelineGraph into a textual representation.
        """
        raise NotImplementedError
