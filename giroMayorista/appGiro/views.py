from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib import messages
import uuid

from appGiro.models import *

from appGiro.forms import *



def landing_page(request):
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'proveedor'):
            return redirect('dashboard_proveedor')
        elif request.user.is_superuser:
            return redirect('dashboard_admin')
        else:
            return redirect('index')
            
    proveedores = Proveedor.objects.all()
    return render(request, 'landing.html', {'proveedores': proveedores})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if hasattr(user, 'proveedor'):
                return redirect('dashboard_proveedor')
            elif user.is_superuser:
                return redirect('dashboard_admin')
            else:
                return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

def registro_trabajador_view(request):
    if request.method == 'POST':
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            u = formulario.cleaned_data['username']
            p = formulario.cleaned_data['password']
            n = formulario.cleaned_data['nombre']
            a = formulario.cleaned_data['apellido']
            r = formulario.cleaned_data['rutaAsignada']

            
            user = User.objects.create_user(username=u, password=p, first_name=n, last_name=a)
            
            Vendedor.objects.create(
                usuario=user,
                nombre=n,
                apellido=a,
                rutaAsignada=r,
                comisionAcumulada=0.0,
                metaActual=0.0
            )
            
            login(request, user)
            return redirect('index')
    else:
        formulario = RegistroForm()
        
    return render(request, 'registro_trabajador.html', {'formulario': formulario})

def registro_proveedor_view(request):
    if request.method == 'POST':
        formulario = RegistroProveedorForm(request.POST)
        if formulario.is_valid():
            u = formulario.cleaned_data['username']
            p = formulario.cleaned_data['password']
            n = formulario.cleaned_data['nombre_empresa']
            t = formulario.cleaned_data['tipo']

            # Crear el usuario nativo de Django
            user = User.objects.create_user(username=u, password=p)
            
            # Crear el perfil del Proveedor
            Proveedor.objects.create(
                usuario=user,
                nombre_empresa=n,
                tipo=t
            )
            
            login(request, user)
            return redirect('dashboard_proveedor')
    else:
        formulario = RegistroProveedorForm()
        
    return render(request, 'registro_proveedor.html', {'formulario': formulario})




@login_required(login_url='/login/')
def index(request):
    vendedores = Vendedor.objects.all()
    clientes = Cliente.objects.all()
    
    informacion_template = {
        'vendedores': vendedores, 
        'numero_vendedores': len(vendedores),
        'clientes': clientes,
        'numero_clientes': len(clientes)
    }
    return render(request, 'index.html', informacion_template)

@login_required(login_url='/login/')
def obtener_vendedor(request, id):
    vendedor = Vendedor.objects.get(pk=id)
    informacion_template = {'vendedor': vendedor}
    return render(request, 'obtener_vendedor.html', informacion_template)

@login_required(login_url='/login/')
def crear_vendedor(request):
    if request.method=='POST':
        formulario = VendedorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = VendedorForm()
    diccionario = {'formulario': formulario}
    return render(request, 'crearVendedor.html', diccionario)

@login_required(login_url='/login/')
def editar_vendedor(request, id):
    vendedor = Vendedor.objects.get(pk=id)
    if request.method=='POST':
        formulario = VendedorForm(request.POST, instance=vendedor)
        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = VendedorForm(instance=vendedor)
    diccionario = {'formulario': formulario}
    return render(request, 'editarVendedor.html', diccionario)

@login_required(login_url='/login/')
def eliminar_vendedor(request, id):
    vendedor = Vendedor.objects.get(pk=id)
    vendedor.delete()
    return redirect(index)

# Vistas para el Cliente Dueño de tienda

@login_required(login_url='/login/')
def crear_cliente(request):
    if request.method=='POST':
        formulario = ClienteForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = ClienteForm()
    diccionario = {'formulario': formulario}
    return render(request, 'crearCliente.html', diccionario)

@login_required(login_url='/login/')
def editar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    if request.method=='POST':
        formulario = ClienteForm(request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            return redirect(index)
    else:
        formulario = ClienteForm(instance=cliente)
    diccionario = {'formulario': formulario}
    return render(request, 'editarCliente.html', diccionario)

@login_required(login_url='/login/')
def crear_pedido_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    
    # Obtener el vendedor desde el usuario logueado
    try:
        vendedor = request.user.vendedor
    except:
        vendedor = None
        
    productos = Producto.objects.all()

    if request.method=='POST':
        formulario = PedidoClienteForm(cliente, vendedor, request.POST)
        if formulario.is_valid():
            # Guardamos con commit=False porque falta el totalMonto, la hora, el estado y el numeroPedido
            pedido = formulario.save(commit=False)
            pedido.totalMonto = 0.0 
            pedido.hora = timezone.now().time()
            pedido.estado = 'Pendiente'
            # Generar numero de pedido 
            pedido.numeroPedido = f"PED-{uuid.uuid4().hex[:6].upper()}"
            pedido.save() 
            
            total_calculado = 0.0
            
            
            for p in productos:
                cantidad_str = request.POST.get(f'producto_{p.id}')
                if cantidad_str:
                    try:
                        cantidad = int(cantidad_str)
                    except ValueError:
                        cantidad = 0
                        
                    if cantidad > 0:
                        # Crear el DetallePedido
                        subtotal = cantidad * p.precioUnitario
                        total_calculado += subtotal
                        
                        DetallePedido.objects.create(
                            cantidadSolicitada=cantidad,
                            cantidadDespachada=0, # Por defecto 0 hasta entregar
                            precioUnitario=p.precioUnitario,
                            subtotal=subtotal,
                            pedido=pedido,
                            producto=p
                        )
                        
                        # Restar del inventario
                        p.stockDiponible -= cantidad
                        p.save()
            
            # Actualizar el total del pedido
            pedido.totalMonto = total_calculado
            pedido.save()
            
            messages.success(request, f'¡Pedido {pedido.numeroPedido} generado exitosamente!')
            
            return redirect('index')
    else:
        formulario = PedidoClienteForm(cliente, vendedor)
        
    diccionario = {
        'formulario': formulario, 
        'cliente': cliente,
        'productos': productos
    }
    return render(request, 'crearPedidoCliente.html', diccionario)


# === DASHBOARD PARA EL ADMIN (KPIs) ===

def es_admin(user):
    return user.is_superuser

@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/panel/')
def dashboard_admin(request):
    import json
    
    total_pedidos = Pedido.objects.count()
    monto_total_vendido = Pedido.objects.aggregate(total=Sum('totalMonto'))['total'] or 0

    zonas_abastecidas = Cliente.objects.values('rutaId').annotate(
        total_clientes=Count('id'),
        total_pedidos_zona=Count('pedidos')
    ).order_by('-total_pedidos_zona')
    
    # 1. Datos para grafico: Ventas por vendedor
    ventas_vendedores = Vendedor.objects.annotate(
        total_ventas=Sum('pedidos__totalMonto')
    ).values('nombre', 'apellido', 'total_ventas')
    
    nombres_vendedores = []
    ventas_vendedores_data = []
    for v in ventas_vendedores:
        nombres_vendedores.append(f"{v['nombre']} {v['apellido']}")
        ventas_vendedores_data.append(float(v['total_ventas'] or 0.0))
        
    # 2. Datos para grafico: Pedidos por ruta
    nombres_rutas = []
    pedidos_rutas_data = []
    for z in zonas_abastecidas:
        nombres_rutas.append(f"Ruta {z['rutaId']}")
        pedidos_rutas_data.append(z['total_pedidos_zona'])

    diccionario = {
        'total_pedidos': total_pedidos,
        'monto_total_vendido': monto_total_vendido,
        'zonas_abastecidas': zonas_abastecidas,
        'nombres_vendedores_json': json.dumps(nombres_vendedores),
        'ventas_vendedores_json': json.dumps(ventas_vendedores_data),
        'nombres_rutas_json': json.dumps(nombres_rutas),
        'pedidos_rutas_json': json.dumps(pedidos_rutas_data),
    }
    return render(request, 'dashboard_admin.html', diccionario)


@login_required(login_url='/login/')
def mis_pedidos(request):
    """
        Módulo para que el vendedor vea el estado de sus pedidos.
    """
    try:
        vendedor = request.user.vendedor
        pedidos = Pedido.objects.filter(vendedor=vendedor).order_by('-fecha', '-hora')
    except:
        pedidos = []
        
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})

@login_required(login_url='/login/')
def dashboard_proveedor(request):
    try:
        proveedor = request.user.proveedor
    except:
        return redirect('index') 
        
    if request.method == 'POST':
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            producto.proveedor = proveedor
            # Generar SKU automaticamente 
            producto.codigoSKU = f"SKU-{uuid.uuid4().hex[:6].upper()}"
            producto.save()
            messages.success(request, 'Producto registrado exitosamente.')
            return redirect('dashboard_proveedor')
    else:
        formulario = ProductoForm()
        
    productos = Producto.objects.filter(proveedor=proveedor)
    
    return render(request, 'dashboard_proveedor.html', {
        'formulario': formulario,
        'productos': productos,
        'proveedor': proveedor
    })

@login_required(login_url='/login/')
def trazabilidad_proveedor(request):
    try:
        proveedor = request.user.proveedor
    except:
        return redirect('index')
        
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('estado')
        nueva_ruta = request.POST.get('rutaAsignada')
        
        if pedido_id:
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                # Validar que el proveedor actual tenga que ver con este pedido
                if pedido.detalles.filter(producto__proveedor=proveedor).exists():
                    if nuevo_estado:
                        pedido.estado = nuevo_estado
                    if nueva_ruta:
                        pedido.rutaAsignada = nueva_ruta
                    pedido.save()
                    messages.success(request, f'Pedido {pedido.numeroPedido} actualizado.')
            except Pedido.DoesNotExist:
                pass
                
        return redirect('trazabilidad_proveedor')
        
    # Buscar pedidos que contengan al menos un producto de este proveedor
    pedidos_db = Pedido.objects.filter(detalles__producto__proveedor=proveedor).distinct().order_by('-fecha', '-hora')
    
    pedidos_data = []
    for pedido in pedidos_db:
        # Filtrar solo los detalles de productos de este proveedor
        detalles_prov = pedido.detalles.filter(producto__proveedor=proveedor)
        total_prov = sum(d.subtotal for d in detalles_prov)
        
        pedidos_data.append({
            'pedido': pedido,
            'detalles': detalles_prov,
            'total_proveedor': total_prov
        })
    
    return render(request, 'trazabilidad_proveedor.html', {
        'pedidos_data': pedidos_data,
        'proveedor': proveedor,
        'estados': Pedido.ESTADO_CHOICES,
        'rutas': RUTAS_CHOICES
    })
