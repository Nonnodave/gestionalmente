from django.contrib import admin
from .models import Sottocampo, Campo, Prodotto, CampoSottocampo, Societa, CustomUser

# Register your models here.
admin.register(Sottocampo)
admin.register(Campo)
admin.register(Prodotto)
admin.register(CampoSottocampo)
admin.register(Societa)

admin.site.register(CustomUser)