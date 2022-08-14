from re import template
from django.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include("accounts.urls")),
    path('api/filesystem/',include("fileSystem.urls")),
    path('api/transfer/',include("transfer.urls")),
    path('api/share/',include("share.urls")),
    # path(r'index', index.as_view(template_name='index.html')),
]