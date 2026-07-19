import hashlib
import hmac
import typing
from decimal import Decimal

import requests
from fastapi import HTTPException, Request, status
from fastapi.datastructures import URL

from . import constants

__all__ = [
    "constants",
    "create_paymob_intention",
    "calculate_hmac",
    "webhook_hmac_check",
]


async def create_paymob_intention(
    amount: Decimal,
    item_name: str,
    item_description: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    redirection_url: str,
    notification_url: str,
    special_reference: str,
    expiration: int | None = None,
) -> URL:
    """Creates Paymob intention and returns the checkout URL."""
    amount_cents = int(amount * 100)
    response = requests.post(
        url=constants.PAYMOB_INTENTION_URL,
        headers=constants.INTENTION_CREATE_HEADERS,
        json={
            "amount": amount_cents,
            "currency": constants.PAYMOB_CURRENCY,
            "payment_methods": constants.PAYMENT_INTEGRATION_IDS,
            "items": [
                {
                    "name": item_name,
                    "amount": amount_cents,
                    "description": item_description,
                    "quantity": 1,
                }
            ],
            "billing_data": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number": phone,
            },
            "notification_url": notification_url,
            "expiration": expiration,
            "redirection_url": redirection_url,
            # "special_reference": special_reference,
        },
    )

    if response.status_code >= 400:
        print(f"Paymob error {response.status_code}: {response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Paymob Error"
        )

    resbody: dict[str, object] = response.json()  # pyright: ignore[reportAny]
    client_secret = resbody["client_secret"]

    return constants.PAYMOB_UNIFIED_CHECKOUT_URL.replace_query_params(
        clientSecret=client_secret, publicKey=constants.PAYMOB_PUBLIC_KEY
    )


async def calculate_hmac(obj: dict[str, typing.Any]):
    hmac_keys = [
        "amount_cents",
        "created_at",
        "currency",
        "error_occured",
        "has_parent_transaction",
        "id",
        "integration_id",
        "is_3d_secure",
        "is_auth",
        "is_capture",
        "is_refunded",
        "is_standalone_payment",
        "is_voided",
        "order.id",
        "owner",
        "pending",
        "source_data.pan",
        "source_data.sub_type",
        "source_data.type",
        "success",
    ]

    def flatten_and_filter_hmac(d: dict[str, object], parent_key: str = "", separator: str = "."):
        flattened: list[tuple[str, object]] = []
        for key, value in d.items():
            new_key = (parent_key + separator + key) if parent_key else key
            if isinstance(value, dict):
                flattened.extend(
                    flatten_and_filter_hmac(value, new_key, separator=separator)  # pyright: ignore[reportUnknownArgumentType]
                )
            elif new_key in hmac_keys:
                flattened.append((new_key, value))

        return flattened

    flattened_filtered_data = flatten_and_filter_hmac(obj)
    sorted_items: list[tuple[str, object]] = sorted(
        flattened_filtered_data,
        key=lambda item: item[0],
    )
    hmac_concat = ""
    for _, value in sorted_items:
        hmac_concat += str(value).lower() if isinstance(value, bool) else str(value)

    return hmac.digest(
        key=constants.PAYMOB_HMAC.encode("ascii"),
        msg=hmac_concat.encode("ascii"),
        digest=hashlib.sha512,
    ).hex()


async def webhook_hmac_check(provided_hmac: str, request: Request) -> dict[str, typing.Any]:
    data: dict[str, typing.Any] = await request.json()  # pyright: ignore[reportAny]
    obj: dict[str, typing.Any] = data["obj"]  # pyright: ignore[reportAny]
    calculated_hmac = await calculate_hmac(obj)
    if provided_hmac != calculated_hmac:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid HMAC.")

    return data
