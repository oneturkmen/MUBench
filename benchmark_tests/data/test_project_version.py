import yaml
from os.path import join
from tempfile import mkdtemp

from nose.tools import assert_equals, assert_raises

from benchmark.data.misuse import Misuse
from benchmark.data.project import Project
from benchmark.data.project_checkout import LocalProjectCheckout, GitProjectCheckout, SVNProjectCheckout
from benchmark.data.project_version import ProjectVersion
from benchmark.utils.io import remove_tree, create_file, safe_open


from benchmark_tests.test_utils.data_util import create_project, create_version, create_misuse


class TestProjectVersion:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-test-project-version_")

        self.project_id = "project"
        self.version_id = "v1"
        self.uut = ProjectVersion(self.temp_dir, self.project_id, self.version_id)

    def teardown(self):
        remove_tree(self.temp_dir)

    def test_sets_path(self):
        assert_equals(join(self.temp_dir, self.project_id, Project.VERSIONS_DIR, self.version_id), self.uut.path)

    def test_rejects_non_project_version_directory(self):
        assert not ProjectVersion.is_project_version(self.temp_dir)

    def test_accepts_project_version_directory(self):
        create_file(self.uut._version_file)
        assert ProjectVersion.is_project_version(self.uut.path)

    def test_reads_version_file(self):
        test_dict = {"revision": "42"}
        with safe_open(self.uut._version_file, 'w+') as stream:
            yaml.dump(test_dict, stream)

        assert_equals(test_dict, self.uut._yaml)

    def test_finds_misuses(self):
        misuse = create_misuse("1", project=create_project(self.project_id, base_path=self.temp_dir))
        create_file(misuse.misuse_file)
        self.uut._YAML = {"misuses": ["1"]}

        actual_misuses = self.uut.misuses

        assert_equals([misuse], actual_misuses)

    def test_finds_only_own_misuses(self):
        project = create_project(self.project_id, base_path=self.temp_dir)
        misuse1 = create_misuse("1", project=project)
        create_file(misuse1.misuse_file)
        misuse2 = create_misuse("2", project=project)
        create_file(misuse2.misuse_file)
        self.uut._YAML = {"misuses": ["2"]}

        misuses = self.uut.misuses

        assert_equals([misuse2], misuses)


    def test_creates_build_config(self):
        self.uut._YAML = {"build": {"src": "src/java/", "commands": ["mvn compile"], "classes": "target/classes/"}}
        assert_equals("src/java/", self.uut.source_dir)
        assert_equals(["mvn compile"], self.uut.compile_commands)
        assert_equals("target/classes/", self.uut.classes_dir)

    def test_creates_build_config_with_defaults(self):
        self.uut._YAML = {}
        assert_equals("", self.uut.source_dir)
        assert_equals([], self.uut.compile_commands)
        assert_equals("", self.uut.classes_dir)

    def test_id(self):
        assert_equals("{}.{}".format(self.project_id, self.version_id), self.uut.id)

    def test_derives_additional_compile_sources_path(self):
        assert_equals(join(self.uut.path, "compile"), self.uut.additional_compile_sources)

    def test_derives_compile_base_path(self):
        project_compile = self.uut.get_compile("/base/path")

        assert_equals(join("/base/path", self.project_id, self.version_id), project_compile.base_path)


class TestProjectCheckout:
    def test_synthetic_project(self):
        version = create_version("v1", project=create_project("-project-", meta={"repository": {"type": "synthetic"}}))

        checkout = version.get_checkout("-base_path-")

        assert isinstance(checkout, LocalProjectCheckout)
        assert_equals(join(version.path, "compile"), checkout.url)
        assert_equals("-project-", checkout.name)

    def test_git_project(self):
        project = create_project("-project-", meta={"repository": {"type": "git", "url": "ssh://foobar.git"}})
        version = create_version("-version-", meta={"revision": "-revision-"}, project=project)

        checkout = version.get_checkout( "-base_path-")

        assert isinstance(checkout, GitProjectCheckout)
        assert_equals("ssh://foobar.git", checkout.url)
        assert_equals("-project-", checkout.name)
        assert_equals("-version-", checkout.version)
        assert_equals("-revision-~1", checkout.revision)

    def test_svn_project(self):
        project = create_project("-project-", meta={"repository": {"type": "svn", "url": "http://url/svn"}})
        version = create_version("-version-", meta={"revision": "667"}, project=project)

        checkout = version.get_checkout("-base_path-")

        assert isinstance(checkout, SVNProjectCheckout)
        assert_equals("http://url/svn", checkout.url)
        assert_equals("-project-", checkout.name)
        assert_equals("-version-", checkout.version)
        assert_equals("666", checkout.revision)

    def test_unknown_type(self):
        version = create_version("-v-", project=create_project("-p-", meta={"repository": {"type": "unknown"}}))
        assert_raises(ValueError, version.get_checkout, "-base_path-")