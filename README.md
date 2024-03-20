## django-text-translator

A Django application that supports adding multiple third-party engines for text translation.

Currently, it supports the following engines:
- DeepL
- DeepLX
- OpenAI
- ClaudeAI
- Azure OpenAI
- Google Gemini
- Google Translate(Web)
- Microsoft Translate API
- Caiyun API
- Moonshot AI


Installation
-----------
1. Install: `pip install django-text-translator`
1. Add "django_text_translator" to your INSTALLED_APPS setting like this:
    ```
        INSTALLED_APPS = [
            ...,
            "django_text_translator",
        ]
    ```
1. Run `python manage.py makemigrations` and `python manage.py migrate` to create the models.
1. Start the development server and visit the admin to add a translator.
1. Translate a text:
    ```
    from django_text_translator.models import OpenAITranslator

    openai_translator = OpenAITranslator.filter(valid=True).first()

    results = openai_translator.translate(text="Hello, world!",target_language="Chinese")

    print(results.text) # 你好，世界！
    print(results.tokens) # 51

    ```
1. More details can be found in the models.py file.
