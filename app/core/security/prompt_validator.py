"""Defense-in-depth security validator for prompt engineering."""
import re
import math
import logging
from typing import List, Tuple, Dict, Any
from fastapi import HTTPException
import tiktoken

logger = logging.getLogger(__name__)

class PromptSecurityValidator:
    """Military-grade validator for LLM inputs with entropy analysis."""
    
    # Required by V2.0 Spec
    INJECTION_PATTERNS = [
        r"(?i)(ignore|disregard|forget).*(previous|instruction)",
        r"(?i)(system|developer).*(prompt|instruction)",
        r"(\{\{|\}\}|<\{|</s>|###\s*System)",
        r"(?i)(DAN|jailbreak|developer mode|sudo)",
    ]
    
    # Extended patterns for PII and advanced attacks
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b"
    }

    def __init__(self, max_tokens: int = 2000):
        try:
            self.enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback if internet is down/cache missing
            self.enc = None
            logger.warning("Tiktoken encoding failed to initialize, using length estimates.")
        self.max_tokens = max_tokens
        
    def validate(self, text: str, user_id: str = "unknown") -> tuple[bool, dict]:
        """Analyzes text for injection, PII, and obfuscation."""
        violations = []
        
        # 1. Token bomb protection (Hard Required)
        token_count = self._get_token_count(text)
        if token_count > self.max_tokens:
            logger.warning(f"Security Violation: Token bomb detected from user {user_id} ({token_count} tokens)")
            return False, {"violations": ["payload_too_large"], "token_count": token_count}
        
        # 2. Pattern matching (Hard Required)
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text):
                violations.append("prompt_injection")
                break # One hit is enough
        
        # 3. Entropy analysis (Hard Required - detects base64/hex obfuscation)
        entropy = self._shannon_entropy(text)
        # Spec: entropy > 6.0 and len > 100
        if entropy > 6.0 and len(text) > 100:
            violations.append("high_entropy_obfuscation")
            
        # 4. PII Detection (Bonus requirement from PII regex spec)
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, text):
                violations.append(f"pii_detected_{pii_type}")
        
        is_safe = len(violations) == 0
        if not is_safe:
            logger.warning(f"Security violations detected for user {user_id}: {violations}")
            
        return is_safe, {
            "violations": violations, 
            "entropy": round(entropy, 2),
            "token_count": token_count
        }

    def _get_token_count(self, text: str) -> int:
        if self.enc:
            return len(self.enc.encode(text))
        return len(text) // 4 # Rough approximation

    def _shannon_entropy(self, data: str) -> float:
        """Calculates Shannon Entropy to detect obfuscation."""
        if not data:
            return 0.0
        entropy = 0
        probs = [data.count(c) / len(data) for c in set(data)]
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

# Global singleton
security_validator = PromptSecurityValidator()
