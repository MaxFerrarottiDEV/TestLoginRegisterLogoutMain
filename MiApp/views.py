from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from .forms import PreinscripcionForm , CustomRegisterForm
from django.contrib import messages # type: ignore
from .models import DatInsc, Estudiantes
from datetime import date
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash, logout


@login_required
def change_password(request):
    if request.method == 'POST':
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']
        
        if new_password1 == new_password2:
            request.user.set_password(new_password1)
            request.user.save()
            logout(request)  # Cerrar la sesión del usuario
            messages.success(request, "Contraseña cambiada exitosamente. Por favor, vuelve a iniciar sesión.")
            return redirect('login')  # Redirigir al login
        else:
            messages.error(request, "Las contraseñas no coinciden.")
    
    return render(request, 'change_password.html')

def login(request):
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Esto guarda el usuario en la base de datos
            messages.success(request, 'Tu cuenta ha sido creada con éxito. ¡Ahora puedes iniciar sesión!')
            return redirect('login')  # Redirigir a la página de inicio de sesión
        else:
            messages.error(request, 'Hubo un error en la creación de la cuenta. Inténtalo de nuevo.')
    else:
        form = CustomRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def test(request):
    return render(request, 'test.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def tipo_inscripcion(request):
    return render(request, 'inscripciones/tipo_inscripcion.html')

@login_required
def lista_solicitudes(request):
    # Filtramos las solicitudes que no están confirmadas (cuando ambos campos son False)
    solicitudes = DatInsc.objects.filter(matricula=False, legajo_fisico=False)

    # Inicializamos el formulario de la solicitud
    form = PreinscripcionForm()

    if request.method == 'POST':
        form = PreinscripcionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Se ha agregado exitosamente la solicitud.')
                return redirect('lista_solicitudes')
            except Exception as e:
                messages.error(request, f'Ocurrió un error al agregar la solicitud: {str(e)}')
        else:
            messages.error(request, 'Formulario inválido. Por favor revisa los campos e inténtalo de nuevo.')

    # Siempre devolver el formulario y las solicitudes, incluso para GET
    return render(request, 'inscripciones/solicitudes/lista_solicitudes.html', {
        'solicitudes': solicitudes,
        'form': form  # Pasamos el formulario al contexto
    })

@login_required
def confirmar_solicitud(request, id_datinsc):
    solicitud = get_object_or_404(DatInsc, id_datinsc=id_datinsc)

    if request.method == 'POST':
        matricula = request.POST.get('matricula') == 'True'  # Si no se marca, será False
        legajo_fisico = request.POST.get('legajo_fisico') == 'True'  # Si no se marca, será False

        # Actualizamos los campos en la solicitud
        solicitud.matricula = matricula
        solicitud.legajo_fisico = legajo_fisico
        solicitud.save()

        # Creamos un nuevo estudiante basado en la solicitud
        nuevo_estudiante = Estudiantes.objects.create(
            id_datinsc=solicitud,
            fecha_insc_est=date.today(),  # Corregido a date.today()
            nro_legajo=None,  # Esto puede depender de tus necesidades
            legajo_digital=None  # Esto puede depender de tus necesidades
        )

        # Mensaje de éxito y redirigir a la lista de solicitudes
        messages.success(request, 'Solicitud confirmada exitosamente.')
        return redirect('lista_solicitudes')

    return render(request, 'inscripciones/solicitudes/confirmar_solicitud.html', {'solicitud': solicitud})


@login_required
def editar_solicitud(request, id_datinsc):
    # Obtener la solicitud por su ID
    solicitud = get_object_or_404(DatInsc, id_datinsc=id_datinsc)

    if request.method == 'POST':
        # Llenar el formulario con los datos POST
        form = PreinscripcionForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitud actualizada con éxito.')
            return redirect('lista_solicitudes')
        else:
            messages.error(request, 'Hubo un error en el formulario. Por favor, corrige los errores.')
    else:
        # Pre-poblar el formulario con los datos de la solicitud
        form = PreinscripcionForm(instance=solicitud)

    return render(request, 'inscripciones/solicitudes/editar_solicitud.html', {'form': form})

@login_required
def eliminar_solicitud(request, id_datinsc):
    # Obtener la solicitud o devolver un 404 si no existe
    solicitud = get_object_or_404(DatInsc, id_datinsc=id_datinsc)
    
    if request.method == "POST":
        try:
            solicitud.delete()
            # Si la eliminación es exitosa, enviamos un mensaje de éxito
            messages.success(request, "La solicitud ha sido eliminada correctamente.")
        except Exception as e:
            # Si ocurre un error, enviamos un mensaje de error
            messages.error(request, f"Ocurrió un error al eliminar la solicitud: {str(e)}")
        
        # Redirigir a la lista de solicitudes
        return redirect('lista_solicitudes')
    
    # Si no es POST, simplemente renderizar la página de confirmación
    return render(request, 'inscripciones/solicitudes/eliminar_solicitud.html', {'solicitud': solicitud})

@login_required
def consultas(request):
    dni = request.GET.get('dni')  
    if dni:
        estudiante = DatInsc.objects.filter(dni=dni).first()
        if estudiante:
            print(estudiante.id_datinsc)  
            context = {'estudiante': estudiante}
        else:

            context = {'error': 'Estudiante no encontrado'}
    else:
        
        lista_estudiantes = DatInsc.objects.all()
        for est in lista_estudiantes:
            print(est.id_datinsc) 
        context = {'estudiantes': lista_estudiantes}
    
    return render(request, 'inscripciones/consultas/consultas.html',context)

@login_required
def modificar(request, id):
    estudiante = get_object_or_404(DatInsc, pk=id)
    if request.method == 'POST':
        # Procesar los datos del formulario de modificación (añade tu lógica de actualización aquí)
        estudiante.nombre = request.POST.get('nombre')
        estudiante.apellido = request.POST.get('apellido')
        estudiante.dni = request.POST.get('dni')
        estudiante.Celular_Nro = request.POST.get('telefono')
        estudiante.email = request.POST.get('email')
        estudiante.domicilio = request.POST.get('domicilio')
        estudiante.save()
        messages.success(request, '¡Estudiante modificado exitosamente!')
        return redirect('consultas')
    return render(request, 'inscripciones/consultas/modificar.html', {'estudiante': estudiante})


# Vista para eliminar estudiante
@login_required
def eliminar_estudiante_ajax(request):
    estudiante_id = request.POST.get('id')
    estudiante = get_object_or_404(DatInsc, id_datinsc=estudiante_id)
    estudiante.delete()
    return JsonResponse({'success': True, 'message': 'Estudiante eliminado'}) # type: ignore


# Vista para adjuntar un archivo
@login_required
def adjuntar_archivo(request):
    if request.method == 'POST':
        try:
            archivo = request.FILES['fileUpload']
            return HttpResponse('Archivo subido exitosamente.') # type: ignore
        except KeyError:
            return HttpResponse('No se encontró el archivo.') # type: ignore
    return render(request, 'Insc/consultas.html')

def build(request):
    return render(request, 'build.html')

