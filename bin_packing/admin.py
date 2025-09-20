from django.contrib import admin
from .models import Panel


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ['id', 'csv_file', 'pdf_file', 'zip_file', 'created_at', 'updated_at']
    search_fields = ['id']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']