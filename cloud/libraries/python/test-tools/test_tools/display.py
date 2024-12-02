import json
import os
from difflib import _mdiff

from icdiff import ConsoleDiff
from prettytable import DOUBLE_BORDER, PrettyTable


class CoolConsoleDiff(ConsoleDiff):
    # pylint: disable=too-many-arguments
    def make_table(
        self,
        fromlines,
        tolines,
        fromdesc="",
        todesc="",
        fromperms=None,
        toperms=None,
        context=False,
        numlines=5,
    ):
        context_lines = numlines or None

        fromlines, tolines = self._tab_newline_replace(fromlines, tolines)

        if self.strip_trailing_cr or (self._all_cr_nl(fromlines) and self._all_cr_nl(tolines)):
            fromlines = self._strip_trailing_cr(fromlines)
            tolines = self._strip_trailing_cr(tolines)

        diffs = _mdiff(
            fromlines,
            tolines,
            context_lines,
            linejunk=self._linejunk,
            charjunk=self._charjunk,
        )

        if self._wrapcolumn:
            diffs = self._line_wrapper(diffs)
        diffs = self._collect_lines(diffs)

        for left, right in self._generate_table(fromdesc, todesc, fromperms, toperms, diffs):
            yield (
                self.colorize(self._lpad(left, self.cols // 2 - 1)),
                self.colorize(self._lpad(right, self.cols // 2 - 1)),
            )


def dict_diff(actual_payload, expected_payload, padding=15, sort_keys=True):
    """Prints a table with actual an expected payloads."""

    try:
        terminal_height, _ = os.get_terminal_size()
    except OSError:
        terminal_height = 150

    actual_json = json.dumps(actual_payload, indent=4, sort_keys=sort_keys, default=str).splitlines(
        keepends=True
    )
    expected_json = json.dumps(
        expected_payload, indent=4, sort_keys=sort_keys, default=str
    ).splitlines(keepends=True)

    cool_console_diff = CoolConsoleDiff(cols=terminal_height - 1, tabsize=2)

    cool_table = list(
        cool_console_diff.make_table(actual_json, expected_json, "", "", context=False)
    )

    actual = "\n".join([x[0].rstrip(" ") for x in cool_table])
    expected = "\n".join([x[1].rstrip(" ") for x in cool_table])

    table = PrettyTable(
        align="l",
        field_names=["ACTUAL", "EXPECTED"],
        min_table_width=terminal_height - padding,
        max_table_width=terminal_height - padding,
    )
    table.set_style(DOUBLE_BORDER)
    table.add_row([actual, expected])
    return table.get_string()
