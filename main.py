from pathlib import Path

from gitlabci_doc.infrastructure.yaml_parser import parse

if __name__ == "__main__":
    path_yaml = Path("C:\\Users\\juli1\\PycharmProjects\\gitlabci-doc\\resources\\example-ci.yaml")

    pipeline = parse(path_yaml)
    pipeline.print()
