"""
Data Transformation Functions
Handles date parsing, numeric extraction, and text cleaning for BoE data
"""

import re
from datetime import datetime, date
from typing import Optional, Union


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """
    Parse date from various formats used in BoE documents

    Supported formats:
    - DD/MM/YYYY (e.g., 15/04/2022)
    - DD-MM-YYYY (e.g., 15-04-2022)
    - DD-MMM-YY (e.g., 30-MAR-22)
    - DD-MMM-YYYY (e.g., 30-MAR-2022)
    - YYYY-MM-DD (ISO format)
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()

    # Common date formats in BoE documents
    formats = [
        "%d/%m/%Y",      # 15/04/2022
        "%d-%m-%Y",      # 15-04-2022
        "%d-%b-%y",      # 30-MAR-22
        "%d-%b-%Y",      # 30-MAR-2022
        "%d-%B-%y",      # 30-MARCH-22
        "%d-%B-%Y",      # 30-MARCH-2022
        "%Y-%m-%d",      # 2022-04-15 (ISO)
        "%d.%m.%Y",      # 15.04.2022
        "%d %b %Y",      # 15 Apr 2022
        "%d %B %Y",      # 15 April 2022
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Try to extract date components manually
    # Pattern: DD followed by month followed by YY or YYYY
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    match = re.match(r'(\d{1,2})[-/\s]?([a-zA-Z]{3,9})[-/\s]?(\d{2,4})', date_str)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()[:3]
        year = int(match.group(3))

        if month_str in month_map:
            month = month_map[month_str]
            if year < 100:
                year += 2000 if year < 50 else 1900
            try:
                return date(year, month, day)
            except ValueError:
                pass

    return None


def parse_number(value: Optional[Union[str, int, float]]) -> Optional[float]:
    """
    Parse numeric value from string, handling currency symbols and formatting

    Handles:
    - Currency symbols (Rs., $, etc.)
    - Thousands separators (commas, spaces)
    - Decimal points
    - Negative values (in parentheses or with minus)
    - Empty/null values
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str) or not value.strip():
        return None

    value = value.strip()

    # Remove currency symbols and common prefixes
    # Note: Rs. needs special handling to not remove the period that's part of decimals
    value = re.sub(r'Rs\.?\s*', '', value)  # Remove Rs. or Rs
    value = re.sub(r'[\$\u20b9\u20ac\u00a3]', '', value)  # Remove $, ₹, €, £

    # Check for negative in parentheses: (123.45) -> -123.45
    is_negative = False
    if value.startswith('(') and value.endswith(')'):
        is_negative = True
        value = value[1:-1]
    elif value.startswith('-'):
        is_negative = True
        value = value[1:]

    # Remove thousands separators (commas and spaces)
    value = re.sub(r'[,\s]', '', value)

    # Handle empty or non-numeric
    if not value or value == '-' or value == '.':
        return None

    try:
        result = float(value)
        return -result if is_negative else result
    except ValueError:
        return None


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Clean text by removing OCR artifacts and normalizing whitespace
    """
    if not text or not isinstance(text, str):
        return None

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove common OCR artifacts
    # - Stray punctuation at start/end
    text = re.sub(r'^[.,;:\-_]+|[.,;:\-_]+$', '', text)

    # - Multiple dashes or underscores (often from form fields)
    text = re.sub(r'[-_]{3,}', '', text)

    # - Leading/trailing quotes
    text = text.strip('"\'')

    # Final trim
    text = text.strip()

    return text if text else None


def extract_gstin(text: Optional[str]) -> Optional[str]:
    """
    Extract and validate GSTIN format (15 character alphanumeric)
    Format: 2 digits (state) + 10 chars (PAN) + 1 char + Z + 1 char
    """
    if not text:
        return None

    # GSTIN pattern: 2 digits, 5 chars, 4 digits, 1 char, 1 char, Z, 1 char
    pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}'

    match = re.search(pattern, text.upper())
    if match:
        return match.group(0)

    return clean_text(text)


def extract_iec(text: Optional[str]) -> Optional[str]:
    """
    Extract IEC (Importer Exporter Code) - 10 digit number
    May include branch code suffix (e.g., 0512345678/6)
    """
    if not text:
        return None

    # IEC with optional branch: 10 digits, optionally followed by /digit
    pattern = r'\d{10}(?:/\d+)?'

    match = re.search(pattern, text)
    if match:
        return match.group(0)

    return clean_text(text)


def extract_be_number(text: Optional[str]) -> Optional[str]:
    """
    Extract Bill of Entry number (typically 7-10 digits)
    """
    if not text:
        return None

    # BE number is typically all digits, 7-10 characters
    pattern = r'\d{7,10}'

    match = re.search(pattern, str(text))
    if match:
        return match.group(0)

    return clean_text(str(text))


def extract_port_code(text: Optional[str]) -> Optional[str]:
    """
    Extract Indian port code (format: INXXX# where X is letter, # is digit)
    Example: INDEL4, INBOM6, INCHD8
    """
    if not text:
        return None

    # Indian port code pattern
    pattern = r'IN[A-Z]{3}\d'

    match = re.search(pattern, text.upper())
    if match:
        return match.group(0)

    return clean_text(text)


def normalize_boolean_field(value: Optional[str]) -> Optional[str]:
    """
    Normalize Y/N/Yes/No fields to consistent format
    """
    if not value:
        return None

    value = str(value).strip().upper()

    if value in ('Y', 'YES', 'TRUE', '1'):
        return 'Y'
    elif value in ('N', 'NO', 'FALSE', '0'):
        return 'N'

    return value if value else None


def parse_quantity(value: Optional[Union[str, int, float]], uqc: Optional[str] = None) -> Optional[float]:
    """
    Parse quantity, handling different decimal conventions
    """
    num = parse_number(value)
    if num is None:
        return None

    # Some quantities use different decimal precision
    if uqc and uqc.upper() in ('NOS', 'PCS', 'UNITS', 'SET'):
        # Integer quantities
        return float(int(num))

    return num


def safe_int(value: Optional[Union[str, int, float]]) -> Optional[int]:
    """
    Safely convert to integer
    """
    if value is None:
        return None

    if isinstance(value, int):
        return value

    num = parse_number(value)
    if num is not None:
        return int(num)

    return None
