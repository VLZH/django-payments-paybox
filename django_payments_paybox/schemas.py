import enum
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, IPvAnyAddress


class PayboxCurrency(enum.Enum):
    KZT = "KZT"
    USD = "USD"
    EUR = "EUR"
    KGS = "KGS"


class PayboxOnOff(enum.Enum):
    ON = 1
    OFF = 0


class PayboxLanguage(enum.Enum):
    RU = "ru"
    EN = "en"


class PayboxRequestMethod(enum.Enum):
    GET = "GET"
    POST = "POST"
    XML = "XML"


class PayboxInitPaymentData(BaseModel):
    pg_merchant_id: int
    pg_order_id: str
    pg_amount: int
    pg_currency: Optional[PayboxCurrency]
    pg_payment_system: Optional[str]
    pg_lifetime: Optional[int]
    pg_description: str
    pg_postpone_payment: Optional[PayboxOnOff]
    pg_language: Optional[PayboxLanguage]
    pg_testing_mode: Optional[PayboxOnOff]
    # urls
    pg_check_url: Optional[HttpUrl]
    pg_result_url: Optional[HttpUrl]
    pg_refund_url: Optional[HttpUrl]
    pg_capture_url: Optional[HttpUrl]
    pg_success_url: Optional[HttpUrl]
    pg_failure_url: Optional[HttpUrl]
    pg_state_url: Optional[HttpUrl]
    pg_site_url: Optional[HttpUrl]
    # request methods
    pg_request_method: Optional[PayboxRequestMethod]
    pg_success_url_method: Optional[PayboxRequestMethod]
    pg_failure_url_method: Optional[PayboxRequestMethod]
    pg_state_url_method: Optional[PayboxRequestMethod]
    # user
    pg_user_phone: Optional[str]
    pg_user_contact_email: Optional[EmailStr]
    pg_user_ip: Optional[IPvAnyAddress]
    # recurring
    pg_recurring_start: Optional[PayboxOnOff]
    pg_recurring_lifetime: Optional[int]
    # sig
    pg_salt: str
    pg_sig: Optional[str]


class PayboxRedirectUrlType(enum.Enum):
    NEED_DATA = "need data"
    PAYMENT_SYSTEM = "payment system"


class PayboxInitResponseStatus(enum.Enum):
    OK = "ok"
    ERROR = "error"


class PayboxInitPaymentResponse(BaseModel):
    pg_status: PayboxInitResponseStatus
    # success
    pg_payment_id: Optional[int]
    pg_redirect_url: Optional[HttpUrl]
    pg_redirect_url_type: Optional[PayboxRedirectUrlType]
    pg_salt: Optional[str]
    pg_sig: Optional[str]
    # error
    pg_error_code: Optional[str]
    pg_error_description: Optional[str]


class PayboxCheckUrlData(BaseModel):
    pg_order_id: str
    pg_payment_id: int
    pg_amount: int
    pg_currency: PayboxCurrency
    pg_ps_currency: PayboxCurrency
    pg_ps_amount: int
    pg_ps_full_amount: int
    pg_payment_system: str
    pg_salt: str
    pg_sig: Optional[str]


class PayboxProviderOptions(BaseModel):
    merchant_id: int
    secret: str
    site_url: HttpUrl
    testing_mode: PayboxOnOff = PayboxOnOff.ON
