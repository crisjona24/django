import random
from django.db import IntegrityError
from .models import *
from .serializer import *
from django.contrib.auth.hashers import make_password
#from rest_framework import viewsets, generics
from django.contrib.auth import authenticate, login, logout
import re
from django.http import JsonResponse
#from django.urls import reverse
from datetime import datetime, timedelta
import jwt
import secrets
import string
from django.contrib.auth.models import User
import pytz

# from django.views.decorators.csrf import csrf_exempt
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
# from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken, Token, UntypedToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from django.core.mail import send_mail

# Token de verificacion de cuenta
from django.core.signing import Signer, BadSignature


##### METODOS PARA DECODIFICAR TOKEN #####


## Métodos para decodificar el token obtenido de las peticiones get y post desde el frontend
## permitiendo validar las mismas y controlar el logueo de los usuarios
def get_user_from_token(key):
    try:
        token = Token.objects.get(key=key)
        return token.user
    except Token.DoesNotExist:
        return None

def get_user_from_token_jwt(key):
    try:
        # Validar el token y obtener el payload
        UntypedToken(key)
        
        # Obtener el user de JWTAuthentication
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(key)
        user = jwt_auth.get_user(validated_token)
        return user
    except TokenError:
        raise InvalidToken("Error al decodificar el token.")



###### METODOS PARA VALIDACIONES DE ROL DE USUARIO #####


## Método para identificar si un correo ingresado durante el registro, envio de correo de
## recuperación cumple con el formato de correo electrónico
def es_correo_valido(correo):
    er = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    if re.match(er, correo) is not None:
        return True
    else:
        return False

## Método para validar el cumplimiento de un formato de clave que cumpla con las necesidades
## minimas de seguridad
def validar_clave(ob1):
    """
    Controlar si la contraseña cumple con las especificaciones de seguridad mínimas.
    - Al menos 8 caracteres.
    - Al menos una letra mayúscula.
    - Al menos una letra minúscula.
    - Al menos un número.
    - Al menos un símbolo.
    """
    if len(ob1) < 8:
        return False
    if not re.search(r"[A-Z]", ob1):
        return False
    if not re.search(r"[a-z]", ob1):
        return False
    if not re.search(r"[0-9]", ob1):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", ob1):
        return False
    return True


## Método para confirmar que el correo electrónico es único y pertenezca a un solo usuario
def correo_unico(ob1):
    """Verifica si el correo es único."""
    try:
        # Filtramos existencia de correo en el modleo User
        if User.objects.filter(email=ob1).exists():
            return False
        return True
    except User.objects.DoesNotExist:
        return False


## Validar cédula única
def cedula_unica(ob1):
    """Verifica si la cédula es única."""
    try:
        # Buscamos la cedula en los modelos Usuario. Usuario comun y paciente
        if Usuario.objects.filter(dni=ob1).exists():
            return False
        elif UsuarioComun.objects.filter(dni=ob1).exists():
            return False
        elif Paciente.objects.filter(dni=ob1).exists():
            return False
        return True
    except Usuario.DoesNotExist:
        return False
    except Paciente.DoesNotExist:
        return False
    except UsuarioComun.DoesNotExist:
        return False


## Método para validar que la cédula registrada sea válida
def verificar_cedula_ecuatoriana(cedula):
    """ 
    Algoritmo de Verificación:
    1: Se agrupan los nueve primeros dígitos en dos conjuntos: los que están en posiciones impares y 
    los que están en pares. Por ejemplo, para la cédula de identidad 1713175071, las posiciones 
    impares serían 1, 1, 1, 5 y 7, mientras que las posiciones pares serían 7, 3, 7 y 0.
    2: A las posiciones impares se multiplican por dos (2). Si el resultado de esta multiplicación 
    es mayor a nueve, se le resta nueve. Por ejemplo, si los números en posiciones impares son 1, 1, 
    1, 5 y 7, la multiplicación por dos de cada número sería 2, 2, 2, 10 y 14. Ya que algunos resultados 
    son mayores a nueve, se procede a restar nueve a esos valores, quedando así: 2, 2, 2, 1 y 5.
    3: Se suman los dígitos en posiciones pares, más los resultados de las operaciones en las posiciones 
    impares. Por ejemplo, si los dígitos pares son 7, 3, 7 y 0, la suma de dígitos en posiciones pares 
    sería 17. Por otro lado, si el resultado de las operaciones en las posiciones impares es 2, 2, 2, 1 y 5, 
    su suma sería 12. El total de la suma sería 17 + 12 = 29
    4: Se obtiene el módulo 10 de la suma total anterior, es decir, se toma el dígito más a la derecha del 
    resultado de la suma. Por ejemplo, si suma 29, el módulo 10 sería 9.
    5: Si el resultado anterior es cero entonces el dígito verificador es cero, caso contrario al número 
    10 se le resta el resultado obtenido en el anterior paso. Por ejemplo, si el resultado del paso anterior 
    es 9, la resta sería 10 menos 9 = 1, siendo 1 el dígito verificador calculado.

    Tomado de: https://www.jybaro.com/blog/cedula-de-identidad-ecuatoriana/
    """
    # Verificar si la cédula tiene 10 dígitos
    if len(cedula) != 10:
        return False
    # Obtener los nueve primeros dígitos
    digitos = list(map(int, cedula[:9]))
    # Calcular el décimo dígito
    suma_impares = 0
    for i in range(0, 9, 2):
        resultado = digitos[i] * 2
        if resultado > 9:
            resultado -= 9
        suma_impares += resultado
    suma_pares = sum(digitos[1::2])
    suma_total = suma_impares + suma_pares
    decimo_digito = suma_total % 10

    # Calcular el dígito verificador
    if decimo_digito == 0:
        digito_verificador = 0
    else:
        digito_verificador = 10 - decimo_digito
    # Comparar el dígito verificador con el décimo dígito de la cédula
    return digito_verificador == int(cedula[9])


## Validar entradas de nombres para evitar expresiones regulares que desencadenen ataques de sql injection
def validar_nombres(ob1, ob2):
    # Expresión regular para verificar que ambos nombres cumplan con el formato deseado
    formato_valido = re.compile(r'^[A-Za-zÁáÉéÍíÓóÚúÑñ]+\s[A-Za-zÁáÉéÍíÓóÚúÑñ]+$')

    if formato_valido.match(ob1) and formato_valido.match(ob2):
        return True
    else:
        return False


## Validacion del formato del correo en el registro
def validar_formato_email(ob1):
    # Expresión regular para verificar que el correo cumpla con el formato deseado
    # para correos de gmail y del dominio de la UNL
    formato_valido = re.compile(r'^[a-zA-Z0-9._%+-]+@(gmail\.com|unl\.edu\.ec)$')
    if formato_valido.match(ob1):
        return True
    else:
        return False


###### METODOS PARA VALIDACIONES DE ROL DE USUARIO #####


# Método para identificar que un usuario es tecnico
def is_tecnico(user):
    """Verifica si el usuario es un técnico."""
    try:
        usuario__ob = Usuario.objects.get(user=user)
        if usuario__ob.is_tecnico:
            return True
        else:
            return False
    except Usuario.DoesNotExist:
        return False

# Método para identificar que un usuario es usuario comun
def is_comun(user):
    """Verifica si el usuario es un usuario comun."""
    try:
        usuario__ob = UsuarioComun.objects.get(user=user)
        if usuario__ob.is_comun:
            return True
        else:
            return False
    except UsuarioComun.DoesNotExist:
        return False

# Método para identificar que un usuario es paciente
def is_paciente(user):
    """Verifica si el usuario es un paciente."""
    try:
        usuario__ob = Paciente.objects.get(user=user)
        if usuario__ob.is_paciente:
            return True
        else:
            return False
    except Paciente.DoesNotExist:
        return False  
    

###### METODOS PARA INICIO Y CIERRE DE SESION #####


# Métdo de control de inicio de sesión de usuario
@api_view(['POST'])
def api_login(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)
            # Autenticar usuario
            if user is not None:
                if user.is_authenticated:
                    login(request, user)
                    refresh=RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    # Verificamos el tipo de usuario
                    if is_paciente(user):
                        user_ob = Paciente.objects.get(user=user)
                        if user_ob.is_activo:
                            context = {
                                'success': True,
                                'tipo': 'paciente',
                                'token': access_token,
                            }
                            return JsonResponse(context)
                        else:
                            context = {
                                'error': 'El usuario no esta activo',
                            }
                            return JsonResponse(context, status=401)
                    elif is_tecnico(user):
                        user_ob = Usuario.objects.get(user=user)
                        if user_ob.is_activo:
                            context = {
                                'success': True,
                                'tipo': 'tecnico',
                                'token': access_token,
                            }
                            return JsonResponse(context)
                        else:
                            context = {
                                'error': 'El usuario no esta activo',
                            }
                            return JsonResponse(context, status=401)
                    elif is_comun(user):
                        user_ob = UsuarioComun.objects.get(user=user)
                        if user_ob.is_activo:
                            context = {
                                'success': True,
                                'tipo': 'comun',
                                'token': access_token,
                            }
                            return JsonResponse(context)
                        else:
                            context = {
                                'error': 'El usuario no esta activo',
                            }
                            return JsonResponse(context, status=401)
                else:
                    context = {
                        'error': 'Usuario o contraseña incorrectos',
                    }
                    return JsonResponse(context)
            else:
                context = {
                    'error': 'Usuario o contraseña incorrectos',
                }
                return JsonResponse(context, status=401)
        else:
            return JsonResponse({'error': 'Ups! Algo salió mal'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Método de control de cierre de sesión de usuario
@api_view(['POST'])
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})


###### METODOS DE VERIFICACION DE ROL DE USUARIO #####

## Verificar que un usuario se encuentre logueado en la aplicación y con ello conocer el rol
## que desempeña
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificar_usuario(request):
    if request.user.is_authenticated:
        # Decodifica el token para obtener el usuario
        token = request.headers.get('Authorization').split(" ")[1]
        user = get_user_from_token_jwt(token)
        try:
            # Encontrar al usuario relacionado al user
            usuario__ob = Usuario.objects.get(user=user)
            # Verificar si el usuario existe
            if user and usuario__ob:
                # Verificar el tipo de usuario
                if usuario__ob.is_tecnico:
                    context = {
                        'success': True,
                        'tipo': 'tecnico',
                        'identificador': usuario__ob.id,
                    }
                    return JsonResponse(context)
            else:
                return JsonResponse({'error': 'El usuario no existe'}, status=401)
        except Usuario.DoesNotExist:
            try:
                # Encontrar al usuario relacionado al user
                paciente__ob = Paciente.objects.get(user=user)
                # Verificar si el usuario existe
                if user and paciente__ob:
                    # Verificar el tipo de usuario
                    if paciente__ob.is_paciente:
                        context = {
                            'success': True,
                            'tipo': 'paciente',
                            'identificador': paciente__ob.id,
                        }
                        return JsonResponse(context)
                else:
                    return JsonResponse({'error': 'El usuario no existe'}, status=401)
            except Paciente.DoesNotExist:
                try:
                    # Encontrar al usuario relacionado al user
                    comun__ob = UsuarioComun.objects.get(user=user)
                    # Verificar si el usuario existe
                    if user and comun__ob:
                        # Verificar el tipo de usuario
                        if comun__ob.is_comun:
                            context = {
                                'success': True,
                                'tipo': 'comun',
                                'identificador': comun__ob.id,
                            }
                            return JsonResponse(context)
                    else:
                        return JsonResponse({'error': 'El usuario no existe'}, status=401)
                except UsuarioComun.DoesNotExist:
                    return JsonResponse({'error': 'El usuario no existe'}, status=401)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        

## Obtención de los datos de usuario
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def datos_usuario(request):
    if request.user.is_authenticated:
        # Decodifica el token para obtener el usuario
        token = request.headers.get('Authorization').split(" ")[1]
        user = get_user_from_token_jwt(token)
        #user = get_user_from_token(token)
        try:
            # Encontrar al usuario relacionado al user
            usuario__ob = Usuario.objects.get(user=user)
            # Verificar si el usuario existe
            if user and usuario__ob:
                # Verificar el tipo de usuario
                if usuario__ob.is_tecnico:
                    context = {
                        'success': True,
                        'tipo': 'tecnico',
                        'nombre': usuario__ob.nombre_usuario,
                        'apellido': usuario__ob.apellido_usuario,
                        'email': usuario__ob.email_usuario,
                        'username': usuario__ob.username_usuario,
                        'edad': usuario__ob.edad,
                        'fecha_nacimiento': usuario__ob.fecha_nacimiento,
                        'celular': usuario__ob.celular,
                        'fecha_union': usuario__ob.fecha_registro_usuario,
                        'identificador': user.id,
                    }
                    return JsonResponse(context)
            else:
                return JsonResponse({'success': False})
        except Usuario.DoesNotExist:
            try:
                # Encontrar al usuario relacionado al user
                paciente__ob = Paciente.objects.get(user=user)
                # Verificar si el usuario existe
                if user and paciente__ob:
                    # Verificar el tipo de usuario
                    if paciente__ob.is_paciente:
                        context = {
                            'success': True,
                            'tipo': 'paciente',
                            'nombre': paciente__ob.nombre_usuario,
                            'apellido': paciente__ob.apellido_usuario,
                            'email': paciente__ob.email_usuario,
                            'celular': paciente__ob.celular,
                            'contacto_emergencia': paciente__ob.contacto_emergencia,
                            'fecha_nacimiento': paciente__ob.fecha_nacimiento,
                            'edad': paciente__ob.edad,
                            'fecha_union': paciente__ob.fecha_registro_usuario,
                            'identificador': user.id,
                        }
                        return JsonResponse(context)
                else:
                    return JsonResponse({'success': False})
            except Paciente.DoesNotExist:
                try:
                    # Encontrar al usuario relacionado al user
                    comun__ob = UsuarioComun.objects.get(user=user)
                    # Verificar si el usuario existe
                    if user and comun__ob:
                        # Verificar el tipo de usuario
                        if comun__ob.is_comun:
                            context = {
                                'success': True,
                                'tipo': 'comun',
                                'nombre': comun__ob.nombre_usuario,
                                'apellido': comun__ob.apellido_usuario,
                                'email': comun__ob.email_usuario,
                                'celular': comun__ob.celular,
                                'fecha_nacimiento': comun__ob.fecha_nacimiento,
                                'genero': comun__ob.genero,
                                'area_estudio': comun__ob.area_estudio,
                                'edad': comun__ob.edad,
                                'fecha_union': comun__ob.fecha_registro_usuario,
                                'identificador': user.id,
                            }
                            return JsonResponse(context)
                    else:
                        return JsonResponse({'success': False})
                except UsuarioComun.DoesNotExist:
                    return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': False})



###### METODOS DE REGISTRO DE USUARIO, RECUPERACION/CAMBIO DE CLAVE #####


## Método para verificar si un registro existe o no dentro de la base de datos
def existe__registro(ob1, ob2):
    try:
        if Paciente.objects.filter(nombre_usuario__iexact=ob1, apellido_usuario__iexact=ob2).exists():
            return True
        elif UsuarioComun.objects.filter(nombre_usuario__iexact=ob1, apellido_usuario__iexact=ob2).exists():
            return True
        elif Usuario.objects.filter(nombre_usuario__iexact=ob1, apellido_usuario__iexact=ob2).exists():
            return True
    except Paciente.DoesNotExist:
        return False
    except UsuarioComun.DoesNotExist:
        return False
    except Usuario.DoesNotExist:
        return False
    return False

## Método para verificar si un registro de un username especifico existe o no dentro de la base de datos
def username_exist(ob1):
    try:
        if Paciente.objects.filter(username_usuario__iexact=ob1).exists():
            return True
        elif UsuarioComun.objects.filter(username_usuario__iexact=ob1).exists():
            return True
        elif Usuario.objects.filter(username_usuario__iexact=ob1).exists():
            return True
    except Paciente.DoesNotExist:
        return False
    except UsuarioComun.DoesNotExist:
        return False
    except Usuario.DoesNotExist:
        return False
    return False

## Envio de correo para verifiacion de cuenta
def validar_correo_link(_email):
    try:
        signer = Signer()
        token_firmado = signer.sign(_email)
        # Email
        subject = 'Confirmación de cuenta'
        #message = f'Haz clic en el siguiente enlace para verificar tu cuenta: {settings.SITE_URL}/verificar/{token_firmado}'
        message = f'Reciba un cordial saludo de los administradores de WAPIPTDAH. ' \
            f'\nRecibimos una solicitud de activación de cuenta para el correo: {_email}. ' \
            f'\nEste es un mensaje para activar su cuenta por lo tanto debe seguir las instrucciones: ' \
            f'\n\n1. Copia y pega el siguiente código especial para activar tu cuenta: ' \
            f'\n{token_firmado}'\
            f'\n\n2. Ingresa los datos solicitados en la ventana que aparecerá. ' \
            f'\n' \
            f'\nSi usted no hizo esta solicitud, ignore completamente este mensaje. ' \
            f'\n' \
            f'\nAtentamente: WAPIPTDAH.'
        from_email = settings.EMAIL_HOST_USER
        receiver_email = [_email]
        send_mail(subject, message, from_email, receiver_email, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando el correo: {e}")
        return False

## Generador de token 
def generar_token_unico(longitud=50):
    # Define los caracteres que se implementarán en la generación de token
    caracteres = string.ascii_letters + string.digits
    # Genera un token único aleatorio en base a las especificaciones
    token = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return token

## Metodo de generacion de token con tiempo de expiracion
## El tiempo y el token son controlados por medio de una entidad de 
## recuperacion que avala la validez
def generar_token_tiempo(ob1, tiempo_Exp=60):
    # Calcula la fecha y hora de expiración para ser registrada en el objeto de Recuperación
    expiracion_tiempo = datetime.utcnow() + timedelta(minutes=tiempo_Exp)
    # Crea una instancia de la entidad Recuperacion
    recuperacion = Recuperacion(usuario=ob1, fecha_creacion=datetime.utcnow(), fecha_limite=expiracion_tiempo)
    recuperacion.save()
    # Crea un token único
    token = generar_token_unico()  
    # Asocia el token único con la instancia de RecuperacionContrasena
    recuperacion.token = token
    recuperacion.save()  # Actualiza el registro con el token
    # Crea los datos que se incluirán en el token y seran enviado por medio del correo
    datos = {
        'usuario_id': ob1.id,
        'token': token,
        'exp': expiracion_tiempo
    }
    # Genera el token firmado por medio del tipo de algoritmo HS256
    token = jwt.encode(datos, settings.SECRET_KEY, algorithm='HS256')
    # Devolvemos el token
    return token

def generar_token_verificacion(email_, tiempo_Exp=60):
    # Calcula la fecha y hora de expiración para ser registrada en el objeto de Recuperación
    expiracion_tiempo = datetime.utcnow() + timedelta(minutes=tiempo_Exp)
    # Crea una instancia de la entidad Recuperacion
    verificacion = Verificacion(fecha_creacion=datetime.utcnow(), fecha_limite=expiracion_tiempo, correo= email_)
    verificacion.save()
    # Crea un token único
    token = generar_token_unico()  
    # Asocia el token único con la instancia de Verificacion
    verificacion.token = token
    verificacion.save()  # Actualiza el registro con el token
    # Crea los datos que se incluirán en el token y seran enviado por medio del correo
    datos = {
        'token': token,
        'exp': expiracion_tiempo
    }
    # Genera el token firmado por medio del tipo de algoritmo HS256
    token = jwt.encode(datos, settings.NEW_SECRET_KEY, algorithm='HS256')
    # Devolvemos el token
    return token

## Metodo que permite la verificación de la validez del token enviado al usuario cuando
## requiere cambiar o en su defecto recuperar su cuenta. El token es validado por medio de 
## un tiempo de duracion equivalente a 1 hora
def verificar_token_tiempo(token):
    try:
        # Formateo de tipo de servidor para comparar fechas de limite y registro
        utc = pytz.timezone('UTC')
        # Decodifica el token y verifica la firma
        datos_obtenidos = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # Recupera el usuario y la instancia de Recuperacion
        usuario_id = datos_obtenidos['usuario_id']
        token = datos_obtenidos['token']
        usuario = User.objects.get(id=usuario_id)
        # Verificar si existe el objeto de Recuperacion
        if not entidad_R_existe(usuario, token):
            return None
        # Obtenemos los datos del objeto Recuperacion asociado
        ob_recuperacion = Recuperacion.objects.filter(usuario=usuario, token=token).first()
        fecha_obtenida = ob_recuperacion.fecha_limite
        # Parseamos
        fecha_obtenida = fecha_obtenida.replace(microsecond=0, tzinfo=utc)
        # Comprueba si el token ha expirado
        fecha_actual = datetime.utcnow()
        fecha_actual = datetime.utcnow().replace(tzinfo=utc, microsecond=0)
        # Comparamos
        if fecha_actual > fecha_obtenida:
            return None
        if ob_recuperacion.esta_vencido():
            return None
        
        # Devuelve el usuario y la instancia de Recuperacion
        if ob_recuperacion:
            return usuario, ob_recuperacion
        else:
            return None
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.DecodeError:
        # Token inválido
        return None

## Metodo que permite la verificación de la validez del token enviado al usuario cuando
## durante el proceso de verificacion de cuenta de usuario
def verificar_token_verificacion(token):
    try:
        # Formateo de tipo de servidor para comparar fechas de limite y registro
        utc = pytz.timezone('UTC')
        # Decodifica el token y verifica la firma
        datos_obtenidos = jwt.decode(token, settings.NEW_SECRET_KEY, algorithms=['HS256'])
        # Recupera la instancia Verificacion
        token = datos_obtenidos['token']
        # Verificar si existe el objeto de Verificacion
        if not entidad_V_existe(token):
            return None
        # Obtenemos los datos del objeto Recuperacion asociado
        ob_verificacion = Verificacion.objects.filter(token=token).first()
        fecha_obtenida = ob_verificacion.fecha_limite
        # Parseamos
        fecha_obtenida = fecha_obtenida.replace(microsecond=0, tzinfo=utc)
        # Comprueba si el token ha expirado
        fecha_actual = datetime.utcnow()
        fecha_actual = datetime.utcnow().replace(tzinfo=utc, microsecond=0)
        # Comparamos
        if fecha_actual > fecha_obtenida:
            return None
        if ob_verificacion.esta_vencido():
            return None
        
        # Devuelve el usuario y la instancia de Verificacion
        if ob_verificacion:
            return ob_verificacion
        else:
            return None
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.DecodeError:
        # Token inválido
        return None


## Método para verificar que el objeto de Recuperacion exista o no
## caso contrario se evitara cualquier acción
def entidad_R_existe(ob1, ob2):
    try:
        if Recuperacion.objects.filter(usuario=ob1, token=ob2).exists():
            return True
    except Recuperacion.DoesNotExist:
        return False


def entidad_V_existe(ob1):
    try:
        if Verificacion.objects.filter(token=ob1).exists():
            return True
    except Verificacion.DoesNotExist:
        return False

## Envio de correo de recuperacion de cuenta de usuario
## se envia un correo con un token firmado con un limite de tiempo
## Envio de correo para verifiacion de cuenta
def validar_correo_verificacion(_email):
    try:
        # Llamamos al metodo generador de token
        token_firmado = generar_token_verificacion(_email)
        # Email
        subject = 'Verificación de cuenta'
        message = f'Reciba un cordial saludo de los administradores de WAPIPTDAH. ' \
            f'\nRecibimos una solicitud de verificación de cuenta para el correo: {_email}. ' \
            f'\nEste es un mensaje para verificar su cuenta por lo tanto debe seguir las instrucciones: ' \
            f'\n\n1. Copia y pega el siguiente código especial para verificar tu cuenta: ' \
            f'\n{token_firmado}'\
            f'\n\n2. Ingresa los datos solicitados en la ventana que aparecerá. ' \
            f'\n' \
            f'\nSi usted no hizo esta solicitud, ignore completamente este mensaje. ' \
            f'\n' \
            f'\nAtentamente: WAPIPTDAH.'
        from_email = settings.EMAIL_HOST_USER
        receiver_email = [_email]
        # Envio del correo
        send_mail(subject, message, from_email, receiver_email, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando el correo: {e}")
        return False

def validar_correo_recuperacion_2(ob1, _email):
    try:
        # Llamamos al metodo generador de token
        token_firmado = generar_token_tiempo(ob1)
        # Email
        subject = 'Recuperación de cuenta'
        message = f'Reciba un cordial saludo de los administradores de WAPIPTDAH. ' \
            f'\nRecibimos una solicitud de recuperación de cuenta para el correo: {_email}. ' \
            f'\nEste es un mensaje para recuperar su cuenta por lo tanto debe seguir las instrucciones: ' \
            f'\n\n1. Copia y pega el siguiente código especial para recuperar tu cuenta: ' \
            f'\n{token_firmado}'\
            f'\n\n2. Ingresa los datos solicitados en la ventana que aparecerá. ' \
            f'\n' \
            f'\nSi usted no hizo esta solicitud, ignore completamente este mensaje. ' \
            f'\n' \
            f'\nAtentamente: WAPIPTDAH.'
        from_email = settings.EMAIL_HOST_USER
        receiver_email = [_email]
        # Envio del correo
        send_mail(subject, message, from_email, receiver_email, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando el correo: {e}")
        return False
    
## Verificacion de existencia de correo
def existe__correo(ob1):
    try:
        if Paciente.objects.filter(email_usuario__iexact=ob1).exists():
            return True
        elif UsuarioComun.objects.filter(email_usuario__iexact=ob1).exists():
            return True
        elif Usuario.objects.filter(email_usuario__iexact=ob1).exists():
            return True
    except Paciente.DoesNotExist:
        return False
    except UsuarioComun.DoesNotExist:
        return False
    except Usuario.DoesNotExist:
        return False
    return False



######  METODO DE RECUPERACION DE CUENTA DE USUARIO #######


@api_view(['POST'])
def recuperar_cuenta(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email_ = data.get('correo')
            if existe__correo(email_):
                # Obtenemos el user asociado al email
                user_ = User.objects.get(email=email_)
                # Veriicar correo valido
                if not validar_correo_recuperacion_2(user_, email_):
                    return JsonResponse({'error': 'No existe una cuenta con ese correo'})
                else:
                    return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'No existe una cuenta con ese correo'})
        else:
            return JsonResponse({'error': 'Método no permitido'})
    except Exception as e:
        return JsonResponse({'error': 'Error al crear el usuario'})
    

# METODO DE VERIFICACION DE CORREO


# Permite verificar el token para verificar la existencia de una cuenta de usuario
# y dar paso a la modificación de la clave
@api_view(['POST'])
def verificar_email_recuperacion(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            codigo_ = data.get('codigo')
            # Llamamos al desfirmado
            #signer = Signer()
            #email_original = signer.unsign(codigo_)
            # Obtener el usuario e instancia de Recuperacion
            usuario_ = verificar_token_tiempo(codigo_)
            if usuario_ is not None:
                # Obtener el usuario e instancia de Recuperacion
                usuario, recuperacion = usuario_
                # Modificamos el estado de atencion de Recuperacion
                recuperacion.atendido = True
                recuperacion.save()
                # Verificar el tipo de usuario
                if is_tecnico(usuario):
                    return JsonResponse({'success': True})
                elif is_paciente(usuario):
                    return JsonResponse({'success': True})
                elif is_comun(usuario):
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
            else:
                return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
        else: 
            return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
    except BadSignature:
       return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})



# METODO DE RESTABLECIMIENTO DE CLAVE



# Permite restablecer la nueva clave enviada por parte del usuario
# esto se realiza previo a una verificacion de correo mediante token
@api_view(['POST'])
def restablecer_clave(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email_ = data.get('correo')
            clave2_ = data.get('clave2')
            # Verificar correo
            if existe__correo(email_) == False:
                return JsonResponse({'error': 'No existe una cuenta con ese correo'})
            # Verificar clave
            if validar_clave(clave2_) == False:
                return JsonResponse({'clave': 'Clave sin requisitos mínimos'})
            # Guardamos la clave
            if guardar_clave_(email_, clave2_):
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Error al restablecer la clave'})
        else:
            return JsonResponse({'error': 'Método no permitido'})
    except Exception as e:
        return JsonResponse({'error': 'Error al restablecer la clave'})

def guardar_clave_(ob1, ob2):
    try:
        # Encontrar el usuario relacionado al correo
        user_ob = User.objects.get(email=ob1)
        # Cambiar la clave
        user_ob.password = make_password(ob2)
        # Guardar cambios
        user_ob.save()
        return True
    except User.DoesNotExist:
        return False


# METODO DE VERIFICACION DE CORREO
# Permite verificar el token para verificar la activación de una cuenta de usuario
# si el tokken no es adecuado al desfirmarlo esta no se lee ni se activa
@api_view(['POST'])
def verificar_email_firmado(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            token = data.get('tokenVerificacion')
            #signer = Signer()
            #email_original = signer.unsign(token)
            usuario__ = verificar_token_verificacion(token)
            if usuario__ is not None:
                # LLamamos la verificacion
                user_ob = verificacion_correo_V(usuario__)
                if not user_ob:
                    return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
                if is_tecnico(user_ob):
                    usuario__ob = Usuario.objects.get(user=user_ob)
                    if verificado_correo(usuario__ob):
                        return JsonResponse({'error': 'El usuario ya esta activo'})
                    usuario__ob.is_activo = True
                    usuario__ob.save()
                    return JsonResponse({'success': True})
                elif is_paciente(user_ob):
                    paciente__ob = Paciente.objects.get(user=user_ob)
                    if verificado_correo(paciente__ob):
                        return JsonResponse({'error': 'El usuario ya esta activo'})
                    paciente__ob.is_activo = True
                    paciente__ob.save()
                    return JsonResponse({'success': True})
                elif is_comun(user_ob):
                    comun__ob = UsuarioComun.objects.get(user=user_ob)
                    if verificado_correo(comun__ob):
                        return JsonResponse({'error': 'El usuario ya esta activo'})
                    comun__ob.is_activo = True
                    comun__ob.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
            else:
                return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
        else: 
            return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})
    except BadSignature:
       return JsonResponse({'error': 'Código de verificación inválido o ha expirado'})


def verificado_correo(ob1):
    # verificar si el objeto usuario esta activo
    if ob1.is_activo:
        return True
    else:
        return False

# METODO DE VERIFICACION DE CORREO
def verificacion_correo_V(ob1):
    try:
        # Obtener la instancia de Verificacion
        verificacion = ob1
        # Modificamos el estado de atencion de Verificacion
        verificacion.atendido = True
        verificacion.token = "0000"
        verificacion.save()
        # Obtener el correo de Verificacion
        email_ = verificacion.correo
        # Obtener el usuario asociado al correo
        user_ob = User.objects.get(email=email_)
        # Retornamos el usuario
        return user_ob
    except User.DoesNotExist:
        return False





######  METODOs DE REGISTRO DE USUARIO ######




@api_view(['POST'])
def api_user_register(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            first_name_ = data.get('nombre_usuario')
            last_name_ = data.get('apellido_usuario')
            email_ = data.get('email_usuario')
            username_ = data.get('username_usuario')
            password_ = data.get('password_usuario')
            celular_ = data.get('celular')
            fecha_ = data.get('fecha_nacimiento')
            cedula_ = data.get('cedula')
            if not validar_nombres(first_name_, last_name_):
                return JsonResponse({'error': 'Nombres y apellidos inválidos. Un solo espacio entre los valores..'})
            # Verificar si el usuario ya existe
            if existe__registro(first_name_, last_name_):
                return JsonResponse({'error': 'El usuario ya existe'})
            # Verificar valides de cédula
            if not cedula_unica(cedula_):
                return JsonResponse({'cedula': 'Cédula ya registrada'})
            # Verificar valides de cédula
            if not verificar_cedula_ecuatoriana(cedula_):
                return JsonResponse({'cedula': 'Cédula invalida, verifica el número de cédula ingresado.'})
            # Veriicar correo valido
            if not es_correo_valido(email_):
                return JsonResponse({'correo': 'Correo invalido'})
            # Verificar formato especificado
            if not validar_formato_email(email_):
                return JsonResponse({'correo': 'El formato del correo electrónico no es válido. Debe ser @gmail.com o @unl.edu.ec.'})
            # Validar correo único
            if not correo_unico(email_):
                return JsonResponse({'correo': 'Correo ya registrado'})
            # Verificar clave
            if not validar_clave(password_):
                return JsonResponse({'clave': 'Clave sin requisitos mínimos'})
            else:
                if username_exist(username_):
                    return JsonResponse({'error': 'El nombre de usuario ya existe'})
                else:
                    # Verificar confirmacion de cuenta
                    if not validar_correo_verificacion(email_):
                        return JsonResponse({'error': 'El correo es invalido o no existe'})
                    # Creamos el usuario
                    user = User.objects.create(
                        first_name=first_name_,
                        last_name=last_name_,
                        password=make_password(password_),
                        username=username_,
                        email=email_
                    )
                    # Añadimos a usuario
                    user.save()
                    crear_usuario_normal(first_name_, last_name_, email_, username_, fecha_, celular_, user, cedula_)
                    # Objeto Verificacion
                    verificacion = Verificacion.objects.get(correo=email_)
                    # Agregar el usuario
                    verificacion.usuario = user
                    # Guardar cambios
                    verificacion.save()
                    return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Método no permitido'})
    except Exception as e:
        return JsonResponse({'error': 'Error al crear el usuario'})

# Método para guardar el registro de entidad usuario
def crear_usuario_normal(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8):
    # Capturamos el la fecha de registro
    fecha_registro_usuario_ = datetime.now().date()
    # Guardamos el registro
    usuario__model = Usuario.objects.create(
        nombre_usuario=ob1,
        apellido_usuario=ob2,
        email_usuario=ob3,
        username_usuario=ob4,
        fecha_nacimiento=ob5,
        celular=ob6,
        user=ob7,
        dni=ob8,
        fecha_registro_usuario=fecha_registro_usuario_
    )
    # Añadimos a usuario
    usuario__model.save()



# METODO DE REGISTRO DE PACIENTE
@api_view(['POST'])
def api_paciente_register(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            first_name_ = data.get('nombre_usuario')
            last_name_ = data.get('apellido_usuario')
            email_ = data.get('email_usuario')
            username_ = data.get('username_usuario')
            password_ = data.get('password_usuario')
            celular_ = data.get('celular')
            fecha_ = data.get('fecha_nacimiento')
            contacto_emergencia_ = data.get('contacto_emergencia')
            direccion_ = data.get('direccion')
            cedula_ = data.get('cedula')
            if not validar_nombres(first_name_, last_name_):
                return JsonResponse({'error': 'Nombres y apellidos inválidos. Un solo espacio entre los valores..'})
            # Verificar si el usuario ya existe
            if existe__registro(first_name_, last_name_):
                return JsonResponse({'error': 'El usuario ya existe'})
            # Verificar valides de cédula
            if not cedula_unica(cedula_):
                return JsonResponse({'cedula': 'Cédula ya registrada'})
            # Verificar valides de cédula
            if not verificar_cedula_ecuatoriana(cedula_):
                return JsonResponse({'cedula': 'Cédula invalida, verifica el número de cédula ingresado.'})
            # Veriicar correo valido
            if not es_correo_valido(email_):
                return JsonResponse({'correo': 'Correo invalido'})
            # Verificar formato especificado
            if not validar_formato_email(email_):
                return JsonResponse({'correo': 'El formato del correo electrónico no es válido. Debe ser @gmail.com o @unl.edu.ec.'})
            # Validar correo único
            if not correo_unico(email_):
                return JsonResponse({'correo': 'Correo ya registrado'})
            print("Valide corre unico")
            # Validar edad límite
            if not cumplir_edad_limite(fecha_):
                return JsonResponse({'correo': 'No cumple con la edad establecida para registrarse'})
            print("Valide edad")
            # Verificar clave
            if not validar_clave(password_):
                return JsonResponse({'clave': 'Clave sin requisitos mínimos'})
            else:
                if username_exist(username_):
                    return JsonResponse({'error': 'El nombre de usuario ya existe'})
                else:
                    # Verificar confirmacion de cuenta
                    if not validar_correo_verificacion(email_):
                        return JsonResponse({'error': 'El correo es invalido o no existe'})
                    # Creamos el usuario
                    user_new = User.objects.create(
                        first_name=first_name_,
                        last_name=last_name_,
                        password=make_password(password_),
                        username=username_,
                        email=email_
                    )
                    # Añadimos a usuario
                    user_new.save()
                    crear_paciente_normal(first_name_, last_name_, email_, username_, celular_, contacto_emergencia_, fecha_, direccion_, user_new, cedula_)
                    # Objeto Verificacion
                    verificacion = Verificacion.objects.get(correo=email_)
                    # Agregar el usuario
                    verificacion.usuario = user_new
                    # Guardar cambios
                    verificacion.save()
                    return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Método no permitido'})
    except Exception as e:
        return JsonResponse({'error': 'Error al crear el usuario'})

# Método para guardar el registro de entidad paciente
def crear_paciente_normal(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8, ob9, ob10):
    # Capturamos el la fecha de registro
    fecha_registro_usuario_ = datetime.now().date()
    # Guardamos el registro
    usuario__model = Paciente.objects.create(
        nombre_usuario=ob1,
        apellido_usuario=ob2,
        email_usuario=ob3,
        username_usuario=ob4,
        celular=ob5,
        contacto_emergencia=ob6,
        fecha_nacimiento=ob7,
        direccion=ob8,
        user=ob9,
        dni=ob10,
        fecha_registro_usuario=fecha_registro_usuario_
    )
    # Añadimos a usuario
    usuario__model.save()

# Método para calcular el limite de edad establecido para crear cuenta de entidad paciente
def cumplir_edad_limite(ob1):
    try:
        # Formatear la edad para permitir que los objetos date time sean compatibles
        fecha_nacimiento = datetime.strptime(ob1, "%Y-%m-%d").date()
        fecha_actual = datetime.now().date()
        edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < 
                                                            (fecha_nacimiento.month, fecha_nacimiento.day))
        # Comparamos la edad con el rango de edad permitido que es de 5 a 10
        if 5 <= edad <= 10:
            return True
        else:
            return False
    except Exception as e:
        print("Error:", e)
        return False



# METODO DE REGISTRO DE USUARIO COMUN
@api_view(['POST'])
def api_comun_register(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            first_name_ = data.get('nombre_usuario')
            last_name_ = data.get('apellido_usuario')
            email_ = data.get('email_usuario')
            username_ = data.get('username_usuario')
            password_ = data.get('password_usuario')
            celular_ = data.get('celular')
            fecha_ = data.get('fecha_nacimiento')
            genero_ = data.get('genero')
            area_ = data.get('area_estudio')
            cedula_ = data.get('cedula')
            if not validar_nombres(first_name_, last_name_):
                return JsonResponse({'error': 'Nombres y apellidos inválidos. Un solo espacio entre los valores..'})
            # Verificar si el usuario ya existe
            if existe__registro(first_name_, last_name_):
                return JsonResponse({'error': 'El usuario ya existe'})
            # Verificar valides de cédula
            if not cedula_unica(cedula_):
                return JsonResponse({'cedula': 'Cédula ya registrada'})
            # Verificar valides de cédula
            if not verificar_cedula_ecuatoriana(cedula_):
                return JsonResponse({'cedula': 'Cédula invalida, verifica el número de cédula ingresado.'})
            # Veriicar correo valido
            if not es_correo_valido(email_):
                return JsonResponse({'correo': 'Correo invalido'})
            # Verificar formato especificado
            if not validar_formato_email(email_):
                return JsonResponse({'correo': 'El formato del correo electrónico no es válido. Debe ser @gmail.com o @unl.edu.ec.'})
            # Validar correo único
            if not correo_unico(email_):
                return JsonResponse({'correo': 'Correo ya registrado'})
            # Verificar clave
            if not validar_clave(password_):
                return JsonResponse({'clave': 'Clave sin requisitos mínimos'})
            else:
                if username_exist(username_):
                    return JsonResponse({'error': 'El nombre de usuario ya existe'})
                else:
                    # Verificar confirmacion de cuenta
                    if not validar_correo_verificacion(email_):
                        return JsonResponse({'error': 'El correo es invalido o no existe'})
                    # Creamos el usuario
                    user = User.objects.create(
                        first_name=first_name_,
                        last_name=last_name_,
                        password=make_password(password_),
                        username=username_,
                        email=email_
                    )
                    # Añadimos a usuario
                    user.save()
                    crear_comun_normal(first_name_, last_name_, email_, username_, celular_, fecha_, genero_, area_, user, cedula_)
                    # Objeto Verificacion
                    verificacion = Verificacion.objects.get(correo=email_)
                    # Agregar el usuario
                    verificacion.usuario = user
                    # Guardar cambios
                    verificacion.save()
                    return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Método no permitido'})
    except Exception as e:
        return JsonResponse({'error': 'Error al crear el usuario'})

# Método para guardar el registro de entidad usuario normal
def crear_comun_normal(ob1, ob2, ob3, ob4, ob5, ob6, ob7, ob8, ob9, ob10):
    # Capturamos el la fecha de registro
    fecha_registro_usuario_ = datetime.now().date()
    # Gaurdamos el registro
    usuario__model = UsuarioComun.objects.create(
        nombre_usuario=ob1,
        apellido_usuario=ob2,
        email_usuario=ob3,
        username_usuario=ob4,
        celular=ob5,
        fecha_nacimiento=ob6,
        genero=ob7,
        area_estudio=ob8,
        user=ob9,
        dni=ob10,
        fecha_registro_usuario=fecha_registro_usuario_
    )
    # Añadimos a usuario
    usuario__model.save()



#### METODOS DE VERIFICACIÓN DE REGISTROS EN LA BASE DE DATOS   



# Método para verificar si el usuario ya existe Y esta inscrito en un curso
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verificacion_inscripcion(request):
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
                detalle__inscripcion = DetalleInscripcionCurso.objects.filter(paciente=paciente__ob)
                # Verificar si el curso existe
                if detalle__inscripcion:
                    context = {
                        'success': True,
                        'inscrito': "1"
                    }
                    return JsonResponse(context)
                else:
                    context = {
                        'success': True,
                        'inscrito': "0"
                    }
                    return JsonResponse(context)
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'errorSalida': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)



# Método para verificar la existencia de una separacion por coma en los registros 
# obtneidos desde la base de datos
def comprobar_separacion_coma(valor_respuesta):
    # Verificar si el string contiene una coma
    if ',' in valor_respuesta:
        return True  # Si hay una coma, entonces hay varios valores
    else:
        return False  # Si no hay una coma, entonces solo hay un valor



# Método para dar paso al registro de atención de una petición del usuario común y 
# posteriormente enviar un mensaje por correo electrónico para confirmar la operación 
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def atender_peticion(request):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if is_tecnico(user):
                if request.method == 'POST':
                    data = json.loads(request.body)
                    slug = data.get('slug')
                    estadoR_ = data.get('estadoR')
                    vereficto_ = data.get('vereficto')
                    # Atender la petición
                    if not atención_peticion(slug):
                        return JsonResponse({'error': 'Error al atender la petición'}, status=400)
                    # Si se atiende la petición se da paso al envío del correo
                    peticion__ob = Peticion.objects.get(slug_peticion=slug)
                    tecnico__ob = Usuario.objects.get(user=user)
                    if send_email(peticion__ob, vereficto_, estadoR_):
                        try:
                            # Agregamos detalle de peticion
                            if guardar_detalle(tecnico__ob, peticion__ob):
                                # Actualizamos el contador de ContadorPeticionesAtendidas
                                contador_obj, created = ContadorPeticionesAtendidas.objects.get_or_create(
                                    usuario_comun=peticion__ob.usuario_comun)
                                contador_obj.contador += 1
                                contador_obj.save()
                                # Enviamos la respuesta al front
                                return JsonResponse({'success': True})
                            else:
                                return JsonResponse({'error': 'Error al guardar el detalle'}, status=500)
                        except Exception as e:
                            # Aquí puedes agregar logging o imprimir el error si es necesario
                            return JsonResponse({'error': 'Error al guardar el detalle'}, status=500)
                    else:
                        return JsonResponse({'error': 'Error al enviar el email'}, status=400)

                else:
                    return JsonResponse({'error': 'Algo no esta permitido'}, status=405)
            else:
                return JsonResponse({'errorSalida': 'El usuario no esta autenticado'}, status=401)
        except Peticion.DoesNotExist:
            error = "No existe petición"
            contexto_dos = {'error': error, 'slug': slug}
            return JsonResponse(contexto_dos)
        except Exception as e:
            return JsonResponse({'error': 'Ups! Algo salió mal'}, status=500)
    else:
        return JsonResponse({'errorSalida': 'El usuario no esta autenticado'}, status=401)

# Método para atender petición: cambia el estado de revisión de la petición
def atención_peticion(ob1):
    try: 
        # Obtenemos el objeto peticions
        peticion__ob = Peticion.objects.get(slug_peticion=ob1)
        # Modificamos el estado de revisión
        peticion__ob.estado_revision = True
        # Guardamos los datos y verificar si se guardaron
        peticion__ob.save()
        return True
    except Exception as e:
        return False

# Guardar el detalle de las peticiones atendidas
def guardar_detalle(ob1, ob2):
    try:
        # Obtenemos la fecha
        fecha_actual = datetime.now().date()
        detalle_peticion = DetallePeticion.objects.create(
            fecha_detalle_peticion=fecha_actual,
            usuario_tecnico=ob1,
            peticion=ob2
        )
        # Añadimos a contenido
        detalle_peticion.save()
        return True
    except Exception as e:
        return False

# Método para enviar el correo electrónico de notificación de revisión de petición
def send_email(peticion__ob, ob1, ob2):
    # Capturamos los datos para el email
    subject = 'Notificación de revisión de petición'
    message = f'Reciba un cordial saludo de los administradores de WAPIPTDAH. ' \
        f'\nRecibimos la confirmación de revisión de una petición emitada por usted.' \
        f'\nEste es un mensaje para informar y verificar que la petición fue atendida y revisada por los técnicos en cuestión. ' \
        f'\n\n1. Su peticion de tipo: ' \
        f'\n{peticion__ob.tipo_peticion}'\
        f'\nha sido atendida.'\
        f'\n\n2. El motivo de la misma era: ' \
        f'\n{peticion__ob.motivo_peticion}' \
        f'\nEl verdicto de la revisión es: {ob1} ' \
        f'\nLa misma cuenta con un estado de: {ob2}' \
        f'\nAtentamente: WAPIPTDAH.'
    from_email = settings.EMAIL_HOST_USER
    # receiver_email = ['cristobal.rios@unl.edu.ec']
    # receiver_email= ['genoveva.suing@unl.edu.ec']
    receiver_email = [peticion__ob.usuario_comun.email_usuario]

    send_mail(subject, message, from_email,
              receiver_email, fail_silently=False)
    return True


## Método para obtener y resetear el número de peticiiones emitidas por el usuario común
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_contador_peticiones(request):
    if request.method == 'GET':
        contador_obj = ContadorPeticiones.objects.get(pk=1)
        return JsonResponse({'contador': contador_obj.contador})
    else:
        return JsonResponse({'error': 'No hay contador'}, status=405)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_contador_peticiones(request):
    if request.method == 'GET':
        contador_obj = ContadorPeticiones.objects.get(pk=1)
        contador_obj.contador = 0
        contador_obj.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'No se puede resetear contador'}, status=405)


## Método para obtener y resetear el número de peticiiones atendidas por el usuario 
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_contador_peticiones_atendidas(request):
    try:
        if request.method == 'GET':
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            if (is_comun(user)):
                # Obtenemos el objeto usuario comun
                usuario__ob = UsuarioComun.objects.get(user=user)
                # Filtramos el contador del usuariuo comun
                contador_obj = ContadorPeticionesAtendidas.objects.get(usuario_comun=usuario__ob)
                return JsonResponse({'contador': contador_obj.contador})
            else:
                return JsonResponse({'error': 'Token no proporcionado'}, status=401)
        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_contador_peticiones_atendidas(request):
    try:
        if request.method == 'GET':
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            if (is_comun(user)):
                # Obtenemos el objeto usuario comun
                usuario__ob = UsuarioComun.objects.get(user=user)
                # Filtramos el contador del usuariuo comun
                contador_obj = ContadorPeticionesAtendidas.objects.get(usuario_comun=usuario__ob)
                contador_obj.contador = 0
                contador_obj.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Token no proporcionado'}, status=401)
        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 



## Método para obtener y resetear el número de salas emitidas para el estudiante
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_contador_salas(request):
    try:
        if request.method == 'GET':
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            if (is_paciente(user)):
                if paciente_existe_contador(user):
                    contador = numero_contador(user)
                    return JsonResponse({'contador': contador})
                else:
                    return JsonResponse({'contador': 0})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        else:
            return JsonResponse({'error': 'Algo no esta permitido'}, status=405) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 

# Obtiene el numero del contador existente
def numero_contador(user):
    try:
        # Obtenemos el objeto usuario comun
        usuario__ob = Paciente.objects.get(user=user)
        # Filtramos el contador del usuariuo comun
        contador_obj = ContadorSalas.objects.get(paciente=usuario__ob)
        return contador_obj.contador
    except ContadorSalas.DoesNotExist:
        return 0

# Verificar que existe un contador para un usuario en específico
def paciente_existe_contador(user):
    try:
        # Obtenemos el objeto usuario comun
        usuario__ob = Paciente.objects.get(user=user)
        # Filtramos el contador del usuariuo paciente para verificar su existencia 
        if ContadorSalas.objects.get(paciente=usuario__ob):
            return True
        return False
    except Paciente.DoesNotExist:
        return False
    except ContadorSalas.DoesNotExist:
        return False
    

# Método para resetear el contador de salas existentes para los estudiantes
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_contador_salas(request):
    try:
        if request.method == 'GET':
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            if (is_paciente(user)):
                # Obtenemos el objeto usuario comun
                usuario__ob = Paciente.objects.get(user=user)
                # Filtramos el contador del usuariuo comun
                contador_obj = ContadorSalas.objects.get(paciente=usuario__ob)
                contador_obj.contador = 0
                contador_obj.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        else:
            return JsonResponse({'error': 'Algo no esta permitido'}, status=405) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 


## Método para registrar la atención de las salas de contenido por parte de los esudiantes 
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def atender_sala(request, slug):
    if request.user.is_authenticated:
        try:
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if is_paciente(user):
                if request.method == 'GET':
                    if modificar_estado_sala(slug):
                        return JsonResponse({'success': True})
                    else:
                        error_message = "Error al modificar el estado de la sala."
                        context = {'error': error_message}
                        return JsonResponse(context)
                else:
                    return JsonResponse({'error': 'Algo no esta permitido'}, status=405)
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        except Peticion.DoesNotExist:
            error = "No existe sala"
            contexto_dos = {'error': error, 'slug': slug}
            return JsonResponse(contexto_dos)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)

# Método para modificar el estado de a sala
def modificar_estado_sala(slug):
    try:
        # Obtenemos el objeto sala
        sala__ob = Sala.objects.get(slug_sala=slug)
        # Modificamos el estado de la sala
        sala__ob.sala_atendida = True
        # Guardamos los datos y verificar si se guardaron
        sala__ob.save()
        # Actualizamos el contador
        ob_detalle = DetalleSala.objects.get(sala=sala__ob)
        # Encontrar el usuario comun que creo la sala
        usuario_comun = ob_detalle.usuario_comun
        contador_obj, created = ContadorSalasAtendidas.objects.get_or_create(usuario_comun=usuario_comun)
        contador_obj.contador += 1
        contador_obj.save()
        if send_email_sala(sala__ob, usuario_comun):
            return True
        else:
            return False
    except Exception as e:
        return False

# Envío de correo al dar como resuelta una nueva sala de contenido
def send_email_sala(ob1, ob2):
    # Capturamos los datos para el email
    subject = 'Notificación de resolución de sala'
    message = f'Reciba un cordial saludo de los administradores de WAPIPTDAH. ' \
            f'\nLa sala creada de nombre: {ob1.nombre_sala}. ' \
            f'\nRecibimos una confirmación de resolución de sala del estudiante: {ob1.paciente.nombre_usuario} {ob1.paciente.apellido_usuario}. ' \
            f'\nLa sala resuelta esta formada por las siguientes indicaciones: ' \
            f'\n\n{ob1.anotacione}'\
            f'\n\nLa misma cuenta con un estado de: ' \
            f'\n' \
            f'\nResuelto ' \
            f'\n' \
            f'\nAtentamente: WAPIPTDAH.'
    from_email = settings.EMAIL_HOST_USER
    #receiver_email = ['cristobal.rios@unl.edu.ec']
    #receiver_email= ['genoveva.suing@unl.edu.ec']
    receiver_email = [ob2.email_usuario]

    send_mail(subject, message, from_email, receiver_email, fail_silently=False)
    return True


## Método para verificar el contador de salas atendidas por los estudiantes
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_contador_salas_atendidas(request):
    try:
        if request.method == 'GET':
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            if (is_comun(user)):
                if comunN_existe_contador(user):
                    contador = numero_contador_SA(user)
                    return JsonResponse({'contador': contador})
                else:
                    return JsonResponse({'contador': 0})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        else:
            return JsonResponse({'error': 'Algo no esta permitido'}, status=405) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 

# Verificar la existencia del contador
def comunN_existe_contador(user):
    try:
        # Obtenemos el objeto usuario comun
        usuario__ob = UsuarioComun.objects.get(user=user)
        # Filtramos el contador del usuariuo comun
        if ContadorSalasAtendidas.objects.filter(usuario_comun=usuario__ob).exists():
            return True
    except ContadorSalasAtendidas.DoesNotExist:
        return False
    return False

# Obtener el contador
def numero_contador_SA(user):
    try:
        # Obtenemos el objeto usuario comun
        usuario__ob = UsuarioComun.objects.get(user=user)
        # Filtramos el contador del usuariuo comun
        contador_obj = ContadorSalasAtendidas.objects.get(usuario_comun=usuario__ob)
        return contador_obj.contador
    except ContadorSalasAtendidas.DoesNotExist:
        return 0


# Método para resetear el contador de salas atendidas por los estudiantes
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_contador_salas_atendidas(request):
    try:
        if request.method == 'GET':
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            if (is_comun(user)):
                # Obtenemos el objeto usuario comun
                usuario__ob = UsuarioComun.objects.get(user=user)
                # Filtramos el contador del usuariuo comun
                contador_obj = ContadorSalasAtendidas.objects.get(usuario_comun=usuario__ob)
                contador_obj.contador = 0
                contador_obj.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'El usuario no esta autenticado'}, status=401)
        else:
            return JsonResponse({'error': 'Algo no esta permitido'}, status=405) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 



## Obtener el slug de curso para redireccionamiento interno
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_slug_curso(request, id):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if is_comun(user):
                if request.method == 'GET':
                    id_ = id
                    slug = obtener_slug(id_)
                    if slug:
                        return JsonResponse({'success': True, 'slug': slug})
                    else:
                        error_message = "El curso no existe."
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

# Método para obtener el slug del curso
def obtener_slug(id):
    try:
        # Obtenemos el obtjeto paciente con el id
        paciente__ob = Paciente.objects.get(id=id)
        # Obtenemos el registro de inscripcion a curso asociado
        detalle_inscripcion_curso = DetalleInscripcionCurso.objects.get(paciente=paciente__ob)
        # Obtener el curso asociado a esa inscripcion de paciente
        curso__ob = detalle_inscripcion_curso.curso
        # sacar el slug del curso
        slug = curso__ob.slug_curso
        return slug
    except Paciente.DoesNotExist:
        return False
    except DetalleInscripcionCurso.DoesNotExist:
        return False

## Obtener el slug de dominio para redireccionamiento interno
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_slug_dominio(request, slug):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                if request.method == 'GET':
                    slug_ = slug
                    slug = obtener_slug_domi(slug_)
                    if slug:
                        return JsonResponse({'success': True, 'slug_dominio': slug})
                    else:
                        error_message = "El curso no existe."
                        context = {'error': error_message, 'success': False}
                        return JsonResponse(context)
                else:
                    return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
            else:
                return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Ups! algo salió mal'}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)

# Método para obtener el slug del dominio
def obtener_slug_domi(ob1):
    try:
        # Obtenemos el obtjeto contenido con el slug
        contenido_ob = Contenido.objects.get(slug_contenido=ob1)
        # Obtenemos el dominio del contenido
        dominio = contenido_ob.dominio
        # sacar el slug del dominio
        slug = dominio.slug_dominio
        return slug
    except Contenido.DoesNotExist:
        return False
    except Dominio.DoesNotExist:
        return False
    


## Obtener el slug de contenido para redireccionamiento interno
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_slug_contenido(request, slug):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            #user = get_user_from_token(token)
            if user and token:
                if request.method == 'GET':
                    slug_ = slug
                    slug = obtener_slug_conte(slug_)
                    if slug:
                        return JsonResponse({'success': True, 'slug_contenido': slug})
                    else:
                        error_message = "El contenido no existe."
                        context = {'error': error_message, 'success': False}
                        return JsonResponse(context)
                else:
                    return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
            else:
                return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Ups! algo salió mal'}, status=500)
    else:
        return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)

# Método para obtener el slug del contenido
def obtener_slug_conte(ob1):
    try:
        # Obtenemos el obtjeto individual con el slug
        contenido_ob = ContenidoIndividual.objects.get(slug_contenido_individual=ob1)
        # Obtenemos el contenido del individual
        contenido = contenido_ob.contenido
        # sacar el slug del dominio
        slug = contenido.slug_contenido
        return slug
    except ContenidoIndividual.DoesNotExist:
        return False
    except Contenido.DoesNotExist:
        return False
    

## ENVIAR CORREO DE CONTACTO
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def api_enviar_contacto(request):
    if request.user.is_authenticated:
        # Obtenemos el token
        try:
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
        except Exception as e:
            return JsonResponse({'error': 'El usuario no está autenticado'})
        
        # Verificar metodo permitido
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'})

        # Encontrar al usuario relacionado al user
        usuario__ob = encontrar_usuario(user)
        if usuario__ob:
            if request.method == 'POST':
                data = json.loads(request.body)
                asunto_ = data.get('motivo')
                mensaje_ = data.get('cuerpo')
                if enviar_correo(usuario__ob, asunto_, mensaje_):
                    return JsonResponse({'success': True})
                else:
                    error_message = "Error al enviar el correo."
                    context = {'error': error_message}
                    return JsonResponse(context)
            else:
                return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
        else:
            return JsonResponse({'error': 'Usuario no encontrado'})
    else:
        return JsonResponse({'error': 'El usuario no está autenticado'})

# Método para encontrar usuario
def encontrar_usuario(ob1):
    # Orden de los modelos a verificar
    modelos = [UsuarioComun, Paciente, Usuario]
    for modelo in modelos:
        try:
            # Intenta obtener el usuario de cada modelo
            usuario_ob = modelo.objects.get(user=ob1)
            return usuario_ob
        except modelo.DoesNotExist:
            # Si el usuario no existe en ese modelo, sigue con el siguiente
            continue
    # Si ninguno de los modelos contiene el usuario, retorna False
    return False

# Método para enviar correo
def enviar_correo(ob1, ob2, ob3):
    # Capturamos los datos para el email
    subject = ob2
    message = ob3
    from_email = ob1.email_usuario
    receiver_email = [settings.EMAIL_HOST_USER]
    send_mail(subject, message, from_email, receiver_email, fail_silently=False)
    return True




## Método para modificar el estado del reporte una vez que este haya sido eliminado
## y dar paso a la rectificación del estado de resultado
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def modificar_estado_reporte(request, id):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Verificar existencia del usuario
            if user and token:
                if request.method == 'GET':
                    id_reporte = id
                    # Guardar Reporte
                    if modificar_estado_resultado(id_reporte):
                        return JsonResponse({'success': True})
                    else:
                        error_message = "Error al eliminar el reporte...."
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

# Método para modificar el estado del resultao una vez se haya generado el reporte 
def modificar_estado_resultado(ob1):
    try:
        #Obtenemos el objeto reporte a partir del id
        reporte_ob = Reporte.objects.get(id=ob1)
        # Obtenemos el objeto resultado relacionado al reporte
        resultado_ob = reporte_ob.resultado
        # Modifiamos el estado de reporte del resultado
        resultado_ob.estado_reporte = False
        resultado_ob.save()
        return True
    except Exception as e:
        return False



## Método para obtener la fecha de inscripción del estudiante a un curso
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_fecha_inscripcion(request, id):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Verificar existencia del usuario
            if user and token:
                if request.method == 'GET':
                    id_paciente = id
                    # buscamos la fecha de inscripcion del paciente
                    # Obtenemos el objeto paciente
                    paciente_ob = Paciente.objects.get(id=id_paciente)
                    # Obtenemos la fecha de inscripcion del paciente de DetalleInscripcionCurso
                    inscripcion_ = DetalleInscripcionCurso.objects.get(paciente=paciente_ob)
                    # Obtenemos la fecha de inscripcion
                    fecha_inscripcion = inscripcion_.fecha_inscripcion
                    # Verificamos y devolvemos al frontend
                    return JsonResponse({'success': True, 'fecha_inscripcion': fecha_inscripcion})
                else:
                    return JsonResponse({'error': 'No es posible ejecutar la acción'}, status=405)
            else:
                return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Ups! algo salió mal'}, status=500)
    else:
       return JsonResponse({'error': 'El usuario no se ha autenticado'}, status=401) 

# Método para obtener la fecha de inscripcion del paciente
def obtener_fecha(ob1, ob2):
    try:
        # Verificamos que el usuario sea paciente
        if is_paciente(ob1):
            # Obtenemos el objeto paciente
            paciente_ob = Paciente.objects.get(id=ob2)
            # Obtenemos la fecha de inscripcion del paciente de DetalleInscripcionCurso
            inscripcion_ = DetalleInscripcionCurso.objects.get(paciente=paciente_ob)
            # Obtenemos la fecha de inscripcion
            fecha_inscripcion = inscripcion_.fecha_inscripcion
            return fecha_inscripcion
        else:
            return False
    except Paciente.DoesNotExist:
        return False
    except DetalleInscripcionCurso.DoesNotExist:
        return False


## Método para obtener el nombre de revisor de una petición 
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_nombre_revision(request, id):
    if request.user.is_authenticated:
        try: 
            # Decodifica el token
            token = request.headers.get('Authorization').split(" ")[1]
            user = get_user_from_token_jwt(token)
            # Verificar existencia del usuario
            if user and token:
                if request.method == 'GET':
                    peticion_id = id
                    # Verificamos y obtenemos los valores
                    nombre_usuario, apellido_usuario = nombre_revision(peticion_id)
                    if nombre_usuario and apellido_usuario:
                        # Verificamos y devolvemos al frontend
                        return JsonResponse({'success': True, 
                                            'nombre_u': nombre_usuario, 
                                            'apellido_u': apellido_usuario})
                    else:
                        error_message = "No se pudo obtener el nombre del revisor"
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

# Obtener el nombre del revisor de la petición
def nombre_revision(ob1):
    try:
        # Obtenemos la peticion asociada al id
        peticion_ob = Peticion.objects.get(id=ob1)
        # Obtenemos el objeto de Detalle Peticion 
        detalle_peticion_ob = DetallePeticion.objects.get(peticion=peticion_ob)
        # Obtenemos el nombre y apellido del usuario tecnico
        nombre_usuario = detalle_peticion_ob.usuario_tecnico.nombre_usuario
        apellido_usuario = detalle_peticion_ob.usuario_tecnico.apellido_usuario
        # Retornamos los valores
        return nombre_usuario, apellido_usuario
    except Peticion.DoesNotExist:
        return False
    except DetallePeticion.DoesNotExist:
        return False