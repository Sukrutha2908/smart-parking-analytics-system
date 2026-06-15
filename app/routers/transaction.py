from fastapi import APIRouter, HTTPException

from app.models.transaction_model import TransactionModel

router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)

@router.post("/")
def create_transaction(transaction: TransactionModel):

    try:

        transaction_dict = transaction.dict()

        return {
            "message": "Transaction Successful",
            "data": transaction_dict
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/")
def get_transactions():

    try:

        transactions = []

        if not transactions:

            raise HTTPException(
                status_code=404,
                detail="No Transactions Found"
            )

        return {
            "count": len(transactions),
            "data": transactions
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/{transaction_id}")
def get_transaction(transaction_id: int):

    try:

        transaction = None

        if not transaction:

            raise HTTPException(
                status_code=404,
                detail=f"No Transaction Found for ID {transaction_id}"
            )

        return {
            "data": transaction
        }

    except HTTPException as e:
        raise e

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )