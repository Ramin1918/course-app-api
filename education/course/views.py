from django.http.response import  (
    HttpResponse,
    HttpResponseRedirect,
    Http404,
    HttpResponseNotFound,
)
from django.shortcuts import render
from course.models import Material
from course.models import Kurs

from django.urls import reverse

def index(request):
    context = {
        "kurses": Kurs.objects.all(),
        "materials": Material.objects.all(),
    }
    return render(request, "index.html", context)
