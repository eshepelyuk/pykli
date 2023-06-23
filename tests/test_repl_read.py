from pykli.repl_print import pok
from pprint import pformat, pprint

from sqlparse.tokens import String, Keyword
import sqlparse

from pathlib import Path


def test_sqlparse2():
    sql = """ exit ;  select * from qwe ;  select qwe from asd;  update qwe set as=2;"""
    stmts = [s.strip() for s in sqlparse.split(sql)]
    pok(f"found {len(stmts)} statements:\n")

    for s in stmts:
        pok(f"===>>> {s}")

        p = sqlparse.parse(s)[0]
        p._pprint_tree()

        t1 = p.token_first()
        pok(t1)


# sql = """RUN   SCRIPT   '/qwe/asd/asd.ksql';define zzz='zzz';DEFINE ttt='ttt';"""
def test_sqlparse_run_script():
    sql = """  RUN   SCRIPT   '/qwe/asd/asd.ksql';   run SCRIPT   '/tmp/555/file.ksql';"""
    stmts = [s.strip() for s in sqlparse.split(sql)]
    pok(f"found {len(stmts)} statements:\n")

    for s in stmts:
        print(f"===>>> {s}")

        p = sqlparse.parse(s)[0]
        p._pprint_tree()

        t1 = p.token_first()
        _, t2 = p.token_next(0)

        pok(t1)
        pok(f"{t1}")
        # pok(f"{t1.ttype} -> @{t1.value}@")
        # pok(t1.match(Keyword, (r"run\s+script\b",), regex=True))

        # pok(f"{t2.ttype} -> {t2}")
        # pok(f"{t2.ttype is String.Single}")
        # pok(pformat(Path(t2.value.strip("'"))))
        # pok(Path(t2.value.strip("'")).exists())

# sql = """RUN   SCRIPT   '/qwe/asd/asd.ksql';define zzz='zzz';DEFINE ttt='ttt';"""
