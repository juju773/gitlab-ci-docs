import pathlib

import pytest

from gitlabci_doc.infrastructure.yaml_parser import _load_yaml, InvalidGitlabCIFile


def test_load_yaml_ok(tmp_path: pathlib.Path):
    file = tmp_path / ".gitlab-ci.yml"
    file.write_text("stages:\n  - build\n") # create a stage build in the tmp file

    result = _load_yaml(file)

    assert result == {"stages": ["build"]}


def test_load_yaml_file_not_found():
    with pytest.raises(InvalidGitlabCIFile):
        _load_yaml(pathlib.Path("does_not_exist.yml"))

def test_load_yaml_invalid_yaml(tmp_path: pathlib.Path):
    file = tmp_path / ".gitlab-ci.yml"
    file.write_text("stages: [build")  # YAML invalide

    with pytest.raises(InvalidGitlabCIFile):
        _load_yaml(file)

def test_load_yaml_invalid_encoding(tmp_path: pathlib.Path):
    file = tmp_path / ".gitlab-ci.yml"

    # Octets invalids UTF-8
    file.write_bytes(b"\xff\xfe\xfa")

    with pytest.raises(InvalidGitlabCIFile) as excinfo:
        _load_yaml(file)

    assert "Invalid file encoding" in str(excinfo.value)

def test_load_yaml_not_a_mapping(tmp_path: pathlib.Path):
    file = tmp_path / ".gitlab-ci.yml"
    file.write_text("- build\n- test\n")

    with pytest.raises(InvalidGitlabCIFile) as excinfo:
        _load_yaml(file)

    assert "GitLab CI file must be a YAML mapping" in str(excinfo.value)