"""
Tests for data transformation functions
"""

import pytest
from datetime import date
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.transformers import (
    parse_date,
    parse_number,
    clean_text,
    extract_gstin,
    extract_iec,
    extract_be_number,
    extract_port_code,
    normalize_boolean_field,
    safe_int,
)


class TestParseDate:
    """Tests for date parsing function"""

    def test_dd_mm_yyyy_slash(self):
        """Test DD/MM/YYYY format"""
        assert parse_date("15/04/2022") == date(2022, 4, 15)

    def test_dd_mm_yyyy_dash(self):
        """Test DD-MM-YYYY format"""
        assert parse_date("15-04-2022") == date(2022, 4, 15)

    def test_dd_mmm_yy(self):
        """Test DD-MMM-YY format (common in BoE)"""
        assert parse_date("30-MAR-22") == date(2022, 3, 30)

    def test_dd_mmm_yyyy(self):
        """Test DD-MMM-YYYY format"""
        assert parse_date("30-MAR-2022") == date(2022, 3, 30)

    def test_iso_format(self):
        """Test YYYY-MM-DD (ISO) format"""
        assert parse_date("2022-04-15") == date(2022, 4, 15)

    def test_empty_string(self):
        """Test empty string returns None"""
        assert parse_date("") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert parse_date(None) is None

    def test_whitespace(self):
        """Test whitespace-only string returns None"""
        assert parse_date("   ") is None

    def test_invalid_date(self):
        """Test invalid date returns None"""
        assert parse_date("invalid") is None


class TestParseNumber:
    """Tests for number parsing function"""

    def test_integer(self):
        """Test integer input"""
        assert parse_number(123) == 123.0

    def test_float(self):
        """Test float input"""
        assert parse_number(123.45) == 123.45

    def test_string_integer(self):
        """Test string integer"""
        assert parse_number("123") == 123.0

    def test_string_float(self):
        """Test string float"""
        assert parse_number("123.45") == 123.45

    def test_thousands_comma(self):
        """Test number with thousands separator"""
        assert parse_number("1,234,567.89") == 1234567.89

    def test_currency_symbol_rs(self):
        """Test Rs. currency prefix"""
        assert parse_number("Rs. 1,234.00") == 1234.0

    def test_negative_parentheses(self):
        """Test negative in parentheses"""
        assert parse_number("(123.45)") == -123.45

    def test_negative_minus(self):
        """Test negative with minus sign"""
        assert parse_number("-123.45") == -123.45

    def test_empty_string(self):
        """Test empty string returns None"""
        assert parse_number("") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert parse_number(None) is None


class TestCleanText:
    """Tests for text cleaning function"""

    def test_trim_whitespace(self):
        """Test whitespace trimming"""
        assert clean_text("  hello world  ") == "hello world"

    def test_normalize_whitespace(self):
        """Test multiple whitespace normalization"""
        assert clean_text("hello    world") == "hello world"

    def test_remove_leading_punctuation(self):
        """Test removing leading punctuation"""
        assert clean_text("...hello") == "hello"

    def test_remove_trailing_punctuation(self):
        """Test removing trailing punctuation"""
        assert clean_text("hello...") == "hello"

    def test_empty_string(self):
        """Test empty string returns None"""
        assert clean_text("") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert clean_text(None) is None


class TestExtractGSTIN:
    """Tests for GSTIN extraction"""

    def test_valid_gstin(self):
        """Test valid GSTIN format"""
        assert extract_gstin("27ABCDE1234F1Z5") == "27ABCDE1234F1Z5"

    def test_gstin_in_text(self):
        """Test extracting GSTIN from text"""
        result = extract_gstin("GSTIN: 27ABCDE1234F1Z5/O")
        assert result == "27ABCDE1234F1Z5"

    def test_empty_input(self):
        """Test empty input returns None"""
        assert extract_gstin("") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert extract_gstin(None) is None


class TestExtractIEC:
    """Tests for IEC extraction"""

    def test_valid_iec(self):
        """Test valid 10-digit IEC"""
        assert extract_iec("0512345678") == "0512345678"

    def test_iec_with_branch(self):
        """Test IEC with branch code"""
        assert extract_iec("0512345678/6") == "0512345678/6"

    def test_iec_in_text(self):
        """Test extracting IEC from text"""
        assert extract_iec("IEC: 0512345678/6") == "0512345678/6"

    def test_empty_input(self):
        """Test empty input returns None"""
        assert extract_iec("") is None


class TestExtractBENumber:
    """Tests for BE number extraction"""

    def test_valid_be_number(self):
        """Test valid BE number"""
        assert extract_be_number("7654321") == "7654321"

    def test_be_number_in_text(self):
        """Test extracting BE number from text"""
        assert extract_be_number("BE No: 7654321") == "7654321"

    def test_empty_input(self):
        """Test empty input returns None"""
        assert extract_be_number("") is None


class TestExtractPortCode:
    """Tests for port code extraction"""

    def test_valid_port_code(self):
        """Test valid Indian port code"""
        assert extract_port_code("INDEL4") == "INDEL4"

    def test_port_code_lowercase(self):
        """Test lowercase port code"""
        assert extract_port_code("indel4") == "INDEL4"

    def test_port_code_in_text(self):
        """Test extracting port code from text"""
        assert extract_port_code("Port: INDEL4") == "INDEL4"

    def test_empty_input(self):
        """Test empty input returns None"""
        assert extract_port_code("") is None


class TestNormalizeBooleanField:
    """Tests for boolean field normalization"""

    def test_y_values(self):
        """Test Y values"""
        assert normalize_boolean_field("Y") == "Y"
        assert normalize_boolean_field("YES") == "Y"
        assert normalize_boolean_field("yes") == "Y"

    def test_n_values(self):
        """Test N values"""
        assert normalize_boolean_field("N") == "N"
        assert normalize_boolean_field("NO") == "N"
        assert normalize_boolean_field("no") == "N"

    def test_empty_input(self):
        """Test empty input returns None"""
        assert normalize_boolean_field("") is None


class TestSafeInt:
    """Tests for safe integer conversion"""

    def test_integer(self):
        """Test integer input"""
        assert safe_int(123) == 123

    def test_float(self):
        """Test float truncation"""
        assert safe_int(123.9) == 123

    def test_string_integer(self):
        """Test string integer"""
        assert safe_int("123") == 123

    def test_empty_string(self):
        """Test empty string returns None"""
        assert safe_int("") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert safe_int(None) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
