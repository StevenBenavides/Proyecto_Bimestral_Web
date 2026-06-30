from django.db import models

# Create your models here.

from django.db import models

class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    comisionAcumulada = models.FloatField()
    metaActual = models.FloatField()
    rutaAsignada = models.CharField(max_length=100)

    def __str__(self):
        return "%s %s %s %s %s" % (
            self.nombre, 
            self.apellido, 
            self.comisionAcumulada, 
            self.metaActual, 
            self.rutaAsignada
        )

class Cliente(models.Model):
    nombreTienda = models.CharField(max_length=100)
    propietario = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    coordenadas = models.CharField(max_length=100)
    historialPedidos = models.TextField()
    rutaId = models.IntegerField()

    def __str__(self):
        return "%s %s %s %s %s %s" % (
            self.nombreTienda, 
            self.propietario, 
            self.direccion, 
            self.coordenadas, 
            self.historialPedidos, 
            self.rutaId
        )

class Categoria(models.Model):
    nombreCategoria = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return "%s %s" % (self.nombreCategoria, self.descripcion)


class Producto(models.Model):
    codigoSKU = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precioUnitario = models.FloatField()
    stockDiponible = models.IntegerField()
    stockMinimo = models.IntegerField()
    unidadMedida = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")

    def __str__(self):
        return "%s %s %s %s %s %s %s %s" % (
            self.codigoSKU, 
            self.nombre, 
            self.descripcion, 
            self.precioUnitario, 
            self.stockDiponible, 
            self.stockMinimo, 
            self.unidadMedida, 
            self.categoria
        )


class Pedido(models.Model):
    numeroPedido = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=50)
    estaOffline = models.BooleanField(default=False)
    fecha = models.DateField()
    hora = models.TimeField()
    totalMonto = models.FloatField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pedidos")
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name="pedidos")

    def __str__(self):
        return "%s %s %s %s %s %s %s %s" % (
            self.numeroPedido, 
            self.estado, 
            self.estaOffline, 
            self.fecha, 
            self.hora, 
            self.totalMonto, 
            self.cliente, 
            self.vendedor
        )


class DetallePedido(models.Model):
    cantidadSolicitada = models.IntegerField()
    cantidadDespachada = models.IntegerField()
    precioUnitario = models.FloatField()
    subtotal = models.FloatField()
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="detalles_pedido")

    def __str__(self):
        return "%s %s %s %s %s %s" % (
            self.cantidadSolicitada, 
            self.cantidadDespachada, 
            self.precioUnitario, 
            self.subtotal, 
            self.pedido, 
            self.producto
        )


class Inventario(models.Model):
    cantidad = models.IntegerField()
    fechaHora = models.DateTimeField()
    tipoMovimiento = models.CharField(max_length=50)
    responsableId = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos_inventario")
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, related_name="movimientos_inventario")

    def __str__(self):
        return "%s %s %s %s %s %s" % (
            self.cantidad, 
            self.fechaHora, 
            self.tipoMovimiento, 
            self.responsableId, 
            self.producto, 
            self.pedido
        )