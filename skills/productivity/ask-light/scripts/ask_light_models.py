"""Data models for ask-light with bounded Jev semantic judgments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional


@dataclass
class CompactProjectState:
    """Deterministic compact representation of project evidence."""
    initialized: bool = True
    has_project_contract: bool = True
    current_effort: Optional[str] = None
    active_efforts: List[str] = field(default_factory=list)
    spec_exists: bool = False
    spec_active: bool = False
    spec_paths: List[str] = field(default_factory=list)
    clarification_ready: bool = False
    tickets_exist: bool = False
    ready_tickets: List[str] = field(default_factory=list)
    blocked_tickets: List[str] = field(default_factory=list)
    resolved_tickets: List[str] = field(default_factory=list)
    unknown_tickets: List[str] = field(default_factory=list)
    all_tickets_resolved: bool = False
    review_exists: bool = False
    review_status: Optional[str] = None
    review_verdict: Optional[str] = None
    review_freshness: Optional[str] = None
    working_tree_dirty: bool = False

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompactProjectState:
        valid_keys = {f for f in cls.__annotations__}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class LegalActionsResult:
    """Result of deterministic pre-checks and legal action computation."""
    status: str  # "RECOMMEND", "BLOCKED", "NEED_INPUT", "TERMINAL", "EXPLAIN", "TRANSITION"
    allowed_actions: List[str] = field(default_factory=list)
    target_item: Optional[str] = None
    fail_closed: bool = False
    blocked_reason: Optional[str] = None
    compact_state: Optional[CompactProjectState] = None
    candidate_descriptions: Dict[str, str] = field(default_factory=dict)
    fallback_action: Optional[str] = None
    deterministic_preference: Optional[str] = None
    is_authorized: bool = False

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class JevPolicy:
    """Policy governing Jev uncertainty, query planning, and threshold evaluation."""
    status: str = "provisional"
    source: str = "initial-live-eval"
    version: str = "1.0.0"
    action_choice_min_confidence: float = 0.55
    ambiguity_threshold: float = 0.65
    escalation_threshold: float = 0.60
    execution_intent_threshold: float = 0.80


@dataclass
class SemanticJudgments:
    """Bounded multi-primitive semantic judgments returned by Jev System One."""
    action_choice: Optional[str] = None
    action_confidence: Optional[float] = None
    action_probabilities: Dict[str, float] = field(default_factory=dict)
    execution_intent_probability: Optional[float] = None
    ambiguity_probability: Optional[float] = None
    escalation_probability: Optional[float] = None
    questions_sent: List[str] = field(default_factory=list)
    reason_each_question_needed: Dict[str, str] = field(default_factory=dict)

    # Backwards-compatible properties
    @property
    def wants_immediate_execution_prob(self) -> Optional[float]:
        return self.execution_intent_probability

    @property
    def has_material_ambiguity_prob(self) -> Optional[float]:
        return self.ambiguity_probability

    @property
    def escalation_prob(self) -> Optional[float]:
        return self.escalation_probability

    @property
    def readiness_score(self) -> Optional[float]:
        return None

    @property
    def readiness_confidence(self) -> Optional[float]:
        return None

    def model_dump(self) -> Dict[str, Any]:
        data = asdict(self)
        data["wants_immediate_execution_prob"] = self.execution_intent_probability
        data["has_material_ambiguity_prob"] = self.ambiguity_probability
        data["escalation_prob"] = self.escalation_probability
        return data

    def dict(self) -> Dict[str, Any]:
        return self.model_dump()


@dataclass
class AskLightRecommendation:
    """Final output from ask-light advisor."""
    status: str  # "RECOMMEND", "BLOCKED", "NEED_INPUT", "TERMINAL", "EXPLAIN", "TRANSITION"
    primary_skill: Optional[str] = None
    alternative_skill: Optional[str] = None
    target_item: Optional[str] = None
    confidence: Optional[float] = None
    probabilities: Dict[str, float] = field(default_factory=dict)
    semantic_judgments: Optional[SemanticJudgments] = None
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    escalated: bool = False
    escalation_reason: Optional[str] = None
    fail_closed: bool = False
    justification: str = ""

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return asdict(self)
