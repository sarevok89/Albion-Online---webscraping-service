import os
import sys

import distutils.cmd
import distutils.log
import subprocess

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from sphinx.setup_command import BuildDoc

BASE_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PYTHONPATH'] = BASE_PROJECT_DIR


with open(
        os.path.join(BASE_PROJECT_DIR, 'README.md')) as f:
    long_description = f.read()

with open(
        os.path.join(
            BASE_PROJECT_DIR, 'requirements', 'requirements.txt')) as f:
    requirements = f.read()

with open(
        os.path.join(
            BASE_PROJECT_DIR, 'requirements', 'doc_requirements.txt')) as f:
    doc_requirements = f.read()

with open(
        os.path.join(
            BASE_PROJECT_DIR, 'requirements', 'test_requirements.txt')) as f:
    test_requirements = f.read()


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = "-sxvvv webscraper/tests/"

    def run_tests(self):
        import shlex

        import django
        sys.path.insert(0, os.path.abspath(''))
        os.environ['DJANGO_SETTINGS_MODULE'] = 'albion_compensations.settings'
        django.setup()

        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class Flake8Command(distutils.cmd.Command):
    """
    A custom command to run Pylint on all Python source files.

    """
    description = 'run Flake8 on Python source files'
    user_options = [
      # The format is (long option, short option, description).
      ('config=', None, 'path to .flake8 config file'),
    ]

    def initialize_options(self):
        """
        Set default values for options.

        """
        # Each user option must be listed here with their default value.
        self.config = os.path.join(BASE_PROJECT_DIR, '.flake8')

    def finalize_options(self):
        """
        Post-process options.

        """
        if self.config:
            assert os.path.exists(self.config), (
              'Flake8 config file %s does not exist.' % self.config)

    def run(self):
        """
        Run command.

        """
        command = ['flake8']
        if self.config:
            command.append('--config=%s' % self.config)
        command.append(os.getcwd())
        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as e:
            print(e)


class Sphinx(BuildDoc):
    def initialize_options(self):
        BuildDoc.initialize_options(self)
        self.source_dir = './docs'
        self.build_dir = './docs/_build'
        self.builder = 'html'
        self.project = 'Django tracker'
        self.version = '0.1'
        self.release = '0.1.0'
        self.config_dir = './docs'


setup(
    name='albion_compensations',
    version='0.1',
    packages=find_packages(),
    description='Simple tracking app based on Django',
    long_description=long_description,
    author='Piotr Wieleba',
    author_email='p.wieleba@clearcode.cc',
    install_requires=requirements,
    include_package_data=True,
    python_requires='~=3.7',
    tests_require=test_requirements,
    extras_require={
        'docs': doc_requirements,
    },
    cmdclass={
        'docs': Sphinx,
        'test': PyTest,
        'linter': Flake8Command,
    },
)
