import random
from django.db import IntegrityError
from APPWapiptda.models import *
from APPWapiptda.serializer import *
from APPWapiptda.views import *
#from rest_framework import viewsets, generics
from django.http import JsonResponse
#from django.urls import reverse
from datetime import datetime

# from django.views.decorators.csrf import csrf_exempt
import json
import cloudinary.uploader
import cloudinary.api
import cloudinary
from cloudinary import uploader
# from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail



## METODOS DE GENERACION DE CODIGO IDENTIFICADOR UNICO  ##


# Método para generar un identificador único para cada registro de dominio
def generar_identificador_unico():
    """Genera un identificador único para Dominio."""
    identificador = str(random.randint(1000, 9999))
    while Dominio.objects.filter(identificador_dominio=identificador).exists():
        identificador = str(random.randint(1000, 9999))
    return identificador

# Método para generar un identificador único para cada registro de contenido
def generar_identificador_contenido():
    """Genera un identificador único para Contenido."""
    identificador_c = str(random.randint(10000, 20000))
    while Contenido.objects.filter(identificador_contenido=identificador_c).exists():
        identificador_c = str(random.randint(10000, 20000))
    return identificador_c

# Método para generar un identificador único para cada registro de contenido individual
# que permitirá diferenciar las actividades que serán asignadas mediante las salas de contenido
def generar_identificador_individual():
    """Genera un identificador único para Contenido Individual."""
    identificador_i = str(random.randint(20001, 30000))
    while ContenidoIndividual.objects.filter(identificador_individual=identificador_i).exists():
        identificador_i = str(random.randint(20001, 30000))
    return identificador_i

# Método para generar un identificador único para cada registro de curso
def generar_identificador_curso():
    """Genera un identificador único para Curso."""
    identificador_c = str(random.randint(30001, 40000))
    while Curso.objects.filter(identificador_curso=identificador_c).exists():
        identificador_c = str(random.randint(30001, 40000))
    return identificador_c



## METODOS PARA VERIFICAR LA EXISTENCIA DE REGISTROS
    

## Método para verficar la existencia de un registro de nivel mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_nivel(request, slug):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if is_tecnico(user):
                if request.method == 'GET':
                    # Obtenemos el objeto grado tdah
                    grado__ob = GradoTDAH.objects.get(slug_grado=slug)
                    context = {
                        'success': True,
                        'identificador': grado__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de nivel'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de dominio mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_dominio(request, slug):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                if request.method == 'GET':
                    # Obtenemos el objeto dominio
                    dominio__ob = Dominio.objects.get(slug_dominio=slug)
                    context = {
                        'success': True,
                        'identificador': dominio__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de dominio'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de contenido mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_contenido(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                # Encontrar el contenido en base al slug
                contenido__ob = Contenido.objects.get(slug_contenido=slug)
                # Verificar si el dominio existe
                if contenido__ob:
                    context = {
                        'success': True,
                        'identificador': contenido__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de contenido'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de una actividad mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_contenido_individual(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                # Encontrar el contenido en base al slug
                contenido__ob = ContenidoIndividual.objects.get(slug_contenido_individual=slug)
                # Verificar si el dominio existe
                if contenido__ob:
                    context = {
                        'success': True,
                        'identificador': contenido__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de contenido individual'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de curso mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_curso(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if is_comun(user) or is_tecnico(user):
                # Encontrar el contenido en base al slug
                curso__ob = Curso.objects.get(slug_curso=slug)
                # Verificar si el dominio existe
                if curso__ob:
                    context = {
                        'success': True,
                        'identificador': curso__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de curso'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de una petición mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_peticion(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                # Encontrar el contenido en base al slug
                peticion__ob = Peticion.objects.get(slug_peticion=slug)
                # Verificar si el dominio existe
                if peticion__ob:
                    context = {
                        'identificador': peticion__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de peticion'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de resultado mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_resultado(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                # Encontrar el resultado en base al slug
                resultado__ob = Resultado.objects.get(slug_resultado=slug)
                # Verificar si el dominio existe
                if resultado__ob:
                    context = {
                        'identificador': resultado__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de resultado'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de sala mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_sala(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                # Encontrar el resultado en base al slug
                sala__ob = Sala.objects.get(slug_sala=slug)
                # Verificar si el dominio existe
                if sala__ob:
                    context = {
                        'identificador': sala__ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de sala'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)


## Método para verficar la existencia de un registro de reporte mediante un slug
## que permite buscar y comprobar la existencia del registro
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_reporte(request, slug):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                # Encontrar el resultado en base al slug
                reporte_ob = Reporte.objects.get(slug_reporte=slug)
                # Verificar si el dominio existe
                if reporte_ob:
                    context = {
                        'identificador': reporte_ob.id,
                        'slug': slug
                    }
                    return JsonResponse(context)
                else:
                    context = {'error': 'Error al mostrar datos de reporte'}
                    return JsonResponse(context)
            else:
                context = {'errorSalida': 'El usuario no esta autenticado'}
                return JsonResponse(context, status=401)
        except Exception as e:
            context = {'errorSalida': 'El usuario no esta autenticado'}
            return JsonResponse(context, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)



## METODOS PARA REGISTROS DE ENTIDADES ##



## Método para registro del nivel de TDAH en el sistema, donde se debe considerar la existencia de dos
## niveles y unicamente se podra hacerlo si no existen registros y no sean mayor a dos
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_nivel_register(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token para obtener el usuario
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                # Encontrar al usuario relacionado al user
                usuario__ob = Usuario.objects.get(user=user)
                # Verificar si el usuario existe
                if request.method == 'POST' and user:
                    data = json.loads(request.body)
                    nombre_nivel_ = data.get('nombre')
                    descripcion_grado_ = data.get('descripcion')
                    numero_categorias_ = data.get('numero_categorias')
                    grado_dificultad_ = data.get('grado_dificultad')
                    cont = numero_de_niveles()
                    if cont < 2:
                        # Verificar si el nombre del nivel ya existe
                        if nombre_nivel_exist(nombre_nivel_):
                            return JsonResponse({'error': 'El nombre del nivel ya existe'})
                        else:
                            # Creamos el grado
                            if guardar_nivel(nombre_nivel_, descripcion_grado_, numero_categorias_, grado_dificultad_, usuario__ob):
                                return JsonResponse({'success': True})
                            else:
                                return JsonResponse({'error': 'Error al guardar el nivel'})
                    else:
                        return JsonResponse({'error': 'Solo se permite 2 niveles'})
                else:
                    return JsonResponse({'error': 'No esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Método para guardar el registro de nivel 
def guardar_nivel(ob1, ob2, ob3, ob4, ob5):
    try:
        # Capturamos la fecha de registro del nivel
        fecha_registro_grado_ = datetime.now().date()
        # Guardamos el registro
        grado = GradoTDAH.objects.create(
            nombre_nivel=ob1,
            descripcion_grado=ob2,
            numero_categorias=ob3,
            grado_dificultad=ob4,
            usuario_tecnico=ob5,
            fecha_registro_grado=fecha_registro_grado_
        )
        # Añadimos a contenido
        grado.save()
        return True
    except Exception as e:
        return False

# Verificar la existencia del nombre de un registro de nivel
def nombre_nivel_exist(ob1):
    try:
        if GradoTDAH.objects.filter(nombre_nivel__iexact=ob1).exists():
            return True
    except GradoTDAH.DoesNotExist:
        return False
    return False

# Verificar el número de niveles y dominios registrados en el sistema
def numero_de_niveles():
    try:
        return GradoTDAH.objects.all().count()
    except GradoTDAH.DoesNotExist:
        return 0

def numero_de_dominios():
    try:
        return Dominio.objects.all().count()
    except Dominio.DoesNotExist:
        return 0


## Método para devolver el contador de niveles para controla el registro de dominios
## y controlar el número de controladores de dominios
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_nivel_contador(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token para obtener el usuario
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                # Verificar si el usuario existe
                if request.method == 'GET' and user:
                    # Contamos el numero de niveles
                    contador = numero_de_niveles()
                    # Contamos el numero de dominios
                    contador_dominios = numero_de_dominios()
                    return JsonResponse({'success': True, 'contador': contador, 'dominioc': contador_dominios})
                else:
                    return JsonResponse({'error': 'No esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})
 

# Método para el registro de dominios en el sistema controlado por medio del numero de 
## categorías que se encuentra registrado en el registro de nivel. Esto es controlado por 
## la duplicidad del registro de dominio por medio del nombre
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_dominio_register(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token para obtener el usuario
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                # Encontrar al usuario relacionado al user
                usuario__ob = Usuario.objects.get(user=user)
                # Verificar si el usuario existe
                if request.method == 'POST' and user:
                    nombre_dominio_ = request.POST.get('nombre')
                    descripcion_ = request.POST.get('descripcion')
                    portada_ = request.FILES.get(
                        'portada_dominio')  # obtener archivo
                    # Verificar si el nombre del dominio ya existe
                    if nombre_dominio_exist(nombre_dominio_):
                        return JsonResponse({'error': 'El nombre del dominio ya existe'})
                    else:
                        # Calculamos el identificador
                        identificador_ = generar_identificador_unico()
                        if control_categorias():
                            # Creamos el contenido
                            if guardar_dominio(nombre_dominio_, identificador_, descripcion_, portada_, usuario__ob):
                                return JsonResponse({'success': True})
                            else:
                                return JsonResponse({'error': 'Error al guardar el dominio'})
                        else:
                            return JsonResponse({'error': 'No se puede registrar el dominio porque se excede lo permitido'})
                else:
                    return JsonResponse({'error': 'No esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al crear el dominio'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Métdo para guardar el registro de dominio en el sistema
def guardar_dominio(ob1, ob2, ob3, ob4, ob5):
    try:
        # Capturamos la fecha del registro de dominio
        fecha_registro_dominio_ = datetime.now().date()
        dominio = Dominio.objects.create(
            nombre=ob1,
            identificador_dominio=ob2,
            descripcion=ob3,
            portada_dominio=ob4,
            usuario=ob5,
            fecha_registro_dominio=fecha_registro_dominio_
            )
        # Añadimos a contenido
        dominio.save()
        return True
    except Exception as e:
        return False

# Verificar la existencia del nombre de un registro de dominio
def nombre_dominio_exist(ob1):
    try:
        if Dominio.objects.filter(nombre__iexact=ob1).exists():
            return True
    except Dominio.DoesNotExist:
        return False
    return False

# Verificar el numero de categorias permitidad en el sistema
def control_categorias():
    try:
        # Obtenemos los registros de nivel
        grado__ob = GradoTDAH.objects.all()
        # Buscamos el numero_categorias de los niveles
        numero_categorias_ = 0
        for grado in grado__ob:
            # Capturamos siempre el mayor numero de categorias
            if grado.numero_categorias > numero_categorias_:
                numero_categorias_ = grado.numero_categorias
        # Buscamos el numero de dominios registrados
        dominiio_ob = Dominio.objects.all()
        numero_dominios_ = dominiio_ob.count()
        # Verificar si el numero de dominios es menor al numero de categorias
        if numero_dominios_ < numero_categorias_:
            return True
        else:
            return False
    except GradoTDAH.DoesNotExist:
        return False



#### EDICION DE DOMINIO 


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_dominio_edicion(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token para obtener el usuario
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                # Encontrar al usuario relacionado al user
                usuario__ob = Usuario.objects.get(user=user)
                # Verificar si el usuario existe y esta en la operación correcta
                if request.method == 'POST' and user:
                    id_dominio = request.POST.get('identificador')
                    nombre_dominio_ = request.POST.get('nombre')
                    descripcion_ = request.POST.get('descripcion')
                    portada_ = request.FILES.get(
                        'portada_dominio')  # obtener archivo
                    # Verificar si portada dominio es null o contiene contenido
                    if portada_:
                        portada_nueva = portada_
                    else:
                        portada_nueva = None
                    # Verificar que portada es NONE
                    if portada_nueva == None:
                        return JsonResponse({'error': 'No se pudo editar el registro de dominio'})
                    # Verificar si el nombre del dominio es el mismo que el anterior o es nuevo
                    if nombre_dominio_exist(nombre_dominio_):
                        # Obtener el identificador público del archivo en Cloudinary de portada en Dominio
                        public_id = obtener_public_id(id_dominio)
                        # Verificamos el public id obtenido
                        if public_id:
                            # Eliminar la imagen de portada de Cloudinary
                            resultado_eliminacion  = eliminar_archivo_cloudinary(public_id)
                            if resultado_eliminacion and resultado_eliminacion.get('result') == 'ok':
                                # Editamos el dominio
                                if editar_dominio(id_dominio, nombre_dominio_, descripcion_, portada_nueva, usuario__ob):
                                    return JsonResponse({'success': True})
                                else:
                                    return JsonResponse({'error': 'Error al editar el dominio'})
                            else:
                                return JsonResponse({'error': 'No se pudo editar el registro de dominio'})
                        else:
                            return JsonResponse({'error': 'No se pudo editar el registro de dominio'})
                    else:
                        # Verificar si el nombre del dominio ya existe
                        if nombre_dominio_exist(nombre_dominio_):
                            return JsonResponse({'error': 'El nombre del dominio ya existe. No es posible editar.'})
                        else:
                            # Verificamos el public id obtenido
                            if public_id:
                                # Eliminar la imagen de portada de Cloudinary
                                resultado_eliminacion  = eliminar_archivo_cloudinary(public_id)
                                if resultado_eliminacion and resultado_eliminacion.get('result') == 'ok':
                                    # Editamos el dominio
                                    if editar_dominio(id_dominio, nombre_dominio_, descripcion_, portada_nueva, usuario__ob):
                                        return JsonResponse({'success': True})
                                    else:
                                        return JsonResponse({'error': 'Error al editar el dominio'})
                                else:
                                    return JsonResponse({'error': 'No se pudo editar el registro de dominio'})
                            else:
                                return JsonResponse({'error': 'No se pudo editar el registro de dominio'})
                else:
                    return JsonResponse({'error': 'No esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al editar el dominio'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

## Método para editar el dominio
def editar_dominio(ob1, ob2, ob3, ob4, ob5):
    try:
        # Obtenemos el objeto dominio del id 
        dominio_ob = Dominio.objects.get(id=ob1)
        # Editamos el registro
        dominio_ob.nombre = ob2
        dominio_ob.descripcion = ob3
        dominio_ob.portada_dominio = ob4
        dominio_ob.usuario = ob5
        # Guardamos el registro
        dominio_ob.save()
        return True
    except Dominio.DoesNotExist:
        return False
    except Exception as e:
        return False

## Método para obtener el public id del archivo relacionado al registro para dar 
## paso a la eliminación del archivo en Cloudinary
def obtener_public_id(ob1):
    try:
        # Obtener el objeto de Dominio por su ID
        dominio_ob = Dominio.objects.get(id=ob1)
        # Verificar si el Dominio tiene una imagen de portada
        if dominio_ob.portada_dominio:
            # Obtener el public ID de la imagen en Cloudinary
            public_id = cloudinary.CloudinaryImage(dominio_ob.portada_dominio.name).public_id
            return public_id
        else:
            # El Dominio no tiene una imagen de portada
            return None
    except Dominio.DoesNotExist:
        # Manejar la excepción si el Dominio no existe
        print("El Dominio no existe.")
        return None
    except Exception as e:
        # Manejar otras excepciones
        print("Error al obtener el public ID:", e)
        return None

## Método que da origen a la eliminación del archivo en Cloudinary
def eliminar_archivo_cloudinary(public_id):
    try:
        result = uploader.destroy(public_id)
        return result
    except Exception as e:
        return None



##### EDICION DE CONTENIDO 


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_contenido_edicion(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token para obtener el usuario
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                # Verificar si el usuario existe y esta en la operación correcta
                if request.method == 'POST' and user:
                    id_contenido = request.POST.get('identificador')
                    nombre_contenido_ = request.POST.get('nombre')
                    dominio_tipo_ = request.POST.get('dominio_tipo')
                    portada_ = request.FILES.get(
                        'portada')  # obtener archivo
                    # Verificar si portada dominio es null o contiene contenido
                    if portada_:
                        portada_nueva = portada_
                    else:
                        portada_nueva = None
                    # Verificar que portada es NONE
                    if portada_nueva == None:
                        return JsonResponse({'error': 'No se pudo editar el registro de contenido'})
                    # Verificar si el nombre del contenido es el mismo que el anterior o es nuevo
                    if nombre_contenido_exist(nombre_contenido_):
                        # Obtener el identificador público del archivo en Cloudinary de portada en Dominio
                        public_id = obtener_public_id_contenido(id_contenido)
                        # Verificamos el public id obtenido
                        if public_id:
                            # Eliminar la imagen de portada de Cloudinary
                            eliminar_conte  = eliminar_archivo_cloudinary(public_id)
                            if eliminar_conte and eliminar_conte.get('result') == 'ok':
                                # Editamos el contenido
                                if editar_contenido(id_contenido, nombre_contenido_, dominio_tipo_, portada_nueva):
                                    return JsonResponse({'success': True})
                                else:
                                    return JsonResponse({'error': 'Error al editar el contenido'})
                            else:
                                return JsonResponse({'error': 'No se pudo editar el registro de contenido'})
                        else:
                            return JsonResponse({'error': 'No se pudo editar el registro de contenido'})
                    else:
                        # Verificar si el nombre del contenido ya existe
                        if nombre_contenido_exist(nombre_contenido_):
                            return JsonResponse({'error': 'El nombre del contenido ya existe. No es posible editar.'})
                        else:
                            # Obtener el identificador público del archivo en Cloudinary de portada en Dominio
                            public_id = obtener_public_id_contenido(id_contenido)
                            # Verificamos el public id obtenido
                            if public_id:
                                # Eliminar la imagen de portada de Cloudinary
                                eliminar_conte  = eliminar_archivo_cloudinary(public_id)
                                if eliminar_conte and eliminar_conte.get('result') == 'ok':
                                    # Editamos el contenido
                                    if editar_contenido(id_contenido, nombre_contenido_, dominio_tipo_, portada_nueva):
                                        return JsonResponse({'success': True})
                                    else:
                                        return JsonResponse({'error': 'Error al editar el contenido'})
                                else:
                                    return JsonResponse({'error': 'No se pudo editar el registro de contenido'})
                            else:
                                return JsonResponse({'error': 'No se pudo editar el registro de contenido'})
                else:
                    return JsonResponse({'error': 'No esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al editar el contenido'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

## Método para obtener el public id del archivo relacionado al registro para dar 
## paso a la eliminación del archivo en Cloudinary
def obtener_public_id_contenido(ob1):
    try:
        # Obtener el objeto de Contenido por su ID
        contenido_ob = Contenido.objects.get(id=ob1)
        # Verificar si el Contenido tiene una imagen de portada
        if contenido_ob.portada:
            # Obtener el public ID de la imagen en Cloudinary
            public_id = cloudinary.CloudinaryImage(contenido_ob.portada.name).public_id
            return public_id
        else:
            # El Contenido no tiene una imagen de portada
            return None
    except Contenido.DoesNotExist:
        # Manejar la excepción si el Dominio no existe
        print("El Contenido no existe.")
        return None
    except Exception as e:
        # Manejar otras excepciones
        print("Error al obtener el public ID:", e)
        return None

## Método para editar el contenido
def editar_contenido(ob1, ob2, ob3, ob4):
    try:
        # Obtenemos el objeto contenido del id 
        contenido_ob = Contenido.objects.get(id=ob1)
        # Editamos el registro
        contenido_ob.nombre = ob2
        contenido_ob.dominio_tipo = ob3
        contenido_ob.portada = ob4
        # Guardamos el registro
        contenido_ob.save()
        return True
    except Contenido.DoesNotExist:
        return False
    except Exception as e:
        return False



## Método para registrar un registro de contenido en el sistema verificado por ser único
## para evitar la duplicidad de registros y que se encuentre relacionado a un dominio
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_contenido_register(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                # Verificar si el usuario existe
                if request.method == 'POST' and user:
                    nombre_contenido_ = request.POST.get('nombre')
                    dominio_ = request.POST.get('dominio_tipo')
                    portada_ = request.FILES.get('portada')
                    # Verificar si el nombre del contenido ya existe
                    if nombre_contenido_exist(nombre_contenido_):
                        return JsonResponse({'error': 'El nombre del contenido ya existe'})
                    else:
                        # Calculamos el identificador
                        identificador_ = generar_identificador_contenido()
                        # Obtenemos el objeto dominio por el nombre
                        dominio__ob = Dominio.objects.get(nombre=dominio_)
                        # Creamos el contenido
                        if guardar_contenido(nombre_contenido_, identificador_, dominio_, portada_, dominio__ob):
                            return JsonResponse({'success': True})
                        else:
                            return JsonResponse({'error': 'Error al guardar el contenido'})
                else:
                    return JsonResponse({'error': 'No esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al crear el contenido'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Métdo para guardar el registro de contenido en el sistema
def guardar_contenido(ob1, ob2, ob3, ob4, ob5):
    try:
        # Capturamos la fecha de registro del contenido
        fecha_registro_contenido_ = datetime.now().date()
        # Guardamos el registro
        contenido = Contenido.objects.create(
            nombre=ob1,
            identificador_contenido=ob2,
            dominio_tipo=ob3,
            portada=ob4,
            dominio=ob5,
            fecha_registro_contenido=fecha_registro_contenido_
        )
        # Añadimos a contenido
        contenido.save()
        return True
    except Exception as e:
        return False

# Verificar la existencia del nombre de un registro de contenido
def nombre_contenido_exist(ob1):
    try:
        if Contenido.objects.filter(nombre__iexact=ob1).exists():
            return True
    except Contenido.DoesNotExist:
        return False
    return False



# Método para guardar un registro de actividad en el sistema controlado por medio del 
## tipo de actividad y a través de esto verificar cuantos registros de archivos de contenido
# ## tipo imagen se van a realizar.  
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_contenido_individual_register(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            # Validamos si el usuario es tecnico
            if is_tecnico(user):
                if request.method == 'POST' and user:
                    descripcion_ = request.POST.get('descripcion_individual')
                    tipocontenido_ = request.POST.get('tipo_contenido')
                    respuesta_ = request.POST.get('respuesta')
                    contenido_ = request.FILES.get('contenido_individual')
                    img1_ = request.FILES.get('img1')
                    img2_ = request.FILES.get('img2')
                    img3_ = request.FILES.get('img3')
                    img4_ = request.FILES.get('img4')
                    img5_ = request.FILES.get('img5')
                    portada_ = request.FILES.get('portada_individual')
                    pertenece_ = request.POST.get('conten')
                    nombre_nivel_ = request.POST.get('nombre_nivel')
                    # Obtenemos el objeto contenido por el nombre
                    contenido__ob = Contenido.objects.get(nombre=pertenece_)
                    # Calculamos el identificador
                    identificador_ = generar_identificador_individual()
                    # Creamos el contenido
                    if tipocontenido_ == 'pintar_imagen':
                        if guardar_contenido_individual_4(descripcion_, identificador_, tipocontenido_, contenido_, 
                                                        portada_, respuesta_, nombre_nivel_, contenido__ob,
                                                         img1_):
                            return JsonResponse({'success': True})
                        else:
                            return JsonResponse({'error': 'Error al guardar el contenido individual'})
                    elif tipocontenido_ == 'seleccionar_imagen' or tipocontenido_ == 'selecion_multiple_img' or tipocontenido_ == 'pictograma':
                        # Para imagen 1, 2 y 3 y que no exista imagen 4 y 5
                        if img1_ and img2_ and img3_ and not img4_ and not img5_:
                            if guardar_contenido_individual_2(descripcion_, identificador_, tipocontenido_, contenido_, 
                                                            portada_, respuesta_, nombre_nivel_, contenido__ob, img1_, img2_, img3_):
                                return JsonResponse({'success': True})
                            else:
                                return JsonResponse({'error': 'Error al guardar el contenido individual'})
                        elif img1_ and img2_ and img3_ and img4_ and img5_:
                            if guardar_contenido_individual_3(descripcion_, identificador_, tipocontenido_, contenido_, 
                                                            portada_, respuesta_, nombre_nivel_, contenido__ob, img1_, img2_, img3_):
                                return JsonResponse({'success': True})
                            else:
                                return JsonResponse({'error': 'Error al guardar el contenido individual'})
                        else:
                            return JsonResponse({'error': 'Error al guardar el contenido individual'})
                    else:
                        if guardar_contenido_individual(descripcion_, identificador_, tipocontenido_, contenido_, 
                                                    portada_, respuesta_, nombre_nivel_, contenido__ob):
                            return JsonResponse({'success': True})
                        else:
                            return JsonResponse({'error': 'Error al guardar el contenido individual'})
                else:
                    return JsonResponse({'error': 'Error al guardar el contenido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al crear el contenido individual'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Métodos para guardar el registro de actividad en el sistema dependiendo del tipo de contenido que
# se desea ingresar. Se controla segun el numero de imagenes que se ingresa 
def guardar_contenido_individual(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8):
    try:
        # Obtenemos la fecha actual de registro de la actividad
        fecha_registro_individual_ = datetime.now().date()
        contenido_individual = ContenidoIndividual.objects.create(
            descripcion_individual=ob1,
            identificador_individual=ob2,
            tipo_contenido=ob3,
            contenido_individual=ob4,
            portada_individual=ob5,
            respuesta=ob6,
            nivel=ob7,
            contenido=ob8,
            fecha_registro_individual=fecha_registro_individual_
        )
        # Añadimos a contenido
        contenido_individual.save()
        return True
    except Exception as e:
        return False

def guardar_contenido_individual_2(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8, ob9, ob10, ob11):
    try:
        # Obtenemos la fecha actual de registro de la actividad
        fecha_registro_individual_ = datetime.now().date()
        contenido_individual = ContenidoIndividual.objects.create(
            descripcion_individual=ob1,
            identificador_individual=ob2,
            tipo_contenido=ob3,
            contenido_individual=ob4,
            imagen1=ob9,
            imagen2=ob10,
            imagen3=ob11,
            portada_individual=ob5,
            respuesta=ob6,
            nivel=ob7,
            contenido=ob8,
            fecha_registro_individual=fecha_registro_individual_
        )
        # Añadimos a contenido
        contenido_individual.save()
        return True
    except Exception as e:
        return False

def guardar_contenido_individual_3(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8, ob9, ob10, ob11, ob12, ob13):
    try:
        # Obtenemos la fecha actual de registro de la actividad
        fecha_registro_individual_ = datetime.now().date()
        contenido_individual = ContenidoIndividual.objects.create(
            descripcion_individual=ob1,
            identificador_individual=ob2,
            tipo_contenido=ob3,
            contenido_individual=ob4,
            imagen1=ob9,
            imagen2=ob10,
            imagen3=ob11,
            imagen4=ob12,
            imagen5=ob13,
            portada_individual=ob5,
            respuesta=ob6,
            nivel=ob7,
            contenido=ob8,
            fecha_registro_individual=fecha_registro_individual_
        )
        # Añadimos a contenido
        contenido_individual.save()
        return True
    except Exception as e:
        return False

def guardar_contenido_individual_4(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8, ob9):
    try:
        # Obtenemos la fecha actual de registro de la actividad
        fecha_registro_individual_ = datetime.now().date()
        contenido_individual = ContenidoIndividual.objects.create(
            descripcion_individual=ob1,
            identificador_individual=ob2,
            tipo_contenido=ob3,
            contenido_individual=ob4,
            imagen1=ob9,
            portada_individual=ob5,
            respuesta=ob6,
            nivel=ob7,
            contenido=ob8,
            fecha_registro_individual=fecha_registro_individual_
        )
        # Añadimos a contenido
        contenido_individual.save()
        return True
    except Exception as e:
        return False



# Método para realizar el registro de curso en el sistema controlado por medio del nombre único
## para evitar la duplicidad de registros y que se encuentre relacionado a un usuario común
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_curso_register(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            # Validamos si el usuario es comun
            if is_comun(user):
                print("Pasamos el if")
                if request.method == 'POST' and user:
                    data = json.loads(request.body)
                    nombre_curso_ = data.get('nombre_curso')
                    descripcion_ = data.get('descripcion')
                    # Verificar si el nombre del curso ya existe
                    if nombreCurso_exist(nombre_curso_):
                        return JsonResponse({'error': 'El nombre del curso ya existe'})
                    else:
                        # Calculamos el identificador
                        identificador_ = generar_identificador_curso()
                        comun__ob = UsuarioComun.objects.get(user=user)
                        # Creamos el curso
                        if guardar_curso(nombre_curso_, descripcion_, identificador_, comun__ob):
                            return JsonResponse({'success': True})
                        else:
                            return JsonResponse({'error': 'No es posible crear el curso'})
                else:
                    return JsonResponse({'error': 'Error al crear el curso'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al crear el curso'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Registro de curso en el sistema
def guardar_curso(ob1, ob2, ob3, ob4):
    try:
        # Obtenemos la fecha actual de registro
        fecha_registro_curso_ = datetime.now().date()
        curso = Curso.objects.create(
            nombre_curso=ob1,
            descripcion_curso=ob2,
            identificador_curso=ob3,
            usuario_comun=ob4,
            fecha_registro_curso=fecha_registro_curso_
        )
        # Añadimos a contenido
        curso.save()
        return True
    except Exception as e:
        return False

# Verificación de existencia de registro de curso por medio del nombre del mismo
def nombreCurso_exist(ob1):
    try:
        if Curso.objects.filter(nombre_curso__iexact=ob1).exists():
            return True
    except Curso.DoesNotExist:
        return False
    return False



# Método para guardar el registro de inscripción de un estudiante en un curso 
## donde la inscripción al curso debe ser única
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_curso_inscripcion(request, id):
    if request.user.is_authenticated:
        try:
            # Verificar existencia de token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if is_paciente(user):
                # Encontrar el paciente del user
                paciente__ob = Paciente.objects.get(user=user)
                # Encontrar el curso en base al id
                curso__ob = Curso.objects.get(id=id)
                # Verificar si el curso existe
                if curso__ob:
                    # Creamos el detalle de inscripcion
                    if guardar_inscripcion(paciente__ob, curso__ob):
                        return JsonResponse({'success': True})
                    else:
                        return JsonResponse({'error': 'No pudo inscribirse'}, status=500)
            else:
                return JsonResponse({'errorSalida': 'El usuario no esta autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'errorSalida': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)

# Guardar el registro de inscripción de un estudiante en un curso específico
def guardar_inscripcion(ob1, ob2):
    try:
        detalle_inscripcion = DetalleInscripcionCurso.objects.create(
            paciente=ob1,
            curso=ob2
        )
        # Añadimos a contenido
        detalle_inscripcion.save()
        return True
    except Exception as e:
        return False



# Método para guardar el registro de petición en el sistema controlado por el envió de un correo
## electrónico a los usuarios técnicos registrados en el sistema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_peticion_register(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token para obtener el usuario
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            # Validamos si el usuario es tecnico
            if is_comun(user):
                # Encontrar al usuario relacionado al user
                usuario__ob = UsuarioComun.objects.get(user=user)
                # Verificar si el usuario existe
                if request.method == 'POST' and usuario__ob:
                    data = json.loads(request.body)
                    motivo_peticion_ = data.get('motivo')
                    tipo_peticion_ = data.get('tipo')
                    peticion_cuerpo_ = data.get('peticion_cuerpo')
                    # Verificar envios de correo
                    if not enviar_correo_peticion(usuario__ob):
                        return JsonResponse({'error': 'No se pudo notificar adecuadamente a los técnicos. Vuelve a intentarlo.'})
                    # Creamos el contenido
                    if guardar_peticion(motivo_peticion_, tipo_peticion_, peticion_cuerpo_, usuario__ob):
                    # Actualizamos el contador
                        contador_obj, created = ContadorPeticiones.objects.get_or_create(pk=1)
                        contador_obj.contador += 1
                        contador_obj.save()
                        # Enviamos una respuesta al front
                        return JsonResponse({'success': True})
                    else:
                        return JsonResponse({'error': 'No se pudo guardar la petición'})
                else:
                    return JsonResponse({'error': 'Algo no es esta permitido'})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except Exception as e:
            return JsonResponse({'error': 'Error al crear la petición'})
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Método para guardar el registro de petición en el sistema
def guardar_peticion(ob1, ob2, ob3, ob4):
    try:
        # Capturamos la fecha actual de registro de petición
        fecha_registro_peticion_ = datetime.now().date()
        peticion = Peticion.objects.create(
            motivo_peticion=ob1,
            tipo_peticion=ob2,
            peticion_cuerpo=ob3,
            usuario_comun=ob4,
            fecha_registro_peticion=fecha_registro_peticion_
        )
        # Añadimos a peticion
        peticion.save()
        return True
    except Exception as e:
        return False

# Método para enviar correo de notificación de petición existentes a los usuarios tecnicos 
## registrados en el sistema
def enviar_correo_peticion(ob1):
    try:
        # Obtenemos el nombre de usuario y appellido del usuario comun
        nombre_u = ob1.nombre_usuario
        apellido_u = ob1.apellido_usuario
        # Obtener los correos de usuarios tecnico
        tecnico__ob = Usuario.objects.all()
        for tecnico in tecnico__ob:
            correo = tecnico.user.email
            # Email
            subject = 'Registro de peticiones en WAPIPTDAH'
            message = f'Reciba un cordial saludo de los administradores de WAPIPTDAH. ' \
                f'\nRecibimos el registro de nuevas peticiones por parte del usuario: {nombre_u} {apellido_u}. ' \
                f'\nEste es un mensaje para notificar la existencia de nuevas actividades. ' \
                f'\n\n' \
                f'\nSe recomeinda de la manera mas comedida atender a las peticiones existenes.'\
                f'\n\n' \
                f'\nGracias por preferirnos como su sitio de trabajo. !Hasta pronto¡ ' \
                f'\n' \
                f'\nAtentamente: WAPIPTDAH.'
            from_email = settings.EMAIL_HOST_USER
            receiver_email = [correo]
            # Envio del correo
            send_mail(subject, message, from_email, receiver_email, fail_silently=False)
        # Enviamos una respuesta al front
        return True
    except Exception as e:
        print(f"Error enviando el correo: {e}")
        return False


# Método para guardar el registro de resultado originado por un estudiante al momento de responder a 
## una actividad específica en el sistema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def save_resultado(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if (is_paciente(user)):
                if request.method == 'POST':
                    data = json.loads(request.body)
                    tiempo_transcurrido_m = data.get('tiempoTranscurrido__minutos')
                    tiempo_transcurrido_s = data.get('tiempoTranscurrido__segundos')
                    respuesta__contenido = data.get('respuesta')
                    slug__con = data.get('slug__')
                    # Obtenemos el objeto contenido
                    contenido__ob = ContenidoIndividual.objects.get(slug_contenido_individual=slug__con)
                    # Obtenemos el objeto paciente
                    paciente__ob = Paciente.objects.get(user=user)
                    # Capturamos la fecha actual o del momento de registro
                    # Obtiene la fecha actual sin la hora
                    fecha_registro_resultado_ = datetime.now().date()
                    # Captura de respuesta
                    if tiempo_transcurrido_m == 0 and tiempo_transcurrido_s == 0:
                        tiempo_transcurrido_m_ = 40
                        tiempo_transcurrido_s_ = 1
                        respuesta__contenido_ = "No resuelto"
                        observacion = "No resuelto"
                        # Guardamos el resultado
                        if guardar_resultado_no(
                            tiempo_transcurrido_m_, tiempo_transcurrido_s_, respuesta__contenido_,
                            observacion, contenido__ob, paciente__ob, fecha_registro_resultado_):
                            # Enviamos una respuesta al front
                            return JsonResponse({'success': True})
                        else:
                            error_message = "Error al agregar resultado."
                            context = {'error': error_message, 'success': False}
                            return JsonResponse(context)

                    else:
                        if tiempo_transcurrido_m or tiempo_transcurrido_s:
                            # Guardamos el resultado
                            if guardar_resultado(tiempo_transcurrido_m, tiempo_transcurrido_s, 
                                            respuesta__contenido, contenido__ob, paciente__ob, fecha_registro_resultado_):
                                # Enviamos una respuesta al front
                                return JsonResponse({'success': True})
                            else:
                                error_message = "Error al agregar resultado."
                                context = {'error': error_message, 'success': False}
                                return JsonResponse(context)
                        else:
                            error_message = "Tiempo transcurrido no proporcionado."
                            context = {'error': error_message, 'success': False}
                            return JsonResponse(context)
                else:
                    error_message = "Error al agregar resultado."
                    context = {'error': error_message, 'success': False}
                    return JsonResponse(context)
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'})
        except IntegrityError:
            error_message = "Error al agregar."
            context = {'error': error_message, 'success': False}
            return JsonResponse(context)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'})

# Métodos para guardar el registro de resultado en el sistema asociado a un estudiante en específico
def guardar_resultado(ob1, ob2, ob3, ob4, ob5, ob6):
    try:
        resultado_obj = Resultado.objects.create(
            tiempo_m=ob1,
            tiempo_s=ob2,
            respuesta=ob3,
            contenido_individual=ob4,
            paciente=ob5,
            fecha_registro_resultado=ob6
        )
        resultado_obj.save()
        return True
    except Exception as e:
        return False

def guardar_resultado_no(ob1, ob2, ob3, ob4, ob5, ob6, ob7):
    try:
        resultado_obj = Resultado.objects.create(
            tiempo_m=ob1,
            tiempo_s=ob2,
            respuesta=ob3,
            observacion=ob4,
            contenido_individual=ob5,
            paciente=ob6,
            fecha_registro_resultado=ob7
        )
        resultado_obj.save()
        return True
    except Exception as e:
        return False




# Método para guardar el registro de sala en el sistema controlado la existencia 
## de un curso, el estudiante en un curso registrado por el usuario común, la existencia 
## del identificador de actividad otorgado 
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_sala_register(request):
    if request.user.is_authenticated:
        try:
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
        except Exception as e:
            return JsonResponse({'error': 'El usuario no está autenticado'})

        # Verifica si el usuario es técnico.
        if not is_comun(user):
            return JsonResponse({'error': 'El usuario no está autenticado'})

        # Encontrar al usuario relacionado al user
        try:
            usuario__ob = UsuarioComun.objects.get(user=user)
        except UsuarioComun.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'})

        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'})

        data = json.loads(request.body)
        nombre_sala_ = data.get('nombre_sala')
        anotaciones_ = data.get('anotaciones')
        codigo_identificador_ = data.get('codigo_identificador')
        nombre_paciente_ = data.get('nombre_paciente')
        nombres_divididos = nombre_paciente_.split(' ')
        # Toma las dos primeras posiciones para nombre y las dos siguientes para apellido
        nombre = nombres_divididos[0] + ' ' + nombres_divididos[1]
        apellido = nombres_divididos[2] + ' ' + nombres_divididos[3]

        if not curso_existe(usuario__ob):
            return JsonResponse({'error': "No tiene un curso registrado. No puede registrar salas."})

        if not paciente_existe(nombre, apellido):
            return JsonResponse({'error': 'El paciente no existe.'})

        paciente__ob = Paciente.objects.get(nombre_usuario__iexact=nombre, apellido_usuario__iexact=apellido)

        if not paciente_existe_curso(paciente__ob, usuario__ob):
            return JsonResponse({'error': "El paciente no se encuentra inscrito en un curso o no existe."})

        # Verificar si existen multiples codigos identificadores separados por coma o un solo codigo
        if comprobar_separacion_coma(codigo_identificador_):
            identificadores_separados = codigo_identificador_.split(', ')
            # Cada identificador debe convertirse en dato entero
            for identificador in identificadores_separados:
                # Convertir identificador en entero
                identificador = int(identificador)
                if not identificador_existe(identificador):
                    return JsonResponse({'error': "El contenido que requiere evaluar no existe. Ingresa un identificador válido."})
        else:
            codigo_ = int(codigo_identificador_)
            if not identificador_existe(codigo_):
                return JsonResponse({'error': "El contenido que requiere evaluar no existe. Ingresa un identificador válido."})        
            
        if nombresala_exist(nombre_sala_):
            return JsonResponse({'error': "El nombre de la sala ya existe. Ingresa otro nombre."})
        
        try: 
            if guardar_sala(nombre_sala_, anotaciones_, codigo_identificador_, usuario__ob, paciente__ob):
                # Actualizamos el contador
                contador_obj, created = ContadorSalas.objects.get_or_create(paciente=paciente__ob)
                contador_obj.contador += 1
                contador_obj.save()
                # Enviamos una respuesta al front
                return JsonResponse({'success': True})
            else:
                print("Estoy aqui en el error")
                error_message = "Error al agregar sala."
                context = {'error': error_message}
                return JsonResponse(context)
        except Exception as e:
            print(e)
            return JsonResponse({'error': "Algo salió mal"})
    else:
        return JsonResponse({'error': 'El usuario no está autenticado'})

# Método para guardar el registro de sala en el sistema. La sala es creada por un usuario común
# es asociada a un estudiante específico, por tanto solo el puede acceder a sus salas
def guardar_sala (ob1, ob2, ob3, ob4, ob5):
    try:
        print("Entre al guardar")
        # Capturamos la fecha actual de registro
        fecha_registro_sala_ = datetime.now().date()
        print("Obtuve fecha")
        print(fecha_registro_sala_)
        # Guardamos el objeto de sala
        sala_obj = Sala.objects.create(
            nombre_sala=ob1,
            anotaciones=ob2,
            codigo_identificador=ob3,
            paciente=ob5,
            fecha_registro_sala=fecha_registro_sala_
        )
        print("Pase el guadar datos")
        sala_obj.save()
        # Creamos el detalle de sala
        detalle_obj = DetalleSala.objects.create(
            sala = sala_obj,
            usuario_comun=ob4
        )
        detalle_obj.save()
        return True
    except Exception as e:
        return False

# Verificar la existencia del nombre de un registro de sala
def paciente_existe_curso(paciente_ob, usuario_ob):
    try:
        # validamos la existencia
        if DetalleInscripcionCurso.objects.filter(paciente=paciente_ob, curso__usuario_comun=usuario_ob).exists():
            return True
    except DetalleInscripcionCurso.DoesNotExist:
        return False
    return False
    
# Verificar la existencia de un registro de curso dentro del sistema para dar paso a la creación de salas
def curso_existe(usuario_ob):
    try:
        cursos = Curso.objects.filter(usuario_comun=usuario_ob)
        if not cursos.exists():
            return False
        for curso in cursos:
            inscripciones = DetalleInscripcionCurso.objects.filter(curso=curso, curso__usuario_comun=usuario_ob).exists()
            if inscripciones:
                return True
        return False
    except Exception as e:
        return False
    
# Verificar la existencia de un estudiante registrado en un curso de aquellos que se encuentran inscritos
def paciente_existe(nombre, apellido):
    try:
        # buscamos al paciente mediante el nombre y apellido proporcionado
        if Paciente.objects.filter(nombre_usuario__iexact=nombre, apellido_usuario__iexact=apellido).exists():
            return True
    except Paciente.DoesNotExist:
        return False
    return False

# Verificar que el identificador de actividad proporcionado para la sala sea existente
def identificador_existe(ob1):
    try:
        # buscamos al paciente mediante el nombre y apellido proporcionado
        if ContenidoIndividual.objects.filter(identificador_individual__iexact=ob1).exists():
            return True
    except ContenidoIndividual.DoesNotExist:
        return False
    return False

# Verificar la existencia de una sala ya registrada
def nombresala_exist(ob1):
    try:
        if Sala.objects.filter(nombre_sala__iexact=ob1).exists():
            return True
    except Sala.DoesNotExist:
        return False
    return False



# Método para editar el registro de sala por medio del identificador de la misma. 
## Se verifica la existencia de un curso, la existencia del nombre de la sala 
## y la existencia del identificador de actividad otorgado
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_sala_edicion(request):
    if request.user.is_authenticated:
        try:
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
        except Exception as e:
            return JsonResponse({'error': 'El usuario no está autenticado'})

        # Verifica si el usuario es técnico.
        if not is_comun(user):
            return JsonResponse({'error': 'El usuario no está autenticado'})

        # Encontrar al usuario relacionado al user
        try:
            usuario__ob = UsuarioComun.objects.get(user=user)
        except UsuarioComun.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'})

        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'})

        data = json.loads(request.body)
        nombre_sala_ = data.get('nombre_sala')
        anotaciones_ = data.get('anotaciones')
        codigo_identificador_ = data.get('codigo_identificador')
        identificador_sala_ = data.get('identificador_sala')

        if not curso_existe(usuario__ob):
            return JsonResponse({'error': "No tiene un curso registrado. No puede registrar salas."})

        # Verificar si existen multiples codigos identificadores separados por coma o un solo codigo
        if comprobar_separacion_coma(codigo_identificador_):
            identificadores_separados = codigo_identificador_.split(', ')
            # Cada identificador debe convertirse en dato entero
            for identificador in identificadores_separados:
                # Convertir identificador en entero
                identificador = int(identificador)
                if not identificador_existe(identificador):
                    return JsonResponse({'error': "El contenido que requiere evaluar no existe. Ingresa un identificador válido."})
        else:
            codigo_ = int(codigo_identificador_)
            if not identificador_existe(codigo_):
                return JsonResponse({'error': "El contenido que requiere evaluar no existe. Ingresa un identificador válido."})        
            
        if nombresala_exist_edicion(nombre_sala_, identificador_sala_):
            return JsonResponse({'error': "El nombre de la sala ya existe. Ingresa otro nombre."})
        
        try: 
            if actualizar_sala(nombre_sala_, anotaciones_, codigo_identificador_, identificador_sala_):
                # Enviamos una respuesta al front
                return JsonResponse({'success': True})
            else:
                error_message = "Error al editar sala."
                context = {'error': error_message}
                return JsonResponse(context)
        except Exception as e:
            print(e)
            return JsonResponse({'error': "Algo salió mal"})
    else:
        return JsonResponse({'error': 'El usuario no está autenticado'})


# Método para realizar la actualización de un registro de sala en el sistema
def actualizar_sala(ob1, ob2, ob3, ob4):
    try:
        sala_obj = Sala.objects.get(id=ob4)
        sala_obj.nombre_sala = ob1
        sala_obj.anotaciones = ob2
        sala_obj.codigo_identificador = ob3
        sala_obj.save()
        return True
    except Exception as e:
        return False

# Verificar la existencia de un registro de sala
def nombresala_exist_edicion(ob1, ob2):
    try:
        # Buscamos el objeto sala
        sala__ob = Sala.objects.get(id=ob2)
        # Comparar si el nombre del registro es el mismo que viene en el request muestra falso
        if sala__ob.nombre_sala == ob1:
            return False
        # Buscamos si existe el nombre de la sala y que no sea el nombre del registro ya existente
        if Sala.objects.filter(nombre_sala__iexact=ob1).exists():
            return True
    except Sala.DoesNotExist:
        return False
    return False



## Generación del registro de reporte en el sistema controlado por medio de la existencia de un resultado
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generar_reporte_resultado(request, id):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Verificar existencia del usuario
            if user and token:
                if request.method == 'GET':
                    id_resultado_ = id
                    # Guardar Reporte
                    if guardar_reporte(id_resultado_, user):
                        return JsonResponse({'success': True})
                    else:
                        error_message = "Error al generar el reporte...."
                        context = {'error': error_message}
                        return JsonResponse(context)
                else:
                    return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
            else:
                return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Ups! algo salió mal'}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)

# Método para guardar el registro de reporte en el sistema. El reporte es asociado a los registro de resultados
# siempre y cuando estos deben tener registrada una observación
def guardar_reporte(ob1, ob2):
    try:
        #Obtenemos el objeto resultado
        resultado_ob = Resultado.objects.get(id=ob1)
        # Obtenemos datos necesarios para el reporte
        #paciente_ob = resultado_ob.paciente
        #contenido_individual_ob = resultado_ob.contenido_individual
        usuario_comun_ob = UsuarioComun.objects.get(user=ob2)
        # Capturamos la fecha del momento de registro
        fecha_registro_reporte_ = datetime.now().date()
        # Creamos el reporte
        reporte_ob = Reporte.objects.create(
            titulo_reporte = "Reporte de Resultado",
            descripcion_reporte = "No hay una descripción, debe ser agregada.",
            usuario_comun = usuario_comun_ob,
            #contenido_individual = contenido_individual_ob,
            #paciente = paciente_ob,
            resultado = resultado_ob,
            fecha_registro_reporte = fecha_registro_reporte_
        )
        reporte_ob.save()
        # Modifiamos el estado de reporte del resultado
        resultado_ob.estado_reporte = True
        resultado_ob.save()
        return True
    except Exception as e:
        return False
    


# Generación del registro de reportes por medio del nombre de un estudiante
## Se verifica la existencia de un curso, la existencia del nombre del estudiante, del estado 
## de los resultados con respecto a la existencia de un registro de reporte asociado
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generar_reporte_all(request):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Verificar existencia del usuario
            if user and token:
                # Verificar que sea usuario comun
                if (is_comun(user)):
                    if request.method == 'POST':
                        # Obtener el valor del nombre del paciente
                        data = json.loads(request.body)
                        nombre_paciente_ = data.get('nombre')
                        cedula_ = data.get('cedula')
                        # Verificar si es por nombre o cedula
                        if nombre_paciente_:
                            # Obtener el nombre y apellido del paciente de nombre_paciente
                            nombres_apellido = nombre_paciente_.split(' ')
                            # Verificar cuantos valores existen separados por un espacio
                            # Mayor o igual a 1
                            if len(nombres_apellido) <= 3:
                                error_message = "El nombre del paciente no es válido."
                                print("Mequede aqui")
                                context = {'error': error_message}
                                return JsonResponse(context)
                            elif len(nombres_apellido) == 4:
                                nombre = nombres_apellido[0] + " " + nombres_apellido[1]
                                apellido = nombres_apellido[2] + " " + nombres_apellido[3]
                            else:
                                error_message = "El nombre del paciente no es válido."
                                print("Mequede aqui x2")
                                context = {'error': error_message}
                                return JsonResponse(context)
                            # Validar entradas validas
                            if not validar_nombres(nombre, apellido):
                                error_message = "El nombre del paciente no es válido."
                                context = {'error': error_message}
                                return JsonResponse(context)
                        else:
                            # Obtener el usuario paciente por medio de la cédula
                            if Paciente.objects.filter(dni=cedula_).exists():
                                ob_paciente = Paciente.objects.get(dni=cedula_)
                                # Obtenemos el nombre y apellido
                                nombre = ob_paciente.nombre_usuario
                                apellido = ob_paciente.apellido_usuario
                            else:
                                error_message = "El paciente no existe con esa cédula. No se puede generar reportes."
                                context = {'error': error_message}
                                return JsonResponse(context)
                        # Ejecutamos
                        if not verificar_paciente_curso(nombre, apellido, user):
                            error_message = "El estudiante no se encuentra inscrito en un curso o no existe."
                            context = {'error': error_message}
                            return JsonResponse(context)
        
                        if not verificar_resultado_estado(nombre, apellido):
                            error_message = "El estudiante no tiene resultados con observación registrada. Verifica."
                            context = {'resultado': error_message}
                            return JsonResponse(context)
                        # Guardar Reporte
                        if Reporte_general_Nombre(nombre, apellido, user):
                            return JsonResponse({'success': True})
                        else:
                            error_message = "No es posibles generar el reporte...."
                            context = {'error': error_message}
                            return JsonResponse(context)
                    
                    else:
                        return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
                else:
                    return JsonResponse({'error': 'El usuario no ha autenticado'})
            else:
                return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Ups! algo salió mal'}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)

# Verificación de existencia de un estudiante en un curso. Permite dar paso a la generación del 
# registro de los reportes generales
def verificar_paciente_curso(ob1, ob2, ob3):
    try:
        # Obtenemos el paciente
        paciente_ = Paciente.objects.get(nombre_usuario__iexact=ob1, apellido_usuario__iexact=ob2)
        # Obtenemos el usuario comun asociado
        usuario_comun_ = UsuarioComun.objects.get(user=ob3)
        # Obtener los cursos registrados por el usuario
        cursos = Curso.objects.filter(usuario_comun=usuario_comun_)
        # Obtener los paciente inscritos en los cursos creados por el usuario comun
        for curso in cursos:
            if DetalleInscripcionCurso.objects.filter(curso=curso, paciente=paciente_).exists():
                return True
        return False
    except Paciente.DoesNotExist:
        return False
    except UsuarioComun.DoesNotExist:
        return False
    except Curso.DoesNotExist:
        return False
    except DetalleInscripcionCurso.DoesNotExist:
        return False

# Verifica elestado de los resultados para evitar leer resultados cuyos reportes ya existan o en su defecto
# no tengan cargado una observación
def verificar_resultado_estado(ob1, ob2):
    try:
        # Obtenemos el paciente
        paciente_ = Paciente.objects.get(nombre_usuario__iexact=ob1, apellido_usuario__iexact=ob2)
        # Obtenemos los resultados del paciente filtrando la observacion en no nulo o la obseravion diga No resuelto
        resultados = Resultado.objects.filter(paciente=paciente_, observacion__isnull=False, estado_reporte=False).exclude(observacion__iexact="No resuelto")
        # Si al menos hay un registro de resultado lanzamos true
        if resultados.exists():
            return True
        return False
    except Paciente.DoesNotExist:
        return False
    except Resultado.DoesNotExist:
        return False

# Generar reportes de los resultados por nombre del estudiante
def Reporte_general_Nombre(ob1, ob2, ob3):               
    # Obtener el paciente
    paciente_ob = Paciente.objects.get(nombre_usuario__iexact=ob1, apellido_usuario__iexact=ob2)                    
    # Obtener los resultados del paciente filtrando la observacion en no nulo o la obseravion diga No resuelto
    resultados = Resultado.objects.filter(paciente=paciente_ob, observacion__isnull=False, estado_reporte=False).exclude(observacion__iexact="No resuelto")
    # Se crea el reporte por cada resultado
    for resultado in resultados:
        guardar_reporte(resultado.id, ob3)
    return True



# Método para recuperar el contenido de un registro de actividad. Se obtiene la información
## relacionada por medio del slug del resultado que actua como identificador de la actividad
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def contenido_individual(request, slug):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if (user and token):
                # Obtenemos los objetos de Contenido
                contenidoI__ob = ContenidoIndividual.objects.get(
                    slug_contenido_individual=slug)
                contenido__ob = contenidoI__ob.contenido
                # obtenemos la url de contenido
                if contenidoI__ob.contenido_individual:
                    # Variable contenedor
                    contenedor = ""
                    url__contenido = cloudinary.CloudinaryImage(
                        contenidoI__ob.contenido_individual.name).build_url()
                    # Obtener los valores requeridos
                    nombre__contenido = contenido__ob.nombre
                    descripcion__contenido = contenidoI__ob.descripcion_individual
                    identificador = contenidoI__ob.identificador_individual
                    valor_respuesta = contenidoI__ob.respuesta
                    # Obtener el tipo de contenido
                    tipo__contenido = contenido__ob.dominio_tipo
                    # Comprobar si existe una sola descripcion o varias
                    if comprobar_separacion_coma(descripcion__contenido):
                        descripcion_separada = descripcion__contenido.split(', ')
                        descripcion__contenido = descripcion_separada
                    else:
                        descripcion__contenido = descripcion__contenido
                    # Comprobar si existe una sola respuesta o varias
                    if comprobar_separacion_coma(valor_respuesta):
                        valores_separados = valor_respuesta.split(', ')
                        valores_separados = [valor.capitalize()
                                            for valor in valores_separados]
                        contenedor = valores_separados
                        context = {'url__contenido': url__contenido, 'contenedor': contenedor,
                                'nombre__contenido': nombre__contenido, 'descripcion__contenido': descripcion__contenido, 'identificador': identificador,
                                'tipo__contenido': tipo__contenido, 'slug': slug}
                    else:
                        contenedor = valor_respuesta
                        context = {'url__contenido': url__contenido, 'contenedor': contenedor,
                                'nombre__contenido': nombre__contenido, 'descripcion__contenido': descripcion__contenido, 'identificador': identificador,
                                'tipo__contenido': tipo__contenido, 'slug': slug}

                    # Determinar el tipo de contenido y renderizar la plantilla adeacuada al tipo
                    if (contenidoI__ob.tipo_contenido == 'selecion_individual'):
                        context.update({'tipo': 'selecion_individual'})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'verdadero_falso'):
                        context.update({'tipo': 'verdadero_falso'})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'selecion_multiple'):
                        context.update({'tipo': 'selecion_multiple'})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'seleccionar_imagen'):
                        url_c1 = cloudinary.CloudinaryImage(contenidoI__ob.imagen1.name).build_url()
                        url_c2 = cloudinary.CloudinaryImage(contenidoI__ob.imagen2.name).build_url()
                        url_c3 = cloudinary.CloudinaryImage(contenidoI__ob.imagen3.name).build_url()
                        url_c4 = cloudinary.CloudinaryImage(contenidoI__ob.imagen4.name).build_url()
                        url_c5 = cloudinary.CloudinaryImage(contenidoI__ob.imagen5.name).build_url()
                        context.update({'tipo': 'seleccionar_imagen', 'url_c1': url_c1, 
                                        'url_c2': url_c2, 'url_c3': url_c3, 'url_c4': url_c4, 'url_c5': url_c5})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'responder_preguntas'):
                        context.update({'tipo': 'responder_preguntas'})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'pintar_imagen'):
                        url_c1 = cloudinary.CloudinaryImage(contenidoI__ob.imagen1.name).build_url()
                        context.update({'tipo': 'pintar_imagen', 'url_c1': url_c1})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'cuento'):
                        context.update({'tipo': 'cuento'})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'selecion_multiple_img'):
                        url_c1 = cloudinary.CloudinaryImage(contenidoI__ob.imagen1.name).build_url()
                        url_c2 = cloudinary.CloudinaryImage(contenidoI__ob.imagen2.name).build_url()
                        url_c3 = cloudinary.CloudinaryImage(contenidoI__ob.imagen3.name).build_url()
                        context.update({'tipo': 'selecion_multiple_img', 'url_c1': url_c1, 'url_c2': url_c2, 'url_c3': url_c3})
                        return JsonResponse(context)
                    elif (contenidoI__ob.tipo_contenido == 'pictograma'):
                        url_c1 = cloudinary.CloudinaryImage(contenidoI__ob.imagen1.name).build_url()
                        url_c2 = cloudinary.CloudinaryImage(contenidoI__ob.imagen2.name).build_url()
                        url_c3 = cloudinary.CloudinaryImage(contenidoI__ob.imagen3.name).build_url()
                        context.update({'tipo': 'pictograma', 'url_c1': url_c1, 'url_c2': url_c2, 'url_c3': url_c3})
                        return JsonResponse(context)

                else:
                    error_message = "No existe contenido"
                    context = {
                        'errorNormal': error_message, 'slug': slug
                    }
                    return JsonResponse(context, status=404)
            else:
                return JsonResponse({'errorSalida': 'El usuario no esta autenticado'}, status=401)
        except ContenidoIndividual.DoesNotExist:
            error = "No existe contenido"
            contexto_dos = {'errorNormal': error, 'slug': slug}
            return JsonResponse(contexto_dos, status=404)

        except Exception as e:
            return JsonResponse({'errorSalida':'Ups, Algo salió mal'}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)




# Método para obtener la información relacionada a un registro de contenido a través del slug.
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def contenido_principal(request, slug):
    # Decodifica el token
    token = request.headers.get('Authorization').split(" ")[1]
    user = get_user_from_token_jwt(token)
    #user = get_user_from_token(token)
    if user and token:
        if request.method == 'GET':
            # Obtenemos el objeto dominio
            dominio__ob = Dominio.objects.get(slug_dominio=slug)
            context = {'identificador': dominio__ob.id, 'slug': slug}
            return JsonResponse(context)
        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405)
    else:
        return JsonResponse({'error': 'Token no proporcionado'}, status=401)




# Método para obtener la información relacionada a un registro de actividad a través del código.
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_contenido_individual(request, codigo):
    try:
        # Decodifica el token
        token = request.headers.get('Authorization').split(" ")[1]
        user = get_user_from_token_jwt(token)
        #user = get_user_from_token(token)
        if is_paciente(user):
            if request.method == 'GET':
                codigo_ = codigo
                slug = obtener_slug_CI(codigo_)
                if slug:
                    return JsonResponse({'success': True, 'slug': slug})
                else:
                    error_message = "El contenido no existe."
                    context = {'error': error_message}
                    return JsonResponse(context)
            else:
                return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
        else:
            return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)
    except Exception as e:
        return JsonResponse({'error': 'Ups! algo salió mal'}, status=500)

# Método para obtener el slug de un contenido individual
def obtener_slug_CI(codigo):
    try:
        # Obtenemos el objeto contenido individual
        contenidoI__ob = ContenidoIndividual.objects.get(identificador_individual=codigo)
        # Obtenemos el slug
        slug = contenidoI__ob.slug_contenido_individual
        return slug
    except ContenidoIndividual.DoesNotExist:
        return False






