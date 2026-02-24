"""Tests for utility functions."""

from app.utils.calculations import success_rate


class TestSuccessRate:
    def test_normal_calculation(self):
        assert success_rate(9, 10) == 90.0

    def test_zero_total(self):
        assert success_rate(0, 0) == 0.0

    def test_all_successful(self):
        assert success_rate(100, 100) == 100.0

    def test_none_successful(self):
        assert success_rate(0, 50) == 0.0

    def test_rounds_to_one_decimal(self):
        assert success_rate(1, 3) == 33.3

    def test_large_numbers(self):
        assert success_rate(999, 1000) == 99.9

    def test_single_value(self):
        assert success_rate(1, 1) == 100.0
