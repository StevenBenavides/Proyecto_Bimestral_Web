from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from aplicacion.models import Proveedor, Vendedor, Tienda, Producto, SolicitudVendedor, Pedido

class ProveedorForm(ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Nombre de Usuario para el login")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")

    class Meta:
        model = Proveedor
        fields = ['username', 'password', 'nombre_empresa', 'ruc', 'nombre_propietario', 'apellido_propietario', 'correo', 'tipo', 'descripcion', 'logo']
        labels = {
            'nombre_empresa': _('Nombre de la Empresa'),
            'ruc': _('RUC de la empresa'),
            'nombre_propietario': _('Nombre del propietario'),
            'apellido_propietario': _('Apellido del propietario'),
            'correo': _('Correo de la empresa o dueño'),
            'tipo': _('Tipo (Mayorista o Minorista)'),
            'descripcion': _('Descripción de la empresa'),
            'logo': _('Logo de la empresa (PNG)'),
        }

    def clean_ruc(self):
        valor = self.cleaned_data['ruc']
        if len(valor) != 13:
            raise forms.ValidationError("El RUC debe tener 13 dígitos")
        return valor

    def save(self, commit=True):
        # Obtenemos la instancia sin guardarla todavía
        proveedor = super().save(commit=False)
        # Creamos el usuario de Django
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['correo']
        )
        proveedor.usuario = user
        if commit:
            proveedor.save()
        return proveedor


class VendedorForm(ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Nombre de Usuario para el login")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")

    class Meta:
        model = Vendedor
        fields = ['username', 'password', 'cedula', 'ruc_rice', 'nombre', 'apellido', 'correo', 'telefono', 'ciudad', 'sector']
        labels = {
            'cedula': _('Número de cédula'),
            'ruc_rice': _('RUC o RICE (Opcional)'),
            'nombre': _('Nombres'),
            'apellido': _('Apellidos'),
            'correo': _('Correo electrónico válido'),
            'telefono': _('Número de teléfono válido'),
            'ciudad': _('Ciudad donde reside'),
            'sector': _('Sector de preferencia para trabajar'),
        }

    def clean_cedula(self):
        valor = self.cleaned_data['cedula']
        if len(valor) != 10:
            raise forms.ValidationError("Ingrese cédula con 10 dígitos")
        return valor
        
    def save(self, commit=True):
        vendedor = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['correo']
        )
        vendedor.usuario = user
        if commit:
            vendedor.save()
        return vendedor


class TiendaForm(ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Nombre de Usuario para el login")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")

    class Meta:
        model = Tienda
        fields = ['username', 'password', 'cedula', 'ruc_rice', 'nombre_tienda', 'nombre_propietario', 'apellido_propietario', 'telefono', 'correo', 'ubicacion_lat', 'ubicacion_lng']
        labels = {
            'cedula': _('Número de cédula'),
            'ruc_rice': _('RUC o RICE'),
            'nombre_tienda': _('Nombre de la tienda'),
            'nombre_propietario': _('Nombres del propietario'),
            'apellido_propietario': _('Apellidos del propietario'),
            'telefono': _('Número de teléfono'),
            'correo': _('Correo electrónico'),
            'ubicacion_lat': _('Latitud de ubicación'),
            'ubicacion_lng': _('Longitud de ubicación'),
        }
        widgets = {
            'ubicacion_lat': forms.HiddenInput(),
            'ubicacion_lng': forms.HiddenInput(),
        }

    def clean_cedula(self):
        valor = self.cleaned_data['cedula']
        if len(valor) != 10:
            raise forms.ValidationError("Ingrese cédula con 10 dígitos")
        return valor

    def save(self, commit=True):
        tienda = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['correo']
        )
        tienda.usuario = user
        if commit:
            tienda.save()
        return tienda


class SolicitudVendedorForm(ModelForm):
    class Meta:
        model = SolicitudVendedor
        fields = ['descripcion_ganas']
        labels = {
            'descripcion_ganas': _('Describa sus ganas de trabajar con este proveedor'),
        }
        widgets = {
            'descripcion_ganas': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control'
            })
        }


class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_unitario', 'stock_disponible', 'stock_minimo_pedido', 'unidad_medida', 'categoria', 'imagen']
        labels = {
            'nombre': _('Nombre del producto'),
            'descripcion': _('Descripción'),
            'precio_unitario': _('Precio unitario'),
            'stock_disponible': _('Stock disponible'),
            'stock_minimo_pedido': _('Stock mínimo para pedidos'),
            'unidad_medida': _('Unidad de medida (Paquete/Unidad)'),
            'categoria': _('Categoría'),
            'imagen': _('Imagen del producto (PNG)'),
        }

    def clean_stock_disponible(self):
        valor = self.cleaned_data['stock_disponible']
        if valor < 0:
            raise forms.ValidationError("El stock no puede ser negativo")
        return valor


class PedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['metodo_pago', 'numero_transferencia']
        labels = {
            'metodo_pago': _('Método de pago (Efectivo / Transferencia)'),
            'numero_transferencia': _('Número de transferencia (Obligatorio si es transferencia)'),
        }

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        numero_transferencia = cleaned_data.get('numero_transferencia')

        if metodo_pago == 'Transferencia' and not numero_transferencia:
            self.add_error('numero_transferencia', "Debe ingresar el número de transferencia")
        
        return cleaned_data


class CrearPedidoVendedorForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['tienda', 'metodo_pago', 'numero_transferencia']
        labels = {
            'tienda': _('Tienda (Cliente Final)'),
            'metodo_pago': _('Método de pago'),
            'numero_transferencia': _('Número de transferencia (Si aplica)'),
        }
        widgets = {
            'tienda': forms.Select(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        numero_transferencia = cleaned_data.get('numero_transferencia')

        if metodo_pago == 'Transferencia' and not numero_transferencia:
            self.add_error('numero_transferencia', "Debe ingresar el número de transferencia")
        
        return cleaned_data


class AprobarSolicitudForm(ModelForm):
    class Meta:
        model = SolicitudVendedor
        fields = ['comision']
        labels = {
            'comision': _('Porcentaje de comisión para este vendedor (%)'),
        }

    def clean_comision(self):
        valor = self.cleaned_data['comision']
        if valor < 0 or valor > 100:
            raise forms.ValidationError("La comisión debe estar entre 0 y 100")
        return valor


class GestionarPedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'fecha_estimada_entrega', 'numero_contacto']
        labels = {
            'estado': _('Estado actual del pedido'),
            'fecha_estimada_entrega': _('Fecha estimada de entrega (YYYY-MM-DD)'),
            'numero_contacto': _('Número de contacto para entrega'),
        }
