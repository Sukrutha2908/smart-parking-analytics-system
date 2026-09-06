from pydantic import BaseModel
from datetime import datetime

class TransactionModel(BaseModel):
	transaction_id: int
	vehicle_id: int
	amount: float
	payment_method: str
	transaction_time: datetime