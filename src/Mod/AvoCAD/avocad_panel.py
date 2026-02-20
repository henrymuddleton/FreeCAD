# SPDX-License-Identifier: LGPL-2.1-or-later

"""AvoCAD phase-0 AI panel scaffold.

This is intentionally a non-invasive UI shell that demonstrates the planned
Ask/Plan/Execute interaction model without mutating documents yet.
"""

from __future__ import annotations

import FreeCAD
import FreeCADGui

from PySide import QtCore, QtGui


class AvoCADPanel(QtGui.QDockWidget):
    """Dockable panel for AvoCAD AI interactions."""

    PANEL_OBJECT_NAME = "AvoCAD AI"

    def __init__(self, parent=None):
        super().__init__("AvoCAD AI", parent)
        self.setObjectName(self.PANEL_OBJECT_NAME)
        self.setWindowTitle("AvoCAD AI")
        self.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea
            | QtCore.Qt.RightDockWidgetArea
            | QtCore.Qt.BottomDockWidgetArea
        )

        container = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(container)

        self.mode_combo = QtGui.QComboBox(container)
        self.mode_combo.addItems(["Ask", "Plan", "Execute"])

        self.prompt_edit = QtGui.QPlainTextEdit(container)
        self.prompt_edit.setPlaceholderText(
            "Describe what you want to create, edit, or inspect..."
        )

        self.result_view = QtGui.QPlainTextEdit(container)
        self.result_view.setReadOnly(True)
        self.result_view.setPlaceholderText(
            "AvoCAD output will appear here."
        )

        actions_row = QtGui.QHBoxLayout()
        self.run_button = QtGui.QPushButton("Run", container)
        self.clear_button = QtGui.QPushButton("Clear", container)
        actions_row.addWidget(self.run_button)
        actions_row.addWidget(self.clear_button)

        layout.addWidget(QtGui.QLabel("Mode", container))
        layout.addWidget(self.mode_combo)
        layout.addWidget(QtGui.QLabel("Prompt", container))
        layout.addWidget(self.prompt_edit)
        layout.addLayout(actions_row)
        layout.addWidget(QtGui.QLabel("Output", container))
        layout.addWidget(self.result_view)

        self.setWidget(container)

        self.run_button.clicked.connect(self.run_prompt)
        self.clear_button.clicked.connect(self.clear_panel)

    def run_prompt(self):
        mode = self.mode_combo.currentText()
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            self.result_view.appendPlainText("No prompt entered.")
            return

        self.result_view.appendPlainText(
            "[{mode}] Phase-0 scaffold received prompt:\n{prompt}\n".format(
                mode=mode,
                prompt=prompt,
            )
        )
        FreeCAD.Console.PrintMessage(
            "AvoCAD panel received prompt in {mode} mode\n".format(mode=mode)
        )

    def clear_panel(self):
        self.prompt_edit.clear()
        self.result_view.clear()


def get_or_create_panel() -> AvoCADPanel:
    main_window = FreeCADGui.getMainWindow()
    panel = main_window.findChild(QtGui.QDockWidget, AvoCADPanel.PANEL_OBJECT_NAME)
    if panel is not None:
        return panel

    panel = AvoCADPanel(main_window)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, panel)
    return panel
