import os

from fastapi.datastructures import URL

INTENTION_CREATE_HEADERS = {
    "content-type": "application/json",
    "authorization": "Token " + os.environ["PAYMOB_SECRET_KEY"],
}
PAYMENT_INTEGRATION_IDS = list(map(int, os.environ["PAYMOB_PAYMENT_INTEGRATION_IDS"].split(",")))
PAYMOB_BASE_URL = "https://accept.paymob.com/v1"
PAYMOB_PUBLIC_KEY = os.environ["PAYMOB_PUBLIC_KEY"]
PAYMOB_UNIFIED_CHECKOUT_URL = URL("https://accept.paymob.com/unifiedcheckout")
PAYMOB_HMAC = os.environ["PAYMOB_HMAC"]
PAYMOB_INTENTION_URL = PAYMOB_BASE_URL + "/intention"
PAYMOB_CURRENCY = "EGP"
