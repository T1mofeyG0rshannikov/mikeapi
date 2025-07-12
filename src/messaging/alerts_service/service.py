from src.messaging.alerts_service.config import AlertsServiceConfig
from redis import Redis


class AlertsService:
    def __init__(self, redis: Redis, config: AlertsServiceConfig) -> None:
        self.r = redis
        self.c = config
        
    def _get_value(self, key: str) -> bool:
        val = self.r.get(key)
        if val is None:
            return False
        return bool(int(val))
        
    def is_first_send(self) -> bool:
        return self._get_value(self.c.FIRST_SEND)

    def is_second_send(self) -> bool:
        return self._get_value(self.c.SECOND_SEND)
        
    def set_first_send(self, value:bool=False) -> None:
        self.r.set(self.c.FIRST_SEND, int(value))
        if value:
            self.raw_set_pulled_up(False)
        
    def set_second_send(self, value:bool=False) -> None:
        self.r.set(self.c.SECOND_SEND, int(value))
        
    def raw_set_pulled_up(self, value:bool=False) -> None:
        self.r.set(self.c.PULLED_UP, int(value))
        
    def set_pulled_up(self) -> None:
        self.set_first_send(False)
        self.set_second_send(False)
        self.raw_set_pulled_up(True)
        
    def is_pulled_up(self) -> bool:
        return self._get_value(self.c.PULLED_UP)

    
    
    
    
    
    
    def is_first_send_ping(self) -> bool:
        return self._get_value(self.c.FIRST_SEND_PINGS)
        

    def is_second_send_ping(self) -> bool:
        return self._get_value(self.c.SECOND_SEND_PINGS)

    def set_first_send_ping(self, value:bool=False) -> None:
        self.r.set(self.c.FIRST_SEND_PINGS, int(value))
        if value:
            self.raw_set_pulled_up_ping(False)
        
    def set_second_send_ping(self, value:bool=False) -> None:
        self.r.set(self.c.SECOND_SEND_PINGS, int(value))
        
    def raw_set_pulled_up_ping(self, value:bool=False) -> None:
        self.r.set(self.c.PULLED_UP_PINGS, int(value))
        
    def set_pulled_up_ping(self) -> None:
        self.set_first_send_ping(False)
        self.set_second_send_ping(False)
        self.raw_set_pulled_up_ping(True)
        
    def is_pulled_up_ping(self) -> bool:
        return self._get_value(self.c.PULLED_UP_PINGS)
