"""
Handler: Stock Decrease Failed
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer


class StockDecreaseFailedHandler(EventHandler):
    """No stock available - cancel the order immediately"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        return "StockDecreaseFailed"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        # Stock unavailable - no compensation needed, just cancel
        event_data['event'] = "OrderCancelled"
        self.order_producer.get_instance().send(config.KAFKA_TOPIC, value=event_data)
  
