"""Exercise runtime table discovery in a fresh process and working
directory."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from diffpy.srreal import srreal_ext


@pytest.fixture(
    params=[
        (
            "f0_WaasKirf.dat",
            "from diffpy.srreal.scatteringfactortable import SFTXray; "
            "assert 27 < SFTXray().lookup('Ni', 0) < 29",
        ),
        (
            "nsftable.dat",
            "from diffpy.srreal.scatteringfactortable import SFTNeutron; "
            "assert 10 < SFTNeutron().lookup('Ni', 0) < 11",
        ),
        (
            "bvparm2011sel.cif",
            "from diffpy.srreal.srreal_ext import BVParametersTable; "
            "p = BVParametersTable().lookup('Ti', 4, 'O', -2); "
            "assert abs(p.Ro - 1.815) < 1e-12; "
            "assert abs(p.B - 0.37) < 1e-12",
        ),
    ],
    ids=["xray", "neutron", "bond-valence"],
)
def lookup(request):
    return request.param


@pytest.fixture
def custom_tables(tmp_path):
    source = Path(srreal_ext.__file__).parent / "data"
    return shutil.copytree(source, tmp_path / "custom tables")


def run_lookup(directory, code, override=None):
    env = os.environ.copy()
    env.pop("DIFFPYRUNTIME", None)
    if override is not None:
        env["DIFFPYRUNTIME"] = str(override)
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.parametrize("override", [None, ""])
def test_packaged_tables_from_unrelated_working_directory(
    tmp_path, lookup, override
):
    _, code = lookup
    result = run_lookup(tmp_path, code, override)
    assert result.returncode == 0, result.stdout + result.stderr


def test_runtime_override_with_spaces(tmp_path, lookup, custom_tables):
    _, code = lookup
    result = run_lookup(tmp_path, code, custom_tables)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("exists", [False, True])
def test_runtime_override_does_not_fall_back_to_packaged_tables(
    tmp_path, lookup, exists
):
    _, code = lookup
    override = tmp_path / "custom tables"
    if exists:
        override.mkdir()
    result = run_lookup(tmp_path, code, override)
    assert result.returncode != 0
    assert "RuntimeError" in result.stderr
    assert "custom tables" in result.stderr


def test_missing_runtime_table(tmp_path, lookup, custom_tables):
    filename, code = lookup
    (custom_tables / filename).unlink()
    result = run_lookup(tmp_path, code, custom_tables)
    assert result.returncode != 0
    assert "RuntimeError" in result.stderr
    assert filename in result.stderr


def test_custom_table_contents_take_precedence(tmp_path, custom_tables):
    table = custom_tables / "nsftable.dat"
    contents = table.read_text()
    assert "28-Ni,,,10.3(1)," in contents
    table.write_text(contents.replace("28-Ni,,,10.3(1),", "28-Ni,,,12.345,"))
    result = run_lookup(
        tmp_path,
        "from diffpy.srreal.scatteringfactortable import SFTNeutron; "
        "assert abs(SFTNeutron().lookup('Ni', 0) - 12.345) < 1e-12",
        custom_tables,
    )
    assert result.returncode == 0, result.stdout + result.stderr
