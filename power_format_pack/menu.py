# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 Stefan van den Akker <neftas@protonmail.com>
#
# This file is part of Power Format Pack.
#
# Power Format Pack is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Power Format Pack is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with Power Format Pack. If not, see http://www.gnu.org/licenses/.

import os

from PyQt4 import QtGui, QtCore, QtWebKit

import const
import preferences
import utility
from power_format_pack.qt.controllers.keybindings import FormKeyBindings
from prefhelper import PrefHelper


class Options(QtGui.QMenu):
    """
    Display the various options in the main menu.
    """

    def __init__(self, main_window):
        super(Options, self).__init__()
        self.main_window = main_window
        self.radio_buttons = list()
        self.c = preferences.CONFIG
        self.p = preferences.PREFS

    def button_switch(self, new_state, name):
        """
        Puts a button either on or off. Reverses current state.
        """
        current_state = self.p.get(name)
        if current_state is None:
            raise Exception("{!r} not in preferences".format(name))
        if new_state != current_state:
            self.p[name] = not current_state

    def show_markdown_toggled_dialog(self, is_enabled):
        msg_box = QtGui.QMessageBox(self.main_window)
        msg_box.setIcon(QtGui.QMessageBox.Warning)
        # because the preferences are already changed by clicking the
        # checkbox, we change the behavior here to something counter-intuitive
        if is_enabled:
            msg_box.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES, "md_enable"))
            msg_box.setText(self.c.get(const.CONFIG_WARNINGS, "md_enable"))
        else:
            msg_box.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES, "md_disable"))
            msg_box.setText(self.c.get(const.CONFIG_WARNINGS, "md_disable"))
        msg_box.setInformativeText(self.c.get(const.CONFIG_WARNINGS, "md_additional"))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.setDefaultButton(QtGui.QMessageBox.Ok)
        return msg_box.exec_()

    def create_checkbox(self, name, pretty_name=None, label=None):
        checkbox = QtGui.QCheckBox(pretty_name or label or name, self)
        if self.p.get(name):
            checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda: self.button_switch(checkbox.isChecked(), name))
        return checkbox

    @staticmethod
    def create_radiobutton(name):
        return QtGui.QRadioButton(name)

    def setup_power_format_pack_options(self):

        sub_menu_title = self.c.get(const.CONFIG_MENU_NAMES, "sub_menu")
        sub_menu = self.main_window.form.menuTools.addMenu(sub_menu_title)

        options_action = QtGui.QAction(
            self.c.get(const.CONFIG_MENU_NAMES, "options_action"),
            self.main_window,
            triggered=self.show_option_dialog
        )

        keybindings_action = QtGui.QAction(
            self.c.get(const.CONFIG_MENU_NAMES, "keybindings_action"),
            self.main_window,
            triggered=self.show_keybindings_dialog
        )

        doc_action = QtGui.QAction(
            self.c.get(const.CONFIG_MENU_NAMES, "doc_action"),
            self.main_window,
            triggered=self.show_doc_dialog
        )

        about_action = QtGui.QAction(
            self.c.get(const.CONFIG_MENU_NAMES, "about_action"),
            self.main_window,
            triggered=self.show_about_dialog
        )

        sub_menu.addAction(options_action)
        sub_menu.addAction(keybindings_action)
        sub_menu.addAction(doc_action)
        sub_menu.addAction(about_action)

    def show_keybindings_dialog(self):
        dialog = FormKeyBindings(self.main_window, preferences.KEYS)

    def show_doc_dialog(self):
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES, "doc_dialog"))

        filename = os.path.join(PrefHelper.get_addons_folder(),
                                self.c.get(const.CONFIG_DEFAULT, "FOLDER_NAME"),
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

    def enable_radio_buttons(self, checkbox, radiobuttons, prefname):
        if checkbox.isChecked():
            # enable radio buttons
            for rb in radiobuttons:
                rb.setEnabled(True)
                # set chosen type to the selected radio button
                if rb.isChecked():
                    self.p[prefname] = rb.text()
        else:
            # set chosen type to the empty string
            self.p[prefname] = ""
            # disable radiobuttons
            for rb in radiobuttons:
                rb.setEnabled(False)

    def value_comparison_event_handler(self, key, new_value):
        if new_value != self.p.get(key):
            self.p[key] = new_value

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
                                  self.c.get(const.CONFIG_LABELS, "edit_rendered_markdown_label"))
        utility.set_tool_tip(cb, self.c.get(const.CONFIG_TOOLTIPS, "edit_rendered_markdown_tooltip"))
        #
        cb.setChecked(True)
        cb.setDisabled(True)

        return self.put_elems_in_box((cb,), const.HBOX, const.WIDGET)

    def fixed_lists_radio_button_event_handler(self, prefname):
        source = self.sender()
        self.p[prefname] = source.text()

    def create_fixed_list_options(self, config_prop_name, tooltip_prop_name, prefname, types_iter):
        check_box = QtGui.QCheckBox(self.c.get(const.CONFIG_LABELS, config_prop_name), self)

        utility.set_tool_tip(check_box, self.c.get(const.CONFIG_TOOLTIPS, tooltip_prop_name))

        # preference value is empty string when False, otherwise len > 0
        check_box.setChecked(bool(self.p.get(prefname)))

        radio_buttons = list()
        for type_symbol in types_iter:
            radio_button = self.create_radiobutton(type_symbol)
            radio_button.clicked.connect(lambda: self.fixed_lists_radio_button_event_handler(prefname))
            radio_buttons.append(radio_button)

        check_box.stateChanged.connect(lambda: self.enable_radio_buttons(check_box, radio_buttons, prefname))

        list_type = self.p.get(prefname)
        if not list_type:
            radio_buttons[0].toggle()
        else:
            for radio_button in radio_buttons:
                if list_type == radio_button.text():
                    radio_button.toggle()
                    break

        button_group = QtGui.QButtonGroup(self)

        num_radio_button = 0
        for radio_button in radio_buttons:
            button_group.addButton(radio_button, num_radio_button)
            num_radio_button += 1

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(check_box)
        hbox.addStretch(1)
        for radio_button in radio_buttons:
            if not check_box.isChecked():
                radio_button.setEnabled(False)
            hbox.addWidget(radio_button)

        return hbox

    def markdown_skip_warning_option(self):
        cb = self.create_checkbox(const.MARKDOWN_ALWAYS_REVERT,
                                  None,
                                  self.c.get(const.CONFIG_LABELS, "automatic_revert_cb_label"))
        utility.set_tool_tip(cb, self.c.get(const.CONFIG_TOOLTIPS, "automatic_revert_cb_tooltip"))

        return self.put_elems_in_box((cb,), const.HBOX, const.WIDGET)

    def markdown_linenums_option(self):
        linenums_cb = self.create_checkbox(const.MARKDOWN_LINE_NUMS,
                                           None,
                                           self.c.get(const.CONFIG_LABELS, "linenums_cb_label"))
        return self.put_elems_in_box((linenums_cb,), const.HBOX, const.WIDGET)

    def markdown_syntax_styles_option(self):
        md_style_label = QtGui.QLabel(self.c.get(const.CONFIG_LABELS, "md_style_label"), self)
        md_style_combo = QtGui.QComboBox(self)
        md_style_combo.setEnabled(not self.p.get(const.MARKDOWN_CLASSFUL_PYGMENTS))
        md_style_combo.setMinimumWidth(const.MIN_COMBOBOX_WIDTH)
        md_style_files = os.listdir(os.path.join(PrefHelper.get_addons_folder(),
                                                 self.c.get(const.CONFIG_DEFAULT, "FOLDER_NAME"),
                                                 "pygments",
                                                 "styles"))

        # pretty print styles
        for filename in sorted(md_style_files):
            if filename.startswith("_") or filename.endswith(".pyc"):
                continue
            (style, _) = os.path.splitext(filename)
            style = utility.prettify_option_name(style)
            md_style_combo.addItem(style)

        all_items_in_combo = \
            [md_style_combo.itemText(i) for i in xrange(md_style_combo.count())]
        current_style = self.p.get(const.MARKDOWN_SYNTAX_STYLE)
        current_style = utility.prettify_option_name(current_style)
        if current_style and current_style in all_items_in_combo:
            index_current_style = all_items_in_combo.index(current_style)
            md_style_combo.setCurrentIndex(index_current_style)

        md_style_combo.currentIndexChanged[str].connect(
                lambda: self.value_comparison_event_handler(
                    const.MARKDOWN_SYNTAX_STYLE,
                    utility.deprettify_option_name(md_style_combo.currentText())))

        hbox = self.put_elems_in_box((md_style_label, md_style_combo),
                                     const.HBOX,
                                     const.WIDGET)
        hbox.insertStretch(1, 1)

        return hbox

    def markdown_code_align_option(self):
        code_align_label = QtGui.QLabel(self.c.get(const.CONFIG_LABELS, "code_align_label"))
        code_align_combo = QtGui.QComboBox(self)
        code_align_combo.setEnabled(not self.p.get(const.MARKDOWN_CLASSFUL_PYGMENTS))
        code_align_combo.setMinimumWidth(const.MIN_COMBOBOX_WIDTH)
        for direction in const.CODE_DIRECTIONS:
            code_align_combo.addItem(direction)
        current_direction = self.p.get(
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

    @staticmethod
    def toggle_markdown_controls(enabled, *widgets):
        for widget in widgets:
            widget.setEnabled(enabled)

    def init_markdown_option(self):
        md_vbox = QtGui.QVBoxLayout()

        # Markdown switch between user style sheet and inline styling
        classes_or_inline_cb = \
            self.create_checkbox(const.MARKDOWN_CLASSFUL_PYGMENTS,
                                 None,
                                 self.c.get(const.CONFIG_LABELS, "markdown_classful_pygments_label"))
        classes_or_inline_cb.toggled.connect(
            lambda: self.toggle_markdown_controls(not classes_or_inline_cb.isChecked(),
                                                  syntax_styles_combo,
                                                  code_align_combo))
        classes_or_inline_hbox = self.put_elems_in_box((classes_or_inline_cb,), const.HBOX, const.WIDGET)

        md_vbox.addLayout(classes_or_inline_hbox)

        # Markdown syntax highlighting
        syntax_styles_hbox = self.markdown_syntax_styles_option()
        md_vbox.addLayout(syntax_styles_hbox)
        syntax_styles_combo = syntax_styles_hbox.itemAt(2).widget()

        # Markdown code align
        code_align_hbox = self.markdown_code_align_option()
        md_vbox.addLayout(code_align_hbox)
        code_align_combo = code_align_hbox.itemAt(2).widget()

        md_vbox.addWidget(utility.create_horizontal_rule())

        # line numbers Markdown code highlighting
        md_vbox.addLayout(self.markdown_linenums_option())

        # option to always revert automatically back to old Markdown
        # and skip the warning dialog
        md_vbox.addLayout(self.markdown_skip_warning_option())

        md_vbox.setSpacing(self.c.getint(const.CONFIG_QT, "spacing_buttons"))

        md_groupbox = QtGui.QGroupBox(self.c.get(const.CONFIG_LABELS, "md_groupbox"), self)
        md_groupbox.setStyleSheet(const.QGROUPBOX_STYLE)
        md_groupbox.setCheckable(True)
        md_groupbox.setChecked(self.p.get(const.MARKDOWN))

        md_groupbox.toggled.connect(
            lambda: self.button_switch(md_groupbox.isChecked(), const.MARKDOWN))
        md_groupbox.toggled.connect(
            lambda: self.toggle_markdown_controls(md_groupbox.isChecked() and not classes_or_inline_cb.isChecked(),
                                                  syntax_styles_combo,
                                                  code_align_combo))
        md_groupbox.toggled[bool].connect(self.show_markdown_toggled_dialog)

        md_groupbox.setLayout(md_vbox)

        return md_groupbox

    def init_button_options(self):
        grid = QtGui.QGridLayout()
        l = [k for k in self.p.keys() if k not in (const.CODE_CLASS,
                                                   const.LAST_BG_COLOR,
                                                   const.FIXED_OL_TYPE,
                                                   const.FIXED_UL_TYPE,
                                                   const.MARKDOWN_SYNTAX_STYLE,
                                                   const.MARKDOWN_LINE_NUMS,
                                                   const.MARKDOWN_ALWAYS_REVERT,
                                                   const.MARKDOWN_CODE_DIRECTION,
                                                   const.BUTTON_PLACEMENT,
                                                   const.MARKDOWN_OVERRIDE_EDITING,
                                                   const.MARKDOWN,
                                                   const.STYLE_TABLE,
                                                   const.MARKDOWN_CLASSFUL_PYGMENTS)]
        num_items = len(l) / 2.0
        num_items = num_items + 0.5 if (num_items % 1.0 > 0.0) else num_items

        # go through the keys in the prefs and make QCheckBoxes for them
        for index, option in enumerate(sorted(l)):
            pretty_option = utility.prettify_option_name(option)
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
        utility.set_tool_tip(label, self.c.get(const.CONFIG_TOOLTIPS, "code_pre_tooltip"))
        text = QtGui.QLineEdit(self.p.get(const.CODE_CLASS), self)
        text.editingFinished.connect(
                lambda: self.value_comparison_event_handler(
                    const.CODE_CLASS, text.text()))

        return self.put_elems_in_box((label, text), const.HBOX, const.WIDGET)

    def init_button_placement_option(self):
        label = QtGui.QLabel(self.c.get(const.CONFIG_LABELS, "buttons_placement"))
        combo = QtGui.QComboBox(self)
        combo.setMinimumWidth(const.MIN_COMBOBOX_WIDTH)
        for placement in const.PLACEMENT_POSITIONS:
            combo.addItem(placement)
        current_placement = self.p.get(const.BUTTON_PLACEMENT)
        combo.setCurrentIndex(
                const.PLACEMENT_POSITIONS.index(current_placement))
        combo.currentIndexChanged[str].connect(
                lambda: self.value_comparison_event_handler(
                    const.BUTTON_PLACEMENT, combo.currentText()))

        hbox = self.put_elems_in_box((label, combo), const.HBOX, const.WIDGET)
        hbox.insertStretch(1, 1)

        return hbox

    def init_table_styling_option(self):
        cb = self.create_checkbox(const.STYLE_TABLE,
                                  None,
                                  self.c.get(const.CONFIG_LABELS, "table_styling_label"))
        utility.set_tool_tip(cb, self.c.get(const.CONFIG_TOOLTIPS, "table_styling_tooltip"))

        return self.put_elems_in_box((cb,), const.HBOX, const.WIDGET)

    def switch_user_style_sheet_inline_on_off(self, *widgets):
        """
        Switches widgets related to user style sheets on or off.
        """
        is_checked = self.sender().isChecked()
        for widget in widgets:
            widget.setEnabled(not is_checked)

    def create_general_tab(self):

        general_tab = QtGui.QWidget()

        buttons_groupbox = QtGui.QGroupBox(self.c.get(const.CONFIG_LABELS, "buttons_groupbox"), self)
        buttons_groupbox.setStyleSheet(const.QGROUPBOX_STYLE)

        button_grid = self.init_button_options()

        code_css_class_hbox = self.init_code_css_class()

        fixed_ol_option_hbox = self.create_fixed_list_options("ordered_list_type_option_label",
                                                              "ordered_list_type_tooltip",
                                                              const.FIXED_OL_TYPE,
                                                              ("1.", "A.", "a.", "I.", "i."))

        fixed_ul_option_hbox = self.create_fixed_list_options("unordered_list_type_option_label",
                                                              "unordered_list_type_tooltip",
                                                              const.FIXED_UL_TYPE,
                                                              ("disc", "circle", "square"))

        button_placement_hbox = self.init_button_placement_option()

        table_styling_hbox = self.init_table_styling_option()

        buttons_vbox = QtGui.QVBoxLayout()
        buttons_vbox.addLayout(button_grid)
        buttons_vbox.addWidget(utility.create_horizontal_rule())
        buttons_vbox.addLayout(button_placement_hbox)
        buttons_vbox.addWidget(utility.create_horizontal_rule())
        buttons_vbox.addLayout(code_css_class_hbox)
        buttons_vbox.addWidget(utility.create_horizontal_rule())
        buttons_vbox.addLayout(fixed_ol_option_hbox)
        buttons_vbox.addLayout(fixed_ul_option_hbox)
        buttons_vbox.addWidget(utility.create_horizontal_rule())
        buttons_vbox.addLayout(table_styling_hbox)

        buttons_groupbox.setLayout(buttons_vbox)

        general_vbox = self.put_elems_in_box(
                (buttons_groupbox,), const.VBOX, const.WIDGET)

        general_tab.setLayout(general_vbox)

        return general_tab

    def create_markdown_tab(self):
        markdown_tab = QtGui.QWidget()

        markdown_qgroupbox = self.init_markdown_option()
        markdown_vbox = self.put_elems_in_box((markdown_qgroupbox,), const.VBOX, const.WIDGET)
        markdown_vbox.addStretch(1)

        markdown_tab.setLayout(markdown_vbox)

        return markdown_tab

    def show_option_dialog(self):
        option_dialog = QtGui.QDialog(self.main_window)
        option_dialog.setWindowTitle(self.c.get(const.CONFIG_WINDOW_TITLES, "option_dialog"))

        tab_widget = QtGui.QTabWidget(self)

        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")

        markdown_tab = self.create_markdown_tab()
        tab_widget.addTab(markdown_tab, "Markdown")

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(option_dialog.accept)
        button_box.rejected.connect(option_dialog.reject)

        dialog_vbox = QtGui.QVBoxLayout()
        dialog_vbox.addWidget(tab_widget)
        dialog_vbox.addWidget(button_box)
        option_dialog.setLayout(dialog_vbox)

        if option_dialog.exec_() == QtGui.QDialog.Accepted:
            PrefHelper.save_prefs(self.p)
        else:
            default_prefs = PrefHelper.get_default_preferences()
            if PrefHelper.are_dicts_different(self.p, default_prefs):
                self.p = default_prefs
