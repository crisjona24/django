from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Peticion
from .utils import send_peticion_notification

# Verifica el estado de cambio de la peticion y devuelve un V o F
@receiver(post_save, sender=Peticion)
def send_notification(sender, instance, **kwargs):
    # Verifica si estado_revision ha sido modificado
    if 'created' in kwargs:
        if not kwargs['created'] and instance.estado_revision:
            print("La señal post_save se ha activado")
            send_peticion_notification(instance)
    