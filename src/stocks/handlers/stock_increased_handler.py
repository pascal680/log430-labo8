"""
Handler: Stock Increased
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer


class StockIncreasedHandler(EventHandler):
    """Compensation: return stock since payment failed"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        return "StockIncreased"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        # Stock returned successfully - saga is now complete with error flag
        try:
            event_data['event'] = "SagaCompleted"
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)
        except Exception as e:
            self.logger.debug(f"Error finalizing saga: {e}")
            event_data['error'] = str(e)
            event_data['event'] = "SagaCompleted"
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)



