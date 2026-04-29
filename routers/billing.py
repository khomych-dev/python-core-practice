from typing import Annotated, Any

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from auth import require_admin
from config import settings
from dependencies import get_billing_service
from services.billing_service import BillingService

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


class PaymentLinkRequest(BaseModel):
    plate_number: str = Field(..., description="License plate of the car")
    amount: float = Field(..., gt=0, description="Amount to pay in your local currency")


class PaymentLinkResponse(BaseModel):
    url: str


@router.post("/create-link", response_model=PaymentLinkResponse)
async def create_link(
    request: PaymentLinkRequest,
    admin_user: Annotated[dict[str, Any], Depends(require_admin)],
    billing_service: Annotated[BillingService, Depends(get_billing_service)],
) -> Any:

    url = await billing_service.create_payment_link(request.plate_number, request.amount)
    return PaymentLinkResponse(url=url)


@router.get("/success")
async def payment_success(session_id: str) -> dict[str, str]:
    return {"message": "Payment successful! The garage has been notified.", "session_id": session_id}


@router.get("/cancel")
async def payment_cancel() -> dict[str, str]:
    return {"message": "Payment was cancelled. Please try again later."}


@router.post("/webhook")
async def stripe_webhook(
    request: Request, billing_service: Annotated[BillingService, Depends(get_billing_service)]
) -> Response:

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = stripe.Webhook.construct_event(  # type: ignore[no-untyped-call]
            payload=payload, sig_header=sig_header, secret=settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload") from e
    except stripe.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = str(session.get("id"))
        await billing_service.mark_invoice_paid(session_id)

    return Response(status_code=200)
