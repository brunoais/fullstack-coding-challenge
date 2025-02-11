import logging
import threading
import time

from pyodbc import Cursor

import config
import shared.db as db
from shared.exceptions import InvalidTargetLanguage, InvalidSourceLanguage
from shared.translation import TranslationStatus, Translation
from translate import unbabel


LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)


def request_translation(text, target_language, source_language=None, user_id=None):
    LOG.info("Trying to create translation for %s", text)

    target_language = target_language.lower()
    source_language = source_language and source_language.lower()

    if target_language not in config.VALID_TARGET_LANGUAGES:
        raise InvalidTargetLanguage()

    if source_language not in config.VALID_SOURCE_LANGUAGES:
        raise InvalidSourceLanguage()

    with db.connection() as conn:

        LOG.info("requesting unbabel for %s", text)

        translation = unbabel.new_translation(text, target_language, source_language)

        LOG.info("storing unbabel translation in DB. Tr is: %s", translation)

        executed = conn.execute("""
            INSERT INTO comms.translations(
                 unbabel_translation_id, user_id, status,
                 source_language, target_language,
                 request_text
            )
            VALUES (?, ?, ?,
                    ?, ?,
                    ?);
        """,
            (
                translation.uid, user_id, translation.status.name,
                source_language, target_language,
                text
            ))

        LOG.info("Translation successfully created: %s", translation)

        return translation


translations_callback = set()

def add_translation_callback(callback_to):
    translations_callback.add(callback_to)

def broadcast_translation_update(translation):
    for callback in translations_callback:
        callback(translation)


def update_translations():
    """
        This function exists mostly so this feature can be tested
    """
    # Because the status updating is idempotent, this can commit only at the end with no problem if there's repetitions later
    # Regardless, it can need someone monitoring at the error logs to make sure errors are not causing cyclical problems

    with db.connection() as conn:
        translations_waiting: Cursor = conn.execute(
            """
                SELECT translation_req_id, unbabel_translation_id, user_id, status
                FROM comms.translations
                WHERE status in ('new', 'translating', 'accepted')
            """
        )

        # source: https://stackoverflow.com/a/12707465/551625
        column_names = {column[0]: index for index, column in enumerate(translations_waiting.description)}

        translations_count = 0
        updated_count = 0
        try:
            for translation_waiting in translations_waiting:
                previous_status = TranslationStatus[translation_waiting[column_names['status']]]
                translation_data = unbabel.translation_status(
                    uid=translation_waiting[column_names['unbabel_translation_id']])

                translations_count += 1
                if translation_data.status != previous_status:
                    updated_count += 1
                    # Status updated. Broadcast the update
                    broadcast_translation_update(translation_data)

                    conn.execute(
                        """
                            UPDATE comms.translations
                            SET 
                                response_time = now(),
                                status = ?,
                                response_text = ?
                            WHERE 
                                translation_req_id = ?
                        """,
                        (
                            translation_data.status.name,
                            translation_data.translation,
                            translation_waiting[column_names['translation_req_id']],
                        )
                    )
        finally:
            LOG.info("updating translations: out of %d translations needing update, %d were updated", translations_count, updated_count)



def periodic_update_translations():

    while True:
        LOG.info("updating the translations in the system")
        try:
            update_translations()
        except Exception:
            LOG.exception("Failed to update the translations due to an exception")
        time.sleep(config.UPDATE_TRANSLATIONS_POLL_INTERVAL_SECS)


periodic_updating_thread = threading.Thread(target=periodic_update_translations, name="update_translation_status")
periodic_updating_thread.daemon = True
if not config.UNIT_TESTS:
    periodic_updating_thread.start()


def user_translations_stream():
    """
    :return: A generator of the user translations created so far
    """

    # The initial idea to have user accounts is scrapped for now.

    with db.connection() as conn:
        user_translations: Cursor = conn.execute(
            """
                SELECT 
                    translation_req_id, unbabel_translation_id, user_id, status, 
                    source_language, target_language,
                    request_text, response_text
                FROM comms.translations;
            """
        )
        # source: https://stackoverflow.com/a/12707465/551625
        column_names = {column[0]: index for index, column in enumerate(user_translations.description)}

        LOG.info("Listing the translations in the system")

        for user_translation in user_translations:
            tr = Translation(
                user_translation[column_names['unbabel_translation_id']],
                user_translation[column_names['request_text']],
                user_translation[column_names['response_text']],
                user_translation[column_names['target_language']],
                user_translation[column_names['source_language']],
                user_translation[column_names['status']]
            )
            LOG.debug("Translation: %s", tr)
            yield tr
            # time.sleep(1)

