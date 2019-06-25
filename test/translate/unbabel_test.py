from unittest import mock

import pytest


from shared.translation import TranslationStatus
from translate import unbabel
from shared.unbabel import api as unbabel_api


@pytest.mark.parametrize(['text','s_lang', 't_lang', 'status'], [
    pytest.param("fake", 'en', 'es', TranslationStatus.new, id='Fake en-es'),
    pytest.param("Hello", 'en', 'es', TranslationStatus.new, id='Hello en-es'),
    pytest.param("Holla", 'es', 'en', TranslationStatus.new, id='Holla es-en'),
])
def test_unbabel_new_translation(text, s_lang, t_lang, status):
    with mock.patch("translate.unbabel.unbabel") as unb_api:
        response_translation = unbabel_api.Translation('uidid', text,
                                                       source_language=s_lang, target_language=t_lang,
                                                       status=status.name)

        unb_api.post_translations.return_value = response_translation

        result = unbabel.new_translation(text, t_lang, s_lang)

        assert result is not response_translation
        assert unb_api.post_translations.call_args_list == [mock.call(text, t_lang, s_lang, uid=None, text_format='text')]

        assert result.uid == response_translation.uid
        assert result.text == response_translation.text
        assert result.unbabel_status == response_translation.status
        assert result.status == status
        assert result.source_language == response_translation.source_language
        assert result.target_language == response_translation.target_language

        print(result)


@pytest.mark.parametrize(['status'], [
    pytest.param(TranslationStatus.translating, id='translating'),
    pytest.param(TranslationStatus.completed, id='completed'),
])
@pytest.mark.parametrize(['translation', 'uid'], [
    pytest.param("weirduid", None, id='translation mode'),
    pytest.param(None, 'gooduid', id='uid mode'),
])
def test_unbabel_translation_status(translation, uid, status):
    with mock.patch("translate.unbabel.unbabel") as unb_api:

        input_info = {}
        if translation:
            input_info['translation'] = unbabel.UnbabelTranslation(translation)
        else:
            input_info['uid'] = uid

        response_translation = unbabel_api.Translation(translation or uid, 'input_text',
                                                          source_language='en', target_language='es',
                                                          status=status.name)

        unb_api.get_translation.return_value = response_translation

        result = unbabel.translation_status(**input_info)

        assert result is not response_translation
        assert unb_api.get_translation.call_args_list == [mock.call(translation or uid)]

        assert result.uid == response_translation.uid
        assert result.text == response_translation.text
        assert result.unbabel_status == response_translation.status
        assert result.status == status
        assert result.source_language == response_translation.source_language
        assert result.target_language == response_translation.target_language

        print(result)