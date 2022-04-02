from suit_plugins import black, pytest

from suit import suit

lint = suit("lint::black", black.lint("suit"))
format_ = suit("format::black", black.format_("suit"))

tests = suit("tests", pytest.pytest("tests", color="yes"))
