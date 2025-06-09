from pydantic import BaseModel, EmailStr, Field, field_validator


class VerifyCode(BaseModel):
    code: str
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if len(value) != 6:
            raise ValueError("Код должен быть длинной в 6 символов")
        if not value.isdigit():
            raise ValueError("Код должен состоять только из цифрерных символов")
        
        return value