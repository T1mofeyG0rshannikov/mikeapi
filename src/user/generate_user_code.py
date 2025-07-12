from bisect import bisect_left
from random import randrange as r


def generate_code() -> str:
    return f"{chr(r(65, 91))}{r(10)}.{chr(r(65, 91))}{chr(r(65, 91))}{r(10)}{r(10)}"


def get_code_index(codes: list[str], code: str) -> int:
    return bisect_left(codes, code)


def code_exists(codes: list[str], code: str, ind: int) -> bool:
    return ind < len(codes) and codes[ind] == code
