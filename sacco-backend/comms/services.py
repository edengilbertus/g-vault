import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import certifi

from comms.models import MobileMoneyWebhookEvent, SmsNotification

if TYPE_CHECKING:
    from finance.models import LoanApplication, Transaction
    from members.models import User

AFRICAS_TALKING_SMS_URL = "https://api.africastalking.com/version1/messaging"
CURRENCY_CODE = "UGX"


class SmsDispatchError(Exception):
    pass


def normalize_phone_number(phone_number: str) -> str:
    raw = phone_number.strip()
    if not raw:
        raise SmsDispatchError("Recipient phone number is required.")

    if raw.startswith("+"):
        digits = "".join(ch for ch in raw[1:] if ch.isdigit())
    else:
        digits = "".join(ch for ch in raw if ch.isdigit())

    if not digits:
        raise SmsDispatchError("Recipient phone number is invalid.")

    return f"+{digits}"


def format_ugx(amount: Decimal) -> str:
    rounded = amount.quantize(Decimal("1"))
    return f"{CURRENCY_CODE} {int(rounded):,}"


def send_sms_via_africas_talking(recipient_phone: str, message: str) -> dict[str, Any]:
    username = os.getenv("AT_USERNAME", "").strip()
    api_key = os.getenv("AT_API_KEY", "").strip()
    if not username or not api_key:
        raise SmsDispatchError("AT_USERNAME and AT_API_KEY must be configured.")

    normalized_phone = normalize_phone_number(recipient_phone)
    message_value = message.strip()
    if not message_value:
        raise SmsDispatchError("SMS message cannot be empty.")

    payload = urllib.parse.urlencode(
        {"username": username, "to": normalized_phone, "message": message_value}
    ).encode("utf-8")
    request = urllib.request.Request(
        AFRICAS_TALKING_SMS_URL,
        data=payload,
        method="POST",
        headers={
            "apiKey": api_key,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=15, context=ssl_context) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        provider_error = exc.read().decode("utf-8", errors="ignore")
        raise SmsDispatchError(
            f"Africa's Talking request failed with status {exc.code}: {provider_error}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SmsDispatchError(f"Unable to reach Africa's Talking: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SmsDispatchError("Africa's Talking request timed out.") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SmsDispatchError("Africa's Talking returned invalid JSON.") from exc

    if not isinstance(parsed, dict):
        raise SmsDispatchError("Africa's Talking returned an unexpected response format.")

    return parsed


def extract_message_id(provider_response: dict[str, Any]) -> str:
    sms_data = provider_response.get("SMSMessageData")
    if not isinstance(sms_data, dict):
        return ""

    recipients = sms_data.get("Recipients")
    if not isinstance(recipients, list) or not recipients:
        return ""

    first_recipient = recipients[0]
    if not isinstance(first_recipient, dict):
        return ""

    message_id = first_recipient.get("messageId")
    return message_id if isinstance(message_id, str) else ""


def send_member_event_sms(
    *,
    member: "User",
    event_type: str,
    message: str,
    transaction_obj: "Transaction | None" = None,
    loan_application: "LoanApplication | None" = None,
) -> SmsNotification:
    notification = SmsNotification.objects.create(
        provider=MobileMoneyWebhookEvent.Provider.AFRICAS_TALKING,
        member=member,
        event_type=event_type,
        recipient_phone=member.phone_number,
        message=message,
        transaction=transaction_obj,
        loan_application=loan_application,
    )

    try:
        provider_response = send_sms_via_africas_talking(member.phone_number, message)
    except SmsDispatchError as exc:
        notification.status = SmsNotification.Status.FAILED
        notification.error_message = str(exc)
        notification.save(update_fields=["status", "error_message", "updated_at"])
        return notification

    notification.status = SmsNotification.Status.SENT
    notification.provider_response = provider_response
    notification.external_message_id = extract_message_id(provider_response)
    notification.save(update_fields=["status", "provider_response", "external_message_id", "updated_at"])
    return notification
