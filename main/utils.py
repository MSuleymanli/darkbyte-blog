from django.http import HttpResponseForbidden
from functools import wraps

def admin_cookie_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.COOKIES.get("admin_secret_key") != "v7KS&a$a!e4VcLK0Q9DQYM31&*OlE]u8~{sdP,Hb":
            return HttpResponseForbidden("Page not found.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
