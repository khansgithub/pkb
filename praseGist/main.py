from prasegist.comments.parse_comments import (
    load_comments,
    _extract_body,
    parse_comments,
    save_comments,
)
from prasegist.gist.parse_gist import load_gist, save_gist, parse_gist
from prasegist.merge.merge import merge2
from prasegist.rows.make_rows import build_rows, make_rows
from prasegist.rows.rows_to_csv import build_csv


def gist_fucntions():
    gist = load_gist()
    tree = parse_gist(gist)
    # x =json.dumps([asdict(s) for s in tree], indent=4)
    # print(json.dumps(convert_tree(tree), indent=4))
    # save_gist(convert_tree(tree))
    save_gist(tree)


def comments_functions():
    comments = _extract_body(load_comments())
    tree = parse_comments(comments)
    save_comments(tree)


def merge_functions():
    merge2()


def row_functions():
    make_rows()
    build_csv()

if __name__ == "__main__":
    gist_fucntions()
    comments_functions()
    merge_functions()
    row_functions()
    pass
