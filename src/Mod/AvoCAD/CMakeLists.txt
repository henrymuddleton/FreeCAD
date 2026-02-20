# SPDX-License-Identifier: LGPL-2.1-or-later

set(AvoCAD_Scripts
    Init.py
)

if(BUILD_GUI)
    list(APPEND AvoCAD_Scripts
        InitGui.py
        avocad_panel.py
    )
endif()

add_custom_target(AvoCADScripts ALL
    SOURCES ${AvoCAD_Scripts}
)

fc_target_copy_resource(AvoCADScripts
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}/Mod/AvoCAD
    ${AvoCAD_Scripts}
)

install(
    FILES
        ${AvoCAD_Scripts}
    DESTINATION
        Mod/AvoCAD
)
