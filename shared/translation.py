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

status_to_simplified_status = {
    TranslationStatus.new: 'requested',
    TranslationStatus.translating: 'pending',
    TranslationStatus.failed: 'pending',
    TranslationStatus.accepted: 'pending',
    TranslationStatus.rejected: 'pending',
    TranslationStatus.canceled: 'requested',
    TranslationStatus.completed: 'translated',
}


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
        self.simplified_status = status and status_to_simplified_status[status]

    def __repr__(self):
        return "%s %s %s->%s" % (
            self.uid, self.status, self.source_language, self.target_language)

    def __str__(self):
        return "%s %s %s->%s" % (
            self.uid, self.status, self.source_language, self.target_language)
