from src.repositories.settings_repository import SettingsRepository
from src.repositories.log_repository import LogRepository
from src.entites.trader import TraderWatch
from src.repositories.trader_repository import TraderRepository
from src.entites.deal import DealOperations
from collections import deque
import datetime


class TradersActivity:
    def __init__(
        self, 
        repository: TraderRepository, 
        deal_repository: LogRepository,
        settings_repository: SettingsRepository
    ) -> None:
        self.repository = repository
        self.deal_repository = deal_repository
        self.settings_repository = settings_repository

    async def __call__(self) -> None:
        traders = await self.repository.filter(watch=TraderWatch.on)
        traders = traders[0:5]
        print(traders)

        settings = await self.settings_repository.get()
        comission = settings.commission

        for trader in traders:
            print(trader)
            deals = await self.deal_repository.filter(trader_id=trader.id, start_time=settings.start_date)
            cash_balance = 0
            active_lots = {}
            deals_count = len(deals)
            trade_volume = 0
            income = 0
            
            for deal in deals:
                if active_lots[deal.ticker.slug]:
                    active_lots[deal.ticker.slug].append(deal)
                else:
                    active_lots[deal.ticker.slug] = [deal]
    
                trade_volume += deal.price
                
                if deal.operation == DealOperations.buy:
                    cash_balance -= (deal.price * deal.ticker.lot) * (100 + comission) / 100                    
                else:
                    cash_balance += (deal.price * deal.ticker.lot) * (100 - comission) / 100
        
            cash_balance = max(0, cash_balance)
        
            stock_balance = 0
            active_lots_count = 0
            profitable_deals = 0
            unprofitable_deals = 0
            
            for ticker_slug, ticker_deals in active_lots:
                que = deque()
                current_price = self.deal_repository.last(ticker_slug=ticker_slug).price
                
                for deal in ticker_deals:
                    if deal.operation == DealOperations.buy:
                        que.append(deal)
                    else:
                        last_deal = que.popleft()
                        profit = deal.price - last_deal.price - (deal.price + last_deal.price) * comission / 100
                        income += profit
                        if profit > 0:
                            profitable_deals += 1
                        else:
                            unprofitable_deals += 1
                          
                stock_balance += current_price * len(que)
                active_lots_count += len(que)
            
            yield_ = 2 * income / trade_volume if trade_volume != 0 else 0

            tickers_count = len(active_lots)
            gain = profitable_deals / (profitable_deals + unprofitable_deals) if (profitable_deals + unprofitable_deals) != 0 else 0

            date = datetime.date.today()
            await self.repository.create_statistics(
                date=date,
                cash_balance=cash_balance,
                stock_balance=stock_balance * comission,
                active_lots=active_lots,
                deals=deals_count,
                trade_volume=trade_volume,
                income=income,
                yield_=yield_,
                gain=gain,
                tickers=tickers_count
            )
            
