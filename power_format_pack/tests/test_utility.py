# -*- coding: utf-8 -*-
import unittest
import re
import base64
import json
import sys

import power_format_pack.markdowner

if "/usr/share/anki/" not in sys.path:
    sys.path.append("/usr/share/anki/")
from power_format_pack import utility
from power_format_pack.prefhelper import PrefHelper


class UtilityTester(unittest.TestCase):
    def __init__(self, arg1):
        super(UtilityTester, self).__init__(arg1)
        self.whitespace_regex = re.compile(r"\s+")
        self.left_paren_regex = re.compile(r"\\\(")
        self.right_paren_regex = re.compile(r"\\\)")

    # replace_link_img_matches
    def test_replace_link_img_matches_should_accept_and_return_unicode(self):
        image = "![](image \(1\).jpg)"
        self.assertRaises(AssertionError,
                          utility.replace_link_img_matches,
                          self.whitespace_regex, "&#32;", image)

    def test_replace_link_img_matches_accepts_russian_input(self):
        image = "![](изображение \(1\).jpg)"
        expected = "![](изображение&#32;\(1\).jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replaces_single_whitespace(self):
        image = "![](image \(1\).jpg)"
        expected = "![](image&#32;\(1\).jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replaces_link_with_whitespace(self):
        image = "[](image \(1\).jpg)"
        expected = image
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual, "Uncorrectly replaced whitespace in link with &#32;")

    def test_replace_link_img_matches_replaces_link_with_title(self):
        image = "[text](image \(1\).jpg)"
        expected = "[text](image \(1\).jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual, "Did uncorrectly replace whitespace with &#32;")

    def test_replace_link_img_matches_replaces_link_with_title_that_contains_whitespace(self):
        image = "[random text](image \(1\).jpg)"
        expected = image
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual, "Uncorrectly replaced whitespace in link with &#32;")

    def test_replace_link_img_matches_makes_no_changes_when_final_paren_is_missing(self):
        image = "[](image \(1\).jpg"
        expected = "[](image \(1\).jpg"
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_does_not_replace_unescaped_left_parens(self):
        image = "[](image (1\).jpg"
        expected = "[](image (1\).jpg"
        actual = utility.replace_link_img_matches(self.left_paren_regex, "&#32;", image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_returns_same_when_whitespace_before_opening_paren(self):
        image = "![] (image \(1\).jpg)"
        expected = "![] (image \(1\).jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replaces_whitespace_in_different_parts(self):
        image = "![](image \(1\) .jpg)"
        expected = "![](image&#32;\(1\)&#32;.jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replace_left_paren_with_char_entity(self):
        image = "![](image \(1\).jpg)"
        expected = "![](image &#40;1\).jpg)"
        actual = utility.replace_link_img_matches(self.left_paren_regex,
                                                  "&#40;",
                                                  image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replace_multiple_left_parens_with_char_entity(self):
        image = "![](image \(\(\(1\)\)\).jpg)"
        expected = "![](image &#40;&#40;&#40;1\)\)\).jpg)"
        actual = utility.replace_link_img_matches(self.left_paren_regex,
                                                  "&#40;",
                                                  image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replaces_multiple_escaped_right_parens(self):
        image = "![](image \(\(\(1\)\)\).jpg)"
        expected = "![](image \(\(\(1&#41;&#41;&#41;.jpg)"
        actual = utility.replace_link_img_matches(self.right_paren_regex,
                                                  "&#41;",
                                                  image)
        self.assertEqual(expected, actual)

    def test_replace_link_img_matches_replaces_whitespace_in_multiple_imgs(self):
        image = "random text before\n" + \
                "![](image \(1\).jpg)\n" + \
                "and more text\n" + \
                "![](image \(2\).jpg)"
        expected = "random text before\n" + \
                   "![](image&#32;\(1\).jpg)\n" + \
                   "and more text\n" + \
                   "![](image&#32;\(2\).jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_replaces_whitespace_and_parens_in_multiple_imgs(self):
        image = "random text before\n" + \
                "![](image \(1\).jpg)\n" + \
                "and more text\n" + \
                "![](image \(2\).jpg)"
        expected = "random text before\n" + \
                   "![](image&#32;&#40;1&#41;.jpg)\n" + \
                   "and more text\n" + \
                   "![](image&#32;&#40;2&#41;.jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        actual = utility.replace_link_img_matches(self.left_paren_regex,
                                                  "&#40;",
                                                  actual)
        actual = utility.replace_link_img_matches(self.right_paren_regex,
                                                  "&#41;",
                                                  actual)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_does_not_replace_whitespace_in_backticks(self):
        image = "begin `def x[R](f: => R)` end"
        expected = "begin `def x[R](f: => R)` end"
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_does_not_replace_whitespace_in_code_blocks(self):
        image = """
        hallo `welerd

```
hello world [](what about it) yes
```

and`
"""
        expected = image
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_does_not_replace_whitespace_in_code_blocks_but_does_in_normal_link(self):
        image = """
        hallo `welerd

```
hello world [](what about it) yes
```

but here ![cat](cat (1).jpg) is a cat
and`
"""
        expected = """
        hallo `welerd

```
hello world [](what about it) yes
```

but here ![cat](cat&#32;(1).jpg) is a cat
and`
"""
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_does_not_replace_whitespace_in_fenced_code_blocks(self):
        image = """
blah

```
def x[R](f: => R)
```
"""
        expected = image
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_does_not_replace_whitespace_in_indented_code_blocks(self):
        image = """
blah

    def x[R](f: => R)
"""
        expected = image
        actual = utility.replace_link_img_matches(self.whitespace_regex,
                                                  "&#32;",
                                                  image)
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_replace_link_img_matches_only_replaces_image_links(self):
        link = "Only [one `primary key` per table](http://link.com)"
        expected = link
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", link)
        self.assertEqual(expected, actual, "Replaced too much or too little!")
        self.assertEqual(len(expected), len(actual), "Length of actual actual does not match length of expected actual")

    def test_replace_link_img_matches_only_replaces_text_between_parentheses(self):
        image = "Only ![one `primary key` per table](file name.jpg)"
        expected = "Only ![one `primary key` per table](file&#32;name.jpg)"
        actual = utility.replace_link_img_matches(self.whitespace_regex, "&#32;", image)
        self.assertEqual(expected, actual)

    # filter_indices
    def test_filter_indices_does_not_change_anything_when_no_overlap(self):
        positions1 = [[0, 20]]
        positions2 = [[30, 60]]
        expected = [[0, 20]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_changes_end_value_when_overlaps(self):
        positions1 = [[0, 20]]
        positions2 = [[20, 60]]
        expected = [[0, -1]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_changes_start_value_when_overlaps(self):
        positions1 = [[50, 70]]
        positions2 = [[20, 60]]
        expected = [[-1, 70]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_do_not_change_anything_when_end_value_positions3_is_min_1(self):
        positions1 = [[50, 70]]
        positions2 = [[20, -1]]
        expected = [[50, 70]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_still_changes_end_value_when_end_value_positions3_is_min_1(self):
        positions1 = [[0, 20]]
        positions2 = [[20, -1]]
        expected = [[0, -1]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_changes_both_start_and_end_value_when_inline_block_is_inside_code_block1(self):
        positions1 = [[40, 48]]
        positions2 = [[20, 50]]
        expected = [[-1, -1]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_changes_both_start_and_end_value_when_inline_block_is_inside_code_block2(self):
        positions1 = [[40, 50]]
        positions2 = [[20, 50]]
        expected = [[-1, -1]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_changes_both_start_and_end_value_when_inline_block_is_inside_code_block3(self):
        positions1 = [[22, 48]]
        positions2 = [[20, 50]]
        expected = [[-1, -1]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    def test_filter_indices_changes_both_start_and_end_value_of_multiple_inline_code_blocks_when_inline_blocks_are_inside_code_block3(
            self):
        positions1 = [[22, 30], [32, 40]]
        positions2 = [[20, 50]]
        expected = [[-1, -1], [-1, -1]]
        utility.filter_indices(positions1, positions2)
        self.assertEqual(expected, positions1)

    # escape_html_chars
    def test_escape_html_chars_throws_assertion_error_when_input_is_not_unicode(self):
        s = "this&that"
        self.assertRaises(AssertionError, utility.escape_html_chars, s)

    def test_escape_html_chars_returns_correctly_escaped_string_when_input_is_russian(self):
        s = "об этом & о том"
        expected = "об этом &amp; о том"
        actual = utility.escape_html_chars(s)
        self.assertEqual(expected, actual)

    def test_escape_html_chars_returns_string_with_ampersand_escaped(self):
        s = "this&that"
        expected = "this&amp;that"
        actual = utility.escape_html_chars(s)
        self.assertEqual(expected, actual)

    def test_escape_html_chars_returns_string_with_multiple_ampersands_escaped(self):
        s = "this&that&so"
        expected = "this&amp;that&amp;so"
        actual = utility.escape_html_chars(s)
        self.assertEqual(expected, actual)

    def test_escape_html_chars_returns_empty_string_when_empty_string_passed(self):
        s = ""
        expected = ""
        actual = utility.escape_html_chars(s)
        self.assertEqual(expected, actual)

    def test_escape_html_chars_returns_string_with_five_chars_that_should_be_escaped(self):
        s = "this&that\"so\'and<and>"
        expected = "this&amp;that&quot;so&apos;and&lt;and&gt;"
        actual = utility.escape_html_chars(s)
        self.assertEqual(expected, actual)

    def test_escape_html_chars_fails_when_input_is_not_unicode(self):
        s = "this&that\"so\'and<and>"
        self.assertRaises(AssertionError, utility.escape_html_chars, s)

    # check_alignment
    def test_check_alignment_fails_when_input_is_not_unicode(self):
        s = ""
        self.assertRaises(AssertionError, utility.get_alignment, s)

    def test_check_alignment_returns_center_when_input_is_colon_dash_colon(self):
        s = ":-:"
        expected = "center"
        actual = utility.get_alignment(s)
        self.assertEqual(expected, actual)

    def test_check_alignment_returns_left_when_input_is_not_recognized_string(self):
        s = "random"
        expected = "left"
        actual = utility.get_alignment(s)
        self.assertEqual(expected, actual)

    def test_check_alignment_returns_left_when_input_is_empty_string(self):
        s = ""
        expected = "left"
        actual = utility.get_alignment(s)
        self.assertEqual(expected, actual)

    def test_check_alignment_returns_left_when_input_is_none(self):
        self.assertRaises(AssertionError, utility.get_alignment, None)

    # check_size_heading
    def test_check_size_heading_throws_assertion_error_when_input_not_unicode(self):
        s = ""
        self.assertRaises(AssertionError, utility.check_size_heading, s)

    def test_check_size_heading_returns_minus_one_when_input_is_empty_string(self):
        s = ""
        expected = -1
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    def test_check_size_heading_returns_minus_one_when_input_is_random_text(self):
        s = "random text"
        expected = -1
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    def test_check_size_heading_returns_six_when_input_is_seven_hashes(self):
        s = "#######heading"
        expected = 6
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    def test_check_size_heading_returns_three_when_input_is_seven_hashes_with_a_space(self):
        s = "### ####heading"
        expected = 3
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    def test_check_size_heading_returns_three_when_input_starts_with_space(self):
        s = "    ###heading"
        expected = 3
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    def test_check_size_heading_returns_three_when_input_starts_with_tab(self):
        s = "\t###heading"
        expected = 3
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    def test_check_size_heading_returns_three_when_input_starts_with_newline(self):
        s = "\n###heading"
        expected = 3
        actual = utility.check_size_heading(s)
        self.assertEqual(expected, actual)

    # string_leading_whitespace
    def test_strip_leading_whitespace_throws_assertion_error_when_input_is_not_unicode(self):
        s = " text"
        self.assertRaises(AssertionError, utility.strip_leading_whitespace, s)

    def test_strip_leading_whitespace_deletes_tab_from_start_of_string(self):
        s = "\ttext"
        expected = "text"
        actual = utility.strip_leading_whitespace(s)
        self.assertEqual(expected, actual)

    def test_strip_leading_whitespace_deletes_multiple_nbsp_from_start_of_string(self):
        s = "&nbsp;&nbsp;&nbsp;text"
        expected = "text"
        actual = utility.strip_leading_whitespace(s)
        self.assertEqual(expected, actual)

    def test_strip_leading_whitespace_does_not_delete_non_leading_nbsp(self):
        s = "text&nbsp;text"
        expected = "text&nbsp;text"
        actual = utility.strip_leading_whitespace(s)
        self.assertEqual(expected, actual)

    def test_strip_leading_whitespace_returns_same_string_when_input_is_empty_string(self):
        s = ""
        expected = ""
        actual = utility.strip_leading_whitespace(s)
        self.assertEqual(expected, actual)

    # normalize_user_prefs
    def test_normalize_user_prefs_adds_key_that_is_not_in_user_prefs(self):
        default_prefs = dict(a="one")
        user_prefs = dict()
        expected = dict(a="one")
        actual = PrefHelper.normalize_user_prefs(default_prefs, user_prefs)
        self.assertEqual(expected, actual)

    def test_normalize_user_prefs_deletes_key_that_is_not_in_default_prefs(self):
        default_prefs = dict()
        user_prefs = dict(a="one")
        expected = dict()
        actual = PrefHelper.normalize_user_prefs(default_prefs, user_prefs)
        self.assertEqual(expected, actual)

    def test_normalize_user_prefs_add_and_delete_key_from_user_dict(self):
        default_prefs = dict(b="two")
        user_prefs = dict(a="one")
        expected = dict(b="two")
        actual = PrefHelper.normalize_user_prefs(default_prefs, user_prefs)
        self.assertEqual(expected, actual)

    def test_normalize_user_prefs_empty_input_dicts_return_empty_dict(self):
        default_prefs = dict()
        user_prefs = dict()
        expected = dict()
        actual = PrefHelper.normalize_user_prefs(default_prefs, user_prefs)
        self.assertEqual(expected, actual)

    # split_string
    def test_split_string_throws_assertion_error_when_text_is_not_unicode(self):
        text = ""
        splitlist = ""
        self.assertRaises(AssertionError, utility.split_string, text, splitlist)

    def test_split_string_returns_list_with_text_when_input_starts_with_delim(self):
        text = "!text"
        splitlist = "!"
        expected = ["text"]
        actual = utility.split_string(text, splitlist)
        self.assertEqual(expected, actual)

    def test_split_string_returns_empty_list_when_text_is_only_delims(self):
        text = "!@#"
        splitlist = "!@#"
        expected = []
        actual = utility.split_string(text, splitlist)
        self.assertEqual(expected, actual)

    def test_split_string_returns_list_with_items_using_multiple_delims(self):
        text = "!one@two#three$"
        splitlist = "!@#$"
        expected = ["one", "two", "three"]
        actual = utility.split_string(text, splitlist)
        self.assertEqual(expected, actual)

    def test_split_string_returns_list_with_single_item_when_splitlist_is_empty_str(self):
        text = "!one@two#three$"
        splitlist = ""
        expected = ["!one@two#three$"]
        actual = utility.split_string(text, splitlist)
        self.assertEqual(expected, actual)

    # validate_key_sequence
    @staticmethod
    def test_validate_key_sequence_multiple_tests():
        assert utility.validate_key_sequence("") == ""
        assert utility.validate_key_sequence(None) == ""
        assert utility.validate_key_sequence("-") == "-"
        assert utility.validate_key_sequence("a") == "a"
        assert utility.validate_key_sequence("ctrl+,") == "ctrl+,"
        assert utility.validate_key_sequence("ctrl-,") == "ctrl+,"
        assert utility.validate_key_sequence(",+ctrl") == "ctrl+,"
        assert utility.validate_key_sequence("p-Alt-Ctrl") == "ctrl+alt+p"
        assert utility.validate_key_sequence(",+ctr") == ""
        assert utility.validate_key_sequence("alt+shift+greka+q") == ""
        assert utility.validate_key_sequence("alt+shift+greka+q", "darwin") == ""
        assert utility.validate_key_sequence("alt+shift+ctrl") == ""
        assert utility.validate_key_sequence("alt+alt+ctrl+p") == "ctrl+alt+p"
        assert utility.validate_key_sequence("alt-shift++") == "shift+alt++"
        assert utility.validate_key_sequence("alt-shift+++") == "shift+alt++"
        assert utility.validate_key_sequence("alt-alt------shift+p") == "shift+alt+p"
        assert utility.validate_key_sequence("alt-alt------shift+p", "darwin") == "shift+alt+p"
        print("OF INTEREST:")
        assert utility.validate_key_sequence("Q-Meta-CTRL", "darwin") == "ctrl+meta+q"
        assert utility.validate_key_sequence("MeTA---META---ShIFT++++", "darwin") == "meta+shift++"
        assert utility.validate_key_sequence("ctrl alt p", "darwin") == ""
        assert utility.validate_key_sequence("ctrl+1") == "ctrl+1"
        assert utility.validate_key_sequence("ctrl+!") == "ctrl+!"
        assert utility.validate_key_sequence("F12") == "f12"
        assert utility.validate_key_sequence("F12+Shift") == "shift+f12"
        assert utility.validate_key_sequence("F12+F11") == ""
        assert utility.validate_key_sequence("F12+a") == ""
        assert utility.validate_key_sequence("ctrl+shift+alt+meta+f5", "darwin") == "ctrl+meta+shift+alt+f5"
        assert utility.validate_key_sequence("shift+F12") == "shift+f12"

    # check_user_keybindings
    def test_check_user_keybindings_return_default_upon_invalid_user_keybinding(self):
        invalid_keybinding = {"a": "ctrl-iota-a"}
        default_keybindings = {"a": "ctrl-alt-del"}
        expected = default_keybindings
        actual = utility.check_user_keybindings(default_keybindings, invalid_keybinding)
        self.assertEqual(expected, actual)

    def test_check_user_keybindings_return_new_upon_valid_user_keybinding(self):
        valid_keybinding = {"a": "ctrl-shift-a"}
        default_keybindings = {"a": "ctrl-alt-del"}
        expected = {"a": "ctrl+shift+a"}
        actual = utility.check_user_keybindings(default_keybindings, valid_keybinding)
        self.assertEqual(expected, actual)

    def test_check_user_keybindings_return_empty_dict_when_user_keybindings_is_empty(self):
        valid_keybinding = dict()
        default_keybindings = dict(a="ctrl-alt-del")
        expected = dict()
        actual = utility.check_user_keybindings(default_keybindings, valid_keybinding)
        self.assertEqual(expected, actual)

    # start_safe_block
    def test_start_safe_block_return_none_when_hashmap_is_empty(self):
        hashmap = dict()
        expected = None
        actual = utility.start_safe_block(hashmap)
        self.assertEqual(expected, actual)

    def test_start_safe_block_returns_map_with_two_keys_when_input_is_map_with_two_valid_keys(self):
        hashmap = dict(start_time="", safe_block="")
        self.assertFalse(hashmap.get("start_time"))
        utility.start_safe_block(hashmap)
        self.assertTrue(hashmap.get("safe_block"))
        self.assertTrue(hashmap.get("start_time"))

    # end_safe_block
    def test_end_safe_block_return_none_when_hashmap_is_empty(self):
        hashmap = dict()
        expected = None
        actual = utility.end_safe_block(hashmap)
        self.assertEqual(expected, actual)

    def test_end_safe_block_sets_hashmap_key_to_false_when_correct_dict_is_passed(self):
        hashmap = dict(start_time="", safe_block="")
        expected = dict(start_time="", safe_block=False)
        utility.end_safe_block(hashmap)
        self.assertEqual(expected.get("safe_block"), hashmap.get("safe_block"))

    # convert_html_to_markdown
    def test_convert_html_to_markdown_throws_assertion_error_when_input_is_not_unicode(self):
        html = "<div>- aaa</div>"
        self.assertRaises(AssertionError, utility.strip_html_from_markdown, html)

    def test_convert_html_to_markdown_returns_empty_string_when_input_is_empty_string(self):
        html = ""
        expected = ""
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_returns_empty_string_when_input_is_empty_string_and_keep_empty_lines_is_true(
            self):
        html = ""
        expected = ""
        actual = utility.strip_html_from_markdown(html, True)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_leading_dash(self):
        html = "<div>- aaa</div>"
        expected = "- aaa\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_leading_plus_sign(self):
        html = "<div>+ aaa</div>"
        expected = "+ aaa\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_backward_slash(self):
        html = "<div>`:\`</div>"
        expected = "`:\`\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_backward_slash_followed_by_dash(self):
        html = "\- one<div>\- two</div>"
        expected = "\- one\n\- two\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_backward_slash_followed_by_underscore(self):
        html = "\_ one<div>\_ two</div>"
        expected = "\_ one\n\_ two\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_dots(self):
        html = "1. one<div>2. two</div>"
        expected = "1. one\n2. two\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_dots_with_keep_empty_lines(self):
        html = "1. one<div>2. two</div>"
        expected = "1. one\n\n2. two\n"
        actual = utility.strip_html_from_markdown(html, True)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_curly_braces(self):
        html = "{ and { and } and }"
        expected = "{ and { and } and }\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_curly_braces_in_divs(self):
        html = "{ and<div>{ and</div><div>} and }</div>"
        expected = "{ and\n{ and\n} and }\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_inverted_comma(self):
        html = "` and<div>`</div>"
        expected = "` and\n`\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    def test_convert_html_to_markdown_does_not_escape_hash_sign(self):
        html = "# one<div># two</div>"
        expected = "# one\n# two\n"
        actual = utility.strip_html_from_markdown(html)
        self.assertEqual(expected, actual)

    # convert_clean_md_to_html
    def test_convert_clean_md_to_html_throws_assertion_error_when_input_is_not_unicode(self):
        s = ""
        self.assertRaises(AssertionError, utility.convert_clean_md_to_html, s)

    def test_convert_clean_md_to_html_returns_correct_html_when_input_is_correct_md(self):
        s = "    :::python\n    def fn(): pass"
        expected = "<div>&nbsp; &nbsp; :::python</div><div>&nbsp; &nbsp; def fn(): pass</div>"
        actual = utility.convert_clean_md_to_html(s)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_empty_string_when_input_is_empty_string(self):
        s = ""
        expected = ""
        actual = utility.convert_clean_md_to_html(s)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_div_with_break_when_input_is_solely_whitespace(self):
        s = "    "
        expected = "<div><br /></div>"
        actual = utility.convert_clean_md_to_html(s)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_empty_div_when_input_is_solely_newline(self):
        s = "\n"
        expected = "<div></div>"
        actual = utility.convert_clean_md_to_html(s)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_div_with_break_when_input_is_solely_newline_and_put_breaks_is_true(self):
        s = "\n"
        expected = "<div><br /></div>"
        actual = utility.convert_clean_md_to_html(s, put_breaks=True)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_div_with_char_when_input_is_char_with_newline(self):
        s = "a\n"
        expected = "<div>a</div>"
        actual = utility.convert_clean_md_to_html(s)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_two_divs_with_char_when_input_is_newline_with_char(self):
        s = "\na"
        expected = "<div></div><div>a</div>"
        actual = utility.convert_clean_md_to_html(s)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_text_in_divs_when_input_contains_only_text(self):
        s = "random"
        expected = "<div>random</div>"
        actual = utility.convert_clean_md_to_html(s, put_breaks=True)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_two_divs_when_linebreak_in_input_text(self):
        s = "random\nrandom"
        expected = "<div>random</div><div>random</div>"
        actual = utility.convert_clean_md_to_html(s, put_breaks=True)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_correct_leading_whitespace_when_input_has_leading_whitespace(self):
        s = "    random"
        expected = "<div>&nbsp; &nbsp; random</div>"
        actual = utility.convert_clean_md_to_html(s, put_breaks=True)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_correct_leading_whitespace_when_input_has_two_lines_with_leading_whitespace(
            self):
        s = "    random\n    more"
        expected = "<div>&nbsp; &nbsp; random</div><div>&nbsp; &nbsp; more</div>"
        actual = utility.convert_clean_md_to_html(s, put_breaks=True)
        self.assertEqual(expected, actual)

    def test_convert_clean_md_to_html_returns_correct_leading_whitespace_when_input_is_russian(self):
        s = "    пизза"
        expected = "<div>&nbsp; &nbsp; пизза</div>"
        actual = utility.convert_clean_md_to_html(s, put_breaks=True)
        self.assertEqual(expected, actual)

    # convert_markdown_to_html
    def test_convert_markdown_to_html_throws_assertion_error_when_input_is_not_unicode(self):
        s = ""
        self.assertRaises(AssertionError, power_format_pack.markdowner.Markdowner.convert_markdown_to_html, s)

    # get_md_data_from_string
    def test_get_md_data_from_string_throws_assertion_error_when_input_is_not_unicode(self):
        s = "text"
        self.assertRaises(AssertionError, utility.get_md_data_from_string, s)

    def test_get_md_data_from_string_returns_empty_unicode_string_when_input_is_empty_string(self):
        s = ""
        expected = ""
        actual = utility.get_md_data_from_string(s)
        self.assertEqual(expected, actual)

    def test_get_md_data_from_string_returns_empty_string_when_input_does_not_contain_any_marker(self):
        s = "<div></div>"
        expected = ""
        actual = utility.get_md_data_from_string(s)
        self.assertEqual(expected, actual)

    def test_get_md_data_from_string_returns_empty_string_when_input_does_not_contain_end_marker(self):
        s = "<div></div><!----SBAdata{data:data}"
        expected = ""
        actual = utility.get_md_data_from_string(s)
        self.assertEqual(expected, actual)

    def test_get_md_data_from_string_returns_dict_when_markers_are_present(self):
        d = dict(a="one")
        encoded = base64.b64encode(json.dumps(d))
        s = "<div></div><!----SBAdata:{}---->".format(encoded)
        expected = encoded
        actual = utility.get_md_data_from_string(s)
        self.assertEqual(expected, actual)

    def test_get_md_data_from_string_returns_random_string_in_data_part(self):
        s = "<div></div><!----SBAdata:randomtext---->"
        expected = "randomtext"
        actual = utility.get_md_data_from_string(s)
        self.assertEqual(expected, actual)

    def test_get_md_data_from_string_returns_empty_string_when_data_part_is_empty(self):
        s = "<div></div><!----SBAdata:---->"
        expected = ""
        actual = utility.get_md_data_from_string(s)
        self.assertEqual(expected, actual)

    # decompress_and_json_load
    def test_decompress_and_json_load_throws_assertion_error_when_input_is_not_unicode(self):
        s = "text"
        self.assertRaises(AssertionError, utility.decompress_and_json_load, s)

    def test_decompress_and_json_load_returns_empty_unicode_string_when_input_is_empty_string(self):
        s = ""
        expected = ""
        actual = utility.decompress_and_json_load(s)
        self.assertEqual(expected, actual)

    def test_decompress_and_json_load_throws_type_error_when_padding_of_base64_data_is_invalid(self):
        data = "randomtext"  # lenght of string should be multiples of 4
        # so `randomtext==` would not throw an error
        # because it is padded correctly
        expected = "corrupted"
        actual = utility.decompress_and_json_load(data)
        self.assertEqual(expected, actual)

    def test_decompress_and_json_load_returns_corrupted_when_base64_data_is_invalid_json(self):
        data = "randomtext=="
        expected = "corrupted"
        actual = utility.decompress_and_json_load(data)
        self.assertEqual(expected, actual)

    def test_decompress_and_json_load_returns_corrupted_when_base64_data_contains_non_ascii_chars(self):
        data = "ëandomtext=="
        expected = "corrupted"
        actual = utility.decompress_and_json_load(data)
        self.assertEqual(expected, actual)

    def test_decompress_and_json_load_returns_valid_json_when_base64_data_is_valid(self):
        d = dict(a="one")
        data = str(base64.b64encode(json.dumps(d)))
        expected = d
        actual = utility.decompress_and_json_load(data)
        self.assertEqual(expected, actual)

    # json_dump_and_compress
    def test_json_dump_and_compress_returns_base64_string_when_input_is_dict(self):
        data = dict(a="one")
        expected = str(base64.b64encode(json.dumps(data)))
        actual = utility.json_dump_and_compress(data)
        self.assertEqual(expected, actual)

    def test_json_dump_and_compress_returns_base64_string_when_input_is_russian(self):
        data = "привет"
        expected = str(base64.b64encode(json.dumps(data)))
        actual = utility.json_dump_and_compress(data)
        self.assertEqual(expected, actual)

    # is_same_markdown
    def test_is_same_markdown_throws_assertion_error_when_input_is_not_unicode(self):
        s1 = ""
        s2 = ""
        self.assertRaises(AssertionError, utility.is_same_markdown, s1, s2)

    def test_is_same_markdown_returns_true_when_markdown_with_russian_is_same(self):
        s1 = "ещё **один** тест"
        expected = True
        actual = utility.is_same_markdown(s1, s1)
        self.assertEqual(expected, actual)

    # remove_white_space
    def test_remove_white_space_returns_empty_unicode_string_when_input_is_empty_string(self):
        s = ""
        expected = ""
        actual = utility.remove_white_space(s)
        self.assertEqual(expected, actual)

    def test_remove_white_space_throws_assertion_error_when_input_is_not_unicode(self):
        s = ""
        self.assertRaises(AssertionError, utility.remove_white_space, s)

    def test_remove_white_space_returns_unicode_string_when_input_is_russian(self):
        s = "ой ты Пушкин, ой ты сукин сын"
        expected = "ойтыПушкин,ойтысукинсын"
        actual = utility.remove_white_space(s)
        self.assertEqual(expected, actual)

    # put_md_data_in_json_format
    def test_put_md_data_in_json_format_throws_assertion_error_when_md_is_not_unicode(self):
        md1 = ""
        self.assertRaises(AssertionError,
                          utility.markdown_data_to_json,
                          1,
                          True,
                          md1)

    def test_put_md_data_in_json_format_returns_dict_when_md_contain_russian(self):
        md = "один"
        expected = dict(id=1, isconverted=True, md=md, lastmodified="")
        actual = utility.markdown_data_to_json(1, True, md)
        self.assertEqual(expected.get("md"), actual.get("md"))
        self.assertNotIn("html", expected)

    # remove_whitespace_before_abbreviation_definition
    def test_remove_whitespace_before_abbreviation_definition_does_not_make_changes_when_no_leading_whitespace(self):
        s = """The HTML specification
is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium"""
        expected = s
        actual = utility.remove_whitespace_before_abbreviation_definition(s)
        self.assertEqual(expected, actual)

    def test_remove_whitespace_before_abbreviation_definition_throws_assertion_error_when_input_is_not_unicode(self):
        s = "text"
        self.assertRaises(AssertionError, utility.remove_whitespace_before_abbreviation_definition, s)

    def test_remove_whitespace_before_abbreviation_definition_returns_same_if_input_is_empty_string(self):
        s = ""
        expected = ""
        self.assertEqual(s, expected)

    def test_remove_whitespace_before_abbreviation_definition_removes_leading_whitespace_after_newline(self):
        s = "adsfsdfsd\n  \n  *[adsfsdfsd]: PSV!!!\n"
        expected = 'adsfsdfsd\n  \n*[adsfsdfsd]: PSV!!!\n'
        actual = utility.remove_whitespace_before_abbreviation_definition(s)
        self.assertEqual(expected, actual)

    def test_remove_whitespace_before_abbreviation_definition_removes_leading_whitespace_with_multiple_abbreviations(
            self):
        s = "adsfsdfsd and PSV\n  \n  *[adsfsdfsd]: PSV!!!" + \
            "\n  *[PSV]: Philips Sport Vereniging\n"
        expected = "adsfsdfsd and PSV\n  \n*[adsfsdfsd]: PSV!!!" + \
                   "\n*[PSV]: Philips Sport Vereniging\n"
        actual = utility.remove_whitespace_before_abbreviation_definition(s)
        self.assertEqual(expected, actual)

    def test_remove_whitespace_before_abbreviation_definition_does_not_remove_leading_whitespace_when_pattern_does_not_match(
            self):
        s = "adsfsdfsd and PSV\n  \n  [adsfsdfsd]: PSV!!!"
        expected = "adsfsdfsd and PSV\n  \n  [adsfsdfsd]: PSV!!!"
        actual = utility.remove_whitespace_before_abbreviation_definition(s)
        self.assertEqual(expected, actual)

    # remove_leading_whitespace_from_dd_element
    def test_remove_leading_whitespace_from_dd_element_removes_whitespace_when_input_is_valid(self):
        s = "**a**\n    : first letter\n  \n**b**\n    : second letter\n  \n"
        expected = "**a**\n: first letter\n  \n**b**\n: second letter\n  \n"
        actual = utility.remove_leading_whitespace_from_dd_element(s)
        self.assertEqual(expected, actual)

    def test_remove_leading_whitespace_from_dd_element_does_not_remove_whitespace_when_input_contains_three_spaces(
            self):
        s = "**a**\n   : first letter\n  \n**b**\n   : second letter\n  \n"
        expected = "**a**\n   : first letter\n  \n**b**\n   : second letter\n  \n"
        actual = utility.remove_leading_whitespace_from_dd_element(s)
        self.assertEqual(expected, actual)

    def test_remove_leading_whitespace_from_dd_element_does_not_remove_whitespace_when_input_does_not_contain_colons(
            self):
        s = "**a**\n     first letter\n  \n**b**\n     second letter\n  \n"
        expected = "**a**\n     first letter\n  \n**b**\n     second letter\n  \n"
        actual = utility.remove_leading_whitespace_from_dd_element(s)
        self.assertEqual(expected, actual)

    def test_remove_leading_whitespace_from_dd_element_does_not_remove_whitespace_when_input_does_not_contain_space_after_colon(
            self):
        s = "**a**\n    :first letter\n  \n**b**\n    :second letter\n  \n"
        expected = "**a**\n    :first letter\n  \n**b**\n    :second letter\n  \n"
        actual = utility.remove_leading_whitespace_from_dd_element(s)
        self.assertEqual(expected, actual)

    def test_remove_leading_whitespace_from_dd_element_removes_whitespace_from_correct_input_but_does_not_from_incorrect_input_in_same_string(
            self):
        s = "**a**\n    : first letter\n  \n**b**\n    :second letter\n  \n"
        expected = "**a**\n: first letter\n  \n**b**\n    :second letter\n  \n"
        actual = utility.remove_leading_whitespace_from_dd_element(s)
        self.assertEqual(expected, actual)

    def test_remove_leading_whitespace_from_dd_element_inserts_newline_between_two_dd_elements(self):
        s = "**a**\n    : first letter\n**b**\n    :second letter\n  \n"
        expected = "**a**\n: first letter\n\n**b**\n    :second letter\n  \n"
        actual = utility.remove_leading_whitespace_from_dd_element(s, True)
        self.assertEqual(expected, actual)

    # put_colons_in_html_def_list
    def test_put_colons_in_html_def_list_throws_assertion_error_when_input_is_not_unicode(self):
        s = "text"
        self.assertRaises(AssertionError, utility.put_colons_in_html_def_list, s)

    def test_put_colons_in_html_def_list_returns_empty_string_when_input_is_empty_string(self):
        s = ""
        expected = s
        actual = utility.put_colons_in_html_def_list(s)
        self.assertEqual(expected, actual)

    def test_put_colons_in_html_def_list_returns_string_with_colons_when_input_is_correct(self):
        s = '\n<dl>\n<dt align="left"><strong>a</strong></dt>\n' + \
            '<dd align="left">one</dd>\n<dt align="left"><strong>' + \
            'b</strong></dt>\n<dd align="left">two</dd>\n</dl>'
        expected = '\n<dl>\n<dt align="left"><strong>a</strong></dt>\n' + \
                   '<dd align="left">: one</dd>\n<dt align="left"><strong>' + \
                   'b</strong></dt>\n<dd align="left">: two</dd>\n</dl>'
        actual = utility.put_colons_in_html_def_list(s)
        self.assertEqual(expected, actual)

    def test_put_colons_in_html_def_list_returns_string_with_colons_when_input_nodevalue_is_empty(self):
        s = '\n<dl>\n<dt align="left"><strong>a</strong></dt>\n' + \
            '<dd align="left"></dd>\n<dt align="left"><strong>' + \
            'b</strong></dt>\n<dd align="left"></dd>\n</dl>'
        expected = '\n<dl>\n<dt align="left"><strong>a</strong></dt>\n' + \
                   '<dd align="left">: </dd>\n<dt align="left"><strong>' + \
                   'b</strong></dt>\n<dd align="left">: </dd>\n</dl>'
        actual = utility.put_colons_in_html_def_list(s)
        self.assertEqual(expected, actual)

    def test_put_colons_in_html_def_list_should_return_unaltered_string_when_input_does_not_contain_dt(self):
        s = '\n<dl>\n' + \
            '<dd align="left"></dd>\n<dd align="left">text</dd>\n</dl>'
        expected = '\n<dl>\n' + \
                   '<dd align="left"></dd>\n<dd align="left">text</dd>\n</dl>'
        actual = utility.put_colons_in_html_def_list(s)
        self.assertEqual(expected, actual)

    def test_put_colons_in_html_def_list_should_return_colon_after_dt_but_nothing_when_not_dt(self):
        s = '\n<dl>\n' + \
            '<dt></dt><dd align="left"></dd>\n<dd align="left">text</dd>\n</dl>'
        expected = '\n<dl>\n' + \
                   '<dt></dt><dd align="left">: </dd>\n<dd align="left">text</dd>\n</dl>'
        actual = utility.put_colons_in_html_def_list(s)
        self.assertEqual(expected, actual)
