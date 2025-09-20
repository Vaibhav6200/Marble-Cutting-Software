from django.db import models
import uuid


class Panel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    csv_file = models.FileField(upload_to='csv', null=True, blank=True)
    zip_file = models.FileField(upload_to='zip', null=True, blank=True)
    json_file = models.JSONField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='pdf', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

