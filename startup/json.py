import datetime
import json

from werkzeug.datastructures import FileStorage

class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        """ Minimalistic incomplete json transformation
            which is enough for logging and for analytics
        """
        if isinstance(o, FileStorage):

            return {
                "name": o.name,
                "filename": o.filename,
                "content_length": o.content_length,
                "content_type": o.content_type,
                "headers": list(o.headers),
                "mimetype": o.mimetype,
            }

        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)

json._default_encoder = CustomJsonEncoder()
