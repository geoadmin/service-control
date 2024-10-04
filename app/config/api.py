from distributions.api import router as distributions_router
from ninja import NinjaAPI, Router
from provider.api import router as provider_router

from django.http.request import HttpRequest

root = NinjaAPI()


# we don't want to have checker underneath /api but still use the
# ninja functionality
@root.get('/checker')
def checker(request: HttpRequest) -> dict[str, bool | str]:
    return {"success": True, "message": " OK"}


api = Router()
api.add_router("/providers", provider_router)
api.add_router("/distributions", distributions_router)

root.add_router('api', api)
