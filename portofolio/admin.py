from django.contrib import admin

from .models import Mahasiswa


@admin.register(Mahasiswa)
class MahasiswaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'npm')
    search_fields = ('nama', 'npm')
