#!/usr/bin/env python
##############################################################################
#
# diffpy.srreal     Complex Modeling Initiative
#                   (c) 2014 Brookhaven Science Associates,
#                   Brookhaven National Laboratory.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""Converters from other structure representations in Python to
diffpy.srreal StructureAdapter classes."""

import numpy

from diffpy.srreal.srreal_ext import (
    AtomicStructureAdapter,
    PeriodicStructureAdapter,
    convertObjCrystCrystal,
    convertObjCrystMolecule,
)
from diffpy.srreal.structureadapter import RegisterStructureAdapter

# Converters for Molecule and Crystal from pyobjcryst ------------------------


RegisterStructureAdapter(
    "pyobjcryst._pyobjcryst.Molecule", convertObjCrystMolecule
)
RegisterStructureAdapter(
    "pyobjcryst._pyobjcryst.Crystal", convertObjCrystCrystal
)

# Converter for Structure class from diffpy.structure ------------------------


# TODO prune in version 1.4.
@RegisterStructureAdapter("diffpy.Structure.structure.Structure")
@RegisterStructureAdapter("diffpy.structure.structure.Structure")
def convertDiffPyStructure(stru):
    """Adapt Structure class from diffpy.structure package."""
    haslattice = (1, 1, 1, 90, 90, 90) != stru.lattice.cell_parms()
    isperiodic = haslattice
    adpt = (
        PeriodicStructureAdapter() if isperiodic else AtomicStructureAdapter()
    )
    _fetchDiffPyStructureData(adpt, stru)
    return adpt


# Adapter classes and helpers for diffpy.structure class ---------------------


# Keep the historical class paths so saved adapters can still be restored.
# Their pdffit state, if present in a pickle, is inert.
class DiffPyStructureAtomicAdapter(AtomicStructureAdapter):
    """Legacy adapter retained for pickle compatibility."""


class DiffPyStructurePeriodicAdapter(PeriodicStructureAdapter):
    """Legacy adapter retained for pickle compatibility."""


def _fetchDiffPyStructureData(adpt, stru):
    """Copy structure data from diffpy Structure object to this Adapter.

    Attributes
    ----------
    adpt
        instance of AtomicStructureAdapter or PeriodicStructureAdapter
    stru
        instance of Structure class from diffpy.structure

    No return value.
    """
    n = len(stru)
    atomtypes = [a.element for a in stru]
    xyz = numpy.array([a.xyz for a in stru], dtype=float).reshape(n, 3)
    occupancy = [a.occupancy for a in stru]
    anisotropy = [a.anisotropy for a in stru]
    uij = numpy.zeros((n, 3, 3))
    if not all(anisotropy):
        # Atom.U of isotropic atoms, without its cost per access
        uiso = [0.0 if f else a.Uisoequiv for a, f in zip(stru, anisotropy)]
        numpy.multiply.outer(uiso, stru.lattice.isotropicunit, out=uij)
    if any(anisotropy):
        uij[anisotropy] = [a.U for a, f in zip(stru, anisotropy) if f]
    if hasattr(adpt, "setLatPar"):
        adpt.setLatPar(*stru.lattice.cell_parms())
        adpt._setLatticeAtomArrays(atomtypes, xyz, occupancy, anisotropy, uij)
    else:
        adpt.setAtomArrays(atomtypes, xyz, occupancy, anisotropy, uij)
    return


# End of file
