"""payment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Rest app para la gestión de pedidos",
        default_version='v1',
        description="""
        * Agendar un pedido a un conductor en una fecha y hora, y especificar su lugar de recogida (latitud y longitud) y destino. 
        * Consultar todos los pedidos asignados en un día en específico ordenados por la hora. 
        * Consultar todos los pedidos de un conductor en un día en específico ordenados por la hora. 
        * Hacer búsquedas del conductor que esté más cerca de un punto geográfico en una fecha y hora. (Tener en consideración los pedidos ya asignados al conductor).         
        """,
        contact=openapi.Contact(email="chanix1998@gmail.com"),

   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('transations/', include('transations.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
