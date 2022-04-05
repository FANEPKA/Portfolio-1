from decimal import Decimal
from config import cashier


def get_pay_url(amount):
    invoice = cashier.create_bill(
        amount=Decimal(f"{amount}"),
        currency='RUB',
        comment='Golden Alex')
    return invoice.pay_url, invoice.bill_id
