def admin_context(request):
    es_admin = False
    if request.user.is_authenticated:
        es_admin = request.user.groups.filter(name='Administradores').exists()
    return {'es_admin': es_admin}
