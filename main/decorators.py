from django.http import JsonResponse

def require_secret_cookie(view_func):
    """
    İsteğin çerezlerinde 'SecretCookie' olup olmadığını kontrol eden dekoratör.
    Eğer doğru çerez yoksa, 403 Forbidden hatası döndürür.
    """
    def wrapped_view(request, *args, **kwargs):
        if request.COOKIES.get("SecretCookie") != "Secret123":
            return JsonResponse({"error": "Forbidden"}, status=403)

        return view_func(request, *args, **kwargs)

    return wrapped_view
