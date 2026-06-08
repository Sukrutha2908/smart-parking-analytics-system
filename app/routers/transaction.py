from fastapi import APIRouter

from app.models.transaction_model import TransactionModel

router = APIRouter(
prefix="/transaction",
tags=["Transaction"]
)

# Create Transaction

@router.post("/")
def create_transaction(transaction: TransactionModel):
    return {
        "message": "Transaction Successful",
        "data": transaction
    }

# Get Transactions

@router.get("/")
def get_transactions():

    return {
        "message": "All Transactions"
    }

# Get Transaction By ID

@router.get("/{transaction_id}")
def get_transaction(transaction_id: int):

    return {
        "message": f"Transaction Details for ID {transaction_id}"
    }