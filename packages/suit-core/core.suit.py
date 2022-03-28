from suit import Runtime, Scope, suit


@suit("lint")
def lint(runtime: Runtime, scope: Scope):
    runtime.debug("linting here")
