from typing import NamedTuple

from sqlparse import keywords
from sqlparse.sql import Statement
from sqlparse.lexer import Lexer
from sqlparse.tokens import Keyword

from . import LOG


class Stmt(NamedTuple):
    ksql: Statement

class PullQuery(NamedTuple):
    ksql: str

class QueryResponse(NamedTuple):
    val: dict

class StmtResponse(NamedTuple):
    val: list[dict]

class Info(NamedTuple):
    srv: str

class ErrMsg(NamedTuple):
    msg: str

class SessionVar(NamedTuple):
    name: str
    val: str | None

KRunScript = Keyword.KRunScript

KSQL = Keyword.KSQL

def initialize_sqlparse():
    lex = Lexer.get_default_instance()
    lex.clear()

    lex.set_SQL_REGEX([
        (r"run\s+script\b", KRunScript),
    ] + keywords.SQL_REGEX)

    lex.add_keywords(keywords.KEYWORDS_COMMON)
    lex.add_keywords(keywords.KEYWORDS)

    lex.add_keywords({"DEFINE": KSQL.Define})
    lex.add_keywords({"UNDEFINE": KSQL.Undefine})

    LOG.info("KSQL grammar for sqlparse initialized")
