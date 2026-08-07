from django.urls import path

from . import views


urlpatterns = [

    path(
        "servers/",
        views.server_list,
        name="server_list"
    ),

]