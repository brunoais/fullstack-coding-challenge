
from unittest import mock

import pytest

from shared.translation import TranslationStatus, Translation

@pytest.skip("Need to rethink how to test there while having SocketIO to account for")
def test_index(blueprinted_server, app_context):
    from translate import http
    with mock.patch("translate.http.translation") as translation_mock:
        translation_mock.user_translations_stream.return_value = [
            Translation(
                uid='tuid',
                source_language='source_lang',
                target_language='target_lang',
                status=TranslationStatus.translating,
                text='input text',
                translatedText=None
            )
        ]

        response = app_context.client.get('/translate/text')
        print(response)
