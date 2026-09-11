"""TEMPORARY DEBUG: dump the generated post-build.bat for onnxruntime_pybind11_state.

cmd.exe fails to parse this file on the -novec Windows builds with
"(set was unexpected at this time.", while the identical vectorized build
(whose only difference is a 6-character-shorter work directory) succeeds.
Print every line's length so we can see whether one crosses cmd's 8191-char
batch line limit, and where the parser would land inside the overflow.
"""

import glob
import os
import sys

LIMIT = 8191

paths = [
    r"build-ci\Release\CMakeFiles\onnxruntime_pybind11_state.dir\post-build.bat",
]
paths += sorted(glob.glob(r"build-ci\Release\CMakeFiles\*.dir\post-build.bat"))

print("CWD:", os.getcwd())
print("PREFIX len:", len(os.environ.get("PREFIX", "")), os.environ.get("PREFIX"))
print("SRC_DIR len:", len(os.environ.get("SRC_DIR", "")), os.environ.get("SRC_DIR"))

seen = set()
for path in paths:
    if path in seen or not os.path.exists(path):
        continue
    seen.add(path)
    with open(path, "rb") as fh:
        text = fh.read().decode("utf-8", "replace")
    lines = text.splitlines()
    print("=" * 70)
    print("FILE:", path, "lines:", len(lines), "bytes:", len(text))
    for i, line in enumerate(lines, 1):
        n = len(line)
        flag = "  <<<< OVER LIMIT" if n > LIMIT else ""
        print("-" * 60)
        print("line %d: %d chars%s" % (i, n, flag))
        if n <= 400:
            print("  full: %r" % line)
        else:
            print("  head: %r" % line[:250])
            print("  tail: %r" % line[-250:])
            if n > LIMIT:
                # What cmd would see once the line is cut at the limit.
                print("  at limit: %r" % line[LIMIT - 200:LIMIT + 200])
    sys.stdout.flush()
