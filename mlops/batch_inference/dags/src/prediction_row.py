from pydantic import BaseModel, validator

from .constants import (BOOLEAN_TYPES, CONTRACT_TYPES, GENDER_TYPES,
                        INTERNET_DEPENDENT_TYPES, INTERNET_SERVICE_TYPES,
                        MULTIPLE_LINES_TYPES, PAYMENT_METHOD_TYPES)


class DataRow(BaseModel):
    gender: str
    senior_citizen: str
    partner: str
    dependents: str
    phone_service: str
    multiple_lines: str
    internet_service: str
    online_security: str
    online_backup: str
    device_protection: str
    tech_support: str
    streaming_tv: str
    streaming_movies: str
    contract: str
    paperless_billing: str
    payment_method: str
    tenure: int
    monthly_charges: float
    total_charges: float

    @validator(
        'senior_citizen',
        'partner',
        'dependents',
        'phone_service',
        'paperless_billing'
    )
    def validate_yes_no(cls, v: str) -> str:
        if v in BOOLEAN_TYPES:
            return v
        raise ValueError('value must one of', BOOLEAN_TYPES)

    @validator('internet_service')
    def validate_internet_service(cls, v: str) -> str:
        if v in INTERNET_SERVICE_TYPES:
            return v
        raise ValueError('value must be one of', INTERNET_SERVICE_TYPES)

    @validator(
        'online_security',
        'online_backup',
        'device_protection',
        'tech_support',
        'streaming_tv',
        'streaming_movies'
    )
    def validate_internet_services(cls, v: str) -> str:
        if v in INTERNET_DEPENDENT_TYPES:
            return v
        raise ValueError('value must be one of', INTERNET_DEPENDENT_TYPES)

    @validator('gender')
    def validate_gender(cls, v: str) -> str:
        if v in GENDER_TYPES:
            return v
        raise ValueError('value must be one of', GENDER_TYPES)

    @validator('contract')
    def validate_contract(cls, v: str) -> str:
        if v in CONTRACT_TYPES:
            return v
        raise ValueError('value must be one of', CONTRACT_TYPES)

    @validator('payment_method')
    def validate_payment_method(cls, v: str) -> str:
        if v in PAYMENT_METHOD_TYPES:
            return v
        raise ValueError('value must be one of', PAYMENT_METHOD_TYPES)

    @validator('multiple_lines')
    def validate_multiple_lines(cls, v: str) -> str:
        if v in MULTIPLE_LINES_TYPES:
            return v
        raise ValueError('value must be one of', MULTIPLE_LINES_TYPES)

    @validator('tenure')
    def validate_tenure(cls, v: int) -> int:
        assert v >= 0, 'value must be positive'
        return v

    @validator('monthly_charges', 'total_charges')
    def validate_float(cls, v: float) -> float:
        assert v >= 0, 'value must be positive'
        return v
