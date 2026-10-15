# Copyright © 2026 Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
# Agent Two — Elite Upgrade (Security Gate)
# Source of truth: chichi-lyman/saphira-ai monorepo

from __future__ import annotations
from typing import Any, Dict
import asyncio
import logging
import uuid

logger = logging.getLogger("AgentTwo")

SYSTEM_VOICE = "You are Agent Two — security and policy gate. Protect the user and the system."
CAPABILITIES = ["security.gate", "policy.evaluate", "threat.scan"]
NAME = "agent_two"


class AgentTwo:
    name = NAME
    capabilities = CAPABILITIES
    default_policy = "REQUIRE_APPROVAL"
    SYSTEM_VOICE = SYSTEM_VOICE
    max_timeout_s = 45.0
    max_retries = 2

    def __init__(self, memory_store=None):
        self.memory = memory_store

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        isolation_token = payload.get("isolation_token") or str(uuid.uuid4())
        last_error = None
        for attempt in range(1, self.max_retries + 2):
            try:
                result = await asyncio.wait_for(
                    self.process({**payload, "isolation_token": isolation_token}),
                    timeout=self.max_timeout_s,
                )
                result.setdefault("agent", self.name)
                result.setdefault("isolation_token", isolation_token)
                return result
            except asyncio.TimeoutError:
                last_error = "timeout"
            except Exception as e:
                last_error = str(e)
        return {
            "agent": self.name,
            "status": "recovered_from_failure",
            "error": last_error,
            "isolation_token": isolation_token,
        }

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("intent") or payload.get("objective") or ""
        risk = self._score_risk(str(action), payload)
        if risk >= 0.7 and not payload.get("confirmed"):
            return {
                "status": "blocked",
                "message": "This action needs your confirmation first.",
                "risk_score": risk,
                "requires": "user_confirmation",
            }
        return {
            "status": "success",
            "decision": "clear",
            "risk_score": risk,
            "message": "Security clear.",
            "voice_lock": True,
        }

    def _score_risk(self, action: str, payload: Dict[str, Any]) -> float:
        a = action.lower()
        if any(w in a for w in ("delete", "purchase", "send", "transfer", "unlock")):
            return 0.85
        if payload.get("sensitivity") == "confidential":
            return 0.6
        return 0.15
