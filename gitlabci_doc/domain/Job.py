from dataclasses import dataclass
from typing import Mapping, Sequence, Any


@dataclass(frozen=True)
class Job:
    """
    A class representing a gitlab-ci job

    ...
    Attributes
    ----------
    name : str
        The name of the job
    stage : Stage
        The stage of the job
    script: list[str] | None
        list of commands to run by the job
    variables : Mapping[str, str] | None
        list of environment variables added only for the job
    image : str | None
        name of the image to run the job
    cache : list[str] | None
        list of cached artifacts needs or added by the job
    artifacts : list[str] | Non
        list of artifacts added and available from the job
    services : list[str] | None
        list of services needed by the job
    runner : str | None
        tag/name of the runner that will run the job
    rules : list[str] | None
        list of rules that authorize the execution of the job
    needs : list[Job] | None
        list of jobs that are necessary for it to run
    """
    name: str
    stage: str
    script: Sequence[str]

    variables: Mapping[str, str] | None = None
    image: str | None = None
    services: list[str] | None = None

    cache: list[str] | None = None
    artifacts: Mapping[str, Any] | None = None
    runner: str | None = None

    needs: list[str] | None = None
    rules: list[Mapping[str, Any]] | None = None


    def print(self):
        print(f"\t{self.name}")
        print(f"\t\tscript: {self.script}")
        print(f"\t\tstage: {self.stage}")
        print(f"\t\tvariables: {self.variables}")
        print(f"\t\timage: {self.image}")
        print(f"\t\tservices: {self.services}")
        print(f"\t\tcache: {self.cache}")
        print(f"\t\tartifacts: {self.artifacts}")
        print(f"\t\trunner: {self.runner}")
        print(f"\t\tneeds: {self.needs}")
        print(f"\t\trules: {self.rules}\n")