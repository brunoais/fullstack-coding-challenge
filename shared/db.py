
import pyodbc

import config


def connection():
    # Connection reuse is on in the ini file. This is safe to do as many times as needed
    cnxn: pyodbc.Connection = pyodbc.connect(config.ODBC_CONN_STR, autocommit=False)

    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    cnxn.setencoding(encoding='utf-8')
    cnxn.maxwrite = 1024 * 1024 * 1024

    return cnxn
