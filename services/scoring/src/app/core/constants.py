from typing import Any

AGE_POINTS_RULES: list[dict[str, Any]] = [
    {'min': 18, 'max': 25, 'points': 1},
    {'min': 26, 'max': 40, 'points': 3},
    {'min': 41, 'max': float('inf'), 'points': 2}
]
INCOME_POINTS: list[dict[str, Any]] = [
    {'min': 1000000, 'max': 2999900, 'points': 1},
    {'min': 3000000, 'max': 5000000, 'points': 2},
    {'min': 5000001, 'max': float('inf'), 'points': 3}
]
EMPLOYMENT_TYPE: list[dict[str, Any]] = [
    {'type': 'freelance', 'points': 1},
    {'type': 'full_time', 'points': 3}
]
PIONEER_PRODUCTS_POINTS: list[dict[str, Any]] = [
    {'min': 5, 'max': 6, 'name': 'MicroLoan'},
    {'min': 7, 'max': 8, 'name': 'QuickMoney'},
    {'min': 9, 'max': 100, 'name': 'ConsumerLoan'}
]
REJECT_RESPONSE = {'decision': 'rejected', 'product': None}
REPEATER_PRODUCTS_POINTS: list[dict[str, Any]] = [
    {'min': 6, 'max': 7, 'decision': 'accepted', 'name': 'LoyaltyLoan'},
    {'min': 8, 'max': 9, 'decision': 'accepted', 'name': 'AdvantagePlus'},
    {'min': 10, 'max': 100, 'decision': 'accepted', 'name': 'PrimeCredit'},
]
LAST_CREDIT_AMOUNT_POINTS: list[dict[str, Any]] = [
        {'min': 0, 'max': 4999900, 'points': 1},
        {'min': 5000000, 'max': 10000000, 'points': 2},
        {'min': 10000001, 'max': float('inf'), 'points': 3},
    ]
FIRST_CREDIT_AGE_DAYS = 365
FIRST_CREDIT_POINTS = 3
