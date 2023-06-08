from pprint import pformat
from pykli.repl_print import format_ksql_type

STRING_COLUMN = {
    'name': 'StrFld',
    'schema': {'fields': None, 'memberSchema': None, 'type': 'STRING'},
}

STRING_KEY_COLUMN = {
    'name': 'StrFldKey', 'type': 'KEY',
    'schema': {'fields': None, 'memberSchema': None, 'type': 'STRING'},
}

STRUCT_COLUMN = {
    'name': 'Payload',
    'schema': {
        'memberSchema': None, 'type': 'STRUCT', 'fields': [
            {'name': 'Username', 'schema': {'fields': None, 'memberSchema': None, 'type': 'STRING'}},
            {'name': 'IsMobile', 'schema': {'fields': None, 'memberSchema': None, 'type': 'BOOLEAN'}},
        ]
    },
}

HEADER_COLUMN = {
    'headerKey': 'tenant_id', 'name': '_tenant_id', 'type': 'HEADER',
    'schema': {'fields': None, 'memberSchema': None, 'type': 'BYTES'},
}

def test_format_ksql_type():
    assert format_ksql_type({}) == pformat({})
    assert format_ksql_type(None) == pformat(None)
    assert format_ksql_type(STRING_COLUMN) == "VARCHAR"
    assert format_ksql_type(STRING_KEY_COLUMN) == "VARCHAR (key)"
    assert format_ksql_type(STRUCT_COLUMN) == "STRUCT<Username, IsMobile>"
    assert format_ksql_type(HEADER_COLUMN) == "BYTES (header('tenant_id'))"

