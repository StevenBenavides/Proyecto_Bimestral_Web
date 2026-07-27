from django.db import models
from django.contrib.auth.models import User
import random
import datetime

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    TIPO_CHOICES = (
        ('Mayorista', 'Mayorista'),
        ('Minorista', 'Minorista'),
    )
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_proveedor')
    nombre_empresa = models.CharField(max_length=100)
    ruc = models.CharField(max_length=13, unique=True)
    nombre_propietario = models.CharField(max_length=50)
    apellido_propietario = models.CharField(max_length=50)
    correo = models.EmailField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    logo = models.ImageField(upload_to='logos_proveedores/', null=True, blank=True)
    es_verificado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_empresa} - {self.ruc}"

    def get_nombre_completo_propietario(self):
        return f"{self.nombre_propietario} {self.apellido_propietario}"

class Vendedor(models.Model):
    SECTOR_CHOICES = (
        ('Norte', 'Norte'),
        ('Sur', 'Sur'),
        ('Este', 'Este'),
        ('Oeste', 'Oeste'),
    )
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_vendedor')
    cedula = models.CharField(max_length=10, unique=True)
    ruc_rice = models.CharField(max_length=13, blank=True, null=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    ciudad = models.CharField(max_length=50)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class SolicitudVendedor(models.Model):
    ESTADO_CHOICES = (
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    )
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='solicitudes')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='solicitudes_vendedores')
    descripcion_ganas = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    comision = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Porcentaje

    def aprobar_solicitud(self, comision_asignada):
        if comision_asignada is None or comision_asignada <= 0:
            return False, "Debe asignar una comisión válida."
        self.comision = comision_asignada
        self.estado = 'Aprobado'
        self.save()
        return True, "Solicitud aprobada exitosamente."

    def __str__(self):
        return f"Solicitud de {self.vendedor} a {self.proveedor}"

class Tienda(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_tienda')
    cedula = models.CharField(max_length=10)
    ruc_rice = models.CharField(max_length=13, blank=True, null=True)
    nombre_tienda = models.CharField(max_length=100)
    nombre_propietario = models.CharField(max_length=50)
    apellido_propietario = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    ubicacion_lat = models.FloatField()
    ubicacion_lng = models.FloatField()

    def __str__(self):
        return self.nombre_tienda

class NotificacionTienda(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    sector = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notificación de {self.tienda} en sector {self.sector}"

class Producto(models.Model):
    UNIDAD_CHOICES = (
        ('Paquete', 'Paquete'),
        ('Unidad', 'Unidad'),
    )
    sku = models.CharField(max_length=20, unique=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock_disponible = models.IntegerField()
    stock_minimo_pedido = models.IntegerField()
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generar_sku()
        super().save(*args, **kwargs)

    def generar_sku(self):
        # Genera un Unidad de Mantenimiento de Stock (SKU) 
        # basado en el proveedor y un numero random
        prefijo = self.proveedor.nombre_empresa[:3].upper() if self.proveedor else "PRD"
        numero = random.randint(1000, 9999)
        return f"{prefijo}-{numero}"

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    METODO_PAGO_CHOICES = (
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
    )
    ESTADO_CHOICES = (
        ('En proceso', 'En proceso'),
        ('Enviado', 'Enviado'),
        ('En ruta', 'En ruta'),
        ('Entregado', 'Entregado'),
    )
    numero_pedido = models.CharField(max_length=20, unique=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    numero_transferencia = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='En proceso')
    fecha_estimada_entrega = models.DateField(null=True, blank=True)
    numero_contacto = models.CharField(max_length=15, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Genera un numero de pedido unico si no existe
        if not self.numero_pedido:
            self.numero_pedido = self.generar_numero_pedido()
        super().save(*args, **kwargs)

    def generar_numero_pedido(self):
        #logica para generar un numero de pedido unico basado en la fecha y un numero random
        fecha_str = datetime.datetime.now().strftime("%Y%m%d")
        numero = random.randint(1000, 9999)
        return f"PED-{fecha_str}-{numero}"
    
    def avanzar_estado(self, nuevo_estado):
        orden_estados = ['En proceso', 'Enviado', 'En ruta', 'Entregado']
        if self.estado in orden_estados and nuevo_estado in orden_estados:
            indice_actual = orden_estados.index(self.estado)
            indice_nuevo = orden_estados.index(nuevo_estado)
            if indice_nuevo > indice_actual:
                self.estado = nuevo_estado
                self.save()
                return True, "Estado actualizado correctamente."
            else:
                return False, "No se puede retroceder el estado del pedido."
        return False, "Estado no válido."
        
    def calcular_total(self):
        # Esta logica suma los detalles para un pedido
        detalles = self.detalles.all()
        total = sum([detalle.get_subtotal() for detalle in detalles])
        return total

    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.tienda.nombre_tienda}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class SolicitudVisita(models.Model):
    ESTADO_CHOICES = (
        ('Pendiente', 'Pendiente'),
        ('Atendida', 'Atendida'),
    )
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='solicitudes_visita')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='notificaciones_visita')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    
    def __str__(self):
        # Logica para mostrar la solicitud de visita con el nombre de la tienda y el vendedor
        return f"Visita solicitada por {self.tienda.nombre_tienda} a {self.vendedor.nombre} - {self.estado}"

    def get_subtotal(self):
        # Calcula el subtotal del detalle del pedido
        return self.cantidad * self.precio_unitario
