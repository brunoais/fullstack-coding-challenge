from shared.unbabel.api import UnbabelApi

import config
from shared.translation import Translation, TranslationStatus

unbabel = UnbabelApi(config.UNBABEL_USERNAME, config.UNBABEL_API_KEY, sandbox=True)

no_uid = object()



# This is now just a copy of unbabel's Translation but it removes the dependency of such object outside this module in case that one changes
class UnbabelTranslation(Translation):
    def __init__(
            self,
            uid=-1,
            text="",
            translatedText=None,
            target_language="",
            source_language=None,
            status_text=None,
            translators=(),
            topics=None,
            price=None,
            text_format='text',
            origin=None,
            price_plan=None,
            balance=None,
            client=None,
            order_number=None,
            unbabel_translation=None):

        if unbabel_translation is not None:
            uid = unbabel_translation.uid
            text = unbabel_translation.text
            translatedText = unbabel_translation.translation
            target_language = unbabel_translation.target_language
            source_language = unbabel_translation.source_language
            status_text = unbabel_translation.status
            translators = unbabel_translation.translators
            topics = unbabel_translation.topics
            price = unbabel_translation.price
            text_format = unbabel_translation.text_format
            origin = unbabel_translation.origin
            price_plan = unbabel_translation.price_plan
            client = unbabel_translation.client
            balance = unbabel_translation.balance
            order_number = unbabel_translation.order_number

        super().__init__(
            uid,
            text,
            translatedText,
            target_language,
            source_language,
            status_text and TranslationStatus[status_text],)
        self.unbabel_status = status_text
        self.translators = translators
        self.topics = topics
        self.price = price
        self.text_format = text_format
        self.origin = origin
        self.price_plan = price_plan
        self.client = client
        self.balance = balance
        self.order_number = order_number

    def __repr__(self):
        return "%s %s %s_%s" % (
            self.uid, self.status, self.source_language, self.target_language)

    def __str__(self):
        return "%s %s %s_%s" % (
            self.uid, self.status, self.source_language, self.target_language)



def new_translation(text, target_language, source_language=None, uid=None, text_format='text'):

    unbabel_translation = unbabel.post_translations(text, target_language, source_language, uid=uid, text_format=text_format)

    return UnbabelTranslation(unbabel_translation=unbabel_translation)


def translation_status(*, translation=None, uid=None):
    uid = uid or translation.uid

    unbabel_translation = unbabel.get_translation(uid)

    return UnbabelTranslation(unbabel_translation=unbabel_translation)



