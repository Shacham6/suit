from suit import Runtime, Scope, suit


@suit("prepare-docs")
def prepare_docs(runtime: Runtime, scope: Scope):
    runtime.print("Running...")
