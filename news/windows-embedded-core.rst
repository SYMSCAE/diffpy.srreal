**Fixed:**

* Restore Windows builds of the embedded libdiffpy core with modern MSVC.
  Enable mathematical constants, replace compiler-specific declarations,
  and locate packaged runtime tables relative to the extension module while
  honoring ``DIFFPYRUNTIME``. Add Windows CI for Python 3.12, 3.13, and 3.14.
