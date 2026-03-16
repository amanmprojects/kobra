from __future__ import annotations

import math
import re
from collections import Counter
from urllib.parse import urlparse


SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club"}
BRAND_KEYWORDS = [
    "paypal",
    "google",
    "facebook",
    "amazon",
    "microsoft",
    "apple",
    "netflix",
    "instagram",
    "linkedin",
]

FEATURE_ORDER = [
    "url_length",
    "n_subdomains",
    "has_ip_address",
    "special_char_count",
    "entropy",
    "suspicious_tld",
    "brand_mimic_score",
    "is_https",
    "redirect_count",
    "domain_age_days",
]


def extract_features(url: str) -> dict[str, float]:
    parsed = urlparse(url.strip())
    hostname = (parsed.hostname or "").lower()
    full = url.strip().lower()
    return {
        "url_length": float(len(url)),
        "n_subdomains": float(max(len([part for part in hostname.split(".") if part]) - 2, 0)),
        "has_ip_address": float(bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", hostname))),
        "special_char_count": float(sum(full.count(char) for char in ["@", "-", "%", "=", "_"])),
        "entropy": float(_entropy(full)),
        "suspicious_tld": float(any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS)),
        "brand_mimic_score": float(_brand_mimic(hostname)),
        "is_https": float(parsed.scheme == "https"),
        "redirect_count": float(max(full.count("http") - 1, 0)),
        "domain_age_days": -1.0,
    }


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    total = len(value)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _brand_mimic(hostname: str) -> int:
    normalized = hostname
    replacements = {"0": "o", "1": "i", "3": "e", "4": "a", "5": "s"}
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    for brand in BRAND_KEYWORDS:
        if brand in normalized and brand not in hostname:
            return 1
    return 0

