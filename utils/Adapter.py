from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import stripe

class PurchaseData:
    def init(self, id: str, customer: Dict[str, str], items: List[Dict[str, float]], total: float):
        self.id = id
        self.customer = customer
        self.items = items
        self.total = total

    def repr(self):
        return f"PurchaseData(id={self.id}, customer={self.customer}, items={self.items}, total={self.total})"

class PurchaseDataProvider(ABC):
    @abstractmethod
    def retrieve_latest_purchase(self) -> PurchaseData:
        pass

class StripePurchaseDataProvider(PurchaseDataProvider):
    def init(self, secret_key: str):
        if not secret_key:
            raise ValueError("Stripe secret key is required")
        stripe.api_key = secret_key

    def retrieve_latest_purchase(self) -> PurchaseData:
        """Obtém a transação mais recente do Stripe."""
        try:
            charges = stripe.Charge.list(limit=1)

            if not charges['data']:
                return self._empty_purchase()

            charge = charges['data'][0]

            return PurchaseData(
                id=charge['id'],
                customer={
                    "email": charge.get("billing_details", {}).get("email", "Desconhecido")
                },
                items=[{
                    "description": charge.get("description", "Sem descrição"),
                    "amount": charge['amount'] / 100
                }],
                total=charge['amount'] / 100
            )

        except stripe.error.StripeError as e:
            print(f"Erro ao buscar dados do Stripe: {e}")
            return self._empty_purchase()

    def _empty_purchase(self) -> PurchaseData:
        return PurchaseData(
            id="",
            customer={"email": ""},
            items=[],
            total=0.0
        )