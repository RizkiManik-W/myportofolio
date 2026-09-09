from django.shortcuts import render

from .models import Mahasiswa

mhs_name = "Putu Rizki Manik Widiadnyana"

def index(request):
    response = {
        'name': mhs_name,
        'mahasiswa_list': Mahasiswa.objects.all(),
    }
    return render(request,'index.html',response)