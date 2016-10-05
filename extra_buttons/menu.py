# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 Stefan van den Akker <srvandenakker.dev@gmail.com>
#
# This file is part of Supplementary Buttons for Anki.
#
# Supplementary Buttons for Anki is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Supplementary Buttons for Anki is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with Supplementary Buttons for Anki. If not, see http://www.gnu.org/licenses/.

from PyQt4 import QtGui, QtCore, QtWebKit
import os
import utility
import const
import preferences
from prefhelper import PrefHelper


class ExtraButtons_Options(QtGui.QMenu):
    """
    Display the various options in the main menu.
    """

    def __init__(self, main_window, preferences):
        super(ExtraButtons_Options, self).__init__()
        self.main_window = main_window
        self.radio_buttons = list()
        self.c = utility.get_config_parser()

    def button_switch(self, state, name, callback=None):
        """
        Puts a button either on or off. Reverses current state.
        """
        current_state = preferences.PREFS.get(name)
        if current_state is None:
            raise Exception("{!r} not in preferences".format(name))
        if bool(state) != current_state:
            preferences.PREFS[name] = not current_state
        if callback is not None:
            callback()

    def prettify_option_name(self, s):
        """
        Replace the underscore in the option name with a space and capitalize
        the resulting string.
        """
        return s.replace("_", " ").capitalize()

    def deprettify_option_name(self, s):
        """
        Replace the space in the option name with an underscore and make the
        resultant string lowercase.
        """
        return s.replace(" ", "_").lower()

    def show_markdown_dialog(self):
        mess = QtGui.QMessageBox(self.main_window)
        mess.setIcon(QtGui.QMessageBox.Warning)
        # because the preferences are already changed by clicking the
        # checkbox, we change the behavior here to something counter-intuitive
        if preferences.PREFS.get(const.MARKDOWN):
            mess.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES,
                                           "md_enable"))
            mess.setText(self.c.get(const.CONFIG_WARNINGS,
                                    "md_enable"))
        else:
            mess.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES,
                                           "md_disable"))
            mess.setText(self.c.get(const.CONFIG_WARNINGS,
                                    "md_disable"))
        mess.setInformativeText(self.c.get(const.CONFIG_WARNINGS,
                                           "md_additional"))
        mess.setStandardButtons(QtGui.QMessageBox.Ok)
        mess.setDefaultButton(QtGui.QMessageBox.Ok)
        return mess.exec_()

    def create_checkbox(self, name, pretty_name=None, label=None, callback=None):
        checkbox = QtGui.QCheckBox(pretty_name or label or name, self)
        if preferences.PREFS.get(name):
            checkbox.setChecked(True)
        checkbox.stateChanged.connect(
                lambda: self.button_switch(checkbox.isChecked(), name, callback))
        return checkbox

    def create_radiobutton(self, name):
        return QtGui.QRadioButton(name)

    def setup_extra_buttons_options(self):

        sub_menu_title = self.c.get(const.CONFIG_MENU_NAMES, "sub_menu")
        sub_menu = self.main_window.form.menuTools.addMenu(sub_menu_title)

        options_action = QtGui.QAction(
                self.c.get(const.CONFIG_MENU_NAMES, "options_action"),
                self.main_window)
        options_action.triggered.connect(self.show_option_dialog)

        about_action = QtGui.QAction(
                self.c.get(const.CONFIG_MENU_NAMES, "about_action"),
                self.main_window)
        about_action.triggered.connect(self.show_about_dialog)

        doc_action = QtGui.QAction(
                self.c.get(const.CONFIG_MENU_NAMES, "doc_action"),
                self.main_window)
        doc_action.triggered.connect(self.show_doc_dialog)

        sub_menu.addAction(options_action)
        sub_menu.addAction(about_action)
        sub_menu.addAction(doc_action)

    def show_doc_dialog(self):
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES,
                                         "doc_dialog"))

        filename = os.path.join(PrefHelper.get_addons_folder(),
                                const.FOLDER_NAME,
                                "docs",
                                "doc_start.html")

        if not os.path.exists(filename):
            print "FILENAME {!r} DOES NOT EXIST".format(filename)
            return

        help_buttons = QtGui.QDialogButtonBox(dialog)
        help_buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        help_buttons.accepted.connect(dialog.accept)

        view = QtWebKit.QWebView(dialog)
        view.load(QtCore.QUrl(filename))

        help_vbox = QtGui.QVBoxLayout()
        help_vbox.addWidget(view)
        help_vbox.addWidget(help_buttons)

        dialog.setLayout(help_vbox)

        dialog.exec_()

    def show_about_dialog(self):
        QtGui.QMessageBox.about(self.main_window,
                                self.c.get(const.CONFIG_WINDOW_TITLES, "about"),
                                self.c.get(const.CONFIG_ABOUT, "about"))

    def enable_radio_buttons(self, checkbox):
        if checkbox.isChecked():
            # enable radio buttons
            for rb in self.radio_buttons:
                rb.setEnabled(True)
                # set chosen type to the selected radio button
                if rb.isChecked():
                    preferences.PREFS[const.FIXED_OL_TYPE] = rb.text()
        else:
            # set chosen type to the empty string
            preferences.PREFS[const.FIXED_OL_TYPE] = ""
            # disable radiobuttons
            for rb in self.radio_buttons:
                rb.setEnabled(False)

    def value_comparison_event_handler(self, key, new_value):
        if new_value != preferences.PREFS.get(key):
            preferences.PREFS[key] = new_value

    def put_elems_in_box(self, elems, type_box, type_elem):
        """
        Depending on `type_box`, create a horizontal or vertical `QBoxLayout`
        and add the elements in `elems` as widgets or layouts to it.
        """
        if type_box == const.HBOX:
            box = QtGui.QHBoxLayout()
        elif type_box == const.VBOX:
            box = QtGui.QVBoxLayout()
        for elem in elems:
            if type_elem == const.WIDGET:
                box.addWidget(elem)
            elif type_elem == const.LAYOUT:
                box.addLayout(elem)

        return box

    def override_disabled_buttons_rendered_markdown(self):
        """
        Create a checkbox that controls whether or not to allow editing when
        the Markdown is rendered.
        """
        cb = self.create_checkbox(const.MARKDOWN_OVERRIDE_EDITING,
                                  None,
                                  self.c.get(const.CONFIG_LABELS,
                                             "edit_rendered_markdown_label"))
        utility.set_tool_tip(cb, self.c.get(const.CONFIG_TOOLTIPS,
                                            "edit_rendered_markdown_tooltip"))

        return self.put_elems_in_box((cb,), const.HBOX, const.WIDGET)

    def rb_event_handler(self, clicked):
        source = self.sender()
        preferences.PREFS[const.FIXED_OL_TYPE] = source.text()

    def init_fixed_ol_options(self):
        cb = QtGui.QCheckBox(self.c.get(const.CONFIG_LABELS,
                             "ordered_list_type_option_label"),
                             self)

        cb.setToolTip(self.c.get(const.CONFIG_TOOLTIPS,
                                 "ordered_list_type_tooltip"))

        # const.FIXED_OL_TYPE is empty string when False, otherwise len > 0
        cb.setChecked(bool(preferences.PREFS.get(const.FIXED_OL_TYPE)))

        cb.stateChanged.connect(lambda: self.enable_radio_buttons(cb))

        # make sure self.radio_buttons is empty before adding new buttons
        self.radio_buttons = list()
        for type_ol in ("1.", "A.", "a.", "I.", "i."):
            rb = self.create_radiobutton(type_ol)
            rb.clicked.connect(self.rb_event_handler)
            self.radio_buttons.append(rb)

        ol_type = preferences.PREFS.get(const.FIXED_OL_TYPE)
        if not ol_type:
            self.radio_buttons[0].toggle()
        else:
            for rb in self.radio_buttons:
                if ol_type == rb.text():
                    rb.toggle()
                    break

        buttonGroup = QtGui.QButtonGroup(self)

        num_radio_button = 0
        for rb in self.radio_buttons:
            buttonGroup.addButton(rb, num_radio_button)
            num_radio_button += 1

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(cb)
        for rb in self.radio_buttons:
            if not cb.isChecked():
                rb.setEnabled(False)
            hbox.addWidget(rb)

        return hbox

    def markdown_skip_warning_option(self):
        cb = self.create_checkbox(const.MARKDOWN_ALWAYS_REVERT,
                                  None,
                                  self.c.get(const.CONFIG_LABELS,
                                             "automatic_revert_cb_label"))
        utility.set_tool_tip(cb, self.c.get(const.CONFIG_TOOLTIPS,
                                            "automatic_revert_cb_tooltip"))

        return self.put_elems_in_box((cb,), const.HBOX, const.WIDGET)

    def markdown_linenums_option(self):
        linenums_cb = self.create_checkbox(const.MARKDOWN_LINE_NUMS,
                                           None,
                                           self.c.get(const.CONFIG_LABELS,
                                                      "linenums_cb_label"))
        return self.put_elems_in_box((linenums_cb,), const.HBOX, const.WIDGET)

    def markdown_syntax_styles_option(self):
        md_style_label = QtGui.QLabel(
                    self.c.get(const.CONFIG_LABELS, "md_style_label"), self)
        md_style_combo = QtGui.QComboBox(self)
        md_style_combo.setMinimumWidth(const.MIN_COMBOBOX_WIDTH)
        md_style_files = os.listdir(os.path.join(PrefHelper.get_addons_folder(),
                                                 const.FOLDER_NAME,
                                                 "pygments",
                                                 "styles"))

        # pretty print styles
        for filename in sorted(md_style_files):
            if filename.startswith("_") or filename.endswith(".pyc"):
                continue
            (style, _) = os.path.splitext(filename)
            style = self.prettify_option_name(style)
            md_style_combo.addItem(style)

        all_items_in_combo = \
            [md_style_combo.itemText(i) for i in xrange(md_style_combo.count())]
        current_style = preferences.PREFS.get(const.MARKDOWN_SYNTAX_STYLE)
        current_style = self.prettify_option_name(current_style)
        if current_style and current_style in all_items_in_combo:
            index_current_style = all_items_in_combo.index(current_style)
            md_style_combo.setCurrentIndex(index_current_style)

        md_style_combo.currentIndexChanged[str].connect(
                lambda: self.value_comparison_event_handler(
                    const.MARKDOWN_SYNTAX_STYLE,
                    self.deprettify_option_name(md_style_combo.currentText())))

        hbox = self.put_elems_in_box((md_style_label, md_style_combo),
                                     const.HBOX,
                                     const.WIDGET)
        hbox.insertStretch(1, 1)

        return hbox

    def markdown_code_align_option(self):
        code_align_label = QtGui.QLabel(self.c.get(const.CONFIG_LABELS,
                                                   "code_align_label"))
        code_align_combo = QtGui.QComboBox(self)
        code_align_combo.setMinimumWidth(const.MIN_COMBOBOX_WIDTH)
        for direction in const.CODE_DIRECTIONS:
            code_align_combo.addItem(direction)
        current_direction = preferences.PREFS.get(
                const.MARKDOWN_CODE_DIRECTION)
        code_align_combo.setCurrentIndex(
                const.CODE_DIRECTIONS.index(current_direction))

        code_align_combo.currentIndexChanged[str].connect(
                lambda: self.value_comparison_event_handler(
                    const.MARKDOWN_CODE_DIRECTION,
                    code_align_combo.currentText()))

        hbox = self.put_elems_in_box((code_align_label, code_align_combo),
                                     const.HBOX,
                                     const.WIDGET)
        hbox.insertStretch(1, 1)

        return hbox

    def init_markdown_option(self):
        md_groupbox = QtGui.QGroupBox(
                self.c.get(const.CONFIG_LABELS, "md_groupbox"),
                self)
        md_groupbox.setStyleSheet(const.QGROUPBOX_STYLE)
        md_groupbox.setCheckable(True)
        md_groupbox.setChecked(preferences.PREFS.get(const.MARKDOWN))

        md_groupbox.toggled.connect(
                lambda: self.button_switch(md_groupbox.isChecked(),
                                           const.MARKDOWN,
                                           self.show_markdown_dialog))

        md_vbox = QtGui.QVBoxLayout()

        # Markdown syntax highlighting
        md_vbox.addLayout(self.markdown_syntax_styles_option())

        # Markdown code align
        md_vbox.addLayout(self.markdown_code_align_option())

        # line numbers Markdown code highlighting
        md_vbox.addLayout(self.markdown_linenums_option())

        # option to always revert automatically back to old Markdown
        # and skip the warning dialog
        md_vbox.addLayout(self.markdown_skip_warning_option())

        # override disabled buttons in rendered Markdown
        md_vbox.addLayout(self.override_disabled_buttons_rendered_markdown())

        md_groupbox.setLayout(md_vbox)

        return md_groupbox

    def init_button_options(self):
        grid = QtGui.QGridLayout()
        l = [k for k in preferences.PREFS.keys() if k not in (
                                                const.CODE_CLASS,
                                                const.LAST_BG_COLOR,
                                                const.FIXED_OL_TYPE,
                                                const.MARKDOWN_SYNTAX_STYLE,
                                                const.MARKDOWN_LINE_NUMS,
                                                const.MARKDOWN_ALWAYS_REVERT,
                                                const.MARKDOWN_CODE_DIRECTION,
                                                const.BUTTON_PLACEMENT,
                                                const.MARKDOWN_OVERRIDE_EDITING,
                                                const.MARKDOWN
                                            )]
        num_items = len(l) / 2.0
        num_items = num_items + 0.5 if (num_items % 1.0 > 0.0) else num_items

        # go through the keys in the prefs and make QCheckBoxes for them
        for index, option in enumerate(sorted(l)):
            pretty_option = self.prettify_option_name(option)
            checkbox = self.create_checkbox(option, pretty_option)
            if index >= num_items:
                col = 1
                row = index - num_items
            else:
                col = 0
                row = index
            grid.addWidget(checkbox, row, col)

        return grid

    def init_code_css_class(self):
        label = QtGui.QLabel(
            self.c.get(const.CONFIG_LABELS, "code_pre_label"), self)
        utility.set_tool_tip(label, self.c.get(const.CONFIG_TOOLTIPS,
                                               "code_pre_tooltip"))
        text = QtGui.QLineEdit(preferences.PREFS.get(const.CODE_CLASS), self)
        text.editingFinished.connect(
                lambda: self.value_comparison_event_handler(
                    const.CODE_CLASS, text.text()))

        return self.put_elems_in_box((label, text), const.HBOX, const.WIDGET)

    def init_button_placement_option(self):
        label = QtGui.QLabel(self.c.get(const.CONFIG_LABELS,
                                        "buttons_placement"))
        combo = QtGui.QComboBox(self)
        combo.setMinimumWidth(const.MIN_COMBOBOX_WIDTH)
        for placement in const.PLACEMENT_POSITIONS:
            combo.addItem(placement)
        current_placement = preferences.PREFS.get(const.BUTTON_PLACEMENT)
        combo.setCurrentIndex(
                const.PLACEMENT_POSITIONS.index(current_placement))
        combo.currentIndexChanged[str].connect(
                lambda: self.value_comparison_event_handler(
                    const.BUTTON_PLACEMENT, combo.currentText()))

        hbox = self.put_elems_in_box((label, combo), const.HBOX, const.WIDGET)
        hbox.insertStretch(1, 1)

        return hbox

    def show_option_dialog(self):
        option_dialog = QtGui.QDialog(self.main_window)
        option_dialog.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES,
                                                "option_dialog"))

        button_grid = self.init_button_options()

        code_css_class_hbox = self.init_code_css_class()

        fixed_ol_option_hbox = self.init_fixed_ol_options()

        markdown_qgroupbox = self.init_markdown_option()

        button_placement_hbox = self.init_button_placement_option()

        button_box = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(option_dialog.accept)
        button_box.rejected.connect(option_dialog.reject)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(button_grid)
        vbox.addWidget(utility.create_horizontal_rule())
        vbox.addLayout(button_placement_hbox)
        vbox.addWidget(utility.create_horizontal_rule())
        vbox.addLayout(code_css_class_hbox)
        vbox.addWidget(utility.create_horizontal_rule())
        vbox.addLayout(fixed_ol_option_hbox)
        vbox.addWidget(markdown_qgroupbox)
        vbox.addWidget(button_box)

        # some extra space between fix ordered list type and Markdown toggle
        vbox.insertSpacing(7, 5)

        option_dialog.setLayout(vbox)

        if option_dialog.exec_() == QtGui.QDialog.Accepted:
            PrefHelper.save_prefs(preferences.PREFS)
        else:
            if PrefHelper.are_prefs_changed(
                    preferences.PREFS,
                    PrefHelper.load_preferences_from_disk()):
                print "Reverting preferences..."
                preferences.PREFS = PrefHelper.load_preferences_from_disk()
