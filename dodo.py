"""Create wheel by default."""

import glob
from doit.tools import create_folder

DOIT_CONFIG = {'default_tasks': ['wheel']}


def task_html():
    """Make HTML documentation."""
    return {
        'actions': ['docs\make.bat html'],
    }


def task_test():
    """Preform tests."""
    return {
        'actions': ['python -W ignore::DeprecationWarning -m unittest tests/parser_tests.py -v'],
        'task_dep': ['translation']
    }


def task_pot():
    """Re-create .pot ."""
    return {
        'actions': ['pybabel extract --input-dirs VMK_bot -o VMK_bot/user.pot'],
        'file_dep': glob.glob('VMK_bot/*.py'),
        'targets': ['VMK_bot/user.pot'],
        'clean': True,
    }


def task_po():
    """Update translations."""
    return {
        'actions': ['pybabel update -D user -d VMK_bot/translation -i VMK_bot/user.pot'],
        'file_dep': ['VMK_bot/user.pot'],
        'targets': ['VMK_bot/translation/en/LC_MESSAGES/user.po'],
    }


def task_translation():
    """Compile translations."""
    return {
        'actions': ['pybabel compile -d VMK_bot/translation -D user'],
        'file_dep': ['VMK_bot/translation/en/LC_MESSAGES/user.po'],
        'targets': ['VMK_bot/translation/en/LC_MESSAGES/user.mo'],
        'clean': True,
    }


def task_lint():
    """Check codestyle with flake8."""
    return {
        'actions': ['flake8 VMK_bot']
    }


def task_docstring():
    """Check docstrings with flake8."""
    return {
        'actions': ['flake8 --docstring-convention google VMK_bot']
    }


def task_check():
    """Perform all checks."""
    return {
        'actions': None,
        'task_dep': ['lint', 'docstring', 'test']
    }


def task_wheel():
    """Create binary wheel distribution."""
    return {
        'actions': ['python -m build -w'],
        'task_dep': ['translation'],
    }


def task_gitclean():
    """Clean repository."""
    return {
        'actions': ['git clean -xdf -e VMK_bot/config.py -e .doit.db.*']
    }
