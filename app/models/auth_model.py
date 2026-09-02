from pydantic import BaseModel, Field, EmailStr, field_validator


# =========================================================
# USER REGISTRATION
# =========================================================

class UserRegister(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=100
    )


    # -----------------------------------------------------
    # Validate password requirements
    # -----------------------------------------------------

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):

        if not any(
            char.isupper()
            for char in password
        ):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(
            char.islower()
            for char in password
        ):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not any(
            char.isdigit()
            for char in password
        ):
            raise ValueError(
                "Password must contain at least one number"
            )

        if not any(
            not char.isalnum()
            for char in password
        ):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return password


    # -----------------------------------------------------
    # Validate password confirmation
    # -----------------------------------------------------

    def model_post_init(self, __context):

        if self.password != self.confirm_password:

            raise ValueError(
                "Passwords do not match"
            )


# =========================================================
# USER LOGIN
# =========================================================

class UserLogin(BaseModel):

    username: str = Field(
        min_length=1,
        max_length=50
    )

    password: str = Field(
        min_length=1,
        max_length=100
    )


# =========================================================
# JWT TOKEN
# =========================================================

class Token(BaseModel):

    access_token: str

    token_type: str


# =========================================================
# USER RESPONSE
# =========================================================

class UserResponse(BaseModel):

    username: str

    email: EmailStr