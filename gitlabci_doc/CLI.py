from pathlib import Path

from gitlabci_doc.application.pipeline_graph_builder import PipelineGraphBuilder
from gitlabci_doc.infrastructure.yaml_parser import parse
from gitlabci_doc.renderers.asciidoc_mermaid import AsciiDocMermaidRenderer
from gitlabci_doc.writer.asciidoc import asciidoc_write

pipeline = parse(Path("C:\\Users\\juli1\\PycharmProjects\\gitlabci-doc\\resources\\example-ci2.yaml"))

graph = PipelineGraphBuilder().build(pipeline)

renderer = AsciiDocMermaidRenderer(stage_order=[stage.name for stage in pipeline.stages])
content = renderer.render(graph)

asciidoc_write(content, Path("pipeline.adoc"))