from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, include
from django.views.generic import RedirectView

from a_psat.views import problem_list_view

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path('', problem_list_view, name='home'),
    path('', include('a_common.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon/favicon.ico'))),

    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('check_in_as_boss/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('components/', include('components.urls')),

    path('psat/', include('a_psat.urls')),
    path('police/', include('a_police.urls')),
    path('predict/', include('a_predict.urls')),
]
