"""Modular LLM service for CareerPilot AI.

Provides a unified interface for AI model inference via Ollama.
The service handles:
- Health checks (is Ollama running?)
- Structured JSON generation with Pydantic validation
- Timeout and error handling
- Safe, logged-only prompts (no secret leakage)
"""

import json
import logging
import time
from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "qwen3:4b"

SYSTEM_PROMPT = (
    "You are a professional resume analyst. "
    "You will receive the text of a resume. "
    "Analyze it and respond with valid JSON following this exact schema:\n"
    "{\n"
    '  "candidate_name": string, "professional_summary": string,\n'
    '  "education": string[], "technical_skills": string[],\n'
    '  "soft_skills": string[], "projects": object[],\n'
    '  "internships": object[], "work_experience": object[],\n'
    '  "certifications": string[], "strengths": string[],\n'
    '  "weaknesses": string[], "missing_information": string[],'
    '  "recommended_improvements": string[]\n'
    "}\n"
    "Use only the information present in the resume. "
    "If information is not present, use an empty array or null. "
    "Do not invent qualifications. Do not include any text other than the JSON object."
)


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""


class OllamaUnavailableError(LLMServiceError):
    """Ollama service is unreachable."""


class LLMService:
    """Service for interacting with Ollama or any compatible LLM API."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout_seconds: int = 120,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout_seconds = timeout_seconds
        self._client = http_client

        self._chat_url = f"{self.base_url.rstrip('/')}/api/chat"

    async def health_check(self) -> bool:
        """Check whether Ollama is reachable and responds."""
        try:
            async with self._get_client() as client:
                response = await client.get(
                    f"{self.base_url.rstrip('/')}/api/tags",
                    timeout=5.0,
                )
                return response.status_code == 200
        except httpx.TimeoutException:
            logger.warning(
                "Ollama health check timed out", extra={"model": self.model}
            )
            return False
        except Exception as exc:
            logger.warning(
                "Ollama health check failed", extra={"error": str(exc)}
            )
            return False

    async def generate_json(
        self,
        resume_text: str,
        schema: type[BaseModel] | None = None,
    ) -> BaseModel:
        """Send resume text to Ollama and return a validated Pydantic result.

        Args:
            resume_text: The extracted resume text.
            schema: Pydantic model to validate against.

        Returns:
            Validated Pydantic model with parsed fields.

        Raises:
            OllamaUnavailableError: If Ollama cannot be reached.
            LLMServiceError: For other LLM-related failures.
        """
        start_time = time.monotonic()
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze this resume text:\n\n{resume_text[:30000]}",
                },
            ],
            "format": "json",
        }

        try:
            async with self._get_client() as client:
                response = await client.post(
                    self._chat_url,
                    json=payload,
                    timeout=self.timeout_seconds,
                )

                if response.status_code != 200:
                    error_body = response.text
                    raise OllamaUnavailableError(
                        f"Ollama returned HTTP {response.status_code}: {error_body}"
                    )

                result = response.json()

            content = result.get("message", {}).get("content", "")
            logger.info(
                "LLM completion received",
                extra={
                    "model": self.model,
                    "content_char_count": len(content),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                },
            )

            try:
                data = json.loads(content)
            except json.JSONDecodeError as exc:
                error_detail = (
                    f"Model returned malformed JSON. "
                    f"Start: {content[:500]}"
                )
                logger.error(
                    "LLM returned malformed JSON",
                    extra={"error": str(exc), "start": content[:500]},
                )
                raise LLMServiceError(error_detail) from exc

            return schema(**data)

        except httpx.TimeoutException as exc:
            raise OllamaUnavailableError(
                f"Ollama request timed out after {self.timeout_seconds}s"
            ) from exc
        except OllamaUnavailableError:
            raise
        except Exception as exc:
            raise LLMServiceError(f"LLM generation failed: {exc}") from exc

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout_seconds),
            headers={"Content-Type": "application/json"},
        )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()


# Singleton instance
llm_service = LLMService()
