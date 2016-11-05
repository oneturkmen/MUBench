import json
import logging
from os.path import join, basename
from typing import List
from typing import Tuple, IO
from urllib.parse import urljoin

import requests

from benchmark.data.detector import Detector
from benchmark.data.experiment import Experiment
from benchmark.data.finding import SpecializedFinding
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion
from benchmark.requirements import RequestsRequirement
from benchmark.tasks.project_version_task import ProjectVersionTask


class ProjectVersionReviewData:
    def __init__(self, dataset: str, detector: Detector, project: Project, version: ProjectVersion,
                 result: str, runtime: float, number_of_findings: int, potential_hits: List[SpecializedFinding]):
        super().__init__()
        self.dataset = dataset
        self.detector_name = detector.id
        self.project = project.id
        self.version = version.version_id
        self.result = result
        self.runtime = runtime
        self.number_of_findings = number_of_findings
        self.findings = potential_hits


class ReviewUpload(ProjectVersionTask):
    def __init__(self, experiment: Experiment, dataset: str, review_site_url: str):
        super().__init__()
        self.experiment = experiment
        self.detector = experiment.detector
        self.dataset = dataset
        self.review_site_url = review_site_url

        self.logger = logging.getLogger("review_findings")
        self.__review_data = []  # type: List[ProjectVersionReviewData]

    def get_requirements(self):
        return [RequestsRequirement()]

    def start(self):
        self.logger.info("Prepare findings of %s in %s...", self.detector, self.experiment)

    def process_project_version(self, project: Project, version: ProjectVersion) -> List[str]:
        logger = self.logger.getChild("version")

        detector_run = self.experiment.get_run(version)

        if not detector_run.is_success():
            logger.info("Skipping %s: no result.", version)
            return self.skip(version)

        logger.info("Preparing findings in %s...", version)
        runtime = detector_run.get_runtime()
        number_of_findings = len(detector_run.get_findings())
        potential_hits = detector_run.get_potential_hits()

        logger.info("Found %s potential hits.", len(potential_hits))
        self.__review_data.append(
            ProjectVersionReviewData(self.dataset, self.detector, project, version,
                                     "success", runtime, number_of_findings, potential_hits))

        return self.ok()

    def end(self):
        if not self.__review_data:
            self.logger.info("Nothing to upload.")
        else:
            url = urljoin(self.review_site_url, "upload/" + self.experiment.id)
            self.logger.info("Uploading to %s...", url)
            file_paths = self.get_file_paths(self.__review_data)
            self.post(url, self.__review_data, file_paths)

    @staticmethod
    def get_file_paths(review_data: List[ProjectVersionReviewData]) -> List[str]:
        files = []
        for version_review_data in review_data:
            for finding in version_review_data.findings:
                files.extend(finding.files)
        return files

    @staticmethod
    def post(url: str, data: List[ProjectVersionReviewData], file_paths: List[str]) -> requests.Response:
        user = ""  # TODO set these values
        password = ""
        files = [ReviewUpload._get_request_file_tuple(path) for path in file_paths]
        serialized_data = json.dumps([d.__dict__ for d in data], sort_keys=True)
        requests.post(url, auth=(user, password), data=serialized_data, files=files)

    @staticmethod
    def _get_request_file_tuple(path) -> Tuple[str, Tuple[str, IO[bytes], str]]:
        name = basename(path)
        return name, (name, open(join(path), 'rb'), "image/png")  # TODO make MIME type a parameter
