# django-payments-paybox

> ⚠️⚠️⚠️ Not Ready
> This package in development. Do not use it.

This is [django-payments](https://github.com/mirumee/django-payments) provider for [PayBox.money](https://paybox.money/).

# Installation

```bash
pip install django-payments-paybox
```

Or with [poetry](https://python-poetry.org/)

```bash
poetry add django-payments-paybox
```

## Dependencies

This package require next deps:

- `django-payments`

# Configuration example

In `settings.py` you must connect this provider

```python
PAYMENT_VARIANTS = {
    "default": (
        "django_payments_provider.PayboxProvider",
        {
            "secret": "your_secret",
            "merchant_id": 1000000, # your merchant_id
            "site_url": "https://your_site.dev",
            "testing_mode": 1, # enabled by default
        },
    )
}
```

# Required methods in payment model

```python
from payments.models import BasePayment


class Payment(BasePayment):
    def get_failure_url(self):
        return "https://your_site.dev/failure/"

    def get_success_url(self):
        return "https://your_site.dev/success/"

    def get_process_url(self):
        path = super().get_process_url()
        return f"https://your_site.dev{path}"

```
