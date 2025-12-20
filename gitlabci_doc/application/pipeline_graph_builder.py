from collections import defaultdict
from typing import List, Dict

from gitlabci_doc.domain.Graph import PipelineGraph, JobNode, Dependency
from gitlabci_doc.domain.Job import Job
from gitlabci_doc.domain.Pipeline import Pipeline


class PipelineGraphError(Exception):
    """
    Base exception for errors occurring during pipeline graph construction.
    """
    pass


class PipelineGraphBuilder:
    """
    Responsible for building a PipelineGraph from a Pipeline domain object.

    This class converts a high-level Pipeline (jobs, stages, dependencies)
    into a graph representation suitable for visualization or documentation.
    """

    def build(self, pipeline: Pipeline) -> PipelineGraph:
        """
        Entry point for graph construction.

        - Creates graph nodes from pipeline jobs
        - Resolves dependencies between jobs
        """
        nodes = self._build_nodes(pipeline.jobs)
        dependencies = self._build_dependencies(
            jobs=pipeline.jobs,
            stages=pipeline.stages,
        )

        return PipelineGraph(
            nodes=nodes,
            dependencies=dependencies,
        )

    @staticmethod
    def _build_nodes(jobs: List[Job]) -> List[JobNode]:
        """
        Creates graph nodes from Job domain objects.

        Each job becomes a JobNode with a name and a stage.
        """
        return [
            JobNode(
                name=job.name,
                stage=job.stage,
            )
            for job in jobs
        ]

    def _build_dependencies(
        self,
        jobs: list[Job],
        stages: list,
    ) -> list[Dependency]:
        """
        Builds all dependencies between jobs.

        Dependencies can be:
        - explicit (defined via 'needs')
        - implicit (based on stage ordering)
        """
        # Fast lookup structures to reduce algorithmic complexity
        jobs_by_name = {job.name: job for job in jobs}
        jobs_by_stage = self._group_jobs_by_stage(jobs)

        # Preserve stage execution order
        stage_order = [stage.name for stage in stages]
        stage_index = {name: idx for idx, name in enumerate(stage_order)}

        dependencies: list[Dependency] = []

        for job in jobs:
            dependencies.extend(
                self._dependencies_for_job(
                    job=job,
                    jobs_by_name=jobs_by_name,
                    jobs_by_stage=jobs_by_stage,
                    stage_order=stage_order,
                    stage_index=stage_index,
                )
            )

        return dependencies

    @staticmethod
    def _group_jobs_by_stage(jobs: list[Job]) -> dict[str, list[Job]]:
        """
        Groups jobs by their stage.

        This function has a single responsibility and no business logic.
        """
        jobs_by_stage: dict[str, list[Job]] = defaultdict(list)

        for job in jobs:
            jobs_by_stage[job.stage].append(job)

        return dict(jobs_by_stage)

    def _dependencies_for_job(
        self,
        job: Job,
        jobs_by_name: dict[str, Job],
        jobs_by_stage: dict[str, list[Job]],
        stage_order: list[str],
        stage_index: dict[str, int],
    ) -> list[Dependency]:
        """
        Resolves dependencies for a single job.

        - If the job defines 'needs', dependencies are explicit
        - Otherwise, dependencies are inferred from stage ordering
        """
        if job.needs:
            return self._explicit_dependencies(job, jobs_by_name)

        return self._implicit_dependencies(
            job,
            jobs_by_stage,
            stage_order,
            stage_index,
        )

    @staticmethod
    def _explicit_dependencies(
        job: Job,
        jobs_by_name: dict[str, Job],
    ) -> list[Dependency]:
        """
        Resolves explicit dependencies defined via the 'needs' keyword.
        """
        dependencies: list[Dependency] = []

        for needed in job.needs:
            if needed in jobs_by_name:
                dependencies.append(
                    Dependency(
                        from_job=needed,
                        to_job=job.name,
                        kind="needs"
                    )
                )

        return dependencies

    @staticmethod
    def _implicit_dependencies(
        job: Job,
        jobs_by_stage: dict[str, list[Job]],
        stage_order: list[str],
        stage_index: dict[str, int],
    ) -> list[Dependency]:
        """
        Resolves implicit dependencies based on stage ordering.

        A job depends on all jobs from the previous stage.
        """
        current_stage_idx = stage_index.get(job.stage)

        # First stage or unknown stage: no implicit dependencies
        if current_stage_idx is None or current_stage_idx == 0:
            return []

        previous_stage = stage_order[current_stage_idx - 1]

        return [
            Dependency(
                from_job=previous_job.name,
                to_job=job.name,
                kind="implicit"
            )
            for previous_job in jobs_by_stage.get(previous_stage, [])
        ]
