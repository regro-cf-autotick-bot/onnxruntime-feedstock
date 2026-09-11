"""TEMPORARY DEBUG: find cmd.exe's batch line limit for post-build.bat.

The -novec Windows build fails with "(set was unexpected at this time." while
the vectorized build, whose only difference is a 6-character-shorter work
directory, succeeds. Every copy line in the generated post-build.bat ends with
`|| (set FAIL_LINE=NN& goto :ABORT)`, so a line truncated past cmd's limit
loses its closing paren and leaves an unterminated block.

For every long line: print its length, then run it on its own in a one-line
.bat and report what cmd does with it. The copies are idempotent, so running
them is harmless. The threshold that separates the passing from the failing
line is the answer.
"""

import os
import subprocess
import sys

PATH = r"build-ci\Release\CMakeFiles\onnxruntime_pybind11_state.dir\post-build.bat"
THRESHOLD = 5000

print("CWD:", os.getcwd())
print("PREFIX len:", len(os.environ.get("PREFIX", "")))
print("SRC_DIR len:", len(os.environ.get("SRC_DIR", "")))

with open(PATH, "rb") as fh:
    lines = fh.read().decode("utf-8", "replace").splitlines()

print("FILE:", PATH, "lines:", len(lines))
tmpdir = os.path.abspath("postbuild_probe")
os.makedirs(tmpdir, exist_ok=True)

for i, line in enumerate(lines, 1):
    n = len(line)
    if n < THRESHOLD:
        continue
    bat = os.path.join(tmpdir, "probe_%d.bat" % i)
    with open(bat, "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write("@echo off\n")
        fh.write(line + "\n")
        fh.write("echo PROBE_REACHED_END\n")
    proc = subprocess.run(
        ["cmd", "/c", bat], capture_output=True, text=True, errors="replace"
    )
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    print("-" * 60)
    print("line %d: %d chars -> rc=%d" % (i, n, proc.returncode))
    print("  reached end: %s" % ("PROBE_REACHED_END" in out))
    if out:
        print("  stdout: %r" % out[:400])
    if err:
        print("  stderr: %r" % err[:400])
    print("  tail: %r" % line[-120:])
    sys.stdout.flush()

print("PROBE DONE")
