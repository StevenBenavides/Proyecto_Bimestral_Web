from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Proveedor, Vendedor, Cliente, Categoria, Producto, Pedido, DetallePedido, Inventario

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'tipo', 'usuario')

class ProveedorRestrictAdmin(ImportExportModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'proveedor'):
            return qs.filter(proveedor=request.user.proveedor)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and hasattr(request.user, 'proveedor'):
            obj.proveedor = request.user.proveedor
        super().save_model(request, obj, form, change)

@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    list_display = ('id', 'nombreCategoria', 'descripcion')

@admin.register(Producto)
class ProductoAdmin(ProveedorRestrictAdmin):
    list_display = ('codigoSKU', 'nombre', 'precioUnitario', 'stockDiponible', 'categoria', 'proveedor')
    list_filter = ('categoria',)
    search_fields = ('codigoSKU', 'nombre')

@admin.register(Vendedor)
class VendedorAdmin(ImportExportModelAdmin):
    list_display = ('nombre', 'apellido', 'rutaAsignada', 'metaActual')

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    list_display = ('nombreTienda', 'propietario', 'direccion', 'rutaId')

@admin.register(Pedido)
class PedidoAdmin(ProveedorRestrictAdmin):
    list_display = ('numeroPedido', 'estado', 'fecha', 'cliente', 'vendedor', 'proveedor')

@admin.register(Inventario)
class InventarioAdmin(ProveedorRestrictAdmin):
    list_display = ('producto', 'cantidad', 'tipoMovimiento', 'fechaHora', 'proveedor')

admin.site.register(DetallePedido)