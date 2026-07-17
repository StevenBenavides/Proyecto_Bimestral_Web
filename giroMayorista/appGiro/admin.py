from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Vendedor, Cliente, Categoria, Producto, Pedido, DetallePedido, Inventario

@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    list_display = ('id', 'nombreCategoria', 'descripcion')

@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    list_display = ('codigoSKU', 'nombre', 'precioUnitario', 'stockDiponible', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('codigoSKU', 'nombre')

@admin.register(Vendedor)
class VendedorAdmin(ImportExportModelAdmin):
    list_display = ('nombre', 'apellido', 'rutaAsignada', 'metaActual')

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    list_display = ('nombreTienda', 'propietario', 'direccion', 'rutaId')

# Estos los dejamos normales, a menos que también quieras importarles datos luego
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Inventario)