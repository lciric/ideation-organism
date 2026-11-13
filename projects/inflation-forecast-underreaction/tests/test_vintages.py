"""Vintage letters: W = March, G = June, S = September, A = December, checked against TITLE_COMPL."""
import pytest

from ifu import vintages as vt


def test_quarter_numbers_from_the_preregistrations():
    assert vt.quarter_number(1999, 1) == 7996
    assert vt.quarter_number(2025, 4) == 8103
    assert vt.vintage_number("W21") == 8084
    assert vt.vintage_number("G21") == 8085 and vt.vintage_number("S21") == 8086
    assert vt.vintage_number("W99") == 7996
    assert vt.quarter_label(8106) == "2026-Q3"


def test_vintage_code_is_the_inverse_of_vintage_number():
    for code in ["W99", "G05", "S21", "A25", "S26"]:
        assert vt.vintage_code(vt.vintage_number(code)) == code


def test_title_parsing():
    assert vt.title_month("... - Spring/June 2025  staff macroeconomic projections") == 6
    assert vt.title_year("... - Spring/June 2025  staff macroeconomic projections") == 2025
    assert vt.title_month("no month here") is None


@pytest.mark.parametrize("code, month", [("W21", 3), ("G21", 6), ("S21", 9), ("A21", 12), ("G25", 6), ("S25", 9),
                                          ("W99", 3), ("A05", 12), ("G12", 6), ("S16", 9)])
def test_letter_matches_month_in_title_compl(code, month):
    """The month written in TITLE_COMPL is 3 x the quarter of the letter, and the first projected
    quarter (status F) is the vintage's own quarter."""
    s = vt.load_quarterly(code)
    info = vt.vintage_info(s)
    assert info["title_month"] == month == 3 * vt.LETTER_QUARTER[code[0]]
    assert info["title_year"] == vt.code_year(code)
    assert info["first_F"] == vt.vintage_number(code)


def test_annual_vintages_title_and_first_year():
    for code in ["A01", "W02", "G10", "S21", "A25"]:
        s = vt.load_annual(code)
        info = vt.vintage_info(s)
        assert info["title_month"] == 3 * vt.LETTER_QUARTER[code[0]]
        assert info["first_F"] == vt.code_year(code)
