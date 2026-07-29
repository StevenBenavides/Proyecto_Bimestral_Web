from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib import messages
from aplicacion.models import *
from aplicacion.forms import *

def index(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil_proveedor'):
            return redirect('dashboard_proveedor')
        if hasattr(request.user, 'perfil_vendedor'):
            return redirect('dashboard_vendedor')
        if hasattr(request.user, 'perfil_tienda'):
            return redirect('dashboard_tienda')

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
        # si no tiene un usuario asociado se crea un formulario vacío
        formulario = ProveedorForm()
    return render(request, 'crear_proveedor.html', {'formulario': formulario})

def crear_vendedor(request):
    if request.method == 'POST':
        formulario = VendedorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('login')
    else:
        # si no tiene un usuario asociado se crea un formulario vacío
        formulario = VendedorForm()
    return render(request, 'crear_vendedor.html', {'formulario': formulario})

def crear_tienda(request):
    if request.method == 'POST':
        formulario = TiendaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('login')
    else:
        # si no tiene un usuario asociado se crea un formulario vacío
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
        'total_ventas': proveedor.get_total_ventas(),
        'total_comisiones': proveedor.get_total_comisiones(),
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
@require_POST
# se puso el require_POST para que solo se pueda rechazar mediante una carga 
def rechazar_solicitud(request, id):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    solicitud = get_object_or_404(SolicitudVendedor, pk=id, proveedor=proveedor, estado='Pendiente')
    solicitud.estado = 'Rechazado'
    solicitud.save()
    return redirect('mis_vendedores')


@login_required
@require_POST
def toggle_recepcion_solicitudes(request):
    # Vista para que el proveedor pueda activar o desactivar la recepción de solicitudes de vendedores
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    proveedor.acepta_solicitudes = not proveedor.acepta_solicitudes
    proveedor.save()
    return redirect('mis_vendedores')


@login_required
def editar_comision(request, id):
    # Vista para que el proveedor pueda editar la comisión asignada a un vendedor
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    solicitud = get_object_or_404(SolicitudVendedor, pk=id, proveedor=proveedor, estado='Aprobado')
    
    if request.method == 'POST':
        formulario = AprobarSolicitudForm(request.POST, instance=solicitud)
        if formulario.is_valid():
            formulario.save()
            return redirect('mis_vendedores')
    else:
        formulario = AprobarSolicitudForm(instance=solicitud)
    
    return render(request, 'aprobar_solicitud.html', {'formulario': formulario, 'solicitud': solicitud, 'editando': True})


@login_required
@require_POST
def eliminar_vendedor(request, id):
    if not hasattr(request.user, 'perfil_proveedor'):
        return redirect('index')
        
    proveedor = request.user.perfil_proveedor
    solicitud = get_object_or_404(SolicitudVendedor, pk=id, proveedor=proveedor)
    solicitud.delete()
    return redirect('mis_vendedores')


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
    
    if request.method == 'POST':
        formulario = EditarVendedorForm(request.POST, instance=vendedor)
        if formulario.is_valid():
            formulario.save()
            return redirect('dashboard_vendedor')
    else:
        formulario = EditarVendedorForm(instance=vendedor)
    
    # Pedidos generados por este vendedor
    pedidos = Pedido.objects.filter(vendedor=vendedor)
    # Solicitudes de visita de las tiendas (Notificaciones)
    num_notificaciones = vendedor.notificaciones_visita.filter(estado='Pendiente').count()
    postulaciones = vendedor.solicitudes.all().order_by('-id')
    # Calcular comisiones pendientes con el porcentaje real
    pedidos_pendientes = pedidos.exclude(estado='Entregado')
    comisiones_pendientes = 0
    for p in pedidos_pendientes:
        sol = vendedor.solicitudes.filter(proveedor=p.proveedor).first()
        if sol and sol.comision:
            comisiones_pendientes += p.calcular_total() * (sol.comision / 100)
            
    # Proveedores aprobados para el pedido rapido
    proveedores_aprobados = [sol.proveedor for sol in vendedor.solicitudes.filter(estado='Aprobado')]
    
    context = {
        'vendedor': vendedor,
        'num_pedidos': pedidos.count(),
        'num_proveedores': vendedor.solicitudes.filter(estado='Aprobado').count(),
        'num_notificaciones': num_notificaciones,
        'comisiones_pendientes': comisiones_pendientes,
        'ganancias_totales': vendedor.get_total_ganancias(),
        'postulaciones': postulaciones,
        'proveedores_aprobados': proveedores_aprobados,
        'formulario': formulario,
    }
    return render(request, 'dashboard_vendedor.html', context)


@login_required
def explorar_proveedores(request):
    # el hasattr se usa para verificar si el usuario tiene un perfil de vendedor asociado
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
    
    vendedor = request.user.perfil_vendedor
    # Proveedores a los que aún no ha enviado solicitud
    proveedores_solicitados = vendedor.solicitudes.values_list('proveedor_id', flat=True)
    proveedores_disponibles = Proveedor.objects.exclude(id__in=proveedores_solicitados).filter(es_verificado=True, acepta_solicitudes=True)
    
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
    # Vista para que un vendedor vea sus proveedores aprobados
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
    
    # Lógica de filtrado de productos usando Django puro
    busqueda = request.GET.get('q', '')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    if request.method == 'POST':
        formulario = CrearPedidoVendedorForm(request.POST)
        if formulario.is_valid():
            
            # 1. Validar productos y cantidades antes de crear el pedido
            productos_validos = []
            errores = []
            
            for key, value in request.POST.items():
                if key.startswith('cantidad_prod_') and value.isdigit() and int(value) > 0:
                    producto_id = int(key.replace('cantidad_prod_', ''))
                    cantidad = int(value)
                    try:
                        producto = Producto.objects.get(id=producto_id, proveedor=proveedor)
                        if cantidad < producto.stock_minimo_pedido:
                            errores.append(f"Para {producto.nombre} el mínimo es {producto.stock_minimo_pedido} unidades.")
                        elif cantidad > producto.stock_disponible:
                            errores.append(f"Stock insuficiente para {producto.nombre}.")
                        else:
                            productos_validos.append((producto, cantidad))
                    except Producto.DoesNotExist:
                        continue
            
            # Si no hay productos válidos, abortar la creación del pedido
            if not productos_validos:
                if errores:
                    for error in errores:
                        messages.error(request, error)
                else:
                    messages.error(request, "Debe seleccionar al menos un producto y cantidad válida para generar el pedido.")
                
                # Volver a renderizar la vista con los errores
                return render(request, 'crear_pedido_vendedor.html', {
                    'formulario': formulario, 
                    'proveedor': proveedor, 
                    'productos': productos,
                    'vendedor': vendedor,
                    'busqueda': busqueda
                })
            
            # 2. Si todo está bien, crear el pedido
            pedido = formulario.save(commit=False)
            pedido.vendedor = vendedor
            pedido.proveedor = proveedor
            pedido.estado = 'En proceso'
            pedido.save()
            
            # 3. Procesar los detalles del pedido
            for producto, cantidad in productos_validos:
                exito, mensaje = pedido.agregar_producto(producto, cantidad)
                if not exito:
                    messages.warning(request, f"Atención: {mensaje}")
                        
            messages.success(request, 'Pedido generado correctamente.')
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






# ==============================================================================
# VISTAS DE LA TIENDA / COMPRADOR
# ==============================================================================

@login_required
def dashboard_tienda(request):
    if not hasattr(request.user, 'perfil_tienda'):
        return redirect('index')
    
    tienda = request.user.perfil_tienda
    
    if request.method == 'POST':
        formulario = EditarTiendaForm(request.POST, instance=tienda)
        if formulario.is_valid():
            formulario.save()
            return redirect('dashboard_tienda')
    else:
        formulario = EditarTiendaForm(instance=tienda)
        
    context = {
        'tienda': tienda,
        'formulario': formulario,
    }
    return render(request, 'dashboard_tienda.html', context)


@login_required
def proveedores_tienda(request):
    if not hasattr(request.user, 'perfil_tienda'):
        return redirect('index')
    
    tienda = request.user.perfil_tienda
    # Mostrar proveedores verificados y que aceptan solicitudes
    proveedores = Proveedor.objects.filter(es_verificado=True)
    
    return render(request, 'proveedores_tienda.html', {'proveedores': proveedores, 'tienda': tienda})


@login_required
def catalogo_proveedor_tienda(request, proveedor_id):
    if not hasattr(request.user, 'perfil_tienda'):
        return redirect('index')
    
    tienda = request.user.perfil_tienda
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    productos = proveedor.productos.all()
    
    return render(request, 'catalogo_proveedor_tienda.html', {'proveedor': proveedor, 'productos': productos, 'tienda': tienda})


@login_required
@require_POST
def solicitar_visita_vendedor(request, proveedor_id):
    if not hasattr(request.user, 'perfil_tienda'):
        return redirect('index')
    
    tienda = request.user.perfil_tienda
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    
    # Obtener vendedores aprobados de este proveedor, ordenados por los que menos notificaciones tienen
    vendedores = Vendedor.objects.filter(
        solicitudes__proveedor=proveedor, 
        solicitudes__estado='Aprobado'
    ).annotate(
        num_visitas=Count('notificaciones_visita')
    ).order_by('num_visitas', '?')
    
    if vendedores.exists():
        vendedor_seleccionado = vendedores.first()
        SolicitudVisita.objects.create(
            tienda=tienda,
            vendedor=vendedor_seleccionado,
            proveedor=proveedor,
            estado='Pendiente'
        )
        messages.success(request, '¡Solicitud enviada exitosamente! Pronto un vendedor se acercará para atenderlo.')
        
    return redirect('catalogo_proveedor_tienda', proveedor_id=proveedor_id)


@login_required
@require_POST
def atender_solicitud_visita(request, id):
    if not hasattr(request.user, 'perfil_vendedor'):
        return redirect('index')
    
    solicitud = get_object_or_404(SolicitudVisita, pk=id, vendedor=request.user.perfil_vendedor)
    solicitud.estado = 'Atendido'
    solicitud.save()
    messages.success(request, 'Has marcado la solicitud como atendida.')
    
    return redirect('notificaciones_vendedor')


@login_required
def mis_pedidos_tienda(request):
    if not hasattr(request.user, 'perfil_tienda'):
        return redirect('index')
    
    tienda = request.user.perfil_tienda
    pedidos = Pedido.objects.filter(tienda=tienda).order_by('-fecha')
    
    return render(request, 'mis_pedidos_tienda.html', {'pedidos': pedidos, 'tienda': tienda})


@login_required
def detalle_pedido_tienda(request, pedido_id):
    if not hasattr(request.user, 'perfil_tienda'):
        return redirect('index')
    
    tienda = request.user.perfil_tienda
    pedido = get_object_or_404(Pedido, pk=pedido_id, tienda=tienda)
    detalles = pedido.detalles.all()
    
    return render(request, 'detalle_pedido_tienda.html', {'pedido': pedido, 'detalles': detalles, 'tienda': tienda})
