from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/proveedor/', views.crear_proveedor, name='crear_proveedor'),
    path('crear/vendedor/', views.crear_vendedor, name='crear_vendedor'),
    path('crear/tienda/', views.crear_tienda, name='crear_tienda'),
    path('crear/producto/', views.crear_producto, name='crear_producto'),
    path('proveedor/<int:id>/', views.obtener_proveedor, name='obtener_proveedor'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    
    # Rutas del Dashboard de Proveedor
    path('dashboard/proveedor/', views.dashboard_proveedor, name='dashboard_proveedor'),
    path('dashboard/proveedor/productos/', views.mis_productos, name='mis_productos'),
    path('dashboard/proveedor/productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('dashboard/proveedor/productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('dashboard/proveedor/vendedores/', views.mis_vendedores, name='mis_vendedores'),
    path('dashboard/proveedor/vendedores/aprobar/<int:id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('dashboard/proveedor/pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('dashboard/proveedor/pedidos/gestionar/<int:id>/', views.gestionar_pedido, name='gestionar_pedido'),
    
    # Rutas del Dashboard de Vendedor
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
    path('dashboard/vendedor/proveedores/explorar/', views.explorar_proveedores, name='explorar_proveedores'),
    path('dashboard/vendedor/proveedores/solicitar/<int:proveedor_id>/', views.enviar_solicitud, name='enviar_solicitud'),
    path('dashboard/vendedor/proveedores/mis-redes/', views.mis_proveedores_asociados, name='mis_proveedores_asociados'),
    path('dashboard/vendedor/pedidos/nuevo/<int:proveedor_id>/', views.crear_pedido_vendedor, name='crear_pedido_vendedor'),
    path('dashboard/vendedor/pedidos/historial/', views.historial_pedidos_vendedor, name='historial_pedidos_vendedor'),
    path('dashboard/vendedor/notificaciones/', views.notificaciones_vendedor, name='notificaciones_vendedor'),
]
