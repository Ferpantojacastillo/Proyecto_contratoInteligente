from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.lista_actividades, name='lista_actividades'),

    
    path('registrar/', views.registrar_actividad, name='registrar_actividad'),

    
    path('panel/', views.panel_actividades, name='panel_actividades'),

    
    path('<int:id_actividad>/', views.detalle_actividad, name='detalle_actividad'),

    
    path('<int:id_actividad>/inscribirse/', views.inscribirse, name='inscribirse'),

    
    path('<int:id_actividad>/registrar_credito/<int:id_usuario>/', views.registrar_credito, name='registrar_credito'),
    
    path('<int:id_actividad>/liberar/', views.liberar_actividad, name='liberar_actividad'),
]


