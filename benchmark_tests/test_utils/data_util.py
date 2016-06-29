from typing import Any, Dict, List

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_version import ProjectVersion


def create_project(project_id: str, base_path: str = "-test-", meta: Dict[str, Any] = None):
    project = Project(base_path, project_id)
    project._YAML = {} if meta is None else meta
    return project


def create_version(version_id: str, misuses: List[Misuse] = None, meta: Dict[str, Any] = None, project: Project=None):
    if not project:
        project = create_project("-project-")
    version = ProjectVersion(project._base_path, project.id, version_id)
    version._ProjectVersion__project = project
    version._MISUSES = [] if misuses is None else misuses
    version._YAML = {} if meta is None else meta
    project._VERSIONS.append(version)
    return version


def create_misuse(misuse_id: str, meta: Dict[str, Any] = None, project: Project=None):
    if not project:
        project = create_project("-project-")
    misuse = Misuse(project._base_path, project.id, misuse_id)
    misuse._Misuse__project = project
    misuse._YAML = {"location": {"file": "-dummy-/-file-", "method": "-method-()"}}
    if meta is not None:
        misuse._YAML.update(meta)
    return misuse