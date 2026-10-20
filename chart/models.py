from django.conf import settings
from django.db import models


class SaveDetail(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_analyses",
        null=True,
        blank=True,
    )
    text = models.TextField(verbose_name="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
