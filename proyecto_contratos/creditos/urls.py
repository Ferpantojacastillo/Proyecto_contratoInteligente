from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_creditos, name='panel_creditos'),
    path('mis_creditos/', views.mis_creditos, name='mis_creditos'),
    path('crear/', views.crear_credito, name='crear_credito'),
    path('solicitar/', views.solicitar_credito, name='solicitar_credito'),
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/<int:id_solicitud>/aprobar/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('solicitudes/<int:id_solicitud>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('firmar/alumno/<int:id_credito>/', views.firmar_por_alumno, name='firmar_por_alumno'),
    path('firmar/admin/<int:id_credito>/', views.firmar_por_admin, name='firmar_por_admin'),
    path('wallet/', views.wallet, name='wallet'),
    path('liberar/<int:id_credito>/', views.liberar_credito, name='liberar_credito'),
        path('contrato/<int:id_credito>/', views.contrato, name='contrato'),
    path('admin/lista/', views.lista_creditos_admin, name='lista_creditos_admin'),
    path('admin/asignar/<int:id_credito>/', views.asignar_credito, name='asignar_credito'),
]


