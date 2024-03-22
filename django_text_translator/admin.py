import logging
from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from .models import *

class BaseTranslatorAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        logging.info("Call save_model: %s", obj)
        obj.valid = None
        obj.save()
        try:
            obj.valid = obj.validate()
        except Exception as e:
            obj.valid = False
            logging.error("Error in django_text_translator: %s", e)
        finally:
            obj.save()

    def is_valid(self, obj):
        if obj.valid is None:
            return format_html(
                "<img src='/static/img/icon-loading.svg' alt='In Progress'>"
            )
        elif obj.valid is True:
            return format_html(
                "<img src='/static/admin/img/icon-yes.svg' alt='Succeed'>"
            )
        else:
            return format_html(
                "<img src='/static/admin/img/icon-no.svg' alt='Error'>"
            )

    is_valid.short_description = 'Valid'

    def masked_api_key(self, obj):
        api_key = obj.api_key if hasattr(obj, "api_key") else obj.token
        if api_key:
            return f"{api_key[:3]}...{api_key[-3:]}"
        return ""
    masked_api_key.short_description = "API Key"

@admin.register(OpenAITranslator)
class OpenAITranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "base_url", "model", "prompt", "temperature", "top_p", "frequency_penalty",
              "presence_penalty", "max_tokens"]
    list_display = ["name", "is_valid", "masked_api_key", "model", "prompt", "max_tokens", "base_url"]


@admin.register(AzureAITranslator)
class AzureAITranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "endpoint", "version", "deloyment_name", "prompt", "temperature", "top_p",
              "frequency_penalty", "presence_penalty", "max_tokens"]
    list_display = ["name", "is_valid", "masked_api_key", "deloyment_name", "version", "prompt", "max_tokens", "endpoint"]


@admin.register(DeepLTranslator)
class DeepLTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "server_url", "proxy", "max_characters"]
    list_display = ["name", "is_valid", "masked_api_key", "server_url", "proxy", "max_characters"]


@admin.register(DeepLXTranslator)
class DeepLXTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "deeplx_api", "interval", "max_characters"]
    list_display = ["name", "is_valid", "deeplx_api", "interval", "max_characters"]


# @admin.register(DeepLWebTranslator)
class DeepLWebTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "interval", "proxy", "max_characters"]
    list_display = ["name", "is_valid", "interval", "proxy", "max_characters"]

@admin.register(MicrosoftTranslator)
class MicrosoftTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "location", "endpoint", "max_characters"]
    list_display = ["name", "is_valid", "masked_api_key", "location", "endpoint", "max_characters"]


@admin.register(CaiYunTranslator)
class CaiYunTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "token", "url", "max_characters"]
    list_display = ["name", "is_valid", "masked_api_key", "url", "max_characters"]


@admin.register(GeminiTranslator)
class GeminiTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "model", "prompt", "temperature", "top_p", "top_k", "max_tokens", "interval"]
    list_display = ["name", "is_valid", "masked_api_key", "model", "prompt", "max_tokens", "interval"]


@admin.register(GoogleTranslateWebTranslator)
class GoogleTranslateWebTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "base_url", "interval", "proxy", "max_characters"]
    list_display = ["name", "is_valid", "base_url", "proxy", "interval", "max_characters"]

@admin.register(ClaudeTranslator)
class ClaudeTranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "base_url", "model", "prompt", "temperature", "top_p", "top_k", "max_tokens", "proxy"]
    list_display = ["name", "is_valid", "masked_api_key", "model", "prompt", "max_tokens", "base_url"]

@admin.register(MoonshotAITranslator)
class MoonshotAITranslatorAdmin(BaseTranslatorAdmin):
    fields = ["name", "api_key", "base_url", "model", "prompt", "temperature", "top_p", "frequency_penalty",
              "presence_penalty", "max_tokens"]
    list_display = ["name", "is_valid", "masked_api_key", "model", "prompt", "max_tokens", "base_url"]

if settings.DEBUG:
    @admin.register(Translated_Content)
    class Translated_ContentAdmin(admin.ModelAdmin):
        #fields = ["original_content", "translated_content", "translated_language", "tokens", "characters"]
        list_display = ["original_content", "translated_language", "translated_content", "tokens", "characters"]
    
        def has_change_permission(self, request, obj=None):
            return False

        def has_add_permission(self, request):
            return False


    @admin.register(TestTranslator)
    class TestTranslatorAdmin(BaseTranslatorAdmin):
        fields = ["name", "translated_text", "max_characters", "interval"]
        list_display = ["name", "is_valid", "translated_text", "max_characters", "interval"]