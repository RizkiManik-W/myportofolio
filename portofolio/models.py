from django.db import models


class Mahasiswa(models.Model):
    nama = models.CharField(max_length=30)
    npm = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.nama} ({self.npm})'
