from gitlabci_doc.infrastructure.yaml_parser import _is_job_definition, _parse_jobs


def test_is_job_definition_not_a_mapping():
    assert not _is_job_definition("job", "echo test")


def test_is_job_definition_valid():
    assert _is_job_definition("build-job", {"stage": "build", "script": ["make"]})


def test_is_job_definition_hidden():
    assert not _is_job_definition(".template", {"script": ["echo test"]})


def test_parse_jobs_simple():
    raw = {
        "stages": ["build"],
        "build-job": {
            "stage": "build",
            "script": ["make build"],
        },
    }

    jobs = _parse_jobs(raw)

    assert len(jobs) == 1
    job = jobs[0]

    assert job.name == "build-job"
    assert job.stage == "build"
    assert job.script == ["make build"]
