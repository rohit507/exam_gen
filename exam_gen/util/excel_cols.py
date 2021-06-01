
import exam_gen.util.logging as logging

log = logging.new(__name__, level="WARNING")

def excel_col(char, ind):

    if char.isdigit():
        return str(ind + 1)

    n,r = divmod(ind, 26)

    out = "" if n == 0 else _get_col(char,n / 26)
    out += chr(65 + r).upper() if char.isupper() else chr(65 + r)
    return out
