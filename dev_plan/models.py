from django.db import models

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    development_plan = models.TextField(blank=True)

    def __str__(self):
        return self.file.name
