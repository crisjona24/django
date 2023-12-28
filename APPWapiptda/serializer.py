from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers
import cloudinary
from cloudinary import uploader

# Clase de serialización para user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

# Clase de serialización para el usuario tecnico
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('nombre_usuario', 'apellido_usuario', 'email_usuario', 'dni',
                  'username_usuario', 'celular', 'fecha_nacimiento', 'is_activo', 'user')

# Clase de serialización para el usuario paciente con denominacion formal: Estudiante
class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ( 'id', 'nombre_usuario', 'apellido_usuario', 'email_usuario', 'username_usuario', 'dni',
                  'celular', 'contacto_emergencia', 'fecha_nacimiento', 'direccion', 'edad', 'is_activo', 'user',
                  )

# Clase de serialización para el usuario comun
class ComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioComun
        fields = ('nombre_usuario', 'apellido_usuario', 'email_usuario', 'username_usuario', 'dni',
                  'celular', 'genero', 'fecha_nacimiento', 'area_estudio', 'edad', 'is_activo', 'user')

# Clase de serialización para los niveles de TDAH registrados en el sistema
class GraditoTDAHSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradoTDAH
        fields = ('id', 'nombre_nivel', 'descripcion_grado', 'numero_categorias', 'grado_dificultad',
                  'slug_grado', 'usuario_tecnico')
    
    # Validación de nombre de nivel no duplicado para edicion
    def validar_nombre_nivel(self, value):
        instance = self.instance
        print(f"Valor actual de 'value': {value}")
        existe_otro_nivel = GradoTDAH.objects.exclude(
            id=instance.id if instance else None).filter(nombre_nivel=value).exists()
        print(f"¿Existe otro nivel con el mismo nombre?: {existe_otro_nivel}")
        if existe_otro_nivel:
            raise serializers.ValidationError({"nombre" : "Ya existe un nivel con este nombre"})
        return value
    
    def validate(self, data):
        # Llamando a la validación del nombre de curso
        nombre_nivel = data.get('nombre_nivel')
        self.validar_nombre_nivel(nombre_nivel)
        return data

# Clase de serialización para los dominios registrados en el sistema
class DominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dominio
        fields = ('id', 'nombre', 'descripcion', 'slug_dominio',
                  'identificador_dominio', 'portada_dominio',
                  'fecha_registro_dominio')
        
    # Validación de nombre no duplicado en la edición
    def validar_nombre_dominio(self, value):
        instance = self.instance
        # Verificar si hay algún otro curso con el mismo nombre
        existe_otro_dominio = Dominio.objects.exclude(
            id=instance.id if instance else None).filter(nombre=value).exists()
        if existe_otro_dominio:
            raise serializers.ValidationError({"nombre":"Ya existe un dominio con este nombre"})
        
        if instance:
            public_id = self.obtener_public_id(instance.id)
            # Elimina la imagen actual en Cloudinary solo si se proporciona una nueva imagen
            nueva_imagen = self.initial_data.get('portada_dominio')
            if public_id and nueva_imagen:
                resultado_eliminacion = self.eliminar_archivo_cloudinary(public_id)
                if resultado_eliminacion.get('result') == 'not found':
                    raise serializers.ValidationError({"portada_dominio": "Error al eliminar la imagen actual"})

        return value
    
    # Método para obtener el public id de la portada
    def obtener_public_id(self, dominio_id):
        try:
            dominio_ob = Dominio.objects.get(id=dominio_id)
            if dominio_ob.portada_dominio:
                return cloudinary.CloudinaryImage(dominio_ob.portada_dominio.name).public_id
            return None
        except Dominio.DoesNotExist:
            return None
        except Exception as e:
            return None
        
    # Método para eliminar la imagen de portada
    def eliminar_archivo_cloudinary(self, public_id):
        try:
            result = uploader.destroy(public_id)
            return result
        except Exception as e:
            return None
        
    def validate(self, data):
        # Llamando a la validación del nombre de dominio
        nombre_dominio = data.get('nombre')
        self.validar_nombre_dominio(nombre_dominio)
        return data

# Clase de serialización para los tipos de contenido registrados en el sistema
class ContenidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contenido
        fields = ('id', 'nombre', 'identificador_contenido', 'slug_contenido',
                  'dominio_tipo', 'portada', 'dominio', 'fecha_registro_contenido')
    
    # Validación de nombre no duplicado en la edición
    def validar_nombre_contenido(self, value):
        instance = self.instance
        # Verificar si hay algún otro curso con el mismo nombre
        existe_otro_contenido = Contenido.objects.exclude(
            id=instance.id if instance else None).filter(nombre=value).exists()
        if existe_otro_contenido:
            raise serializers.ValidationError({"nombre": "Ya existe un contenido con este nombre"})
        
        if instance:
            public_id = self.obtener_public_id(instance.id)
            # Elimina la imagen actual en Cloudinary solo si se proporciona una nueva imagen
            nueva_imagen = self.initial_data.get('portada')
            if public_id and nueva_imagen:
                resultado_eliminacion = self.eliminar_archivo_cloudinary(public_id)
                if resultado_eliminacion.get('result') == 'not found':
                    raise serializers.ValidationError({"portada": "Error al eliminar la imagen actual"})

        return value
    
    # Método para obtener el public id de la portada
    def obtener_public_id(self, contenido_id):
        try:
            contenido_ob = Contenido.objects.get(id=contenido_id)
            if contenido_ob.portada:
                return cloudinary.CloudinaryImage(contenido_ob.portada.name).public_id
            return None
        except Contenido.DoesNotExist:
            return None
        except Exception as e:
            return None
        
    # Método para eliminar la imagen de portada
    def eliminar_archivo_cloudinary(self, public_id):
        try:
            result = uploader.destroy(public_id)
            return result
        except Exception as e:
            return None
        
    def validate(self, data):
        # Llamando a la validación del nombre de dominio
        nombre_contenido = data.get('nombre')
        self.validar_nombre_contenido(nombre_contenido)
        return data

# Clase de serialización para las actividades registrados en el sistema
class ContenidIndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContenidoIndividual
        fields = ('id', 'descripcion_individual', 'respuesta', 'identificador_individual', 'slug_contenido_individual',
                  'portada_individual', 'nivel', 'tipo_contenido', 'contenido_individual', 'imagen1', 'contenido',
                  'imagen2', 'imagen3', 'imagen4', 'imagen5', 'fecha_registro_individual')


# Clase de serialización para los registros de resultados de las actividades
# se añaden los datos del paciente y la actividad
class ResultadoSerializer(serializers.ModelSerializer):
    # Paciente
    nombre_paciente = serializers.SerializerMethodField()
    apellido_paciente = serializers.SerializerMethodField()
    correo_paciente = serializers.SerializerMethodField()
    celular_paciente = serializers.SerializerMethodField()
    edad_paciente = serializers.SerializerMethodField()
    # Actividad
    descripcion_individual = serializers.SerializerMethodField()
    respuesta_contenido = serializers.SerializerMethodField()
    tipo_contenido = serializers.SerializerMethodField()

    class Meta:
        model = Resultado
        fields = ('id', 'respuesta', 'tiempo_m', 'tiempo_s', 'observacion', 'fecha_registro_resultado', 
                  'fecha_edicion_resultado',
                  'slug_resultado', 'estado_resultado', 'estado_reporte', 'contenido_individual', 'paciente',
                  'nombre_paciente', 'apellido_paciente', 'correo_paciente', 'celular_paciente', 'edad_paciente',
                  'tipo_contenido', 'descripcion_individual', 'respuesta_contenido')
        
    def get_nombre_paciente(self, obj):
        return obj.paciente.nombre_usuario
    def get_apellido_paciente(self, obj):
        return obj.paciente.apellido_usuario
    def get_correo_paciente(self, obj):
        return obj.paciente.email_usuario
    def get_edad_paciente(self, obj):
        return obj.paciente.edad
    def get_celular_paciente(self, obj):
        return obj.paciente.celular
    def get_descripcion_individual(self, obj):
        return obj.contenido_individual.descripcion_individual
    def get_respuesta_contenido(self, obj):
        return obj.contenido_individual.respuesta
    def get_tipo_contenido(self, obj):
        return obj.contenido_individual.tipo_contenido


class ResultadoSerializerOnly(serializers.ModelSerializer):
    class Meta:
        model = Resultado
        fields = ('id', 'observacion')


# Clase de serialización para los registros de curso generados 
# por el usuario comun
class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ('id', 'nombre_curso', 'descripcion_curso', 'slug_curso', 'usuario_comun',
                  'identificador_curso', 'fecha_edicion_curso', 'fecha_registro_curso')
    
    # Validación de nombre de curso no duplicado para edicion
    def validar_nombre_curso(self, value):
        instance = self.instance
        print(f"Valor actual de 'value': {value}")
        existe_otro_curso = Curso.objects.exclude(
            id=instance.id if instance else None).filter(nombre_curso=value).exists()
        print(f"¿Existe otro curso con el mismo nombre?: {existe_otro_curso}")
        if existe_otro_curso:
            raise serializers.ValidationError({"nombre" : "Ya existe un curso con este nombre"})
        return value
    
    def validate(self, data):
        # Llamando a la validación del nombre de curso
        nombre_curso = data.get('nombre_curso')
        self.validar_nombre_curso(nombre_curso)
        return data
    

# Clase de serialización para los registros de inscripciones a cursos
class DetalleInscripcionCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleInscripcionCurso
        fields = ('id', 'fecha_inscripcion',
                  'estado_detalle', 'paciente', 'curso')

# Clase de serialización para los registros de ipeticiones generados
# # por el usuario comun 
class PeticionSerializer(serializers.ModelSerializer):
    # Datos de usuario comun
    nombre_usuario = serializers.SerializerMethodField()
    apellido_usuario = serializers.SerializerMethodField()
    class Meta:
        model = Peticion
        fields = ('id', 'motivo_peticion', 'tipo_peticion', 'slug_peticion', 'fecha_edicion_peticion',
                  'estado_revision', 'peticion_cuerpo', 'fecha_registro_peticion', 'usuario_comun',
                  'nombre_usuario', 'apellido_usuario')
    def get_nombre_usuario(self, obj):
        return obj.usuario_comun.nombre_usuario
    def get_apellido_usuario(self, obj):
        return obj.usuario_comun.apellido_usuario

# Clase de serialización para los registros de detalle de peticiones
# añadiendo los datos del usuario tecnico
class DetallePeticionSerializer(serializers.ModelSerializer):
    #usuario_tecnico = serializers.SerializerMethodField()
    usuario_tecnico = serializers.CharField(source='usuario_tecnico.nombre_usuario', read_only=True)
    motivo_peticion = serializers.CharField(source='peticion.motivo_peticion', read_only=True)
    class Meta:
        model = DetallePeticion
        fields = ('id', 'fecha_detalle_peticion', 'estado_detalle_revision', 'edi_detalle',
                  'peticion', 'usuario_tecnico', 'motivo_peticion')
        
# Clase de serialización para los registros de salas generados
# por el usuario comun
class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ('id', 'nombre_sala', 'anotaciones', 'codigo_identificador', 'slug_sala', 'estado_sala', 
                  'sala_atendida', 'fecha_registro_sala', 'fecha_edicion_sala', 'paciente')

# Clase de serialización para los registros de detalle de salas
class DetalleSalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleSala
        fields = ('id', 'fecha_detalle_sala', 'estado_detalle_sala', 'sala', 'usuario_comun')

# Clase de serialización para los registros de reportes generados
# por el usuario comun para cada una de las actividades resueltas
class ReporteSerializer(serializers.ModelSerializer):
    # Datos de paciente
    nombre_paciente = serializers.SerializerMethodField()
    apellido_paciente = serializers.SerializerMethodField()
    correo_paciente = serializers.SerializerMethodField()
    celular_paciente = serializers.SerializerMethodField()
    edad_paciente = serializers.SerializerMethodField()
    direccion_paciente = serializers.SerializerMethodField()
    # Datos de contenido individual
    descripcion_individual = serializers.SerializerMethodField()
    respuesta = serializers.SerializerMethodField()
    tipo_contenido = serializers.SerializerMethodField()
    identificador_contenido = serializers.SerializerMethodField()
    # Datos Resultado
    tiempo_m_ = serializers.SerializerMethodField()
    tiempo_s_ = serializers.SerializerMethodField()
    observacion_ = serializers.SerializerMethodField()
    fecha_registro_resultado_ = serializers.SerializerMethodField()
    respuesta_r = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = ('id', 'titulo_reporte', 'descripcion_reporte', 'slug_reporte', 'estado_reporte', 
                  'usuario_comun', 'resultado', 'fecha_registro_reporte',
                  'fecha_edicion_reporte', 'respuesta_r',
                  'nombre_paciente', 'apellido_paciente', 'correo_paciente', 'descripcion_individual',
                  'respuesta', 'tipo_contenido', 'tiempo_m_', 'tiempo_s_', 'observacion_', 'celular_paciente',
                  'fecha_registro_resultado_', 'edad_paciente', 'direccion_paciente', 'identificador_contenido')
    
    def get_nombre_paciente(self, obj):
        return obj.resultado.paciente.nombre_usuario
    def get_apellido_paciente(self, obj):
        return obj.resultado.paciente.apellido_usuario
    def get_correo_paciente(self, obj):
        return obj.resultado.paciente.email_usuario
    def get_edad_paciente(self, obj):
        return obj.resultado.paciente.edad
    def get_celular_paciente(self, obj):
        return obj.resultado.paciente.celular
    def get_direccion_paciente(self, obj):
        return obj.resultado.paciente.direccion
    def get_descripcion_individual(self, obj):
        return obj.resultado.contenido_individual.descripcion_individual
    def get_respuesta(self, obj):
        return obj.resultado.contenido_individual.respuesta
    def get_tipo_contenido(self, obj):
        return obj.resultado.contenido_individual.tipo_contenido
    def get_identificador_contenido(self, obj):
        return obj.resultado.contenido_individual.identificador_individual
    def get_tiempo_m_(self, obj):
        return obj.resultado.tiempo_m
    def get_tiempo_s_(self, obj):
        return obj.resultado.tiempo_s
    def get_observacion_(self, obj):
        return obj.resultado.observacion
    def get_fecha_registro_resultado_(self, obj):
        return obj.resultado.fecha_registro_resultado
    def get_respuesta_r(self, obj):
        return obj.resultado.respuesta
    