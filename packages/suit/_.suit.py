from suit_plugins import black

from suit import suit

lint = suit("lint::black", black.lint("suit"))
format_ = suit("format::black", black.format_("suit"))
