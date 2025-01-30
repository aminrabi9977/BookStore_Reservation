from pydantic import BaseModel
class UserLogin(BaseModel):
    username: str
    password: str

class OTPVerification(BaseModel):
    username: str
    otp: str