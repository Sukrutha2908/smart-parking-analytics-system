from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.models.transaction_model import TransactionModel
from app.mongodb import transaction_collection


router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)


# =========================================================
# CREATE TRANSACTION
# =========================================================

@router.post("/")
def create_transaction(
    transaction: TransactionModel
):

    try:

        transaction_dict = (
            transaction.model_dump()
        )

        result = transaction_collection.insert_one(
            transaction_dict
        )

        return {

            "message":
                "Transaction Successful",

            "inserted_id":
                str(
                    result.inserted_id
                ),

            "data":
                transaction_dict
        }


    except HTTPException:
        raise


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


# =========================================================
# GET ALL TRANSACTIONS
# =========================================================

@router.get("/")
def get_transactions():

    try:

        transactions = list(

            transaction_collection
            .find(
                {},
                {
                    "_id": 0
                }
            )
            .sort(
                "transaction_time",
                -1
            )
        )


        if not transactions:

            raise HTTPException(
                status_code=404,
                detail="No Transactions Found"
            )


        return {

            "count":
                len(transactions),

            "data":
                transactions
        }


    except HTTPException:
        raise


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


# =========================================================
# GET TRANSACTION BY ID
# =========================================================

@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: str
):

    try:

        transaction = (
            transaction_collection
            .find_one(
                {
                    "transaction_id":
                        transaction_id
                },
                {
                    "_id": 0
                }
            )
        )


        if not transaction:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No Transaction Found "
                    f"for ID {transaction_id}"
                )
            )


        return {
            "data":
                transaction
        }


    except HTTPException:
        raise


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