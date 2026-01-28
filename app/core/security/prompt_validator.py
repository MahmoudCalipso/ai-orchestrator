"""Multi-layer prompt injection defense."""
import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    SAFE = "safe"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    is_safe: bool
    risk_level: RiskLevel
    risk_score: float
    detected_patterns: List[str]
    sanitized: str

class PromptValidator:
    """Detects and mitigates prompt injection attacks."""
    
    # Patterns to detect (Regex, Name, Risk Score)
    ATTACK_PATTERNS: List[Tuple[str, str, float]] = [
        (r"ignore\s+(?:all\s+)?previous\s+instruction", "instruction_override", 0.9),
        (r"you\s+are\s+(?:now\s+)?DAN", "dan_jailbreak", 0.95),
        (r"<\|im_start\|>\s*system", "chatml_injection", 0.95),
        (r"\{\{system\}\}", "template_injection", 0.85),
        (r"developer\s+mode\s*:\s*enabled", "developer_mode", 0.9),
        (r"(?:stop|end)\s+(?:all\s+)?previous\s+rules", "rule_termination", 0.8),
    ]
    
    # Suspicious unicode characters often used for obfuscation
    SUSPICIOUS_UNICODE: List[Tuple[str, str]] = [
        ("\u200B", "zero_width_space"),
        ("\u200C", "zero_width_non_joiner"),
        ("\u200D", "zero_width_joiner"),
        ("\u202E", "right_to_left_override"),
    ]
    
    def validate(self, prompt: str) -> ValidationResult:
        """Analyzes a prompt for potential injection risks."""
        score = 0.0
        patterns = []
        
        # Check against regex patterns
        for pattern, name, s in self.ATTACK_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += s
                patterns.append(name)
        
        # Check for suspicious unicode
        for char, name in self.SUSPICIOUS_UNICODE:
            if char in prompt:
                score += 0.3
                patterns.append(name)
        
        # Sanitize the prompt (simple character replacement for now)
        sanitized = self._sanitize(prompt)
        
        # Determine risk level
        if score >= 0.9:
            level = RiskLevel.CRITICAL
            safe = False
        elif score >= 0.7:
            level = RiskLevel.HIGH
            safe = False
        else:
            level = RiskLevel.SAFE
            safe = True
            
        if not safe:
            logger.warning(f"Malicious prompt detected: risk_level={level.value}, score={score}, patterns={patterns}")
        
        return ValidationResult(
            is_safe=safe,
            risk_level=level,
            risk_score=min(score, 1.0),
            detected_patterns=patterns,
            sanitized=sanitized
        )
    
    def _sanitize(self, prompt: str) -> str:
        """Removes suspicious unicode characters."""
        for char, _ in self.SUSPICIOUS_UNICODE:
            prompt = prompt.replace(char, "")
        return prompt

validator = PromptValidator()
