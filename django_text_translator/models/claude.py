import anthropic
from .base import TranslatorEngine
import logging
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext_lazy as _

class ClaudeTranslator(TranslatorEngine):
    # https://docs.anthropic.com/claude/reference/getting-started-with-the-api
    claude_models = ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229']
    model = models.CharField(max_length=50, default="claude-instant-1.2", choices=[(x, x) for x in claude_models])
    api_key = EncryptedCharField(_("API Key"), max_length=255)
    max_tokens = models.IntegerField(default=1000)
    base_url = models.URLField(_("API URL"), default="https://api.anthropic.com")
    prompt = models.TextField(
        default="Translate only the text from the following into {target_language},only returns translations.\n{text}")
    proxy = models.URLField(_("Proxy(optional)"), null=True, blank=True, default=None)
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(null=True, blank=True, default=0.7)
    top_k = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Anthropic Claude"
        verbose_name_plural = "Anthropic Claude"

    def _init(self):
        return anthropic.Anthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            proxies=self.proxy,
        )

    def validate(self) -> bool:
        if self.api_key:
            try:
                res = self.translate("hi", "Chinese Simplified")
                return res.get("text") != ""
            except Exception as e:
                return False

    def translate(self, text:str, target_language:str) -> dict:
        logging.info(">>> Claude Translate [%s]:", target_language)
        client = self._init()
        tokens = client.count_tokens(text)
        translated_text = ''
        try:
            prompt = self.prompt.format(target_language=target_language, text=text)
            res = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            )
            result = res.content
            if result[0].type == "text":
                translated_text = result[0].text
                tokens += res.usage.output_tokens
        except Exception as e:
            logging.error("ClaudeTranslator->%s: %s", e, text)
        finally:
            return {'text': translated_text, "tokens": tokens}
