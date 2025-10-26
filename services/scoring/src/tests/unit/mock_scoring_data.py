from app.api.scoring.schemas import Product, UserData

MOCK_PRODUCTS_REPEATER = [Product(name='LoyaltyLoan', max_amount=30000,
                                  term_days=100, interest_rate_daily=1.6),
                          Product(name='AdvantagePlus', max_amount=60000,
                                  term_days=100, interest_rate_daily=1.4),
                          Product(name='PrimeCredit', max_amount=90000,
                                  term_days=100, interest_rate_daily=1.2)]


MOCK_USER_DATA_PIONEER_ACCEPTED = UserData(
    phone='79112223344',
    age=30,
    monthly_income=5000000,
    employment_type='full_time',
    has_property=True
)

MOCK_USER_DATA_PIONEER_REJECTED_SCORE = UserData(
    phone='79223334455',
    age=20,
    monthly_income=0,
    employment_type='freelance',
    has_property=False
)


MOCK_USER_DATA_PIONEER_REJECTED_STOP_FACTOR = UserData(
    phone='79334445566',
    age=17,
    monthly_income=10000000,
    employment_type='full_time',
    has_property=True
)


MOCK_REPEATER_PROFILE_JSON = {
    'phone': '79556667788',
    'profile': {
        'age': 45,
        'monthly_income': 10000000,
        'employment_type': 'full_time',
        'has_property': True,
    },
    'history': [
        {
            'loan_id': 'loan_1', 'product_name': 'OldCredit', 'amount': 5000000,
            'issue_date': '2023-01-01', 'term_days': 30, 'status': 'closed', 'close_date': '2023-02-01'
        }
    ]
}


MOCK_PRODUCTS_PIONEER = [
    Product(name='MicroLoan', max_amount=30000, term_days=30, interest_rate_daily=1.0),
    Product(name='QuickMoney', max_amount=60000, term_days=60, interest_rate_daily=0.8),
    Product(name='ConsumerLoan', max_amount=120000, term_days=90, interest_rate_daily=0.5),
]

MOCK_PRODUCTS_REPEATER = [
    Product(name='LoyaltyLoan', max_amount=500000, term_days=100, interest_rate_daily=0.4),
    Product(name='AdvantagePlus', max_amount=1200000, term_days=120, interest_rate_daily=0.3),
    Product(name='PrimeCredit', max_amount=5000000, term_days=180, interest_rate_daily=0.2),
]
