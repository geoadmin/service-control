from distributions.api import router as distributions_router
from ninja import NinjaAPI
from provider.api import router as provider_router

root = NinjaAPI()
api = NinjaAPI()


@root.get('/checker')
def checker(request):
    return {"success": True, "message": " OK"}


api.add_router("/providers", provider_router)
api.add_router("", distributions_router)
