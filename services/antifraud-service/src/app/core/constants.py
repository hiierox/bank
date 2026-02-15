B1_MIN_AGE: int = 18
B2_MIN_INCOME: int = 10000
B3_DISALLOWED_EMPLOYMENT_TYPES: list[str] = ['unemployed']

P1_MAX_APPLICATIONS: int = 3
P1_CHECK_PERIOD_HOURS: int = 24
P2_MIN_INCOME_WITH_PROPERTY: int = 30000

R2_PROFILE_CHECK_DAYS: int = 30
R2_INCOME_GROWTH_FACTOR: float = 2
R2_INCOME_FALL_FACTOR: float = 0.5


REJECT_REASON_B1: str = f'Возраст меньше {B1_MIN_AGE}'
REJECT_REASON_B2: str = 'Доход меньше 10000'
REJECT_REASON_B3: str = 'Статус занятости: unemployed'

REJECT_REASON_P1: str = f'Лимит {P1_MAX_APPLICATIONS} ежедневных заявок превышен'
REJECT_REASON_P2: str = 'Недвижимость при низком доходе < 30000'

REJECT_REASON_R1: str = 'Имеется overdue кредит'
REJECT_REASON_R2_INCOME_GROWTH: str = 'Значительное увеличение дохода (x2)'
REJECT_REASON_R2_INCOME_FALL: str = 'Значительное падение дохода (0.5x)'
REJECT_REASON_R2_EMPLOYMENT_CHANGE: str = 'Изменение занятости на freelance, unemployed'
