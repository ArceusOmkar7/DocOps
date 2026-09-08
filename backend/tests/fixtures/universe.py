"""
Fictional Universe Constants for Synthetic Document Generation.
All entities, GSTINs, PANs, bank accounts, and addresses are fictional but
strictly format-valid according to Indian tax, banking, and statutory norms.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CompanyEntity:
    name: str
    trade_name: str
    pan: str
    gstin: str
    state: str
    state_code: str
    address: str
    phone: str
    email: str
    bank_name: str
    account_number: str
    ifsc: str
    branch: str
    logo_color: Tuple[float, float, float]  # RGB normalized 0-1 for reportlab
    logo_initials: str


@dataclass(frozen=True)
class IndividualEntity:
    name: str
    pan: str
    aadhaar_masked: str
    address: str
    designation: str
    employer_name: str
    employer_tan: str
    employer_pan: str
    ppf_account_no: str
    lic_policy_no: str


# --- Corporate Entities ---

RAJPUT_STEELWORKS = CompanyEntity(
    name="Rajput Steelworks Private Limited",
    trade_name="Rajput Steelworks",
    pan="AABCR5678Q",
    gstin="24AABCR5678Q1ZP",
    state="Gujarat",
    state_code="24",
    address="Plot 12, GIDC Industrial Estate, Vatva, Ahmedabad, Gujarat 382445",
    phone="+91 79 2583 4400",
    email="accounts@rajputsteelworks.in",
    bank_name="State Bank of India",
    account_number="10987654321",
    ifsc="SBIN0003456",
    branch="Vatva Industrial Estate Branch",
    logo_color=(0.27, 0.51, 0.71),  # Steel Blue
    logo_initials="RS",
)

KAPOOR_SHAH = CompanyEntity(
    name="Kapoor & Shah Associates",
    trade_name="Kapoor & Shah Chartered Accountants",
    pan="AABFK9234P",
    gstin="27AABFK9234P1ZR",
    state="Maharashtra",
    state_code="27",
    address="Suite 402, Express Towers, Nariman Point, Mumbai, Maharashtra 400021",
    phone="+91 22 6650 9100",
    email="admin@kapoorshah.com",
    bank_name="HDFC Bank",
    account_number="50200011223344",
    ifsc="HDFC0002567",
    branch="Nariman Point Branch",
    logo_color=(0.0, 0.50, 0.50),  # Teal
    logo_initials="K&S",
)

CODEIFY_TECH = CompanyEntity(
    name="Codeify Technologies LLP",
    trade_name="Codeify Technologies",
    pan="AAGFC4321N",
    gstin="27AAGFC4321N1ZT",
    state="Maharashtra",
    state_code="27",
    address="Tower B, 5th Floor, Cyber City, Magarpatta, Pune, Maharashtra 411028",
    phone="+91 20 6712 3000",
    email="finance@codeifytech.io",
    bank_name="Axis Bank",
    account_number="9876501234",
    ifsc="UTIB0001234",
    branch="Magarpatta City Branch",
    logo_color=(0.37, 0.15, 0.45),  # Deep Purple
    logo_initials="CT",
)

# --- Individual Entity ---

ARJUN_KHANNA = IndividualEntity(
    name="Arjun Khanna",
    pan="AKQPK7890G",
    aadhaar_masked="XXXX-XXXX-2345",
    address="Flat 304, Green Meadows, Pancard Club Road, Baner, Pune, Maharashtra 411045",
    designation="Senior Software Architect",
    employer_name="Codeify Technologies LLP",
    employer_tan="PNEC12345D",
    employer_pan="AAGFC4321N",
    ppf_account_no="30123456789",
    lic_policy_no="894561230",
)
