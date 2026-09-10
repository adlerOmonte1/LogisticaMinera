def ip_del_cliente(request) -> str | None:
    if request is None:
        return None
    adelante = request.META.get("HTTP_X_FORWARDED_FOR")
    if adelante:
        return adelante.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
