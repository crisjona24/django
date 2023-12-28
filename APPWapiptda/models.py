from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from cloudinary_storage.storage import MediaCloudinaryStorage, RawMediaCloudinaryStorage
from datetime import date, datetime, timedelta
import pytz

''' 
Los modelos son la representacion de los datos que seran 
almacenados en la base de datos con fines de uso legal 
y en vias del desarrollo del presente PIC. Cristobal Rios

'''

# Correo
from django.utils.crypto import get_random_string

# MODELO DE RECUPERACION DE CLAVE
class Recuperacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    fecha_limite = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    atendido = models.BooleanField(default=False)

    def esta_vencido(self):
        utc = pytz.timezone('UTC')
        # Controlamos la fecha limite de valides del token
        fecha_creacion = self.fecha_creacion + timedelta(hours=1)
        fecha_creacion = fecha_creacion.replace(tzinfo=utc, microsecond=0)
        fecha_actual = datetime.utcnow()
        fecha_actual = datetime.utcnow().replace(tzinfo=utc, microsecond=0)
        return fecha_actual > fecha_creacion
    def __str__(self):
        return f"Usuario : {self.usuario}"

class Verificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=False, null=True)
    token = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    fecha_limite = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    atendido = models.BooleanField(default=False)

    def esta_vencido(self):
        utc = pytz.timezone('UTC')
        # Controlamos la fecha limite de valides del token
        fecha_creacion = self.fecha_creacion + timedelta(hours=1)
        fecha_creacion = fecha_creacion.replace(tzinfo=utc, microsecond=0)
        fecha_actual = datetime.utcnow()
        fecha_actual = datetime.utcnow().replace(tzinfo=utc, microsecond=0)
        return fecha_actual > fecha_creacion
    def __str__(self):
        return f"Usuario creado en : {self.fecha_creacion}"

# MODELO USUARIO
class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=80, blank=False, null=True)
    apellido_usuario = models.CharField(max_length=80, blank=False, null=True)
    email_usuario = models.EmailField(max_length=80, blank=False, null=True)
    username_usuario = models.CharField(unique=True, max_length=80, blank=False, null=True)
    celular = models.CharField(max_length=10, blank=False, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    dni = models.CharField(max_length=10, blank=False, null=True)
    estado_usuario = models.BooleanField(default=True)
    slug_usuario = models.SlugField(unique=True, blank=True)
    fecha_registro_usuario = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edi_usuario = models.DateField(auto_now=True)
    is_tecnico = models.BooleanField(default=True)
    is_activo = models.BooleanField(default=False)
    # Correo
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_usuario = slugify(
            self.nombre_usuario + "-" + self.apellido_usuario)
        super(Usuario, self).save(*args, **kwargs)

    # Correo
    def generate_confirmation_token(self):
        self.confirmation_token = get_random_string(length=40)
        self.save()
    # Correo

    @property
    def edad(self):
        return self.calcular_edad()
    
    def calcular_edad(self):
        hoy = date.today()
        nacido = self.fecha_nacimiento
        return hoy.year - nacido.year - ((hoy.month, hoy.day) < (nacido.month, nacido.day))

    def __str__(self):
        return f"Usuario : {self.nombre_usuario} {self.apellido_usuario}"

# MODELO PACIENTE
class Paciente(models.Model):
    nombre_usuario = models.CharField(max_length=80, blank=False, null=True)
    apellido_usuario = models.CharField(max_length=80, blank=False, null=True)
    email_usuario = models.EmailField(max_length=80, blank=False, null=True)
    username_usuario = models.CharField(unique=True, max_length=80, blank=False, null=True)
    celular = models.CharField(max_length=10, blank=False, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    dni = models.CharField(max_length=10, blank=False, null=True)
    estado_usuario = models.BooleanField(default=True)
    slug_usuario = models.SlugField(unique=True, blank=True)
    fecha_registro_usuario = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edi_usuario = models.DateField(auto_now=True)
    contacto_emergencia = models.CharField(max_length=10, blank=False, null=True)
    direccion = models.CharField(max_length=100, blank=False, null=True)
    is_paciente = models.BooleanField(default=True)
    is_activo = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.slug_usuario = slugify(
            self.nombre_usuario + "-" + self.apellido_usuario)
        super(Paciente, self).save(*args, **kwargs)

    @property
    def edad(self):
        return self.calcular_edad()
    
    def calcular_edad(self):
        hoy = date.today()
        nacido = self.fecha_nacimiento
        return hoy.year - nacido.year - ((hoy.month, hoy.day) < (nacido.month, nacido.day))

    def __str__(self):
        return f"Usuario : {self.nombre_usuario} {self.apellido_usuario}"

# MODELO COMUN
class UsuarioComun(models.Model):
    nombre_usuario = models.CharField(max_length=80, blank=False, null=True)
    apellido_usuario = models.CharField(max_length=80, blank=False, null=True)
    email_usuario = models.EmailField(max_length=80, blank=False, null=True)
    username_usuario = models.CharField(unique=True, max_length=80, blank=False, null=True)
    celular = models.CharField(max_length=10, blank=False, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    dni = models.CharField(max_length=10, blank=False, null=True)
    estado_usuario = models.BooleanField(default=True)
    slug_usuario = models.SlugField(unique=True, blank=True)
    fecha_registro_usuario = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edi_usuario = models.DateField(auto_now=True)
    genero = models.CharField(max_length=100, blank=False, null=True)
    area_estudio = models.CharField(max_length=100, blank=False, null=True)
    is_comun = models.BooleanField(default=True)
    is_activo = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_usuario = slugify(
            self.nombre_usuario + "-" + self.apellido_usuario)
        super(UsuarioComun, self).save(*args, **kwargs)

    @property
    def edad(self):
        return self.calcular_edad()
    
    def calcular_edad(self):
        hoy = date.today()
        nacido = self.fecha_nacimiento
        return hoy.year - nacido.year - ((hoy.month, hoy.day) < (nacido.month, nacido.day))
    
    def __str__(self):
        return f"Usuario : {self.nombre_usuario} {self.apellido_usuario}"

# MODELO DE GRADO DE TDAH
class GradoTDAH(models.Model):
    nombre_nivel = models.CharField(max_length=80, blank=False, null=True, unique=True)
    descripcion_grado = models.CharField(max_length=250, blank=False, null=True)
    numero_categorias = models.IntegerField(blank=False, null=True)
    grado_dificultad = models.CharField(max_length=80, blank=False, null=True)
    slug_grado = models.SlugField(unique=True, blank=True)
    fecha_registro_grado = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_grado = models.DateField(auto_now=True)
    estado_grado = models.BooleanField(default=True)
    # Agregar la clave foránea a UsuarioTecnico
    usuario_tecnico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name='grados_tdah', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_grado = slugify(self.nombre_nivel + "-" + self.grado_dificultad)
        super(GradoTDAH, self).save(*args, **kwargs)

    def __str__(self):
        return f"Grado : {self.nombre_nivel} | Fecha : {self.estado_grado}"

# MODELO DOMINIO
class Dominio(models.Model):
    nombre = models.CharField(max_length=80, blank=False, null=True)
    descripcion = models.TextField(max_length=250, blank=False, null=True)
    identificador_dominio = models.IntegerField(unique=True, blank=False, null=True)
    fecha_registro_dominio = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_dominio = models.DateField(auto_now=True)
    estado_dominio = models.BooleanField(default=True)
    slug_dominio = models.SlugField(unique=True, blank=True)
    portada_dominio = models.ImageField( upload_to='samples/fondo_dominio_react/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    # Llave foranea
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_dominio = slugify(self.nombre + "-" + self.descripcion)
        super(Dominio, self).save(*args, **kwargs)

    def get_portada_url(self):
        if self.portada_dominio and hasattr(self.portada_dominio, 'url'):
            return self.portada_dominio.url
        else:
            return None

    def __str__(self):
        return f"Dominio : {self.nombre} | Fecha : {self.fecha_registro_dominio}"

# MODELO DE CONTENIDO
class Contenido(models.Model):
    nombre = models.CharField(max_length=80, blank=False, null=True)
    identificador_contenido = models.IntegerField(unique=True, blank=False, null=True)
    dominio_tipo = models.CharField(max_length=80, blank=False, null=True)
    fecha_registro_contenido = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_contenido = models.DateField(auto_now=True)
    estado_contenido = models.BooleanField(default=True)
    slug_contenido = models.SlugField(unique=True, blank=True)
    portada = models.ImageField(upload_to='samples/prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)

    # Foranea
    dominio = models.ForeignKey(Dominio, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_contenido = slugify(self.nombre + "-" + self.dominio_tipo)
        super(Contenido, self).save(*args, **kwargs)

    def get_portada_url(self):
        if self.portada and hasattr(self.portada, 'url'):
            return self.portada.url
        else:
            return None

    def __str__(self):
        return f"Nombre : {self.nombre} | Identificador : {self.identificador_contenido}"

# MODELO DE CONTENIDO INDIVIDUAL
class ContenidoIndividual(models.Model):
    descripcion_individual = models.TextField( max_length=250, blank=False, null=True)
    identificador_individual = models.IntegerField(unique=True, blank=False, null=True)
    fecha_registro_individual = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_individual = models.DateField(auto_now=True)
    nivel = models.CharField(max_length=80, blank=False, null=True)
    estado_contenido_i = models.BooleanField(default=True)
    slug_contenido_individual = models.SlugField(max_length=250, unique=True, blank=True)
    tipo_contenido = models.CharField(max_length=80, blank=False, null=True)
    contenido_individual = models.ImageField(upload_to='samples/contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    portada_individual = models.ImageField(upload_to='samples/portada_contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    respuesta = models.CharField(max_length=250, blank=False, null=True)
    # Para seleccion de con imagenes
    imagen1 = models.ImageField(upload_to='samples/contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    imagen2 = models.ImageField(upload_to='samples/contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    imagen3 = models.ImageField(upload_to='samples/contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    imagen4 = models.ImageField(upload_to='samples/contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    imagen5 = models.ImageField(upload_to='samples/contenido_prueba/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    # Foranea
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        ident= str(self.identificador_individual)
        self.slug_contenido_individual = slugify(ident + "-" + self.tipo_contenido)
        super(ContenidoIndividual, self).save(*args, **kwargs)

    def get_portada_url(self):
        if self.portada_individual and hasattr(self.portada_individual, 'url'):
            return self.portada_individual.url
        else:
            return None
        
    def get_contenido_url(self):
        if self.contenido_individual and hasattr(self.contenido_individual, 'url'):
            return self.contenido_individual.url
        else:
            return None

    def __str__(self):
        return f"Descripción : {self.descripcion_individual}"
    
# MODELO DE RESULTADO
class Resultado(models.Model):
    respuesta = models.TextField(blank=False, null=True)
    tiempo_m = models.IntegerField(default=0, blank=False, null=True)
    tiempo_s = models.IntegerField(default=0, blank=False, null=True)
    observacion = models.TextField(blank=False, null=True)
    fecha_registro_resultado = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_resultado = models.DateField(auto_now=True)
    estado_resultado = models.BooleanField(default=True)
    slug_resultado = models.SlugField(unique=False, blank=True)
    estado_reporte = models.BooleanField(default=False)
    # Foranea
    contenido_individual = models.ForeignKey(
        ContenidoIndividual, on_delete=models.SET_NULL, blank=True, null=True)
    paciente = models.ForeignKey(
        Paciente, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Formatear el tiempo como cadenas de texto
        tiempo_formateado = str(self.tiempo_s)
        # Concatenar y slugify la fecha y el tiempo formateados
        base_slug = f"{self.paciente.nombre_usuario}-{self.contenido_individual.tipo_contenido}-{tiempo_formateado}"
        self.slug_resultado = slugify(base_slug)
        super(Resultado, self).save(*args, **kwargs)

    def __str__(self):
        return f" Resultado : {self.estado_resultado} | Fecha : {self.fecha_registro_resultado}"
    
# MODELO DE CURSO
class Curso(models.Model):
    nombre_curso = models.CharField(max_length=100, blank=False, null=True)
    descripcion_curso = models.TextField(max_length=250, blank=False, null=True)
    identificador_curso = models.IntegerField(unique=True, blank=False, null=True)
    fecha_registro_curso = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_curso = models.DateField(auto_now=True)
    estado_curso = models.BooleanField(default=True)
    slug_curso = models.SlugField(unique=True, blank=True, max_length=70)
    # Foranea
    usuario_comun = models.ForeignKey(UsuarioComun, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_curso = slugify(self.nombre_curso + "-" + self.descripcion_curso)
        super(Curso, self).save(*args, **kwargs)

    def __str__(self):
        return f"Nombre : {self.nombre_curso} | Estado : {self.estado_curso}"
    
# MODELO DE DETALLE INSCRIPCION A CURSO
class DetalleInscripcionCurso(models.Model):
    fecha_inscripcion = models.DateField(auto_now=True)
    estado_detalle = models.BooleanField(default=True)
    # Foraneas
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, blank=True, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Fecha : {self.fecha_inscripcion} | Estado : {self.estado_detalle}"

# MODELO DE PETICION
class Peticion(models.Model):
    motivo_peticion = models.CharField(max_length=250, blank=False, null=True)
    tipo_peticion = models.CharField(max_length=80, blank=False, null=True)
    peticion_cuerpo = models.TextField(max_length=250, blank=False, null=True)
    estado_peticion = models.BooleanField(default=True)
    estado_revision= models.BooleanField(default=False)
    fecha_registro_peticion = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_peticion = models.DateField(auto_now=True)
    slug_peticion = models.SlugField(unique=True, blank=True)
    # Foraneas
    usuario_comun = models.ForeignKey(UsuarioComun, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_peticion = slugify(self.motivo_peticion + "-" + self.tipo_peticion)
        super(Peticion, self).save(*args, **kwargs)

    def __str__(self):
        return f"Motivo : {self.motivo_peticion}"

# MODELO DE DETALLE PETICION
class DetallePeticion(models.Model):
    fecha_detalle_peticion = models.DateField(auto_now_add=False, blank=True, null=True)
    edi_detalle = models.DateField(auto_now=True)
    estado_detalle_revision = models.BooleanField(default=True)
    # Foraneas
    peticion = models.ForeignKey(Peticion, on_delete=models.CASCADE, blank=True, null=True)
    usuario_tecnico = models.ForeignKey(Usuario, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Motivo : {self.peticion.motivo_peticion} | Revision : {self.estado_detalle_revision}"

#MODELO DE SALA
class Sala(models.Model):
    nombre_sala = models.CharField(max_length=80, blank=False, null=True)
    anotaciones = models.TextField()
    codigo_identificador = models.CharField(max_length=80, blank=False, null=True)
    fecha_registro_sala = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_sala = models.DateField(auto_now=True)
    estado_sala = models.BooleanField(default=True)
    sala_atendida = models.BooleanField(default=False)
    slug_sala = models.SlugField(unique=True, blank=True)
    # Foraneas
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_sala = slugify(self.nombre_sala)
        super(Sala, self).save(*args, **kwargs)

    def __str__(self):
        return f" Nombre : {self.nombre_sala} | Fecha : {self.fecha_registro_sala}"

# DETALLE SALA
class DetalleSala(models.Model):
    fecha_detalle_sala = models.DateField(auto_now=True)
    estado_detalle_sala = models.BooleanField(default=True)
    # Foraneas
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, blank=True, null=True)
    usuario_comun = models.ForeignKey(UsuarioComun, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Fecha : {self.fecha_detalle_sala} | Estado : {self.estado_detalle_sala}"

#MODELO DE REPORTES
class Reporte(models.Model):
    titulo_reporte = models.CharField(max_length=200, blank=False, null=True)
    descripcion_reporte = models.TextField(blank=False, null=True)
    slug_reporte = models.SlugField(unique=False, blank=False, null=True)
    fecha_registro_reporte = models.DateField(auto_now_add=False, blank=True, null=True)
    fecha_edicion_reporte = models.DateField(auto_now=True)
    estado_reporte = models.BooleanField(default=True)
    # Foraneas
    usuario_comun = models.ForeignKey(UsuarioComun, on_delete=models.SET_NULL, related_name='reportes', blank=True, null=True)
    resultado = models.ForeignKey(Resultado, on_delete=models.SET_NULL, related_name='reportes_resultado', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug_reporte = slugify(self.titulo_reporte + '-' + self.descripcion_reporte)
        super(Reporte, self).save(*args, **kwargs)

    def __str__(self):
        return f" Titulo : {self.titulo_reporte}"


# MODELO DE CONTADOR
class ContadorPeticiones(models.Model):
    contador = models.IntegerField(default=0)

class ContadorPeticionesAtendidas(models.Model):
    contador = models.IntegerField(default=0)
    usuario_comun = models.ForeignKey(UsuarioComun, on_delete=models.CASCADE, blank=True, null=True)

class ContadorSalas(models.Model):
    contador = models.IntegerField(default=0)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, blank=True, null=True)    

class ContadorSalasAtendidas(models.Model):
    contador = models.IntegerField(default=0)
    usuario_comun = models.ForeignKey(UsuarioComun, on_delete=models.CASCADE, blank=True, null=True)
