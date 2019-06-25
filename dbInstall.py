import os

import pyodbc as pyodbc

OBDC_SERVER_NAME = os.environ.get('OBDC_SERVER_NAME', 'localhost')

conn_str = (
    "DRIVER={PostgreSQL Unicode};"
    "DATABASE=user;"
    "UID=user;"
    "PWD=testingpassword;"
    "SERVER=" + OBDC_SERVER_NAME + ";"
    "PORT=5432;"
)

cnxn = pyodbc.connect(conn_str)


db_create_query_1 = """
CREATE TYPE comms.translation_status_t AS ENUM
    ('new', 'translating', 'completed', 'failed', 'canceled', 'accepted', 'rejected');

ALTER TYPE comms.translation_status_t
    OWNER TO "user";
"""
try:
    tables_query = cnxn.execute(db_create_query_1)
except pyodbc.ProgrammingError as e:
    if e.args[0] != '42710':  # Already exists error
        raise

db_create_query_3 = \
"""
CREATE SEQUENCE comms.translations_request_text_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE comms.translations_request_text_seq OWNER TO "user";
"""

try:
    tables_query = cnxn.execute(db_create_query_1)
except pyodbc.ProgrammingError as e:
    if e.args[0] != '42710':  # Already exists error
        raise


db_create_query_3 = \
"""


CREATE TABLE IF NOT EXISTS comms.translations
(
    translation_req_id integer NOT NULL,
    unbabel_translation_id character varying(40) COLLATE pg_catalog."default",
    user_id integer NULL,
    request_text text.js COLLATE pg_catalog."default" NOT NULL,
    response_text text.js COLLATE pg_catalog."default",
    status comms.translation_status_t NOT NULL,
    request_time timestamp without time zone NULL DEFAULT now(),
    response_time timestamp without time zone NULL,
    CONSTRAINT translations_pkey PRIMARY KEY (translation_req_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE comms.translations
    OWNER to "user";
COMMENT ON TABLE comms.translations
    IS 'Records a translate request, its state and the translate result.Meant to avoid requesting unbabel without need.';


ALTER SEQUENCE comms.translations_request_text_seq OWNED BY comms.translations.request_text;
ALTER TABLE ONLY comms.translations ALTER COLUMN translation_req_id SET DEFAULT nextval('comms.translations_translation_req_id_seq'::regclass);


"""

# """
# CREATE TABLE comms.users
# (
#     user_id integer,
#     PRIMARY KEY (user_id)
# )
# WITH (
#     OIDS = FALSE
# )
# TABLESPACE pg_default;
#
# ALTER TABLE comms.users
#     OWNER to "user";
#
# """

try:
    tables_query = cnxn.execute(db_create_query_3)
except pyodbc.ProgrammingError as e:
    if e.args[0] != '42710':  # Already exists error
        raise

