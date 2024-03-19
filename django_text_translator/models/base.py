import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
import cityhash

class TranslatorEngine(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    valid = models.BooleanField(_("Valid"), null=True)

    def translate(self, text: str, target_language: str) -> dict:
        raise NotImplementedError(
            "subclasses of TranslatorEngine must provide a translate() method"
        )

    def min_size(self) -> int:
        if hasattr(self, "max_characters"):
            return self.max_characters * 0.7
        if hasattr(self, "max_tokens"):
            return self.max_tokens * 0.7
        return 0

    def max_size(self) -> int:
        if hasattr(self, "max_characters"):
            return self.max_characters * 0.9
        if hasattr(self, "max_tokens"):
            return self.max_tokens * 0.9
        return 0
    def validate(self) -> bool:
        raise NotImplementedError(
            "subclasses of TranslatorEngine must provide a validate() method"
        )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Translated_Content(models.Model):
    hash = models.BinaryField(max_length=8, unique=True, primary_key=True, editable=False)
    original_content = models.TextField()

    translated_language = models.CharField(max_length=255)
    translated_content = models.TextField()

    tokens = models.IntegerField(default=0)
    characters = models.IntegerField(default=0)

    def __str__(self):
        return self.original_content

    @classmethod
    def is_translated(cls, text, target_language):
        text_hash = cityhash.CityHash64(f"{text}{target_language}").to_bytes(8, byteorder='little')
        try:
            content = Translated_Content.objects.get(hash=text_hash)
            # logging.info("Using cached translations:%s", text)
            return {
                'text': content.translated_content,
                'tokens': content.tokens,
                'characters': content.characters
            }
        except Translated_Content.DoesNotExist:
            logging.info("Does not exist in cache:%s", text)
            return None

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = cityhash.CityHash64(f"{self.original_content}{self.translated_language}").to_bytes(8, byteorder='little')
        # if self.hash not is binary, convert it to binary
        else:
            self.hash = self.hash.to_bytes(8, byteorder='little')
        super(Translated_Content, self).save(*args, **kwargs)

