from dataclasses import dataclass
from decimal import Decimal
from src.exceptions import SavdoLinkError


class CurrencyMismatchError(SavdoLinkError):
    """Turli valyutadagi summalar ustida amal bajarishga urinish."""


@dataclass(frozen=True)          # frozen=True -> o'zgarmas (immutable)
class Money:
    """Pul qiymati: summa va valyuta birga yuriladi.

    O'zgarmas: har bir amal YANGI Money qaytaradi, o'zini o'zgartirmaydi.
    """

    amount: Decimal
    currency: str = "UZS"

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

    # --- ko'rinish ---
    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"

    def __str__(self):
        return f"{self.amount:,.2f} {self.currency}".replace(",", " ")

    # --- taqqoslash ---
    def _check(self, other):
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"{self.currency} != {other.currency}")

    def __eq__(self, other):
        return (isinstance(other, Money)
                and self.amount == other.amount
                and self.currency == other.currency)

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __lt__(self, other):
        self._check(other)
        return self.amount < other.amount

    # --- arifmetika ---
    def __add__(self, other):
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor):
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __bool__(self):
        return self.amount != 0
