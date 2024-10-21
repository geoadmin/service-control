from distributions.api import router as distributions_router
from ninja import NinjaAPI
from provider.api import router as provider_router

api = NinjaAPI()

api.add_router("providers", provider_router)
api.add_router("distributions", distributions_router)
