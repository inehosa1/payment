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
        title="Rest app para la creacion de cuentas y gestion de transaciones",
        default_version='v1',
        description="""        
        * Crear cuentas, especificando un balance inicial y nombre. 
        * Listar todas las cuentas con sus balances. 
        * Obtener un detalle de cuenta completo, con monto, id, balance y  con todas sus transacciones ordenadas por fecha. 
        * Tener un endpoint para crear y eliminar transacciones. Las  transacciones pueden ser ingresos o egresos de dinero en una  cuenta. No tiene que haber endpoint para modificar las  
        transacciones, solo uno para la creación y otro para la eliminación  de transacciones. 
        * Crear un endpoint para cambiar el balance de una cuenta,  especificando el balance nuevo como un número. Como si fuera  una operación de ajuste manual. (ver detalle sobre lógica más  abajo) 
        * Crear endpoint para obtener todas las transacciones de una cuenta  en un mes y año particular. 
        * Crear un endpoint para hacer un movimiento de dinero de una  cuenta a otra. Este endpoint tiene que disparar la creación de  transacciones (con detalle "movimiento entre cuentas") para reflejar  el cambio de balance entre las dos cuentas. 
        * Configurar acceso al Admin de django para ver los registros y que el  balance de las cuentas no se pueda editar (readonly o similar).         
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
