from suit import suit, Runtime, Scope


@suit("lint")
def lint(runtime: Runtime, scope: Scope):
    runtime.log("linting here")
