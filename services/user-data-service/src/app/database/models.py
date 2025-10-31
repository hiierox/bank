from datetime import date
from typing import Literal

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    """Пользователь"""

    __tablename__ = 'users'
    phone: Mapped[str] = mapped_column(String, primary_key=True)
    age: Mapped[int]
    monthly_income: Mapped[int]
    employment_type: Mapped[Literal['full_time', 'freelance']]
    has_property: Mapped[bool]

    loans: Mapped[list['Loan']] = relationship(
        back_populates='user',
        cascade='all, delete'
    )


class Loan(Base):
    """Кредит пользователя"""

    __tablename__ = 'loans'
    loan_id: Mapped[str] = mapped_column(String, primary_key=True)
    product_name: Mapped[str]
    amount: Mapped[int]
    issue_date: Mapped[date]
    term_days: Mapped[int]
    status: Mapped[str]
    close_date: Mapped[date | None]

    user_phone: Mapped['User'] = mapped_column(ForeignKey('users.phone'))
    user: Mapped['User'] = relationship(back_populates='loans')
