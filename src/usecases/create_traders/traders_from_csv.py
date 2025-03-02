from src.usecases.create_traders.data import TRADER_PORTFOLIO
from src.usecases.create_traders.dto import TraderCreateDTO
from src.entites.trader import TraderStatus


def traders_data_from_csv(csvinput: list[str]) -> list[TraderCreateDTO]:
    traders_data = []
    for row in csvinput:
        profit = float(row[6].strip().replace("−", "-"))
        status = row[1].strip() if profit != 0 else TraderStatus.unactive
        if row[1].strip() == TraderStatus.hidden:
            status = TraderStatus.hidden

        traders_data.append(
            TraderCreateDTO(
                username=row[0].strip(),
                status=status,
                subscribes=int(row[2].strip()),
                subscribers=int(row[3].strip()),
                portfolio=TRADER_PORTFOLIO.get(row[4].strip())
                if len(row[4].strip()) > 0
                else None,
                trades=int(row[5].strip()),
                profit=profit,
                badges=[
                    s for s in row[7].split(", ") if len(s) > 2
                ],
            )
        )

    return sorted(set(traders_data), key=lambda t: t.username)