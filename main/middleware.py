from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse

class SwaggerAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith("/api/swagger/"):
            secret_key = request.COOKIES.get("swagger_secret_key")
            if secret_key != "XxCN-F\REKgsf9)1q.lc41)X=G<U6bgsT,:ATt.BYm":
                return HttpResponseNotFound("Page not found")

        return self.get_response(request)



class AdminCookieMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ["/admin/", "/api/add-company/",'/api/update-disclosure-status/','/api/add-disclosures/']

        if any(request.path.startswith(path) for path in protected_paths):
            cookie_value = request.COOKIES.get("admin_secret_key")
            if cookie_value != "v7KS&a$a!e4VcLK0Q9DQYM31&*OlE]u8~{sdP,Hb":
                return HttpResponseNotFound("Page not found.")

        return self.get_response(request)
    
