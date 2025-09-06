from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

MONEY_QUANT = Decimal("0.01")

def as_money(value) -> Decimal:
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)

class PricingRule:
    label: str
    def apply(self, order) -> Tuple[str, Decimal]:
        raise NotImplementedError

class TaxRule(PricingRule):
    def __init__(self, label: str, rate: str | float | Decimal):
        self.label = label
        self.rate = Decimal(str(rate))
    def apply(self, order):
        tax = as_money(order.subtotal * self.rate)
        return (self.label, tax)

class ThresholdPercentDiscount(PricingRule):
    def __init__(self, label: str, threshold: str | float | Decimal, percent: str | float | Decimal):
        self.label = label
        self.threshold = as_money(threshold)
        self.percent = Decimal(str(percent))
    def apply(self, order):
        if order.subtotal >= self.threshold:
            discount = as_money(order.subtotal * self.percent) * Decimal("-1")
            return (self.label, discount)
        return (self.label, Decimal("0"))

class BuyXGetYFree(PricingRule):
    def __init__(self, label: str, item_id: str, x: int, y: int):
        self.label = label
        self.item_id = item_id
        self.x = int(x)
        self.y = int(y)
    def apply(self, order):
        # Find if order has the specific item
        line = next((l for l in order.lines.all() if l.item.id == self.item_id), None)
        if not line:
            return (self.label, Decimal("0"))
        group = self.x + self.y
        free_units = (line.qty // group) * self.y
        discount = as_money(line.item.price * free_units) * Decimal("-1")
        return (self.label, discount if free_units > 0 else Decimal("0"))

PRICING_RULES: List[PricingRule] = [
    ThresholdPercentDiscount("10% OFF on ₹500+", threshold="500", percent="0.10"),
    BuyXGetYFree("Buy 2 Get 1 Free (Fries)", item_id="S1", x=2, y=1),
    TaxRule("GST @ 5%", rate="0.05"),
]

def compute_adjustments(order) -> List[tuple[str, Decimal]]:
    return [rule.apply(order) for rule in PRICING_RULES]

def compute_total(order) -> Decimal:
    total = as_money(order.subtotal)
    for _, delta in compute_adjustments(order):
        total = as_money(total + delta)
    return total
