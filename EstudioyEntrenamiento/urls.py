from django.urls import path
from EstudioyEntrenamiento.views import *
from EstudioyEntrenamiento.controlers import *

urlpatterns = [
    ########### Verificaciones
    path('verificar/nivel/<str:slug>/', verificar_nivel, name='verificar_nivel'),
    path('verificar/numero/niveles/', api_nivel_contador, name='verificar-contador'),
    path('verificar/dominio/<str:slug>/', verificar_dominio, name='verificar_dominio'),
    path('verificar/contenido/<str:slug>/', verificar_contenido, name='verificar_contenido'),
    path('verificar/curso/<str:slug>/', verificar_curso, name='verificar-curso'),
    ########### Listados personalizados
    path('contenidos/<str:slug>/', ContenidoListView.as_view(), name='contenidos-list'),
    path('contenidos/individuales/<str:slug>/', ContenidoIndividualListView.as_view(), name='contenidos-individuales-list'),
    path('contenidos/individuales/todo/<str:slug>/', ContenidoIndividualTodoListView.as_view(), name='contenidos-individuales-todo-list'),
    path('contenidos/individuales/nombre/<str:slug>/<str:nombre>/', CoInNombreListView.as_view(), name='contenidos-individuales-nombre-list'),
    path('peticion/pendiente/', PeticionListViewNo.as_view(), name='peticion-list-no'),
    path('peticion/atendida/', PeticionListViewSi.as_view(), name='peticion-list-si'),
    path('peticion/usuario/<int:id>/', PeticionUCListView.as_view(), name='peticion-list-usuario'),
    path('lista/pacientes/<int:id>/', PacientesListView.as_view(), name='peticion-list-usuario'),
    path('lista/resultados/<str:nombre>/', ResultadoNomApeListView.as_view(), name='resultado-list-paciente'),
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
    path('lista/reportes/<str:nombre>/', EstudianteNomApeListView.as_view(), name='reporte-list-paciente'),

    path('lista/reportes/cedula/<str:cedula>/', ReporteCedulaListView.as_view(), name='reporte-list-cedula'),
    path('lista/resultado/cedula/<str:cedula>/', ResultadoCedulaListView.as_view(), name='resultado-list-cedula'),
    path('estudiante/cedula/<str:cedula>/<str:slug>/', EstudianteCedulaListView.as_view(), name='registro-estudiante'),
    path('lista/peticion/tipo/pendiente/<str:tipo>/', PeticionTipoPendienteListView.as_view(), name='peticion-list-tipo-p'),
    path('lista/peticion/tipo/atendida/<str:tipo>/', PeticionTipoPendienteListViewAA.as_view(), name='peticion-list-tipo-a'),
    path('lista/peticion/usuario/tipo/<str:tipo>/<int:id>/', PeticionTipo_U_ListView.as_view(), name='peticion-list-tipo-u'),



    path('verificar/peticion/<str:slug>/', verificar_peticion, name='verificar-peticion'),
    path('verificar/resultado/<str:slug>/', verificar_resultado, name='verificar-resultado'),
    path('verificar/sala/<str:slug>/', verificar_sala, name='verificar-sala'),
    path('verificar/reporte/<str:slug>/', verificar_reporte, name='verificar-reporte'),
    path('verificar/contenido/individual/<str:slug>/', verificar_contenido_individual, name='verificar_contenido_individual'),

    ########### Registros
    ############ Registro de nivel
    path('registro_nivel/', api_nivel_register, name='api_nivel_register'),
    ############ Registro de dominio
    path('registro_dominio/', api_dominio_register, name='api_dominio_register'),
    path('editar/dominio/', api_dominio_edicion, name='edicion-dominio'),
    ############ Registro de contenido
    path('registro_contenido/', api_contenido_register, name='api_contenido_register'),
    path('editar/contenido/', api_contenido_edicion, name='edicion-contenido'),
    ############ Registro de actividades
    path('registro_contenido_individual/', api_contenido_individual_register, name='registro_individual'),
    ############ Registro de curso
    path('registro_curso/', api_curso_register, name='curso-registro'),
    path('registro/curso/<int:id>/', api_curso_inscripcion, name='inscripcion-registro'),
    ############ Registro de petición
    path('registro_peticion/', api_peticion_register, name='peticion-registro'),
    ############ Registro de resultado
    path('registro_resultado/', save_resultado, name='registro-resultado'),
    ############ Registro & Edicion de sala
    path('registro_sala/', api_sala_register, name='registro-sala'),
    path('edicion_sala/', api_sala_edicion, name='edicion-sala'),
    ############ Registro de reporte
    path('registro/reporte/<int:id>/', generar_reporte_resultado, name='registro-reporte'),
    path('generar/reporte/all/', generar_reporte_all, name='registro-reporte-all'),

    ########### Cargado de contenido
    path('cargar_contenido_individual/<str:slug>/', contenido_individual, name='cargar_individual'),
    path('cargar_contenido_principal/<str:slug>/', contenido_principal, name='cargar_principal'),
    path('codigo/contenido/<int:codigo>/', obtener_contenido_individual, name='obtener-contenido-individual'),
]