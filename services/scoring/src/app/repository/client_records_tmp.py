from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.api.scoring.schemas import ClientProfile, CreditHistoryItem, UserData

PERFECT_REPEATER_PROFILE = ClientProfile(
    user_data=UserData(
        phone='79123456789',
        age=35,
        monthly_income=6000000,
        employment_type='full_time',
        has_property=True
    ),
    credit_history=[
        CreditHistoryItem(
            product_name='MicroLoan',
            amount=3000000,
            issue_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=450),
            term_days=30,
            status='closed',
            close_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=400)
        ),
        CreditHistoryItem(
            product_name='AdvantagePlus',
            amount=12000000,
            issue_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=100),
            term_days=90,
            status='closed',
            close_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=10)
        )
    ]
)


RISKY_REPEATER_PROFILE = ClientProfile(
    user_data=UserData(
        phone='71234567890',
        age=25,
        monthly_income=2500000,
        employment_type='freelance',
        has_property=False
    ),
    credit_history=[
        CreditHistoryItem(
            product_name='MicroLoan',
            amount=2000000,
            issue_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=60),
            term_days=30,
            status='closed',
            close_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=30)
        )
    ]
)


REJECTED_REPEATER_PROFILE = ClientProfile(
    user_data=UserData(
        phone='79876543210',
        age=18,
        monthly_income=2000000,
        employment_type='full_time',
        has_property=False
    ),
    credit_history=[
        CreditHistoryItem(
            product_name='QuickMoney',
            amount=10000000,
            issue_date=datetime.now(tz=ZoneInfo(
                'UTC')).date() - timedelta(days=200),
            term_days=90,
            status='open',
            close_date=None
        )
    ]
)
