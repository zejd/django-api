from django.contrib import admin

# Register your models here.
from . import models

class CarAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "make",
        "model",
        "year"
    ]

admin.site.register(models.Car, CarAdmin)