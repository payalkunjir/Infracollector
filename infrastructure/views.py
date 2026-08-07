from django.shortcuts import render, redirect

from .models import Server
from django.contrib import messages

def server_list(request):

    servers = Server.objects.all().order_by("-created_at")

    return render(
        request,
        "infrastructure/server_list.html",
        {
            "servers": servers
        }
    )


