import pytest

from gitlabci_doc.infrastructure.yaml_parser import _parse_variables, GitlabCIParserError, _parse_needs, _parse_script, \
    _parse_runner, _parse_rules


def test_parse_variables_ok():
    raw = {
        "variables": {
            "ENV": "prod",
            "DEBUG": False,
        }
    }

    variables = _parse_variables(raw)

    assert variables == {
        "ENV": "prod",
        "DEBUG": "False",
    }

def test_parse_no_variables():
    raw = {}

    variables = _parse_variables(raw)

    assert variables == {}

def test_parse_variables_invalid_type():
    raw = {
        "variables": ["A", "B"]
    }

    with pytest.raises(GitlabCIParserError):
        _parse_variables(raw)


def test_parse_needs_object_list():
    content = {
        "needs": [
            {"job": "build"},
            {"job": "lint", "artifacts": True},
        ]
    }

    assert _parse_needs(content) == ["build", "lint"]

def test_parse_needs_string_list():
    content = {"needs": ["build", "lint"]}

    assert _parse_needs(content) == ["build", "lint"]


def test_parse_script_missing():
    with pytest.raises(GitlabCIParserError):
        _parse_script({})

def test_parse_script_list():
    content = {"script": ["make build", "make test"]}

    assert _parse_script(content) == ["make build", "make test"]

def test_parse_script_string():
    content = {"script": "make build"}

    assert _parse_script(content) == ["make build"]

def test_parse_script_invalid_type():
    content = {
        "script": 123
    }

    with pytest.raises(GitlabCIParserError) as excinfo:
        _parse_script(content)

    assert "'script' must be a string or list of strings" in str(excinfo.value)

def test_parse_runner_invalid_type():
    content = {
        "tags": "docker"
    }

    with pytest.raises(GitlabCIParserError) as excinfo:
        _parse_runner(content)

    assert "'tags' must be a list" in str(excinfo.value)

def test_parse_rules_invalid_type():
    content = {
        "rules": {
            "if": "$CI_COMMIT_BRANCH == 'main'"
        }
    }

    with pytest.raises(GitlabCIParserError) as excinfo:
        _parse_rules(content)

    assert "'rules' must be a list" in str(excinfo.value)

def test_parse_rules_valid():
    content = {
        "rules": [
            {"if": "$CI_COMMIT_BRANCH == 'main'"},
            {"when": "manual"},
        ]
    }

    rules = _parse_rules(content)

    assert isinstance(rules, list)
    assert len(rules) == 2