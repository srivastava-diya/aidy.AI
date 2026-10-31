"""Safe webpage reader and text extractor with security barriers."""

import requests
from bs4 import BeautifulSoup
from aidy.core.config import settings
from aidy.core.exceptions import WebRetrievalError
from aidy.core.security import validate_and_normalize_url, sanitize_untrusted_content
from aidy.core.logging import logger


USER_AGENT = "aidy.AI-AcademicResearchBot/1.0 (+https://github.com/hcltech/aidy)"
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB


def read_webpage_content(url: str, max_chars: int = 12000) -> str:
    """Fetches, sanitizes, and extracts article text from an external webpage."""
    norm_url = validate_and_normalize_url(url)
    logger.info(f"Retrieving content from: {norm_url}")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        with requests.get(
            norm_url,
            headers=headers,
            timeout=settings.REQUEST_TIMEOUT_S,
            stream=True,
            allow_redirects=True,
        ) as resp:
            resp.raise_for_status()

            # Check content length
            content_length = resp.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                raise WebRetrievalError(f"Target page exceeds safety limit ({content_length} bytes)")

            # Read bounded chunks
            content_bytes = bytearray()
            for chunk in resp.iter_content(chunk_size=32768):
                content_bytes.extend(chunk)
                if len(content_bytes) > MAX_RESPONSE_BYTES:
                    break

            html = content_bytes.decode(resp.encoding or "utf-8", errors="replace")

        # Parse and extract readable body
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "svg"]):
            tag.decompose()

        # Target main content containers if present
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        raw_text = main_content.get_text(separator="\n", strip=True) if main_content else ""

        # Normalize whitespace
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        sanitized, injection_flag = sanitize_untrusted_content(clean_text, max_chars=max_chars)
        if injection_flag:
            logger.warning(f"Sanitization flagged potential injection patterns in {norm_url}")

        return sanitized

    except requests.RequestException as e:
        logger.error(f"Failed to retrieve {norm_url}: {e}")
        raise WebRetrievalError(f"Could not retrieve webpage at {norm_url}: {str(e)}") from e
