from suit_plugins import black, pytest, install_requires

from suit import suit

lint = suit("lint:black", black.Lint("../suit/suit"))
format_ = suit("format:black", black.Format("../suit/suit"))

tests = suit("tests", pytest.pytest("../suit/tests", color="yes"))
