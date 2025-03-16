# Copyright (c) 2025 kounch
# SPDX-License-Identifier: BSD-2-Clause

cmake_minimum_required(VERSION 3.24)
project("ARC_ROM_Builder")

if ( ${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR} )
    message(FATAL_ERROR "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there. You may need to remove CMakeCache.txt.")
endif()

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/CMake/Find")

set(BASENAME ${PROJECT_NAME})
set(OUTPUT_DIR ${CMAKE_BINARY_DIR})

set(EXTRA_FILES
    cores.json
    cores_neptunoplus.json
    )

set(EXTRA_DOCS
    LICENSE
    README.md
    )

# Get Current version
execute_process(
    COMMAND python3 ARC_ROM_Builder.py --version
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    OUTPUT_VARIABLE VERSIONSTR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    )
if (VERSIONSTR)
    string(REGEX MATCH "ARC_ROM_Builder.py (.*)" _ ${VERSIONSTR})
    set(VERSION ${CMAKE_MATCH_1})
else()
    message(FATAL_ERROR "Cannot determine ARC ROM Builder version")
endif()

# Check module availability
find_package(nuitka)

if (WIN32)
    set(APP_NAME "ARC_ROM_Builder.exe")
elseif (APPLE)
    set(APP_NAME "ARC_ROM_Builder")
    set(ARCH_TO_BUILD "arm64" )
endif()

# Extra Files
message("Prepare extra files build")
set(FILES_DIR "${OUTPUT_DIR}/extra")
file(MAKE_DIRECTORY ${FILES_DIR})

add_custom_target(extra_files ALL
    DEPENDS ${OUTPUT_DIR}/extra
)
foreach(file_i ${EXTRA_FILES})
add_custom_command(TARGET extra_files
    COMMAND ${CMAKE_COMMAND} ARGS -E copy ${PROJECT_SOURCE_DIR}/${file_i} ${OUTPUT_DIR}/extra
    BYPRODUCTS ${OUTPUT_DIR}/extra/${file_i}
)
endforeach(file_i)

# Docs
message("Prepare docs build")
set(DOCS_DIR "${OUTPUT_DIR}/docs")
file(MAKE_DIRECTORY ${DOCS_DIR})

add_custom_target(extra_docs ALL
    DEPENDS ${OUTPUT_DIR}/docs
)
foreach(file_i ${EXTRA_DOCS})
add_custom_command(TARGET extra_docs
    COMMAND ${CMAKE_COMMAND} ARGS -E copy ${PROJECT_SOURCE_DIR}/${file_i} ${OUTPUT_DIR}/docs
    BYPRODUCTS ${OUTPUT_DIR}/docs/${file_i}
)
endforeach(file_i)

# Function to build Mac binaries
function(BUILD_MAC ARCH_TO_BUILD)
    set(MAC_BUILD_DIR "${OUTPUT_DIR}/mac_${ARCH_TO_BUILD}")
    set(MAC_ZIP_FILE "${OUTPUT_DIR}/${BASENAME} macOS ${ARCH_TO_BUILD} v${VERSION}.zip")
    file(MAKE_DIRECTORY ${MAC_BUILD_DIR})

    add_custom_target("ARC_ROM_Builder_mac_${ARCH_TO_BUILD}" ALL
        DEPENDS ${MAC_BUILD_DIR}/${APP_NAME}
        )
    add_custom_command(OUTPUT ${MAC_BUILD_DIR}/${APP_NAME}
        DEPENDS ${PROJECT_SOURCE_DIR}/${BASENAME}.py
        COMMAND ${NUITKA_BINARY} ${PROJECT_SOURCE_DIR}/${BASENAME}.py --output-dir=${MAC_BUILD_DIR} -o ${MAC_BUILD_DIR}/${PROJECT_NAME} --standalone --onefile --lto=yes --macos-target-arch=${ARCH_TO_BUILD} --quiet
        BYPRODUCTS ${MAC_BUILD_DIR}/${BASENAME}.build ${MAC_BUILD_DIR}/${BASENAME}.dist
        COMMENT "MacOS ${ARCH_TO_BUILD} Binary"
        )
    add_custom_command(TARGET "ARC_ROM_Builder_mac_${ARCH_TO_BUILD}" POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/extra ${MAC_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/docs ${MAC_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${MAC_BUILD_DIR}/${PROJECT_NAME}.*
        COMMAND ${CMAKE_COMMAND} -E remove ${MAC_ZIP_FILE}
        COMMAND ${CMAKE_COMMAND} -E tar "cf" "${MAC_ZIP_FILE}" --format=zip -- .
        WORKING_DIRECTORY ${MAC_BUILD_DIR}
        COMMENT "MacOS Zip"
        )
endfunction()

# Build MacOS binaries and packages
if(NUITKA_FOUND)
    message("Prepare MacOS binary builds and packages")

    build_mac("arm64")
    build_mac("x86_64")
endif()

# Function to build Windows packages
function(BUILD_WIN ARCH_TO_PACKAGE)
    set(WIN_BUILD_DIR "${OUTPUT_DIR}/win_${ARCH_TO_PACKAGE}")
    set(WIN_ZIP_FILE "${OUTPUT_DIR}/${BASENAME} Windows ${ARCH_TO_PACKAGE} v${VERSION}.zip")

    add_custom_target("ARC_ROM_Builder_win_${ARCH_TO_PACKAGE}" ALL
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/extra ${WIN_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/docs ${WIN_BUILD_DIR}
        )

    add_custom_command(TARGET "ARC_ROM_Builder_win_${ARCH_TO_PACKAGE}" POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove ${WIN_ZIP_FILE}
        COMMAND ${CMAKE_COMMAND} -E tar "cf" "${WIN_ZIP_FILE}" --format=zip -- .
        WORKING_DIRECTORY ${WIN_BUILD_DIR}
        COMMENT "Compressing"
        )
endfunction()

# Build Windows ZIP files
message("Prepare Windows packages")
build_win("x86_32")
build_win("x86_64")

# Function to build Python ZIP package
function(BUILD_PYTHON)
    set(PYTHON_BUILD_DIR "${OUTPUT_DIR}/py")
    set(PYTHON_ZIP_FILE "${OUTPUT_DIR}/${BASENAME} Python v${VERSION}.zip")

    file(MAKE_DIRECTORY ${PYTHON_BUILD_DIR})
    file(GLOB PY_FILES "${PROJECT_SOURCE_DIR}/*py")

    add_custom_target("ARC_ROM_Builder_python" ALL
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/extra ${PYTHON_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/docs ${PYTHON_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${PY_FILES} ${PYTHON_BUILD_DIR}
        )
    add_custom_command(
        TARGET "ARC_ROM_Builder_python" 
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove ${PYTHON_ZIP_FILE}
        COMMAND ${CMAKE_COMMAND} -E tar "cf" "${PYTHON_ZIP_FILE}" --format=zip -- .
        WORKING_DIRECTORY ${PYTHON_BUILD_DIR}
        COMMENT "Compressing"
        )
endfunction()

# Build generic ZIP Python file
message("Prepare Generic package")
build_python()
