import pytest

from gitlabci_doc.domain.Stage import Stage
from gitlabci_doc.infrastructure.yaml_parser import _parse_stages, GitlabCIParserError


def test_parse_stages_ok():
    raw = {
        "stages": ["build", "test", "deploy"]
    }

    stages = _parse_stages(raw)

    assert stages == [
        Stage(name="build"),
        Stage(name="test"),
        Stage(name="deploy"),
    ]

def test_parse_stages_invalid_type():
    raw = {
        "stages": "build"
    }

    with pytest.raises(GitlabCIParserError):
        _parse_stages(raw)