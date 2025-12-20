import pathlib
from typing import Any, Mapping

import yaml
from yaml import safe_load

from gitlabci_doc.domain.Job import Job
from gitlabci_doc.domain.Pipeline import Pipeline
from gitlabci_doc.domain.Stage import Stage


GITLAB_CI_RESERVED_KEYS = {
    "stages",
    "variables",
    "workflow",
    "default",
    "include",
    "image",
    "services",
    "before_script",
    "after_script",
}

class GitlabCIParserError(Exception):
    """Base exception for GitLab CI parsing errors."""


class InvalidGitlabCIFile(GitlabCIParserError):
    """Raised when the YAML file is invalid or unreadable."""


def _load_yaml(path: pathlib.Path) -> dict[str, Any]:
    """
    Function to load a YAML file.
    :param path:
    :return:
    """
    try:
        with path.open("r", encoding="utf-8") as stream:
            raw = safe_load(stream)
    except FileNotFoundError as exc:
        raise InvalidGitlabCIFile(f"File not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise InvalidGitlabCIFile(f"Invalid YAML file: {path}") from exc
    except UnicodeDecodeError as exc:
        raise InvalidGitlabCIFile(f"Invalid file encoding: {path}") from exc

    if not isinstance(raw, dict):
        raise InvalidGitlabCIFile("GitLab CI file must be a YAML mapping")

    return raw


def _parse_stages(raw: dict[str, Any]) -> list[Stage]:
    """
    Function to parse the stages defined in a YAML file.
    :param raw:
    :return:
    """
    raw_stages = raw.get("stages", [])

    if not isinstance(raw_stages, list):
        raise GitlabCIParserError("'stages' must be a list")

    return [Stage(name=str(stage)) for stage in raw_stages]


def _parse_variables(raw: dict[str, Any]) -> Mapping[str, str]:
    """
    Function to parse the variables defined in a YAML file.
    :param raw:
    :return:
    """
    raw_variables = raw.get("variables", {})

    if raw_variables is None:
        return {}

    if not isinstance(raw_variables, dict):
        raise GitlabCIParserError("'variables' must be a mapping")

    return {str(key): str(value) for key, value in raw_variables.items()}


def _is_job_definition(name: str, value: Any) -> bool:
    """
    Function to determine if the name is a job.
    :param name:
    :param value:
    :return:
    """
    if name in GITLAB_CI_RESERVED_KEYS:
        return False

    if name.startswith("."):
        return False

    if not isinstance(value, dict):
        return False

    return any(key in value for key in ("script", "trigger", "rules"))

def _parse_script(content: dict[str, Any]) -> list[str]:
    """
    Function to parse the script defined in a YAML file.
    :param content:
    :return:
    """
    script = content.get("script")

    if script is None:
        raise GitlabCIParserError("Job must define a script")

    if isinstance(script, str):
        return [script]

    if isinstance(script, list):
        return [str(line) for line in script]

    raise GitlabCIParserError("'script' must be a string or list of strings")

def _parse_runner(content: dict[str, Any]) -> str | None:
    """
    Function to parse the runner defined in a YAML file
    :param content:
    :return:
    """
    tags = content.get("tags")

    if tags is None:
        return None

    if isinstance(tags, list):
        return ", ".join(str(tag) for tag in tags)

    raise GitlabCIParserError("'tags' must be a list")


def _parse_needs(content: dict[str, Any]) -> list[str] | None:
    """
    Function to parse the needs defined in a YAML file.
    :param content:
    :return:
    """
    needs = content.get("needs")

    if needs is None:
        return None

    if isinstance(needs, list):
        result: list[str] = []
        for item in needs:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict) and "job" in item:
                result.append(str(item["job"]))
        return result

    raise GitlabCIParserError("'needs' must be a list")

def _parse_rules(content: dict[str, Any]) -> list[Mapping[str, Any]] | None:
    """
    Function to parse the rules defined in a YAML file.
    :param content:
    :return:
    """
    rules = content.get("rules")

    if rules is None:
        return None

    if not isinstance(rules, list):
        raise GitlabCIParserError("'rules' must be a list")

    return rules

def _parse_workflow(raw: dict[str, Any]) -> Mapping[str, Any] | None:
    workflow = raw.get("workflow")

    if workflow is None:
        return None

    if not isinstance(workflow, dict):
        raise GitlabCIParserError("'workflow' must be a mapping")

    return workflow

def _parse_jobs(raw: dict[str, Any]) -> list[Job]:
    jobs: list[Job] = []

    for name, content in raw.items():
        if not _is_job_definition(name, content):
            continue

        job = Job(
            name=name,
            stage=str(content.get("stage", "test")),
            script=_parse_script(content),
            variables=_parse_variables(content),
            image=content.get("image"),
            services=content.get("services"),
            cache=content.get("cache"),
            artifacts=content.get("artifacts"),
            runner=_parse_runner(content),
            needs=_parse_needs(content),
            rules=_parse_rules(content),
        )

        jobs.append(job)

    return jobs

def parse(path: pathlib.Path) -> Pipeline:
    raw = _load_yaml(path)

    stages = _parse_stages(raw)
    jobs = _parse_jobs(raw)
    variables = _parse_variables(raw)
    workflow = _parse_workflow(raw)

    return Pipeline(
        name=None,
        stages=stages,
        jobs=jobs,
        variables=variables,
        workflow=workflow,
    )

