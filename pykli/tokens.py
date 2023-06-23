from typing import NamedTuple

from sqlparse import keywords
from sqlparse.lexer import Lexer
from sqlparse.tokens import Keyword

class KStmt(NamedTuple):
    ksql: str

class KQuery(NamedTuple):
    ksql: str

class KResponse(NamedTuple):
    val: dict

class KInfo(NamedTuple):
    srv: str

class ErrorMessage(NamedTuple):
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
