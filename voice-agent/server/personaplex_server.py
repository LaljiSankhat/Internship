"""
PersonaPlex Voice Agent Server
Uses NVIDIA PersonaPlex-7b-v1 model for real-time voice conversations
"""
import os
import asyncio
import logging
from typing import Optional
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import soundfile as sf
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonaPlexAgent:
    """Voice agent using PersonaPlex model"""
    
    def __init__(
        self,
        model_name: str = "nvidia/personaplex-7b-v1",
        hf_token: Optional[str] = None,
        device: Optional[str] = None,
        cpu_offload: bool = False
    ):
        """
        Initialize PersonaPlex agent
        
        Args:
            model_name: HuggingFace model identifier
            hf_token: HuggingFace authentication token
            device: Device to run on ('cuda', 'cpu', or None for auto)
            cpu_offload: Whether to offload to CPU if GPU memory insufficient
        """
        self.model_name = model_name
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.cpu_offload = cpu_offload
        
        if not self.hf_token:
            logger.warning("HF_TOKEN not set. Make sure to accept the model license at:")
            logger.warning("https://huggingface.co/nvidia/personaplex-7b-v1")
        
        self.model = None
        self.tokenizer = None
        self.conversation_history = []
        
    def load_model(self):
        """Load the PersonaPlex model"""
        try:
            logger.info(f"Loading model {self.model_name} on {self.device}...")
            
            # Set HuggingFace token
            if self.hf_token:
                os.environ["HF_TOKEN"] = self.hf_token
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=self.hf_token,
                trust_remote_code=True
            )
            
            # Load model with appropriate settings
            model_kwargs = {
                "token": self.hf_token,
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
            }
            
            if self.cpu_offload:
                from accelerate import init_empty_weights, load_checkpoint_and_dispatch
                model_kwargs["device_map"] = "auto"
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            if not self.cpu_offload:
                self.model = self.model.to(self.device)
            
            self.model.eval()
            logger.info("Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def set_persona(
        self,
        text_prompt: str = "You are a wise and friendly assistant. Answer questions or provide advice in a clear and engaging way.",
        voice_prompt_path: Optional[str] = None
    ):
        """
        Set the persona for the agent
        
        Args:
            text_prompt: Text description of the persona/role
            voice_prompt_path: Path to audio file for voice conditioning (optional)
        """
        self.text_prompt = text_prompt
        self.voice_prompt_path = voice_prompt_path
        logger.info(f"Persona set: {text_prompt[:50]}...")
    
    async def process_audio_stream(
        self,
        audio_stream: bytes,
        sample_rate: int = 24000
    ) -> tuple[bytes, str]:
        """
        Process incoming audio stream and generate response
        
        Args:
            audio_stream: Raw audio bytes
            sample_rate: Audio sample rate (24kHz for PersonaPlex)
            
        Returns:
            Tuple of (response_audio_bytes, response_text)
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_stream, dtype=np.float32)
            
            # Process with PersonaPlex model
            # Note: This is a simplified version. Full implementation would use
            # the Moshi server API or direct model inference
            with torch.no_grad():
                # Tokenize audio and text
                # The actual implementation depends on PersonaPlex's API
                # For now, we'll use a placeholder that shows the structure
                
                # In production, you would:
                # 1. Encode audio to tokens
                # 2. Generate response tokens (text + audio)
                # 3. Decode audio tokens to waveform
                # 4. Return both text and audio
                
                response_text = "I received your audio message."
                response_audio = audio_array  # Placeholder
                
            return response_audio.tobytes(), response_text
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise
    
    async def process_text(self, text: str) -> tuple[bytes, str]:
        """
        Process text input and generate voice response
        
        Args:
            text: Input text message
            
        Returns:
            Tuple of (response_audio_bytes, response_text)
        """
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": text})
            
            # Generate response using the model
            prompt = self.text_prompt + "\n\nConversation:\n"
            for msg in self.conversation_history[-5:]:  # Last 5 messages
                prompt += f"{msg['role']}: {msg['content']}\n"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Generate audio from text (simplified - would use TTS in production)
            # For PersonaPlex, audio generation is integrated
            response_audio = np.zeros(24000, dtype=np.float32)  # Placeholder
            
            return response_audio.tobytes(), response_text
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation reset")
