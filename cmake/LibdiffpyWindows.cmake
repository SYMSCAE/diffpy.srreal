# Backport Windows support for the pinned libdiffpy revision. Generate the
# adapted files in the build tree so local source overrides remain untouched.
# Remove these adaptations when the upstream revision includes the fixes.
set(_diffpy_src "${LIBDIFFPY_SOURCE_DIR}/src/diffpy")
set(_diffpy_inc "${CMAKE_CURRENT_BINARY_DIR}/include/diffpy")

function(_diffpy_replace_file source destination before after)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${source}")
    file(READ "${source}" contents)
    string(FIND "${contents}" "${before}" position)
    if(position EQUAL -1)
        message(FATAL_ERROR "Recheck the libdiffpy Windows adaptation for ${source}.")
    endif()
    string(REPLACE "${before}" "${after}" contents "${contents}")
    file(CONFIGURE OUTPUT "${destination}" CONTENT "${contents}" @ONLY)
endfunction()

# Modern MSVC supplies round, remainder and log2 in its standard library.
_diffpy_replace_file("${_diffpy_src}/mathutils.ipp"
    "${_diffpy_inc}/mathutils.ipp"
    "#ifdef _MSC_VER"
    "#if defined(_MSC_VER) && _MSC_VER < 1800")
_diffpy_replace_file("${_diffpy_src}/srreal/StructureAdapter.hpp"
    "${_diffpy_inc}/srreal/StructureAdapter.hpp"
    "        virtual void customPQConfig(PairQuantity* pq) const\n            __attribute__ ((deprecated))"
    "        [[deprecated]] virtual void customPQConfig(PairQuantity* pq) const")

# Keep libdiffpy's LineReader implementation; replace only the POSIX path
# discovery with native Windows module discovery and standard filesystem APIs.
file(READ "${_diffpy_src}/runtimepath.cpp" _runtime_source)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${_diffpy_src}/runtimepath.cpp")
set(_runtime_marker "// Implementation ------------------------------------------------------------")
string(FIND "${_runtime_source}" "${_runtime_marker}" _runtime_start)
if(_runtime_start EQUAL -1)
    message(FATAL_ERROR "Recheck the libdiffpy Windows runtimepath adaptation.")
endif()
string(SUBSTRING "${_runtime_source}" ${_runtime_start} -1 _runtime_body)
file(READ "${CMAKE_CURRENT_LIST_DIR}/windows-runtimepath.cpp.in" _runtime_windows)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_LIST_DIR}/windows-runtimepath.cpp.in")
set(LIBDIFFPY_WINDOWS_RUNTIME "${CMAKE_CURRENT_BINARY_DIR}/runtimepath-windows.cpp")
file(CONFIGURE OUTPUT "${LIBDIFFPY_WINDOWS_RUNTIME}"
    CONTENT "${_runtime_windows}\n${_runtime_body}" @ONLY)
