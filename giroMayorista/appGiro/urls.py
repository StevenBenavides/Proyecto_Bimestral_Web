from django.urls import path
from . import views

urlpatterns = [
        # Nuevas rutas de Autenticación y Landing Page
        path('', views.landing_page, name='landing'),
        path('login/', views.login_view, name='login'),
        path('logout/', views.logout_view, name='logout'),
        path('registro/trabajador/', views.registro_trabajador_view, name='registro_trabajador'),
        path('registro/proveedor/', views.registro_proveedor_view, name='registro_proveedor'),
        
        # Proveedor Dashboard
        path('proveedor/', views.dashboard_proveedor, name='dashboard_proveedor'),
        path('proveedor/pedidos/', views.trazabilidad_proveedor, name='trazabilidad_proveedor'),
        

        path('panel/', views.index, name='index'),
        path('vendedor/<int:id>', views.obtener_vendedor, name='obtener_vendedor'),
        path('crear/vendedor', views.crear_vendedor, name='crear_vendedor'),
        path('editar_vendedor/<int:id>', views.editar_vendedor, name='editar_vendedor'),
        path('eliminar/vendedor/<int:id>', views.eliminar_vendedor, name='eliminar_vendedor'),
            
        # Cliente
        path('crear/cliente', views.crear_cliente, name='crear_cliente'),
        path('editar_cliente/<int:id>', views.editar_cliente, name='editar_cliente'),
            
        # Pedido Asociado a Cliente
        path('crear/pedido/cliente/<int:id>', views.crear_pedido_cliente, name='crear_pedido_cliente'),
        
        # Trazabilidad
        path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
            
        # Dashboard Admin
        path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
]
