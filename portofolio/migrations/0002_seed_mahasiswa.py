from django.db import migrations


STUDENTS = [
    (f'Mahasiswa {number}', f'25000000{number:02d}')
    for number in range(1, 11)
]


def seed_mahasiswa(apps, schema_editor):
    mahasiswa_model = apps.get_model('portofolio', 'Mahasiswa')
    mahasiswa_model.objects.bulk_create(
        [mahasiswa_model(nama=nama, npm=npm) for nama, npm in STUDENTS],
        ignore_conflicts=True,
    )


def remove_mahasiswa(apps, schema_editor):
    mahasiswa_model = apps.get_model('portofolio', 'Mahasiswa')
    mahasiswa_model.objects.filter(nama__in=[nama for nama, _ in STUDENTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('portofolio', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_mahasiswa, remove_mahasiswa),
    ]
