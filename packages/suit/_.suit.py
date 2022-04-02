from suit import suit
from suit_plugins import black

lint = suit("lint::black", black.lint("suit"))
format_ = suit("format::black", black.format_("suit"))
