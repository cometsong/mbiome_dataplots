from os.path import dirname
from subprocess import run, PIPE, STDOUT


def get_version():
    """Return version from latest git tag"""
    try:
        cmd_dir = dirname(__file__)
        cmd = 'git describe --tags'
        p = run(cmd,
                cwd=cmd_dir,
                stdout=PIPE,
                stderr=STDOUT,
                shell=True,
                # capture_output=True,
                )
        out = p.stdout.decode('UTF-8')
    except OSError:
        out = '(undetermined)'
    return out

