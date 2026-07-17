from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.models import User

from appGiro.models import Vendedor, Cliente, Categoria, Producto, Pedido, DetallePedido, Inventario

class VendedorForm(ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nombre', 'apellido', 'comisionAcumulada', 'metaActual', 'rutaAsignada']
        labels = {
            'nombre': _('Ingrese nombre por favor'),
            'apellido': _('Ingrese apellido por favor'),
            'comisionAcumulada': _('Comisión Acumulada'),
            'metaActual': _('Meta Actual'),
            'rutaAsignada': _('Ruta Asignada'),
        }

    def clean_nombre(self):
        valor = self.cleaned_data['nombre']
        num_palabras = len(valor.split())
        if num_palabras < 2:
            raise forms.ValidationError("Ingrese dos nombres por favor")
        return valor

    def clean_apellido(self):
        valor = self.cleaned_data['apellido']
        num_palabras = len(valor.split())
        if num_palabras < 2:
            raise forms.ValidationError("Ingrese dos apellidos por favor")
        return valor


class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombreTienda', 'propietario', 'direccion', 'coordenadas', 'historialPedidos', 'rutaId']
        labels = {
            'nombreTienda': _('Ingrese nombre de la tienda'),
            'propietario': _('Ingrese nombre del propietario'),
            'direccion': _('Ingrese dirección por favor'),
            'coordenadas': _('Coordenadas de la Tienda (Automático)'),
            'historialPedidos': _('Historial de pedidos'),
            'rutaId': _('ID de Ruta'),
        }
        widgets = {
            'coordenadas': forms.TextInput(attrs={'readonly': 'readonly', 'id': 'id_coordenadas', 'placeholder': 'Las coordenadas se cargarán con el mapa...'}),
        }

    def clean_propietario(self):
        valor = self.cleaned_data['propietario']
        num_palabras = len(valor.split())
        if num_palabras < 2:
            raise forms.ValidationError("Ingrese al menos nombre y apellido del propietario")
        return valor


class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['codigoSKU', 'nombre', 'descripcion', 'precioUnitario', 'stockDiponible', 'stockMinimo', 'unidadMedida', 'categoria']
        labels = {
            'codigoSKU': _('Ingrese código SKU'),
            'nombre': _('Ingrese nombre del producto'),
            'descripcion': _('Ingrese descripción'),
            'precioUnitario': _('Precio Unitario'),
            'stockDiponible': _('Stock Disponible'),
            'stockMinimo': _('Stock Mínimo'),
            'unidadMedida': _('Unidad de Medida'),
            'categoria': _('Categoría'),
        }
        widgets ={
            'descripcion': forms.Textarea(attrs={
                'rows':3,
                'class':'form-control'
            })
        }


class PedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['numeroPedido', 'estado', 'estaOffline', 'fecha', 'hora', 'totalMonto', 'cliente', 'vendedor']
        labels = {
            'numeroPedido': _('Número de Pedido'),
            'estado': _('Estado del Pedido'),
            'estaOffline': _('¿Está Offline?'),
            'fecha': _('Fecha del Pedido'),
            'hora': _('Hora del Pedido'),
            'totalMonto': _('Monto Total'),
            'cliente': _('Cliente Asociado'),
            'vendedor': _('Vendedor (Proveedor/Dueño)'),
        }


class PedidoClienteForm(ModelForm):
    """
    Este formulario se parece a NumeroTelefonicoEstudianteForm de tu ejemplo.
    Sirve para crear un pedido asignándolo automáticamente a un cliente.
    """
    def __init__(self, cliente, vendedor, *args, **kwargs):
        super(PedidoClienteForm, self).__init__(*args, **kwargs)
        self.initial['cliente'] = cliente
        self.initial['vendedor'] = vendedor
        self.fields["cliente"].widget = forms.widgets.HiddenInput()
        self.fields["vendedor"].widget = forms.widgets.HiddenInput()

    class Meta:
        model = Pedido
        fields = ['estaOffline', 'fecha', 'cliente', 'vendedor']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

class RegistroForm(forms.Form):
    from appGiro.models import RUTAS_CHOICES
    username = forms.CharField(label='Nombre de Usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    nombre = forms.CharField(label='Nombre', max_length=100)
    apellido = forms.CharField(label='Apellido', max_length=100)
    rutaAsignada = forms.ChoiceField(label='Ruta Asignada', choices=RUTAS_CHOICES)
