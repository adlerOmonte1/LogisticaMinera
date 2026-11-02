"""Lectura de reconocimientos para la consulta comparativa (HU-M04-02). No escribe."""

from django.db.models import Exists, F, OuterRef, Q

from apps.reconocimiento.models import CampoReconocido, ReconocimientoTicket


class ReconocimientoRepository:
    @staticmethod
    def base():
        return ReconocimientoTicket.objects.select_related("ingreso").prefetch_related("campos")

    @classmethod
    def listar(cls, *, desde=None, hasta=None, motor=None, corregidos=None):
        qs = cls.base()
        if desde:
            qs = qs.filter(fecha_proceso__date__gte=desde)
        if hasta:
            qs = qs.filter(fecha_proceso__date__lte=hasta)
        if motor:
            qs = qs.filter(motor=motor)
        if corregidos is not None:
            # Un campo está corregido si lo leído difiere de lo confirmado, o si
            # no hubo lectura (RN-M04-10: derivado, nunca declarado).
            corregido = Exists(
                CampoReconocido.objects.filter(reconocimiento=OuterRef("pk")).filter(
                    Q(valor_reconocido__isnull=True) | ~Q(valor_reconocido=F("valor_confirmado"))
                )
            )
            qs = qs.filter(corregido if corregidos else ~corregido)
        return qs


__all__ = ["ReconocimientoRepository"]
