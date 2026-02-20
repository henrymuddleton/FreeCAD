# SPDX-License-Identifier: LGPL-2.1-or-later

"""AvoCAD phase-0 AI panel scaffold.

The panel acts like a chat window and mirrors AI responses into FreeCAD's main
window surfaces (status bar + report view) so users get feedback while working
in the normal CAD editor.
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

        self.chat_view = QtGui.QListWidget(container)
        self.chat_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

        self.prompt_edit = QtGui.QPlainTextEdit(container)
        self.prompt_edit.setMaximumBlockCount(200)
        self.prompt_edit.setPlaceholderText(
            "Describe what you want to create, edit, or inspect..."
        )

        actions_row = QtGui.QHBoxLayout()
        self.run_button = QtGui.QPushButton("Run", container)
        self.clear_button = QtGui.QPushButton("Clear", container)
        actions_row.addWidget(self.run_button)
        actions_row.addWidget(self.clear_button)

        layout.addWidget(QtGui.QLabel("Mode", container))
        layout.addWidget(self.mode_combo)
        layout.addWidget(QtGui.QLabel("Chat", container))
        layout.addWidget(self.chat_view)
        layout.addWidget(QtGui.QLabel("Prompt", container))
        layout.addWidget(self.prompt_edit)
        layout.addLayout(actions_row)

        self.setWidget(container)

        self.run_button.clicked.connect(self.run_prompt)
        self.clear_button.clicked.connect(self.clear_panel)

    def run_prompt(self):
        mode = self.mode_combo.currentText()
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            self._append_message("System", "No prompt entered.")
            return

        self._append_message("You", prompt)

        response = self._build_scaffold_response(mode, prompt)
        self._append_message("AvoCAD", response)
        self._mirror_output_to_main_window(response)

    def _append_message(self, sender, text):
        item = QtGui.QListWidgetItem(
            "{sender}: {text}".format(sender=sender, text=text)
        )
        if sender == "AvoCAD":
            item.setForeground(QtGui.QBrush(QtGui.QColor("#2E7D32")))
        elif sender == "System":
            item.setForeground(QtGui.QBrush(QtGui.QColor("#B71C1C")))
        self.chat_view.addItem(item)
        self.chat_view.scrollToBottom()

    @staticmethod
    def _build_scaffold_response(mode, prompt):
        return (
            "[{mode}] Received: {prompt}\n"
            "Scaffold behavior: response mirrored to status bar/report view so "
            "feedback is visible while you continue editing CAD geometry in the "
            "main window."
        ).format(mode=mode, prompt=prompt)

    @staticmethod
    def _mirror_output_to_main_window(response):
        main_window = FreeCADGui.getMainWindow()
        if main_window is not None and main_window.statusBar() is not None:
            main_window.statusBar().showMessage(response, 8000)

        FreeCAD.Console.PrintMessage("AvoCAD: {response}\n".format(response=response))
        FreeCAD.Console.PrintMessage(
            "AvoCAD: see this response mirrored in the main window status bar.\n"
        )

    def clear_panel(self):
        self.prompt_edit.clear()
        self.chat_view.clear()


def get_or_create_panel() -> AvoCADPanel:
    main_window = FreeCADGui.getMainWindow()
    panel = main_window.findChild(QtGui.QDockWidget, AvoCADPanel.PANEL_OBJECT_NAME)
    if panel is not None:
        return panel

    panel = AvoCADPanel(main_window)
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, panel)
    return panel
