"""Install a CI wheel in a new venv and test it outside the source tree."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

root = Path(__file__).resolve().parents[1]
artifacts = Path(sys.argv[1]).resolve()
python_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
wheels = list(artifacts.glob(f"*-{python_tag}-{python_tag}-*.whl"))
if len(wheels) != 1:
    raise RuntimeError(f"Expected one {python_tag} wheel, found {wheels}")
wheel = wheels[0]
print(f"Testing artifact: {wheel.name}", flush=True)
print(f"SHA256: {hashlib.sha256(wheel.read_bytes()).hexdigest()}", flush=True)
workspace = Path(tempfile.mkdtemp(prefix="srreal-wheel-consumer-"))
venv_dir = workspace / "venv"
venv.EnvBuilder(with_pip=True).create(venv_dir)
python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
env = {k: v for k, v in os.environ.items() if not k.startswith("CONDA")}
for name in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
    env.pop(name, None)

def run(*args):
    subprocess.run([str(python), "-I", *map(str, args)], cwd=workspace, env=env, check=True)

# Install the binary itself, then sibling distributions that share diffpy/.
run("-m", "pip", "install", "--only-binary=:all:", wheel)
run("-m", "pip", "install", "pytest", "diffpy.structure", "periodictable")
run("-m", "pip", "check")
run("-c", r'''
import importlib.metadata as metadata
from pathlib import Path
import pickle
import sys
import numpy as np
from diffpy.structure import loadStructure
from diffpy.srreal import srreal_ext
from diffpy.srreal.pdfcalculator import PDFCalculator
native = Path(srreal_ext.__file__).resolve()
assert native.is_relative_to(Path(sys.prefix).resolve()), native
structure = loadStructure(sys.argv[1])
calc = PDFCalculator(rmin=0, rmax=10, rstep=0.01, qmax=25)
r, g = calc(structure)
assert r.shape == g.shape and r.size == 1000
assert np.all(np.isfinite(g)) and np.max(np.abs(g)) > 0
restored = pickle.loads(pickle.dumps(calc))
np.testing.assert_allclose(restored()[0], r)
np.testing.assert_allclose(restored()[1], g)
print("Installed version:", metadata.version("diffpy.srreal"))
print("Native extension:", native)
print("Ni PDF and pickle round-trip passed:", r.size, "points")
''', root / "tests/testdata/Ni.stru")
reports = root / "reports"
reports.mkdir(exist_ok=True)
run("-m", "pytest", root / "tests", "-q", "-r", "s", "--junitxml", reports / "wheel-tests.xml")
