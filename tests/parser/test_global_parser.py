import pathlib

from gitlabci_doc.infrastructure.yaml_parser import parse


def test_parse_pipeline(tmp_path: pathlib.Path): #todo change the file with a resource one
    file = tmp_path / ".gitlab-ci.yml"
    file.write_text("""
stages:
  - build

variables:
  ENV: prod

build-job:
  stage: build
  script:
    - make build
""")

    pipeline = parse(file)

    assert pipeline.variables["ENV"] == "prod"
    assert len(pipeline.stages) == 1
    assert len(pipeline.jobs) == 1