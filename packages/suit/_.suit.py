from suit_plugins import black, pytest, install_requires

from suit import suit

lint = suit("lint:black", black.lint("suit"))
format_ = suit("format:black", black.format_("suit"))

tests = suit("tests", pytest.pytest("tests", color="yes"))
install_requires = suit(
    "install-requires", install_requires.InstallRequires("requirements.txt")
)
