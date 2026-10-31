"""Security, URL validation, SSRF defense, and prompt-injection sanitization."""

import re
import ipaddress
import urllib.parse
from typing import Tuple
from aidy.core.exceptions import SecurityViolationError


# Private and reserved IP blocks for SSRF prevention
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local & cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# Prompt injection heuristics in retrieved untrusted text
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(in\s+)?(dan|jailbreak|developer)\s+mode", re.IGNORECASE),
    re.compile(r"disregard\s+all\s+system\s+prompts", re.IGNORECASE),
    re.compile(r"<\|im_start\|>system", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"delete\s+all\s+files", re.IGNORECASE),
]


def validate_and_normalize_url(raw_url: str) -> str:
    """Validates URL format and guards against Server-Side Request Forgery (SSRF)."""
    if not raw_url or not isinstance(raw_url, str):
        raise SecurityViolationError("URL cannot be empty or non-string")

    parsed = urllib.parse.urlparse(raw_url.strip())
    if parsed.scheme not in ("http", "https"):
        raise SecurityViolationError(f"Disallowed URL scheme '{parsed.scheme}'. Only http and https permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SecurityViolationError("Missing hostname in target URL.")

    # Guard against localhost and literal local domains
    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "instance-data"):
        raise SecurityViolationError(f"Access to local host '{hostname}' is blocked for security.")

    # Check if host resolves to private IP block
    try:
        ip = ipaddress.ip_address(hostname)
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                raise SecurityViolationError(f"Access to private IP space '{ip}' is blocked for security.")
    except ValueError:
        # Hostname is a domain name, not a raw IP address; safe to proceed with standard DNS
        pass

    # Normalize: strip trailing slash, fragments
    normalized = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path.rstrip("/"),
        parsed.params,
        parsed.query,
        ""  # strip fragment
    ))
    return normalized


def sanitize_untrusted_content(text: str, max_chars: int = 15000) -> Tuple[str, bool]:
    """Sanitizes scraped external text, delimiting it as untrusted evidence and defusing prompt-injection attempts."""
    if not text:
        return "", False

    injection_detected = False
    cleaned_lines = []

    for line in text.splitlines():
        flagged = False
        for pat in PROMPT_INJECTION_PATTERNS:
            if pat.search(line):
                flagged = True
                injection_detected = True
                break
        if flagged:
            cleaned_lines.append("[POTENTIAL PROMPT INJECTION PATTERN REDACTED FOR SAFETY]")
        else:
            cleaned_lines.append(line)

    sanitized = "\n".join(cleaned_lines)[:max_chars]

    # Wrap in explicit untrusted data block
    wrapped = (
        "=== BEGIN UNTRUSTED RETRIEVED SOURCE CONTENT ===\n"
        f"{sanitized}\n"
        "=== END UNTRUSTED RETRIEVED SOURCE CONTENT ==="
    )
    return wrapped, injection_detected
