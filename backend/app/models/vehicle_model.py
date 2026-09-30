from pydantic import BaseModel, field_validator
import re


class VehicleModel(BaseModel):

    vehicle_id: int
    vehicle_number: str
    vehicle_type: str
    owner_name: str
    owner_phone: str

    @field_validator("vehicle_number")
    @classmethod
    def validate_vehicle_number(cls, value):

        value = value.strip().upper()

        # Indian vehicle registration format
        # Example: AP23TR2345
        pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$"

        if not re.fullmatch(pattern, value):
            raise ValueError(
                "Invalid vehicle number. Example: AP23TR2345"
            )

        return value