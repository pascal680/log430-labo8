"""
Handler: Saga Completed
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer
from db import get_redis_conn

class SagaCompletedHandler(EventHandler):
    """Final step of the saga - logs completion status and syncs payment link to Redis"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        return "SagaCompleted"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        # Log success or failure
        if 'error' in event_data:
            self.logger.info("Saga terminée avec des erreurs. Veuillez consulter les données de l'événement pour plus d'informations.")
        else:
            self.logger.info(f"Saga terminée avec succès ! Votre order_id = {event_data['order_id']}. Votre payment_link = '{event_data['payment_link']}' .")
            # Sync final payment link to Redis
            self._sync_payment_link_to_redis(event_data)
        self.logger.info(event_data)
    
    def _sync_payment_link_to_redis(self, event_data: Dict[str, Any]) -> None:
        try:
            r = get_redis_conn()
            order_id = event_data.get('order_id')
            payment_link = event_data.get('payment_link', '')
            if order_id and payment_link:
                order_data = r.hgetall(f"order:{order_id}")
                if order_data:
                    order_data[b'payment_link'] = payment_link.encode('utf-8')
                    r.hset(f"order:{order_id}", mapping=order_data)
        except Exception as e:
            self.logger.error(f"Could not sync payment link to Redis: {e}")


