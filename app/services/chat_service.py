"""
Day 4 - Chat orchestration service.

Responsibilities:
- Query retrieval
- Context assembly
- Conversation history limiting
- Prompt construction
- Provider selection
- Grounded response generation
- Unknown-query fallback
- Intent/state context
"""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.llm.base import LLMProvider, LLMResponse
from app.llm.gemini_provider import GeminiProvider
from app.llm.claude_provider import ClaudeProvider
from app.prompts.chat_prompts import build_system_prompt
from app.retrieval.context_builder import build_context
from app.retrieval.retriever import RAGRetriever


FALLBACK_RESPONSE = (
    "I don't have enough information to answer that accurately. "
    "I can help with MoinSystems AI's services, technologies, "
    "pricing process, and project-related questions."
)


class ChatService:
    """Orchestrates retrieval and grounded LLM generation."""

    def __init__(
        self,
        db: Session,
        llm_provider: LLMProvider | None = None,
    ) -> None:

        self.settings = get_settings()

        self.retriever = RAGRetriever(db)

        self.llm_provider = (
            llm_provider
            or self._create_provider()
        )

    # =========================================================
    # Provider selection
    # =========================================================

    def _create_provider(self) -> LLMProvider:
        """
        Create the configured LLM provider.

        Supported providers:
        - gemini
        - claude / anthropic
        """

        provider = (
            self.settings.LLM_PROVIDER
            .strip()
            .lower()
        )

        # -----------------------------------------------------
        # Google Gemini
        # -----------------------------------------------------

        if provider == "gemini":
            return GeminiProvider()

        # -----------------------------------------------------
        # Anthropic Claude
        # -----------------------------------------------------

        if provider in {"claude", "anthropic"}:
            return ClaudeProvider()

        raise ValueError(
            "Unsupported LLM_PROVIDER. "
            "Use 'gemini' or 'claude'."
        )

    # =========================================================
    # Conversation preparation
    # =========================================================

    def prepare_messages(
        self,
        messages: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Keep only the most recent valid conversation messages.
        """

        max_history = max(
            1,
            self.settings.RAG_MAX_HISTORY_MESSAGES,
        )

        cleaned_messages: list[dict[str, str]] = []

        for message in messages[-max_history:]:

            role = message.get("role")
            content = message.get("content")

            if role not in {"user", "assistant"}:
                continue

            if not content:
                continue

            cleaned_messages.append(
                {
                    "role": role,
                    "content": content.strip(),
                }
            )

        return cleaned_messages

    # =========================================================
    # Main chat operation
    # =========================================================

    def generate_response(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        intent: str | None = None,
        lead_state: str | None = None,
    ) -> LLMResponse:
        """
        Generate a grounded response.

        Flow:

        User message
            ↓
        Retrieval
            ↓
        Relevance check
            ↓
        RAG context
            ↓
        System prompt
            ↓
        Limited conversation history
            ↓
        Gemini / Claude
            ↓
        Grounded response
        """

        message = message.strip()

        if not message:
            raise ValueError(
                "Message cannot be empty."
            )

        history = history or []

        # =====================================================
        # Retrieval
        # =====================================================

        retrieval_query = self._prepare_retrieval_query(
            message,
            history,
        )

        documents = self.retriever.retrieve(
            retrieval_query
        )

        # =====================================================
        # Unknown / low-confidence handling
        # =====================================================

        if not documents:
            return LLMResponse(
                content=FALLBACK_RESPONSE,
                model="none",
                provider="fallback",
            )

        # =====================================================
        # Context assembly
        # =====================================================

        context = build_context(
            documents[
                : self.settings.RAG_MAX_CONTEXT_RESULTS
            ]
        )

        # =====================================================
        # System prompt
        # =====================================================

        system_prompt = build_system_prompt(
            context
        )

        # =====================================================
        # Conversation history
        # =====================================================

        conversation = self.prepare_messages(
            history
        )

        conversation.append(
            {
                "role": "user",
                "content": message,
            }
        )

        # =====================================================
        # Intent / lead state context
        # =====================================================

        if intent or lead_state:

            state_parts: list[str] = []

            if intent:
                state_parts.append(
                    f"Current intent: {intent}"
                )

            if lead_state:
                state_parts.append(
                    f"Lead state: {lead_state}"
                )

            conversation.insert(
                0,
                {
                    "role": "user",
                    "content": (
                        "Application state for this conversation:\n"
                        + "\n".join(state_parts)
                    ),
                },
            )

        # =====================================================
        # LLM generation
        # =====================================================

        return self.llm_provider.generate(
            system_prompt=system_prompt,
            messages=conversation,
        )

    # =========================================================
    # Retrieval query preparation
    # =========================================================

    @staticmethod
    def _prepare_retrieval_query(
        message: str,
        history: list[dict[str, str]],
    ) -> str:
        """
        Include limited recent conversation context only when
        the current message contains a conversational reference.

        Example:

        User:
            Does MoinSystems build websites?

        User:
            What about mobile apps?

        The second query can be enriched using recent context.
        """

        reference_terms = {
            "that",
            "those",
            "it",
            "this",
            "they",
            "them",
            "same",
            "previous",
            "above",
        }

        message_tokens = {
            token.lower()
            for token in message.split()
        }

        needs_context = bool(
            message_tokens.intersection(
                reference_terms
            )
        )

        # No conversational reference.
        if not needs_context or not history:
            return message

        # Use only the most recent two messages for retrieval
        # continuity.
        recent = history[-2:]

        context_parts: list[str] = []

        for item in recent:

            role = item.get("role")
            content = item.get("content")

            if (
                role in {"user", "assistant"}
                and content
            ):
                context_parts.append(
                    content.strip()
                )

        context_parts.append(message)

        return " ".join(context_parts)