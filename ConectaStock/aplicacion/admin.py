from django.contrib import admin
from .models import (
    Categoria, Proveedor, Vendedor, SolicitudVendedor, 
    Tienda, NotificacionTienda, Producto, Pedido, DetallePedido, SolicitudVisita
)

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'ruc', 'tipo', 'es_verificado')
    search_fields = ('nombre_empresa', 'ruc', 'correo')
    raw_id_fields = ('usuario',)

class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'ciudad', 'sector')
    search_fields = ('nombre', 'apellido', 'cedula', 'correo')
    raw_id_fields = ('usuario',)

class SolicitudVendedorAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'proveedor', 'estado', 'comision')
    search_fields = ('vendedor__nombre', 'vendedor__apellido', 'proveedor__nombre_empresa')
    list_filter = ('estado',)
    raw_id_fields = ('vendedor', 'proveedor')

class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre_tienda', 'cedula', 'nombre_propietario', 'apellido_propietario')
    search_fields = ('nombre_tienda', 'cedula', 'correo')
    raw_id_fields = ('usuario',)

class NotificacionTiendaAdmin(admin.ModelAdmin):
    list_display = ('tienda', 'sector', 'fecha_creacion', 'activa')
    list_filter = ('activa', 'sector')
    raw_id_fields = ('tienda',)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'precio_unitario', 'stock_disponible', 'categoria', 'proveedor')
    search_fields = ('sku', 'nombre')
    list_filter = ('categoria',)
    raw_id_fields = ('proveedor', 'categoria')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'fecha', 'vendedor', 'tienda', 'estado')
    search_fields = ('numero_pedido',)
    list_filter = ('estado', 'metodo_pago')
    raw_id_fields = ('vendedor', 'tienda', 'proveedor')

class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    raw_id_fields = ('pedido', 'producto')

class SolicitudVisitaAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'tienda', 'fecha_solicitud', 'estado')
    list_filter = ('estado',)
    raw_id_fields = ('vendedor', 'tienda')

# Registro de Modelos y sus respectivas clases Admin
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Vendedor, VendedorAdmin)
admin.site.register(SolicitudVendedor, SolicitudVendedorAdmin)
admin.site.register(Tienda, TiendaAdmin)
admin.site.register(NotificacionTienda, NotificacionTiendaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido, DetallePedidoAdmin)
admin.site.register(SolicitudVisita, SolicitudVisitaAdmin)
