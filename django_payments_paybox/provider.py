import enum
import hashlib
import logging
from typing import Union

import requests
import xmltodict
from django.http import HttpResponse
from payments import PaymentError, PaymentStatus, RedirectNeeded, models
from payments.core import BasicProvider

from .utils import randomword
from .schemas import (
    PayboxInitPaymentData,
    PayboxInitResponseStatus,
    PayboxInitPaymentResponse,
    PayboxCheckUrlData,
    PayboxProviderOptions,
)


logger = logging.getLogger(__name__)


class PayboxProvider(BasicProvider):
    ENDPOINT_SCRIPT_NAME = "init_payment.php"
    ENDPOINT_URL = f"https://paybox.kz/{ENDPOINT_SCRIPT_NAME}"

    def __init__(self, *args, **kwargs):
        self.settings = PayboxProviderOptions(**kwargs)
        kwargs.pop("merchant_id")
        kwargs.pop("secret")
        kwargs.pop("site_url")
        kwargs.pop("testing_mode")
        super().__init__(*args, **kwargs)

    def send_request(
        self, init_data: PayboxInitPaymentData
    ) -> PayboxInitPaymentResponse:
        response = requests.post(
            PayboxProvider.ENDPOINT_URL,
            data=init_data.json(),
            headers={"Content-Type": "application/json"},
        )
        response_data = PayboxInitPaymentResponse(
            **xmltodict.parse(response.content)["response"]
        )
        return response_data

    def create_sig(
        self,
        data: Union[
            PayboxCheckUrlData, PayboxInitPaymentResponse, PayboxInitPaymentData
        ],
        script_name,
    ):
        string = script_name
        for key in sorted(list(data.__fields_set__)):
            if key != "pg_sig":
                key_value = getattr(data, key)
                if isinstance(key_value, enum.Enum):
                    key_value = key_value.value
                if key_value:
                    string += ";{}".format(key_value)
        string += ";{}".format(self.settings.secret)
        pg_sig = hashlib.md5(string.encode()).hexdigest()
        return pg_sig

    def check_response(self, paybox_response: PayboxInitPaymentResponse, script_name):
        sig = paybox_response.pg_sig
        my_sig = self.create_sig(paybox_response, script_name)
        if sig != my_sig:
            return False
        return True

    def get_init_data(self, payment: models.BasePayment) -> PayboxInitPaymentData:
        """
        Create initial data for PayBox payment
        """
        data = PayboxInitPaymentData(
            pg_merchant_id=self.settings.merchant_id,
            pg_order_id=payment.token or None,
            pg_amount=int(payment.total) or None,
            pg_salt=randomword(15),
            pg_currency=payment.currency or None,
            pg_site_url=self.settings.site_url,
            pg_description=payment.description or None,
            pg_testing_mode=self.settings.testing_mode,
            # urls
            pg_result_url=payment.get_process_url() or None,
            pg_success_url=payment.get_success_url() or None,
            pg_failure_url=payment.get_failure_url() or None,
            # request methods
            pg_request_method="GET",
            # user
            pg_user_contact_email=payment.billing_email or None,
            # sig
        )
        data.pg_sig = self.create_sig(data, self.ENDPOINT_SCRIPT_NAME)
        return data

    def get_form(self, payment, data=None):
        if not payment.id:
            payment.save()
        init_payment_data = self.get_init_data(payment)
        paybox_response = self.send_request(init_payment_data)
        if paybox_response.pg_status == PayboxInitResponseStatus.ERROR:
            raise PaymentError(paybox_response.pg_error_description)
        if not self.check_response(paybox_response, self.ENDPOINT_SCRIPT_NAME):
            raise PaymentError("Invalid response(from PayBox) signature")
        raise RedirectNeeded(paybox_response.pg_redirect_url)

    def querydict_to_dict(self, querydict):
        data_dict = dict()
        for k, v in querydict.items():
            data_dict[k] = v
        return data_dict

    def process_data(self, payment, request):
        data_dict = self.querydict_to_dict(request.GET)
        logger.warn("Paybox process payment: Paybox data:{}".format(data_dict))
        is_valid_request = self.check_response(data_dict, payment.token)
        if not is_valid_request:
            raise PaymentError("Invalid sig")
        result = data_dict.get("pg_result")
        transaction_id = int(data_dict.get("pg_payment_id"))
        payment.transaction_id = transaction_id
        if result == "1":
            payment.change_status(PaymentStatus.CONFIRMED)
        elif result == "0":
            payment.change_status(PaymentStatus.REJECTED)
            pg_failure_code = data_dict.get("pg_failure_code", "")
            pg_failure_description = data_dict.get("pg_failure_description", "")
            payment.extra_data = "Code: {}; Description: {}".format(
                pg_failure_code, pg_failure_description
            )  # About error
        else:
            raise PaymentError("Unexpected pg_result value")
        logger.info("Success response for paybox")
        return HttpResponse("OK")
