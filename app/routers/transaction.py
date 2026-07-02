from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.transaction_model import TransactionModel

router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)

# Create Transaction
@router.post("/")
def create_transaction(transaction: TransactionModel):

    try:
        # Convert model to dictionary
        transaction_dict = transaction.model_dump()

        # Future MongoDB insert
        # result = transaction_collection.insert_one(transaction_dict)

        return {
            "message": "Transaction Successful",
            "data": transaction_dict
        }

    except HTTPException as e:
        raise e

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )


# Get Transactions
@router.get("/")
def get_transactions():

    try:
        # Example empty list
        transactions = []

        # Future MongoDB fetch
        # transactions = list(
        #     transaction_collection.find({}, {"_id": 0})
        # )

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

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )


# Get Transaction By ID
@router.get("/{transaction_id}")
def get_transaction(transaction_id: int):

    try:
        # Example dummy data
        transaction = None

        # Future MongoDB query
        # transaction = transaction_collection.find_one(
        #     {"transaction_id": transaction_id},
        #     {"_id": 0}
        # )

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

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )