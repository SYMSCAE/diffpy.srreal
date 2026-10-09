**Changed:**

* Align the nanobind migration with pyobjcryst issue 101: use scikit-build-core,
  CMake, and pinned upstream libdiffpy sources compiled into the extension.
  Retain C++23 to match libdiffpy's own build requirements.
* Use pyobjcryst's Python API for Crystal and Molecule conversion, removing
  the build-time libobjcryst dependency and cross-extension C++ ABI coupling.
* Retain the centralized scikit-package testing, release, and documentation
  workflows and their platform matrix. Check out the pinned libdiffpy
  submodule through the shared workflows' ``submodules`` option and include
  its sources in source distributions. Test the current pyobjcryst migration
  on Linux through the shared post-install hook. Preserve tag-based package
  versions.

**Fixed:**

* Allow structureadapter to be imported before other srreal modules.
* Support the custom virtual-method dispatch used by both nanobind 2 and 3.
* Fail pyobjcryst integration tests on conversion errors instead of skipping
  them as if ObjCryst support were unavailable.
* Reject mismatched libdiffpy revisions in Git checkouts, while preserving
  Git-free source-distribution builds.
