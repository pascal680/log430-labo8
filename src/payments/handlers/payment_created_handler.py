"""
Handler: Payment Created
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer

class PaymentCreatedHandler(EventHandler):
    """Handles PaymentCreated events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "PaymentCreated"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        payment_link = event_data.get("payment_link")
        if not payment_link or payment_link == "no-link":
            payment_id = event_data.get("payment_id")
            if payment_id:
                payment_link = f"http://api-gateway:8080/payments-api/payments/process/{payment_id}"
            else:
                payment_link = "payment-link-unavailable"
            event_data["payment_link"] = payment_link

        event_data["event"] = "SagaCompleted"
        self.logger.debug(f"payment_link={payment_link}")
        self.order_producer.get_instance().send(config.KAFKA_TOPIC, value=event_data)


