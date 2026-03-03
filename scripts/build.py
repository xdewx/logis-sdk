from pathlib import Path

from setuptools_scm import _config, get_version

ROOT_DIR = Path(__file__).parent.parent

version_file = ROOT_DIR / "logis/auto_generated_version.py"

get_version(
    root=ROOT_DIR,
    # relative_to=__file__,
    version_scheme=_config.DEFAULT_VERSION_SCHEME,
    write_to=version_file,
)
