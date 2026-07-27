from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from aplicacion.models import *
from aplicacion.forms import *

def index(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil_proveedor'):
            return redirect('dashboard_proveedor')
        if hasattr(request.user, 'perfil_vendedor'):
            return redirect('dashboard_vendedor')
        # Aquí se añadirá la de tienda luego

    proveedores = Proveedor.objects.all()
    informacion_template = {'proveedores': proveedores, 'numero_proveedores': len(proveedores)}
    return render(request, 'index.html', informacion_template)

def crear_proveedor(request):
    if request.method == 'POST':
        formulario = ProveedorForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('login')
    else:
        formulario = ProveedorForm()
    return render(request, 'crear_proveedor.html', {'formulario': formulario})

def crear_vendedor(request):
    if request.method == 'POST':
        formulario = VendedorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('login')
    else:
        formulario = VendedorForm()
    return render(request, 'crear_vendedor.html', {'formulario': formulario})

def crear_tienda(request):
    if request.method == 'POST':
        formulario = TiendaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('login')
    else:
        formulario = TiendaForm()
    return render(request, 'crear_tienda.html', {'formulario': formulario})

def obtener_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    productos = proveedor.productos.all()
    return render(request, 'obtener_proveedor.html', {'proveedor': proveedor, 'productos': productos})

# ==============================================================================
# VISTAS DEL PROVEEDOR (DASHBOARD Y MÓDULOS)
# ==============================================================================

@login_required
def dashboard_proveedor(request):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
    
    proveedor = request.user.perfil_proveedor
    context = {
        'proveedor': proveedor,
        'num_productos': proveedor.productos.count(),
        'num_pedidos': Pedido.objects.filter(proveedor=proveedor, estado='En proceso').count(),
        'num_vendedores': proveedor.solicitudes_vendedores.filter(estado='Aprobado').count(),
        'num_solicitudes': proveedor.solicitudes_vendedores.filter(estado='Pendiente').count(),
    }
    return render(request, 'dashboard_proveedor.html', context)


@login_required
def mis_productos(request):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
    
    proveedor = request.user.perfil_proveedor
    productos = proveedor.productos.all()
    return render(request, 'mis_productos.html', {'productos': productos, 'proveedor': proveedor})


@login_required
def crear_producto(request):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    if request.method == 'POST':
        formulario = ProductoForm(request.POST, request.FILES)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            producto.proveedor = proveedor # Asignación automática
            producto.save()
            return redirect('mis_productos')
    else:
        formulario = ProductoForm()
    return render(request, 'crear_producto.html', {'formulario': formulario})


@login_required
def editar_producto(request, id):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    producto = get_object_or_404(Producto, pk=id, proveedor=proveedor)
    
    if request.method == 'POST':
        formulario = ProductoForm(request.POST, request.FILES, instance=producto)
        if formulario.is_valid():
            formulario.save()
            return redirect('mis_productos')
    else:
        formulario = ProductoForm(instance=producto)
    return render(request, 'crear_producto.html', {'formulario': formulario, 'editando': True})


@login_required
@require_POST
def eliminar_producto(request, id):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    producto = get_object_or_404(Producto, pk=id, proveedor=proveedor)
    producto.delete()
    return redirect('mis_productos')


@login_required
def mis_vendedores(request):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    solicitudes = proveedor.solicitudes_vendedores.filter(estado='Pendiente')
    activos = proveedor.solicitudes_vendedores.filter(estado='Aprobado')
    
    context = {
        'solicitudes': solicitudes,
        'activos': activos,
        'proveedor': proveedor
    }
    return render(request, 'mis_vendedores.html', context)


@login_required
def aprobar_solicitud(request, id):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    solicitud = get_object_or_404(SolicitudVendedor, pk=id, proveedor=proveedor, estado='Pendiente')
    
    if request.method == 'POST':
        formulario = AprobarSolicitudForm(request.POST, instance=solicitud)
        if formulario.is_valid():
            sol = formulario.save(commit=False)
            sol.estado = 'Aprobado'
            sol.save()
            return redirect('mis_vendedores')
    else:
        formulario = AprobarSolicitudForm(instance=solicitud)
    
    return render(request, 'aprobar_solicitud.html', {'formulario': formulario, 'solicitud': solicitud})


@login_required
def mis_pedidos(request):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    pedidos = Pedido.objects.filter(proveedor=proveedor).order_by('-fecha')
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos, 'proveedor': proveedor})


@login_required
def gestionar_pedido(request, id):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    pedido = get_object_or_404(Pedido, pk=id, proveedor=proveedor)
    
    if request.method == 'POST':
        formulario = GestionarPedidoForm(request.POST, instance=pedido)
        if formulario.is_valid():
            # Aqui podríamos agregar lógica adicional para manejar 
            # el estado del pedido, notificaciones, etc.
            formulario.save()
            return redirect('mis_pedidos')
    else:
        formulario = GestionarPedidoForm(instance=pedido)
        
    return render(request, 'gestionar_pedido.html', {'formulario': formulario, 'pedido': pedido})




# ==============================================================================
# VISTAS DEL VENDEDOR
# ==============================================================================

@login_required
def dashboard_vendedor(request):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
    
    vendedor = request.user.perfil_vendedor
    # Pedidos generados por este vendedor
    pedidos = Pedido.objects.filter(vendedor=vendedor)
    # Solicitudes de visita de las tiendas (Notificaciones)
    num_notificaciones = vendedor.notificaciones_visita.filter(estado='Pendiente').count()
    
    context = {
        'vendedor': vendedor,
        'num_pedidos': pedidos.count(),
        'num_proveedores': vendedor.solicitudes.filter(estado='Aprobado').count(),
        'num_notificaciones': num_notificaciones,
        'comisiones_pendientes': sum([p.calcular_total() * 0.05 for p in pedidos if p.estado != 'Entregado']),
    }
    return render(request, 'dashboard_vendedor.html', context)


@login_required
def explorar_proveedores(request):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
    
    vendedor = request.user.perfil_vendedor
    # Proveedores a los que aún no ha enviado solicitud
    proveedores_solicitados = vendedor.solicitudes.values_list('proveedor_id', flat=True)
    proveedores_disponibles = Proveedor.objects.exclude(id__in=proveedores_solicitados).filter(es_verificado=True)
    
    return render(request, 'explorar_proveedores.html', {'proveedores': proveedores_disponibles, 'vendedor': vendedor})


@login_required
def enviar_solicitud(request, proveedor_id):
    
    # Vista para que un vendedor envíe una solicitud a un proveedor
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
        
    vendedor = request.user.perfil_vendedor
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    
    if request.method == 'POST':
        formulario = SolicitudVendedorForm(request.POST)
        if formulario.is_valid():
            solicitud = formulario.save(commit=False)
            solicitud.vendedor = vendedor
            solicitud.proveedor = proveedor
            solicitud.estado = 'Pendiente'
            solicitud.save()
            return redirect('explorar_proveedores')
    else:
        formulario = SolicitudVendedorForm()
        
    return render(request, 'enviar_solicitud.html', {'formulario': formulario, 'proveedor': proveedor, 'vendedor': vendedor})


@login_required
def mis_proveedores_asociados(request):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
        
    vendedor = request.user.perfil_vendedor
    solicitudes_aprobadas = vendedor.solicitudes.filter(estado='Aprobado')
    
    return render(request, 'mis_proveedores_asociados.html', {'solicitudes': solicitudes_aprobadas, 'vendedor': vendedor})


@login_required
def crear_pedido_vendedor(request, proveedor_id):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
        
    vendedor = request.user.perfil_vendedor
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    productos = proveedor.productos.filter(stock_disponible__gt=0)
    
    # Lógica de filtrado de productos usando Python/Django puro
    busqueda = request.GET.get('q', '')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    if request.method == 'POST':
        formulario = CrearPedidoVendedorForm(request.POST)
        if formulario.is_valid():
            pedido = formulario.save(commit=False)
            pedido.vendedor = vendedor
            pedido.proveedor = proveedor
            pedido.estado = 'En proceso'
            pedido.save()
            
            # Aquí procesaríamos los detalles del pedido (productos)
            # Por ahora, simplemente lo guardamos y redirigimos
            return redirect('historial_pedidos_vendedor')
    else:
        formulario = CrearPedidoVendedorForm()
        
    return render(request, 'crear_pedido_vendedor.html', {
        'formulario': formulario, 
        'proveedor': proveedor, 
        'productos': productos,
        'vendedor': vendedor,
        'busqueda': busqueda
    })


@login_required
def historial_pedidos_vendedor(request):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
        
    vendedor = request.user.perfil_vendedor
    pedidos = Pedido.objects.filter(vendedor=vendedor).order_by('-fecha')
    
    return render(request, 'historial_pedidos_vendedor.html', {'pedidos': pedidos, 'vendedor': vendedor})

@login_required
def notificaciones_vendedor(request):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
        
    vendedor = request.user.perfil_vendedor
    notificaciones = vendedor.notificaciones_visita.order_by('-fecha_solicitud')
    
    return render(request, 'notificaciones_vendedor.html', {'notificaciones': notificaciones, 'vendedor': vendedor})
