from django.db import models

class TextEntry(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:200]
