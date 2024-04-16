from openai import OpenAI
from .base import TranslatorEngine
import logging
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext_lazy as _


class OpenAITranslator(TranslatorEngine):
    # https://platform.openai.com/docs/api-reference/chat

    api_key = EncryptedCharField(_("API Key"), max_length=255)
    base_url = models.URLField(_("API URL"), default="https://api.openai.com/v1")
    model = models.CharField(max_length=100, default="gpt-3.5-turbo", help_text="e.g. gpt-3.5-turbo, gpt-4-turbo")
    prompt = models.TextField(
        default="Translate only the text from the following into {target_language},only returns translations.\n{text}")
    temperature = models.FloatField(default=0.5)
    top_p = models.FloatField(default=0.95)
    frequency_penalty = models.FloatField(default=0)
    presence_penalty = models.FloatField(default=0)
    max_tokens = models.IntegerField(default=1000)

    summary_prompt = models.TextField(default="Summarize the following text in {target_language}:\n{text}")

    class Meta:
        verbose_name = "OpenAI"
        verbose_name_plural = "OpenAI"

    def _init(self):
        return OpenAI(
                    api_key=self.api_key,
                    base_url = self.base_url,
                    timeout=120.0,
                )

    def validate(self) -> bool:
        if self.api_key:
            try:
                client = self._init()
                res = client.with_options(max_retries=3).chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": 'Hi'}],
                    max_tokens=10,
                )
                fr = res.choices[0].finish_reason # 有些第三方源在key或url错误的情况下，并不会抛出异常代码，而是返回html广告，因此添加该行。
                logging.info(">>> OpenAI Translate Validate:%s",fr)
                return True
            except Exception as e:
                return False

    def translate(self, text:str, target_language:str, prompt:str=None) -> dict:
        logging.info(">>> OpenAI Translate [%s]:", target_language)
        client = self._init()
        tokens = 0
        translated_text = ''
        prompt = prompt or self.prompt
        try:
            prompt = prompt.format(target_language=target_language, text=text)
            res = client.with_options(max_retries=3).chat.completions.create(
                model=self.model,
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
                logging.info("OpenAITranslator->%s: %s", res.choices[0].finish_reason, text)
            tokens = res.usage.total_tokens
        except Exception as e:
            logging.error("OpenAITranslator->%s: %s", e, text)

        return {'text': translated_text, "tokens": tokens}
    
    def summarize(self, text:str, target_language:str) -> dict:
        logging.info(">>> OpenAI Summarize [%s]:", target_language)
        return self.translate(text, target_language, self.summary_prompt)
