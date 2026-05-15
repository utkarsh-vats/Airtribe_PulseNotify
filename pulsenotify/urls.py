from django.contrib import admin
from django.urls import path, include

import pulse.urls as api_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
]
