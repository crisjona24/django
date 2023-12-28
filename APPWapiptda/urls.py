from django.urls import path, include
from rest_framework import routers
from .views import *
from .controlers import *

# ROUTERS
router = routers.DefaultRouter()
router.register('user', UserView, basename='user')
router.register('usuario', UsuarioView)
router.register('paciente', PacienteView)
router.register('comun', ComunView, basename='comun')
# Movimiento a la otra app
router.register('grado', GradoTDAHView, basename='grado')
router.register('dominio', DominioView)
router.register('contenido', ContenidoView)
router.register('contenido_individual', ContenidoIndividualView)
router.register('resultado', ResultadoView, basename='resultado')
router.register('resultado/solo/', ResultadoViewOnly)
router.register('curso', CursoView)
router.register('detalle_inscripcion', DetalleInscripcionCursoView)
router.register('peticion', PeticionView)
router.register('detalle_peticion', DetallePeticionView)
router.register('sala', SalaView)
router.register('detalle_sala', DetalleSalaView)
router.register('reporte', ReporteView, basename='reporte')
router.register('dominios', ListaSoloDominiosView)
router.register('contenidos', ListaSoloContenidosView)

urlpatterns = [
    path('aplicacion/', include(router.urls)),
    # Token
    path('verificar/cuenta/', verificar_email_firmado, name='verificar-cuenta'),
    path('cambiar/clave/', recuperar_cuenta, name='cambiar-clave'),
    path('verificar/codigo/cuenta/', verificar_email_recuperacion, name='nueva-clave'),
    path('registro/nueva/clave/', restablecer_clave, name='verificar-email-recuperacion'),

    ### LISTADOS PERSONALIZADOS ###
    
    ### REGISTRO ###

    path('registro_usuario/', api_user_register, name='api_user_register'),
    ############ Registro de estudiantes
    path('registro_paciente/', api_paciente_register, name='api_paciente_register'),
    ############ Registro de usuario comun
    path('registro_comun/', api_comun_register, name='api_comun_register'),
    
    ### CONTACTO ###

    ############ Envio de correo de contacto
    path('contacto/', api_enviar_contacto, name='enviar-contacto'),

    ### OBTENER DATOS ###

    ########### Obtención de datos de usuario
    path('datos/usuario/', datos_usuario, name='datos_usuario'),
    ########### Verificaciones
    path('verificar/usuario/', verificar_usuario, name='verificar_usuario'),
    ########### Obtención de slug
    path('obtener/curso/<int:id>/', obtener_slug_curso, name='obtener-slug-curso'),
    path('obtener/dominio/<str:slug>/', obtener_slug_dominio, name='obtener-slug-dominio'),
    path('obtener/contenido/<str:slug>/', obtener_slug_contenido, name='obtener-slug-contenido'),
    path('obtener/fecha/inscripcion/<int:id>/', obtener_fecha_inscripcion, name='obtener-fecha-inscripcion'),

    ### VERIFICACIONES ###
    path('verificar/inscripcion/', verificacion_inscripcion, name='verificar-inscripcion'),
    path('atender/peticion/', atender_peticion, name='atender-peticion'),
    path('atender/sala/<str:slug>/', atender_sala, name='atender-sala'),
    path('obtener/revisor/<int:id>/', obtener_nombre_revision, name='obtener-revisor'),

    ## NOTIFICACIONES ###
    path('contador/peticion/', get_contador_peticiones, name='contador-peticion'),
    path('contador/peticion/reinicio/', reset_contador_peticiones, name='reinicio-peticion'),
    path('contador/peticion/atendida/', get_contador_peticiones_atendidas, name='contador-peticion-atendida'),
    path('contador/atendido/reinicio/', reset_contador_peticiones_atendidas, name='reinicio-peticion-atendida'),
    path('contador/sala/', get_contador_salas, name='contador-sala'),
    path('contador/sala/reinicio/', reset_contador_salas, name='reinicio-sala'),
    path('contador/sala/atendida/', get_contador_salas_atendidas, name='contador-sala-atendida'),
    path('contador/sala/atendida/reinicio/', reset_contador_salas_atendidas, name='reinicio-sala-atendida'),
    path('modificar/estado/resultado/<int:id>/', modificar_estado_reporte, name='modificar-estado-resultado'),
]


'''
    path('contenidos/<str:slug>/', ContenidoListView.as_view(), name='contenidos-list'),
    path('contenidos/individuales/<str:slug>/', ContenidoIndividualListView.as_view(), name='contenidos-individuales-list'),
    path('contenidos/individuales/todo/<str:slug>/', ContenidoIndividualTodoListView.as_view(), name='contenidos-individuales-todo-list'),
    path('contenidos/individuales/nombre/<str:slug>/<str:nombre>/', CoInNombreListView.as_view(), name='contenidos-individuales-nombre-list'),
    path('peticion/pendiente/', PeticionListViewNo.as_view(), name='peticion-list-no'),
    path('peticion/atendida/', PeticionListViewSi.as_view(), name='peticion-list-si'),
    path('peticion/usuario/<int:id>/', PeticionUCListView.as_view(), name='peticion-list-usuario'),
    path('lista/pacientes/<int:id>/', PacientesListView.as_view(), name='peticion-list-usuario'),
    path('lista/resultados/<str:nombre>/', ResultadodePacienteListView2.as_view(), name='resultado-list-paciente'),
    ########### LISTA DE SALA
    path('lista/salas/<int:id>/', SalasListView.as_view(), name='sala-list-usuario'),
    ###########LISTA DE PETICION POR FECHA Y UN RANGO DE DIAS
    path('lista/peticion/fecha/<str:fecha>/<int:id>/', PeticionFechaListView.as_view(), name='peticion-list-fecha'),
    path('lista/peticion/rango/<int:rango>/<int:id>/', PeticionRangoListView.as_view(), name='peticion-list-rango'),
    path('lista/peticion/fecha/pendiente/<str:fecha>/', PeticionFechaPendienteListView.as_view(), name='peticion-list-fecha-p'),
    path('lista/peticion/rango/pendiente/<int:rango>/', PeticionRangoPendienteListView.as_view(), name='peticion-list-rango-p'),
    path('lista/peticion/fecha/atendida/<str:fecha>/', PeticionFechaAtendidaListView.as_view(), name='peticion-list-fecha-a'),
    path('lista/peticion/rango/atendida/<int:rango>/', PeticionRangoAtendidaListView.as_view(), name='peticion-list-rango-a'),
    ########### LISTA DE SALA POR FECHA
    path('lista/sala/fecha/<str:fecha>/<int:id>/', SalaFechaListView.as_view(), name='sala-list-fecha'),
    path('lista/sala/fecha/tecnico/<str:fecha>/', SalaFechaTecnicoListView.as_view(), name='sala-fecha-tecnico'),
    path('lista/sala/fecha/atendida/<str:fecha>/<int:id>/', SalaFechaAtendidaListView.as_view(), name='sala-atendida-fecha'),    
    ########### LISTA DE CURSO POR FECHA
    path('lista/curso/fecha/<str:fecha>/', CursoFechaListView.as_view(), name='curso-lista-por-fecha'),
    path('lista/curso/fecha/tecnico/<str:fecha>/', CursoFechaTecnicoListView.as_view(), name='curso-lista-por-fecha-tec'),
    ########### LISTA DE RESULTADO POR FECHA Y RANGO DE DIAS 
    path('lista/resultado/fecha/tecnico/<str:fecha>/', ResultadoFechaTecnicoListView.as_view(), name='resul-lista-por-fecha-tec'),
    path('lista/resultado/fecha/<str:fecha>/', ResultadoFechaListView.as_view(), name='resul-lista-por-fecha'),
    path('lista/resultado/rango/tecnico/<int:rango>/', ResultadoRangoTecnicoListView.as_view(), name='resul-lista-por-rango-tec'),
    path('lista/resultado/rango/<int:rango>/', ResultadoRangoListView.as_view(), name='resul-lista-por-rango'),
    ########### LISTA DE REPORTE POR FECHA Y RANGO DE DIAS
    path('lista/reporte/fecha/tecnico/<str:fecha>/', ReporteFechaTecnicoListView.as_view(), name='repor-lista-por-fecha-tec'),
    path('lista/reporte/fecha/<str:fecha>/', ReporteFechaListView.as_view(), name='repor-lista-por-fecha'),
    path('lista/reporte/rango/tecnico/<int:rango>/', ReporteRangoTecnicoListView.as_view(), name='repor-lista-por-rango-tec'),
    path('lista/reporte/rango/<int:rango>/', ReporteRangoListView.as_view(), name='repor-lista-por-rango'),
    ########### LISTA DE SALAS ATENDIDAS Y DE PACIENTE
    path('lista/salas/atendidas/<int:id>/', SalasAtendidasListView.as_view(), name='sala-list-atendidas'),
    path('lista/salas/paciente/<int:id>/', SalasPacienteListView.as_view(), name='sala-list-paciente'),
    path('busqueda/salas/<str:nombre>/', BusquedaSalasListView.as_view(), name='salas-busqueda'),
    ########### LISTA DE CURSOS
    path('lista/cursos/', CursosListView.as_view(), name='cursos-list'),
    ########### LISTA DE RESULTADO
    path('lista/resultado/usuario/<int:id>/', ResultadoListaUsuario.as_view(), name='resultado-list-usuario'),
    path('lista/reporte/usuario/<int:id>/', ListaReporteUsuarioComun.as_view(), name='reporte-list'),
    ########### LISTA Y BUSQUEDA DE REGISTROS
    path('busqueda/paciente/curso/<str:nombre>/<str:slug>/', BusquedaPacienteCursoListView.as_view(), name='paciente-curso-busqueda'),
    path('busqueda/contenido/<str:nombre>/<str:slug>/', BusquedaContenidoListView.as_view(), name='contenido-busqueda'),
    path('busqueda/curso/<str:nombre>/', BusquedaCursoListView.as_view(), name='curso-busqueda'),
    path('lista/reportes/<str:nombre>/', ReportedePacienteListView.as_view(), name='reporte-list-paciente'),
    ''' 