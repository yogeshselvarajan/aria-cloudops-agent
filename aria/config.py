from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """All tuneable knobs for ARIA in one place."""

    host: str = "http://localhost:11434"
    model_id: str = "phi3.5"
    temperature: float = 0.3       # Low: consistency > creativity for deterministic triage reasoning
    context_window: int = 4096
    keep_alive: str = "30m"        # Prevent cold-reload (122s on CPU) mid-session; 5m default is too short for war rooms
    window_size: int = 20          # ~10 back-and-forth turns; enough for a full triage without exceeding context
    agent_name: str = "ARIA"
    agent_description: str = "Privacy-first CloudOps triage agent"


DEFAULT_CONFIG = AgentConfig()
