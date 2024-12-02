from pathlib import Path
from buildtools.utils.models import Project
from buildtools.utils import constants
from factory.fuzzy import FuzzyText, FuzzyChoice
from factory import Factory


class TestProject(Project):
    def add_dependency(self, other: "TestProject"):
        if not self.path.exists():
            self.path.mkdir()

        if not other.path.exists():
            other.path.mkdir()

        with (self.path / constants.DEPENDENCIES_FILE_NAME).open("w") as f:
            # lib1 depends on lib2
            f.write(
                f"""
                [tool.poetry.dependencies]
                {other.name} = "1.33.7"
                """
            )


class ProjectFactory(Factory):
    class Meta:
        exclude = ("add_dependency",)
        model = TestProject

    name = FuzzyText()
    path = Path("/tmp")
    category = FuzzyText()
    is_deployable = FuzzyChoice([True, False])


class LibraryProjectFactory(ProjectFactory):
    category = constants.LIBRARIES_FOLDER_NAME


class ServiceProjectFactory(ProjectFactory):
    category = constants.SERVICES_FOLDER_NAME
