import enum

from shared.global_enums import StrEnum


class TranslationStatus(StrEnum):
    new = enum.auto()
    translating = enum.auto()
    completed = enum.auto()
    failed = enum.auto()
    canceled = enum.auto()
    accepted = enum.auto()
    rejected = enum.auto()


# This is now just a copy of
class Translation(object):
    def __init__(
            self,
            uid=-1,
            text="",
            translatedText=None,
            target_language="",
            source_language=None,
            status=None,
            ):
        self.uid = uid
        self.text = text
        self.translation = translatedText
        self.source_language = source_language
        self.target_language = target_language
        self.status = status

    def __repr__(self):
        return "%s %s %s_%s" % (
            self.uid, self.status, self.source_language, self.target_language)

    def __str__(self):
        return "%s %s %s_%s" % (
            self.uid, self.status, self.source_language, self.target_language)
