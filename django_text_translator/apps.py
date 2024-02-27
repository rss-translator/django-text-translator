from django.apps import AppConfig


class TranslatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_text_translator"
    label = "translator"
