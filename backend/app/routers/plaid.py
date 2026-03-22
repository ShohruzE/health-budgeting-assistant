from fastapi import APIRouter

import plaid
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from app.config import get_settings
from plaid.api import plaid_api

router = APIRouter(prefix="/plaid", tags=["plaid"])

PLAID_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "production": plaid.Environment.Production,
}

settings = get_settings()
configuration = plaid.Configuration(
    host=PLAID_ENV_MAP[settings.plaid_env],
    api_key={
        "clientId": settings.plaid_client_id,
        "secret": settings.plaid_secret,
    },
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


@router.get("/")
def test():
    return {"message": "Plaid API is working"}


@router.post("/create-link-token")
async def create_link_token():
    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(
            client_user_id="1234567890",
            legal_name="John Doe",
            phone_number="1234567890",
            email_address="john.doe@example.com",
        ),
        client_name="Nutrition and Budgeting Assistant",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en",
    )
    response = client.link_token_create(request)
    return {"link_token": response.link_token}


@router.post("/sandbox/create-public-token")
async def sandbox_create_public_token():
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",  # Institution ID for Chase Bank
        initial_products=[Products("transactions")],
    )
    response = client.sandbox_public_token_create(request)
    return {"public_token": response.public_token}


@router.post("/exchange-public-token")
async def exchange_public_token(public_token: str):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return {
        "access_token": response.access_token,
        "item_id": response.item_id,
    }
