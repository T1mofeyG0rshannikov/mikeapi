from enum import StrEnum


class DealOperations(StrEnum):
    buy = "buy"
    sell = "sell"

TRADE_OPERATIONS = {"купил": "buy", "продал": "sell"}
