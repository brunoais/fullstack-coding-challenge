from typing import Tuple
from unittest import mock

import pytest

from shared.exceptions import InvalidTargetLanguage, InvalidSourceLanguage
from translate import translation

from shared.translation import Translation, TranslationStatus

# try:
from contextlib import nullcontext as does_not_raise
# except ImportError:
#     from contextlib import ExitStack as does_not_raise


@pytest.mark.parametrize(['text', 'target_language', 'source_language', 'raises'], [
    pytest.param('ABC text', 'es', 'en', does_not_raise(), id='normal translation'),
    pytest.param('ABC text', 'nope', 'en', pytest.raises(InvalidTargetLanguage), id='invalid target language'),
    pytest.param('ABC text', 'es', 'nope', pytest.raises(InvalidSourceLanguage), id='invalid source language'),
])
def test_new_translation(text, target_language, source_language, raises):
    with mock.patch("translate.translation.db") as db, \
         mock.patch("translate.translation.Cursor") as query_cursor, \
         mock.patch("translate.translation.unbabel") as unbabel_driver:

        connection_mock = mock.MagicMock()
        connection_mock.__enter__.return_value = mock.Mock(return_value=connection_mock)
        connection_mock.__enter__.return_value.execute.return_value = query_cursor
        connection_mock.__exit__.return_value = mock.Mock(return_value=False)

        db.connection.return_value = connection_mock


        response_translation = Translation('uidid', text,
                                           source_language=target_language, target_language=source_language,
                                           status=TranslationStatus.new)

        unbabel_driver.new_translation.return_value = response_translation

        with raises as excinfo:
            result = translation.request_translation(text, target_language, source_language)

            assert result is response_translation
            assert connection_mock.__enter__.return_value.execute.call_args_list[0][0][1] == (
                    'uidid', None, TranslationStatus.new,
                    source_language, target_language,
                    text
                )




@pytest.mark.parametrize(['status_before', 'status_after'], [
    pytest.param(TranslationStatus.new, TranslationStatus.translating, id='now translating'),
    pytest.param(TranslationStatus.translating, TranslationStatus.translating, id='still translating'),
    pytest.param(TranslationStatus.translating, TranslationStatus.completed, id='now completed'),
    pytest.param(TranslationStatus.completed, TranslationStatus.completed, id='(unreal) completed'),  # <- DB shouldn't have returned
])
def test_unbabel_translation_status(status_before, status_after):
    with mock.patch("translate.translation.db") as db, \
         mock.patch("translate.translation.Cursor") as query_cursor, \
         mock.patch("translate.translation.unbabel") as unbabel_driver:

        type(query_cursor).description = mock.PropertyMock(return_value=(('translation_req_id',), ('unbabel_translation_id',), ('user_id',), ('status',)))

        query_cursor.__iter__.return_value = (
            ('reqid', 'trid', 'usrid', status_before.value),
        )

        connection_mock = mock.MagicMock()
        connection_mock.__enter__.return_value = mock.Mock(return_value=connection_mock)
        connection_mock.__enter__.return_value.execute.return_value = query_cursor
        connection_mock.__exit__.return_value = mock.Mock(return_value=False)

        db.connection.return_value = connection_mock

        unbabel_response = Translation(
                translatedText="translated sentece",
                status=status_after)

        unbabel_driver.translation_status.return_value = unbabel_response

        translation.update_translations()

        assert len(unbabel_driver.translation_status.call_args_list) == 1

        if status_before is status_after:
            assert len(connection_mock.__enter__.return_value.execute.call_args_list) == 1
        else:
            assert len(connection_mock.__enter__.return_value.execute.call_args_list) == 2
            assert connection_mock.__enter__.return_value.execute.call_args_list[1][0][1] == (unbabel_response.status.name, unbabel_response.translation, 'reqid')

        assert unbabel_driver.translation_status.call_args_list[0][1]['uid'] == 'trid'



