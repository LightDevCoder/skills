"""Data models for agent-config with abstract task profiling and topology selection."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional


@dataclass
class HostCapabilities:
    """Deterministic host capability evidence."""
    harness: str = "generic"
    has_model_selector: bool = True
    supported_effort: List[str] = field(default_factory=list)
    per_agent_config: bool = False
    active_model: str = "default-model"
    available_models: List[str] = field(default_factory=list)
    companion_status: str = "ready"  # "ready", "missing", "stale"
    profile_status: str = "persisted"  # "persisted", "session-local", "missing"
    profile_tiers: Dict[str, str] = field(default_factory=dict)

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HostCapabilities:
        valid_keys = {f for f in cls.__annotations__}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class TaskCharacteristics:
    """Task description and requirements."""
    title: str = ""
    description: str = ""
    shape: str = "single-pass"  # "single-pass", "decomposed"
    formal_tickets_exist: bool = True
    difficulty: str = "standard"  # "routine", "standard", "high", "critical"
    reasoning_policy: Optional[str] = None  # "highest-supported", "standard", "minimal", etc.
    cost_sensitive: bool = False
    latency_sensitive: bool = False

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskCharacteristics:
        valid_keys = {f for f in cls.__annotations__}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class AbstractTaskProfile:
    """Abstract task profile determined semantically without vendor model names."""
    complexity_level: str = "standard"  # "routine", "standard", "high", "critical"
    reasoning_need: str = "medium"  # "none", "low", "medium", "high"
    latency_sensitivity: str = "medium"  # "low", "medium", "high"
    cost_sensitivity: str = "medium"  # "low", "medium", "high"
    recommended_tier: str = "standard"  # "routine", "standard", "high", "review"

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionConfig:
    """Final resolved execution configuration."""
    model: str
    resolved_effort: Optional[str] = None
    topology: str = "Case A"  # "Case A", "Case B", "Case C", "Case D"
    worker_models: Dict[str, str] = field(default_factory=dict)

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentConfigResult:
    """Canonical AgentConfigResult envelope."""
    readiness: str  # "READY", "NEED_INPUT", "NEED_PROJECT_TICKETS", "BLOCKED", "UNSUPPORTED"
    mode: str = "plan-only"  # "persisted", "session-local", "plan-only"
    setup_state: Dict[str, str] = field(
        default_factory=lambda: {"companion": "ready", "profile": "persisted"}
    )
    handoff: Optional[str] = None
    execution_config: Optional[ExecutionConfig] = None
    justification: str = ""
    abstract_profile: Optional[AbstractTaskProfile] = None
    jev_confidence: Optional[float] = None
    fallback_used: bool = False
    fallback_reason: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)
