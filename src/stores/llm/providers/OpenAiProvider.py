from ..LLMInterface import LLMInterface
from ..LLMEnums import OPENAIEnums
from openai import OpenAI
import logging


class OpenAiProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        api_url: str = None,
        default_max_input_characters: int = 1000,
        default_max_output_tokens: int = 1000,
        default_temperature: float = 0.1,
    ):

        self.api_key = api_key
        self.api_url = api_url

        self.default_max_input_characters = default_max_input_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url and len(self.api_url) else None,
        )

        self.enums = OPENAIEnums

        self.logger = logging.getLogger(__name__)

    def set_generartion_model(self, model_id: str):
        self.generation_model_id = model_id
        self.logger.info(f"Set generation model to {model_id}")

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(
            f"Set embedding model to {model_id} with size {embedding_size}"
        )

    def process_text(self, text: str):
        return text[: self.default_max_input_characters].strip()

    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: int = None,
        temperature: float = None,
    ):
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model for openai not set")
            return None
        max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens
        )
        temperature = (
            temperature if temperature is not None else self.default_temperature
        )

        chat_history.append(self.construct_prompt(prompt, OPENAIEnums.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
        ):
            self.logger.error("No response returned from OpenAI")
            return None
        return response.choices[0].message.content

    def embed_text(self, text, document_type=None):
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for openai not set")
            return None

        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
        )

        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("No embedding returned from OpenAI")
            return None
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):

        return {"role": role, "content": self.process_text(prompt)}
