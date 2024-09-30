from ninja import NinjaAPI
from provider.api import router as provider_router

root = NinjaAPI()
api = NinjaAPI()


@root.get('/checker')
def checker(request):
    return {"success": True, "message": " OK"}


api.add_router("/providers", provider_router)
