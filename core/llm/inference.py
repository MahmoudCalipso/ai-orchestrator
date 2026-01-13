"""
CORE LLM INFERENCE ENGINE
Handles all LLM interactions for the Universal AI Agent
"""
import logging
from typing import List
from openai import OpenAI
import os

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMInference:
    """
    LLM Inference Engine
    Supports multiple LLM providers:
    - Ollama (Local, Free, Recommended)
    - Anthropic (Claude)
    - OpenAI (GPT-4, GPT-3.5) - Paid
    - Azure OpenAI - Paid
    """
    
    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        """
        Initialize LLM Inference Engine
        
        Args:
            provider: LLM provider (ollama, anthropic, openai, azure)
            model: Model name
            api_key: API key (not needed for ollama)
        """
        # Default to Ollama (local, free, no API key needed)
        self.provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        
        # Set default models based on provider
        if self.provider == "ollama":
            self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        elif self.provider == "openai":
            self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "azure":
            self.model = model or os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
            self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY")
        else:
            self.model = model or "qwen2.5-coder:7b"
        
        # Initialize client based on provider
        if self.provider == "ollama":
            # Ollama uses OpenAI-compatible API
            self.client = OpenAI(
                base_url=f"{self.base_url}/v1",
                api_key="ollama"  # Ollama doesn't need real API key
            )
            logger.info(f"✓ Ollama initialized - Model: {self.model} (Local, No API key needed)")
        elif self.provider == "openai":
            if not self.api_key:
                logger.warning("⚠ OpenAI API key not found, using mock mode")
                self.client = None
            else:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"✓ OpenAI initialized - Model: {self.model}")
        elif self.provider == "anthropic":
            if not self.api_key or not ANTHROPIC_AVAILABLE:
                logger.warning("⚠ Anthropic API key not found or package not installed, using mock mode")
                self.client = None
            else:
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"✓ Anthropic initialized - Model: {self.model}")
        else:
            logger.warning(f"⚠ Unknown provider: {self.provider}, using mock mode")
            self.client = None
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
        model: str = None
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 - 1.0)
            system_prompt: System prompt for context
            model: Optional model override (uses self.model if not provided)
        
        Returns:
            Generated text response
        """
        
        # Use provided model or fall back to instance model
        target_model = model or self.model
        
        if self.client is None:
            # Mock mode for testing
            return self._mock_generate(prompt)
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            if self.provider in ["openai", "ollama"]:
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                # Anthropic API call
                response = self.client.messages.create(
                    model=target_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._mock_generate(prompt)
    
    def _mock_generate(self, prompt: str) -> str:
        """Mock generation for testing without API keys"""
        return f"""## Analysis
This is a mock response for testing purposes.
The actual LLM would analyze: {prompt[:100]}...

## Solution
```python
# Mock code solution
def example_function():
    '''Generated by Universal AI Agent'''
    return "This is a placeholder"
```

## Explanation
This is a mock response. To use real LLM capabilities:
1. Set OPENAI_API_KEY environment variable
2. Or configure another LLM provider

## Best Practices Applied
- Mock best practices
- Placeholder implementation

## Additional Recommendations
- Configure real LLM provider for production use
"""
    
    async def generate_streaming(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
        model: str = None
    ):
        """Generate response with streaming (for real-time output)"""
        
        # Use provided model or fall back to instance model
        target_model = model or self.model
        
        if self.client is None:
            yield self._mock_generate(prompt)
            return
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            if self.provider in ["openai", "ollama"]:
                stream = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )
                
                for chunk in stream:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            elif self.provider == "anthropic":
                with self.client.messages.stream(
                    model=target_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    for text in stream.text_stream:
                        yield text
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield self._mock_generate(prompt)
    
    def set_provider(self, provider: str, model: str = None):
        """Change LLM provider"""
        self.provider = provider
        self.model = model or self._get_default_model()
        self.client = self._initialize_client()
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for current provider"""
        models = {
            "openai": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            "anthropic": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229"
            ],
            "ollama": [
                "qwen2.5-coder:7b",
                "qwen2.5-coder:32b",
                "deepseek-coder:6.7b",
                "deepseek-coder:33b",
                "codellama:7b",
                "codellama:34b",
                "mistral:7b",
                "phi3:3.8b",
                "qwen2.5:14b"
            ]
        }
        return models.get(self.provider, [])
