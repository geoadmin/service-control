from access.api import router as access_router
from distributions.api import router as distributions_router
from ninja import NinjaAPI
from provider.api import router as provider_router

api = NinjaAPI()

api.add_router("", provider_router)
api.add_router("", distributions_router)
api.add_router("", access_router)
