from django.core.mail import send_mail


def send_peticion_notification(peticion):
    # Enviar correo sólo al usuario_comun asociado con la peticion
    if peticion.usuario_comun:
        subject = 'Notificación de revisión de petición'
        message = ('Su petición de tipo ' + peticion.tipo_peticion + 
                   ' ha sido atendida.\n' +
                   'El motivo de la misma era: ' + peticion.motivo_peticion + 
                   '\nLa misma cuenta con un estado de : ')
        from_email = 'crioss3an@gmail.com'
        recipient_list = ['cristobal.rios@unl.edu.ec']
        send_mail(subject, message, from_email,
                  recipient_list, fail_silently=False)
