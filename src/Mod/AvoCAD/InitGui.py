# SPDX-License-Identifier: LGPL-2.1-or-later

"""AvoCAD GUI init module for phase-0 scaffolding."""

import FreeCAD
import FreeCADGui

from avocad_panel import get_or_create_panel


class _AvoCADOpenPanelCmd:
    """Opens or focuses the AvoCAD AI panel."""

    def GetResources(self):
        return {
            "Pixmap": FreeCAD.getResourceDir() + "Mod/Start/Gui/Resources/icons/StartCommandIcon.svg",
            "MenuText": "AvoCAD AI Panel",
            "ToolTip": "Open the AvoCAD AI panel scaffold",
        }

    def IsActive(self):
        return True

    def Activated(self):
        panel = get_or_create_panel()
        panel.show()
        panel.raise_()


class AvoCADWorkbench(Workbench):
    """AvoCAD workbench scaffold."""

    MenuText = "AvoCAD"
    ToolTip = "AvoCAD AI-assisted CAD workbench"
    Icon = FreeCAD.getResourceDir() + "Mod/Start/Gui/Resources/icons/StartCommandIcon.svg"

    def Initialize(self):
        FreeCADGui.addCommand("AvoCAD_OpenPanel", _AvoCADOpenPanelCmd())
        self.appendToolbar("AvoCAD", ["AvoCAD_OpenPanel"])
        self.appendMenu("AvoCAD", ["AvoCAD_OpenPanel"])

    def Activated(self):
        # Keep activation non-invasive: user can open panel on demand.
        pass

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(AvoCADWorkbench())

if hasattr(FreeCAD, "__unit_test__"):
    FreeCAD.__unit_test__ += ["TestAvoCADGui"]
