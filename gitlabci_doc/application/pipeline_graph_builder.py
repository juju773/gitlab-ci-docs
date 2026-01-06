from collections import defaultdict

from gitlabci_doc.domain.Graph import Dependency, JobNode, PipelineGraph
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

        - Computes strict stage order
        - Creates graph nodes with deterministic ordering
        - Resolves dependencies between jobs
        """
        stage_order = [stage.name for stage in pipeline.stages]

        nodes = self._build_nodes(
            jobs=pipeline.jobs,
            stage_order=stage_order,
        )

        dependencies = self._build_dependencies(
            jobs=pipeline.jobs,
            stage_order=stage_order,
        )

        return PipelineGraph(
            nodes=nodes,
            dependencies=dependencies,
            stage_order=stage_order,
        )

    def _build_nodes(
        self,
        jobs: list[Job],
        stage_order: list[str],
    ) -> list[JobNode]:
        """
        Creates graph nodes from Job domain objects.

        Jobs are ordered deterministically:
        - grouped by stage (strict order)
        - inside a stage:
            - jobs with needs are ordered according to their dependencies
            - jobs without needs are ordered alphabetically
        """
        jobs_by_stage = self._group_jobs_by_stage(jobs)
        job_positions: dict[str, int] = {}

        nodes: list[JobNode] = []
        global_order = 0

        for stage in stage_order:
            stage_jobs = jobs_by_stage.get(stage, [])

            sorted_jobs = self._sort_jobs_in_stage(
                jobs=stage_jobs,
                job_positions=job_positions,
            )

            for job in sorted_jobs:
                job_positions[job.name] = global_order
                nodes.append(
                    JobNode(
                        name=job.name,
                        stage=job.stage,
                        order=global_order,
                    )
                )
                global_order += 1

        return nodes

    def _build_dependencies(
        self,
        jobs: list[Job],
        stage_order: list[str],
    ) -> list[Dependency]:
        """
        Builds all dependencies between jobs.

        Dependencies can be:
        - explicit (defined via 'needs')
        - implicit (based on stage ordering)
        """
        jobs_by_name = {job.name: job for job in jobs}
        jobs_by_stage = self._group_jobs_by_stage(jobs)
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

        for needed in job.needs or []:
            if needed in jobs_by_name:
                dependencies.append(
                    Dependency(
                        from_job=needed,
                        to_job=job.name,
                        kind="needs",
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

        if current_stage_idx is None or current_stage_idx == 0:
            return []

        previous_stage = stage_order[current_stage_idx - 1]

        return [
            Dependency(
                from_job=previous_job.name,
                to_job=job.name,
                kind="implicit",
            )
            for previous_job in jobs_by_stage.get(previous_stage, [])
        ]

    @staticmethod
    def _sort_jobs_in_stage(
        jobs: list[Job],
        job_positions: dict[str, int],
    ) -> list[Job]:
        """
        Sort jobs inside a stage.

        Order rules:
        - jobs with needs come first
        - ordered by average position of their dependencies
        - jobs without needs are ordered alphabetically
        """

        def dependency_score(job: Job) -> float | None:
            if not job.needs:
                return None

            positions = [
                job_positions[n]
                for n in job.needs
                if n in job_positions
            ]

            if not positions:
                return None

            return sum(positions) / len(positions)

        return sorted(
            jobs,
            key=lambda job: (
                dependency_score(job) is None,
                dependency_score(job) or 0,
                job.name.lower(),
            ),
        )
