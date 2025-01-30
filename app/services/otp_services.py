import random
from datetime import datetime, timedelta
from typing import Dict

class OTPService:
    _otps: Dict[str, Dict] = {}  
    
    @staticmethod
    def generate_otp(phone: str) -> str:
        otp = str(random.randint(100000, 999999))
        expiry = datetime.now() + timedelta(minutes=5)
        
        OTPService._otps[phone] = {
            "code": otp,
            "expiry": expiry,
            "attempts": 0
        }
        
        print(f"OTP for {phone}: {otp}")
        return otp

    @staticmethod
    def verify_otp(phone: str, otp: str) -> bool:
        otp_data = OTPService._otps.get(phone)
        if not otp_data:
            return False
            
        if datetime.now() > otp_data["expiry"]:
            OTPService._otps.pop(phone)
            return False
            
        if otp_data["attempts"] >= 3:
            OTPService._otps.pop(phone)
            return False
            
        OTPService._otps[phone]["attempts"] += 1
        
        if otp_data["code"] != otp:
            return False
            
        OTPService._otps.pop(phone)
        return True