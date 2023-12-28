from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Recuperacion)

admin.site.register(Verificacion)

admin.site.register(Usuario)

admin.site.register(UsuarioComun)

admin.site.register(Paciente)

admin.site.register(GradoTDAH)

admin.site.register(Dominio)

admin.site.register(Contenido)

admin.site.register(ContenidoIndividual)

admin.site.register(Resultado)

admin.site.register(Curso)

admin.site.register(DetalleInscripcionCurso)

admin.site.register(Peticion)

admin.site.register(DetallePeticion)

admin.site.register(Sala)

admin.site.register(DetalleSala)

admin.site.register(Reporte)
