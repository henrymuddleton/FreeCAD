# SPDX-License-Identifier: LGPL-2.1-or-later

"""AvoCAD init module.

This file intentionally remains lightweight for phase-0 bootstrapping.
"""

import FreeCAD

# Register unit-test module placeholder for future AvoCAD tests.
if hasattr(FreeCAD, "__unit_test__"):
    FreeCAD.__unit_test__ += ["TestAvoCADApp"]
