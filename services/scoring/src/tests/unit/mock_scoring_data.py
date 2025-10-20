from datetime import date

from app.api.scoring.schemas import ClientProfile, CreditHistoryItem, Product, UserData

MOCK_USER_DATA_SUCCESS = UserData(
    phone='79123456789',
    age=25,
    monthly_income=29999,
    employment_type='full_time',
    has_property=True
)

MOCK_USER_DATA_LOYALTY = UserData(
    phone='79123456789',
    age=25,
    monthly_income=29999,
    employment_type='full_time',
    has_property=False
)

MOCK_USER_DATA_REJECT = UserData(
    phone='79123456789',
    age=25,
    monthly_income=30000,
    employment_type='freelance',
    has_property=False
)

MOCK_USER_DATA_FAIL = UserData(
    phone='79123456789',
    age=15,
    monthly_income=45000,
    employment_type='freelance',
    has_property=False
)


MOCK_PRODUCTS_PIONEER = [
    Product(name='MicroLoan', max_amount=3000000,
            term_days=30, interest_rate_daily=2.0),
    Product(name='QuickMoney', max_amount=1500000,
            term_days=15, interest_rate_daily=2.5),
    Product(name='ConsumerLoan', max_amount=4500000,
            term_days=15, interest_rate_daily=2.5)
]

MOCK_PRODUCTS_REPEATER = [Product(name='LoyaltyLoan', max_amount=30000,
                                  term_days=100, interest_rate_daily=1.6),
                          Product(name='AdvantagePlus', max_amount=60000,
                                  term_days=100, interest_rate_daily=1.4),
                          Product(name='PrimeCredit', max_amount=90000,
                                  term_days=100, interest_rate_daily=1.2)]
FULL_PACK_PRODUCTS = MOCK_PRODUCTS_REPEATER
TWO_PRODUCTS = [Product(name='LoyaltyLoan', max_amount=30000,
                        term_days=100, interest_rate_daily=1.6),
                Product(name='AdvantagePlus', max_amount=60000,
                        term_days=100, interest_rate_daily=1.4)]

MOCK_CREDIT_HISTORY_GOOD = [CreditHistoryItem(
    product_name='QuickMoney',
    amount=30000000,
    issue_date=date(2023, 12, 12),
    term_days=30,
    status='closed',
    close_date=date(2024, 12, 12)
)]

MOCK_CREDIT_HISTORY_NORM = [CreditHistoryItem(
    product_name='QuickMoney',
    amount=3000000,
    issue_date=date(2025, 12, 12),
    term_days=30,
    status='closed',
    close_date=date(2025, 12, 12)
)]

MOCK_CREDIT_HISTORY_BAD = [CreditHistoryItem(
    product_name='QuickMoney',
    amount=3000000,
    issue_date=date(2024, 12, 12),
    term_days=30,
    status='open',
    close_date=None
)]

MOCK_TEST_PROFILE_SUCCESS = ClientProfile(
    user_data=MOCK_USER_DATA_SUCCESS, credit_history=MOCK_CREDIT_HISTORY_NORM)

MOCK_TEST_PROFILE_LOYALTY = ClientProfile(
    user_data=MOCK_USER_DATA_LOYALTY, credit_history=MOCK_CREDIT_HISTORY_NORM)

MOCK_TEST_PROFILE_BAD_BUT_GOOD_HISTORY = ClientProfile(
    user_data=MOCK_USER_DATA_REJECT, credit_history=MOCK_CREDIT_HISTORY_GOOD)

MOCK_TEST_PROFILE_LOW_AGE = ClientProfile(
    user_data=MOCK_USER_DATA_FAIL, credit_history=MOCK_CREDIT_HISTORY_NORM)

MOCK_TEST_PROFILE_LOW_POINTS = ClientProfile(
    user_data=MOCK_USER_DATA_REJECT, credit_history=MOCK_CREDIT_HISTORY_NORM)

MOCK_TEST_PROFILE_OPEN_CREDIT = ClientProfile(
    user_data=MOCK_USER_DATA_SUCCESS, credit_history=MOCK_CREDIT_HISTORY_BAD)

MOCK_TEST_PROFILE_FULL_POINTS = ClientProfile(
    user_data=MOCK_USER_DATA_SUCCESS, credit_history=MOCK_CREDIT_HISTORY_NORM
)

MOCK_PRODUCT_LOYALTY = [Product(name='LoyaltyLoan', max_amount=30000,
                                term_days=100, interest_rate_daily=1.6)]

MOCK_PRODUCT_ADVANTAGE = [Product(name='AdvantagePlus', max_amount=60000,
                                  term_days=100, interest_rate_daily=1.4)]

MOCK_PRODUCT_PRIMECREDIT = [Product(name='PrimeCredit', max_amount=90000,
                                    term_days=100, interest_rate_daily=1.2)]
