from ninja import NinjaAPI

api = NinjaAPI()


@api.get('/checker')
def checker(request):
    return {"success": True, "message": " OK"}
