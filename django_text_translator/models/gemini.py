import google.generativeai as genai
from .base import TranslatorEngine
import logging
from time import sleep
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext_lazy as _

class GeminiTranslator(TranslatorEngine):
    # https://ai.google.dev/tutorials/python_quickstart
    gemini_models = ['gemini-pro','gemini-1.5-pro']

    # base_url = models.URLField(_("API URL"), default="https://generativelanguage.googleapis.com/v1beta/")
    api_key = EncryptedCharField(_("API Key"), max_length=255)
    model = models.CharField(max_length=100, default="gemini-pro", choices=[(x, x) for x in gemini_models])
    prompt = models.TextField(
        default="Translate only the text from the following into {target_language},only returns translations.\n{text}")
    temperature = models.FloatField(default=0.5)
    top_p = models.FloatField(default=1)
    top_k = models.IntegerField(default=1)
    max_tokens = models.IntegerField(default=1000)
    interval = models.IntegerField(_("Request Interval(s)"), default=3)

    class Meta:
        verbose_name = "Google Gemini"
        verbose_name_plural = "Google Gemini"

    def _init(self):
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(self.model)

    def validate(self) -> bool:
        if self.api_key:
            try:
                model = self._init()
                res = model.generate_content("hi")
                return res.candidates[0].finish_reason.name == "STOP"
            except Exception as e:
                return False

    def translate(self, text:str, target_language:str) -> dict:
        logging.info(">>> Gemini Translate [%s]:", target_language)
        model = self._init()
        tokens = 0
        translated_text = ''
        try:
            prompt = self.prompt.format(target_language=target_language, text=text)
            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_tokens
            )
            res = model.generate_content(prompt, generation_config=generation_config)
            finish_reason = res.candidates[0].finish_reason.name if res.candidates else None
            if finish_reason == "STOP":
                translated_text = res.text
            else:
                translated_text = ''
                logging.info("GeminiTranslator finish_reason->%s: %s", finish_reason, text)
            tokens = model.count_tokens(prompt).total_tokens
        except Exception as e:
            logging.error("GeminiTranslator->%s: %s", e, text)
        finally:
            sleep(self.interval)

        return {'text': translated_text, "tokens": tokens}

