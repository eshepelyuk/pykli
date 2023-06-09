from typing import NamedTuple

from sqlparse import keywords
from sqlparse.lexer import Lexer
from sqlparse.tokens import Keyword

from . import LOG

class Stmt(NamedTuple):
    ksql: str

class PullQuery(NamedTuple):
    ksql: str

class QueryResponse(NamedTuple):
    val: dict

class StmtResponse(NamedTuple):
    val: dict

class Info(NamedTuple):
    srv: str

class ErrMsg(NamedTuple):
    msg: str

KRunScript = Keyword.KRunScript

KDefine = Keyword.KDefine

def initialize_sqlparse():
    lex = Lexer.get_default_instance()
    lex.clear()

    lex.set_SQL_REGEX([
        (r"run\s+script\b", KRunScript),
    ] + keywords.SQL_REGEX)

    lex.add_keywords(keywords.KEYWORDS_COMMON)
    lex.add_keywords(keywords.KEYWORDS)

    lex.add_keywords({"DEFINE": Keyword.KDefine})

    LOG.info("initialize_sqlparse done")
