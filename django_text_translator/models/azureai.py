import logging
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext_lazy as _
from openai import AzureOpenAI
from .base import TranslatorEngine


class AzureAITranslator(TranslatorEngine):
    # https://learn.microsoft.com/azure/ai-services/openai/
    api_key = EncryptedCharField(_("API Key"), max_length=255)
    endpoint = models.URLField(_("Endpoint"), default="https://example.openai.azure.com/")
    version = models.CharField(max_length=50, default="2023-12-01-preview")
    deloyment_name = models.CharField(max_length=100)
    prompt = models.TextField(default="Translate the following to {target_language},only returns translations.\n{text}")
    temperature = models.FloatField(default=0.5)
    top_p = models.FloatField(default=0.95)
    frequency_penalty = models.FloatField(default=0)
    presence_penalty = models.FloatField(default=0)
    max_tokens = models.IntegerField(default=1000)

    class Meta:
        verbose_name = "Azure OpenAI"
        verbose_name_plural = "Azure OpenAI"

    def _init(self):
        return AzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.version,
                    azure_endpoint=self.endpoint,
                    timeout=20.0,
                )

    def validate(self) -> bool:
        if self.api_key:
            try:
                client = self._init()
                res = client.with_options(max_retries=3).chat.completions.create(
                    model=self.deloyment_name,
                    messages=[{"role": "user", "content": 'Hi'}],
                    max_tokens=10,
                )
                return True
            except Exception as e:
                return False

    def translate(self, text:str, target_language:str) -> dict:
        logging.info(">>> AzureAI Translate [%s]:", target_language)
        client = self._init()
        tokens = 0
        translated_text = ''
        try:
            prompt = self.prompt.format(target_language=target_language, text=text)
            res = client.with_options(max_retries=3).chat.completions.create(
                model=self.deloyment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                max_tokens=self.max_tokens,
            )
            if res.choices[0].finish_reason == "stop":
                translated_text = res.choices[0].message.content
            else:
                translated_text = ''
                logging.info("AzureAITranslator->%s: %s", res.choices[0].finish_reason, text)
            tokens = res.usage.total_tokens
        except Exception as e:
            logging.error("AzureAITranslator->%s: %s", e, text)

        return {'text': translated_text, "tokens": tokens}
