"""
Handler: Stock Decreased
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from db import get_sqlalchemy_session
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer
from payments.models.outbox import Outbox
from payments.outbox_processor import OutboxProcessor


class StockDecreasedHandler(EventHandler):
    """Next step: persist payment request to Outbox (for resilience) and process it"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        return "StockDecreased"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        # Stock reserved - now persist payment request for durability before calling API
        session = get_sqlalchemy_session()
        try: 
            outbox_item = Outbox(order_id=event_data['order_id'], 
                                user_id=event_data['user_id'], 
                                total_amount=event_data['total_amount'],
                                order_items=event_data['order_items'])
            session.add(outbox_item)
            session.flush() 
            session.commit()
            # Now call payment API (will retry on app restart if needed)
            OutboxProcessor().run(outbox_item)
        except Exception as e:
            session.rollback()
            self.logger.debug(f"Payment request failed: {e}")
            event_data['event'] = "PaymentCreationFailed"
            event_data['error'] = str(e)
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)
        finally:
            session.close()


