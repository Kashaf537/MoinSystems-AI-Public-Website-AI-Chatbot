"""
Day 5 - Lightweight deterministic intent routing.
"""

import re


class IntentService:
    """
    Classifies visitor messages into a small set of stable
    application-level intents.

    The LLM does NOT control this state.
    """

    PRICING_PATTERNS = [
        r"\bprice\b",
        r"\bpricing\b",
        r"\bcost\b",
        r"\bhow much\b",
        r"\bquote\b",
        r"\bquotation\b",
        r"\bbudget\b",
        r"\brate\b",
        r"\bcharges?\b",
        r"\bfee\b",
    ]

    SERVICE_PATTERNS = [
        r"\bservice\b",
        r"\bservices\b",
        r"\bwebsite\b",
        r"\bweb development\b",
        r"\bmobile app\b",
        r"\bmobile application\b",
        r"\be-commerce\b",
        r"\becommerce\b",
        r"\bsoftware development\b",
        r"\bAI development\b",
        r"\bchatbot\b",
        r"\bAPI\b",
    ]

    HIGH_INTENT_PATTERNS = [
        r"\bi want to start\b",
        r"\bi want to build\b",
        r"\bneed a quote\b",
        r"\bneed a proposal\b",
        r"\bhire\b",
        r"\bwork with you\b",
        r"\bget started\b",
        r"\bstart a project\b",
        r"\bmy project\b",
    ]

    @classmethod
    def classify(cls, message: str) -> str:

        text = message.lower().strip()

        if not text:
            return "fallback"

        if cls._matches(
            text,
            cls.PRICING_PATTERNS,
        ):
            return "pricing"

        if cls._matches(
            text,
            cls.HIGH_INTENT_PATTERNS,
        ):
            return "high_intent"

        if cls._matches(
            text,
            cls.SERVICE_PATTERNS,
        ):
            return "service"

        return "normal"

    @staticmethod
    def _matches(
        text: str,
        patterns: list[str],
    ) -> bool:

        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        )