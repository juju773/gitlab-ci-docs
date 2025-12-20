from dataclasses import dataclass
from typing import Mapping, Any

from gitlabci_doc.domain.Job import Job
from gitlabci_doc.domain.Stage import Stage


@dataclass(frozen=True)
class Pipeline:
    """
    A class representing a gitlab-ci pipeline

    ...
    Attributes
    ----------
    name : str
        The name of the stage
    stages : list[Stage] | None
        list of stage associated with this pipeline
    variables : Mapping[str, str] | None
        list of global environment variables added to all jobs
    """
    name: str | None
    stages: list[Stage]
    jobs: list[Job]
    variables: Mapping[str, str] | None = None
    workflow: Mapping[str, Any] | None = None

    def print(self):
        if self.name is not None:
            print(f"Pipeline: {self.name}\n")

        if self.variables is not None:
            print('variables:')
            print(f"\t{self.variables}\n")

        print('stages: ')
        for stage in self.stages:
            print(f"\t{stage}")
        print('')

        print('jobs: ')
        for job in self.jobs:
            job.print()
