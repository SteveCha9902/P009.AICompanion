import re
from typing import Tuple

class PrivacyFilterEngine:
    """
    Guarantees privacy safety by strictly blocking sensitive domains:
    - Health / Medical diagnoses
    - Financial / Bank / Credit card / Crypto
    - Political beliefs
    - Religious affiliations
    - Passwords / Tokens / Credentials
    """

    SENSITIVE_PATTERNS = [
        # Financial
        r"(계좌번호|비밀번호|주민번호|카드번호|신용카드|통장|비트코인|암호화폐|잔고|원\s*송금)",
        r"\b\d{3,4}-\d{2,4}-\d{4,6}\b",
        # Health / Medical
        r"(처방전|우울증약|진료기록|진단서|혈압약|당뇨약|정신과\s*치료|수술\s*기록|약\s*먹었어)",
        # Political / Religious
        r"(정당|선거|투표|지지|후보|정치적|종교|교리|신앙)",
        # Credentials

        r"(password|passwd|api_key|token|인증번호|otp|보안카드)",
    ]

    @classmethod
    def is_safe_to_store(cls, content: str) -> Tuple[bool, str]:
        """
        Returns (is_safe, reason)
        """
        for pat in cls.SENSITIVE_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                return (False, f"Blocked sensitive pattern matching: {pat}")
        return (True, "Passed privacy safety check")
