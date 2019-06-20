
import pyodbc as pyodbc

conn_str = (
    "DRIVER={PostgreSQL Unicode};"
    "DATABASE=postgres;"
    "UID=user;"
    "PWD=testingpassword;"
    "SERVER=localhost;"
    "PORT=5432;"
)

cnxn = pyodbc.connect(conn_str)


db_create_query = """
CREATE TYPE comms.translation_status_t AS ENUM
    ('new', 'translating', 'completed', 'failed', 'canceled', 'accepted', 'rejected');

ALTER TYPE comms.translation_status_t
    OWNER TO "user";

CREATE TABLE comms.translations
(
    translation_req_id integer NOT NULL DEFAULT nextval('comms.translations_translation_req_id_seq'::regclass) ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    unbabel_translation_id character varying(40) COLLATE pg_catalog."default",
    user_id integer NOT NULL,
    request_text text.js COLLATE pg_catalog."default" NOT NULL ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    response_text text.js COLLATE pg_catalog."default",
    status comms.translation_status_t NOT NULL,
    request_time timestamp without time zone NOT NULL DEFAULT now(),
    response_time timestamp without time zone NOT NULL,
    CONSTRAINT translations_pkey PRIMARY KEY (translation_req_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE comms.translations
    OWNER to "user";
COMMENT ON TABLE comms.translations
    IS 'Records a translate request, its state and the translate result.
Meant to avoid requesting unbabel without need.';
"""

"""
CREATE TABLE comms.users
(
    user_id integer,
    PRIMARY KEY (user_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE comms.users
    OWNER to "user";
    
"""


tables_query = cnxn.execute(db_create_query)
