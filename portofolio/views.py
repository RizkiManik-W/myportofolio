from django.shortcuts import render

mhs_name = "Putu Rizki Manik Widiadnyana"

def index(request):
    response = {'name' : mhs_name}
    return render(request,'index.html',response)