import stripe
from fastapi import HTTPException

from config import settings
from models import InvoiceDB
from repositories.invoice_repository import InvoiceRepository

stripe.api_key = settings.stripe_api_key


class BillingService:
    def __init__(self, repo: InvoiceRepository):
        self.repo = repo

    async def create_payment_link(self, plate_number: str, amount: float) -> str:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Car repair services: {plate_number}",
                                "description": "Payment for maintenance and repair parts.",
                            },
                            "unit_amount": int(amount * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{settings.base_url}/api/v1/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.base_url}/api/v1/billing/cancel",
            )
        except stripe.StripeError as e:
            raise HTTPException(status_code=500, detail=f"Stripe payment error: {str(e)}") from e

        if not session.url:
            raise HTTPException(status_code=500, detail="Failed to generate Stripe URL")

        new_invoice = InvoiceDB(
            car_plate_number=plate_number,
            amount=amount,
            stripe_payment_intent_id=session.id,
        )
        await self.repo.add(new_invoice)

        return str(session.url)

    async def mark_invoice_paid(self, session_id: str) -> None:
        invoice = await self.repo.get_by_stripe_id(session_id)
        if invoice and invoice.status != "paid":
            invoice.status = "paid"
            await self.repo.commit()
