def run_manifest(path):
    from .runner import run_manifest as _run_manifest

    return _run_manifest(path)


__all__ = ["run_manifest"]
