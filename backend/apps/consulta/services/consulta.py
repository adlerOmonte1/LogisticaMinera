"""Casos de uso de M07: leer filtros, componer el detalle, el calendario, la
búsqueda de la cabecera, el inicio y los avisos, y exportar el listado.

M07 no escribe datos del dominio (RN-M07-09): la única escritura es el evento
de la exportación, por el servicio de M09 (RN-M07-17). Presenta lo que aporta
cada módulo sin recalcularlo (RN-M07-13).
"""

import calendar
from datetime import date, timedelta

from django.core.files.storage import default_storage
from django.utils import timezone

from apps.accounts.permissions import GESTION, SOLO_ADMINISTRADOR, TODOS
from apps.auditoria.repositories import EventoRepository, referencias
from apps.auditoria.serializers import EventoSerializer
from apps.consulta.repositories import ConsultaRepository, Filtros
from apps.ingresos.models import Ingreso
from apps.trazabilidad.models import LoteProceso
from apps.trazabilidad.services.recorrido import pendientes, toneladas, trazabilidad
from apps.validacion.models import ResultadoValidacion
from common.eventos import Accion, RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ErrorDeValidacionDeDominio

from . import mensajes as m

_CLAVES_BUSQUEDA = ("placa", "fecha")
_CLAVES_LISTADO = ("fecha_desde", "fecha_hasta", "tipo_mineral", "vehiculo", "titularidad", "estado", "q")


def _fecha(valor: str | None, campo: str) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ErrorDeValidacionDeDominio("Datos inválidos", codigo="ERROR_DE_VALIDACION",
                                         detalles={campo: ["Fecha con formato AAAA-MM-DD"]})


def leer_filtros(params, hoy: date) -> tuple[Filtros, bool]:
    """Devuelve los filtros y si la petición es la búsqueda por placa y fecha.

    Búsqueda y listado comparten endpoint (requerimientos funcionales de M07).
    Es búsqueda cuando llega la clave `placa` o `fecha`, aunque vacía: entonces
    exige al menos una de las dos (RN-M07-05, HU-M07-01 CA06). Sin ellas es el
    listado, que sin fechas presenta el mes en curso hasta hoy (HU-M07-02 CA08).
    D-27 lo explica."""
    busqueda = any(k in params for k in _CLAVES_BUSQUEDA)
    placa = (params.get("placa") or "").strip() or None
    fecha = _fecha(params.get("fecha"), "fecha")
    desde = _fecha(params.get("fecha_desde"), "fecha_desde") or fecha
    hasta = _fecha(params.get("fecha_hasta"), "fecha_hasta") or fecha
    if busqueda and not placa and not desde and not hasta:
        raise ErrorDeValidacionDeDominio(m.SIN_CRITERIOS, codigo="SIN_CRITERIOS")
    if desde and hasta and desde > hasta:
        raise ErrorDeValidacionDeDominio(m.RANGO_INVERSO, codigo="RANGO_INVERSO")
    if not busqueda and not desde and not hasta and not params.get("q"):
        desde, hasta = hoy.replace(day=1), hoy
    return Filtros(
        placa=placa, desde=desde, hasta=hasta,
        tipo_mineral=params.get("tipo_mineral") or None, vehiculo=params.get("vehiculo") or None,
        titularidad=params.get("titularidad") or None, estado=params.get("estado") or None,
        texto=(params.get("q") or "").strip() or None,
    ), busqueda


def fila(i: Ingreso) -> dict:
    """Una fila del listado (HU-M07-01, detalles): anulado, En proceso y sin
    respaldo se distinguen sin abrir el detalle (RNF-M07-08)."""
    return {
        "id": i.pk, "codigo": i.codigo, "fecha_hora_pesaje": i.fecha_hora_pesaje, "placa": i.vehiculo.placa,
        "tipo_vehiculo": i.vehiculo.tipo_titularidad, "tipo_mineral": i.tipo_mineral.nombre,
        "peso_bruto_tn": str(i.peso_bruto_tn),
        "peso_neto_tn": None if i.peso_neto_tn is None else str(i.peso_neto_tn),
        "pendiente_destare": i.estado == Ingreso.EN_PROCESO, "estado": i.estado,
        "estado_texto": i.get_estado_display(), "motivo_anulacion": i.motivo_anulacion or None,
        "sin_respaldo_fotografico": i.sin_respaldo_fotografico,
        "motivo_sin_respaldo": i.get_motivo_sin_respaldo_display() or None,
    }


def respaldo(ingreso: Ingreso) -> dict:
    """RN-M07-04: el registrado sin foto y el respaldo que no se puede recuperar
    son dos hechos distintos. Si el almacén falla, el detalle sigue (RNF-M07-09)."""
    if ingreso.sin_respaldo_fotografico:
        return {"tipo": "SIN_RESPALDO_FOTOGRAFICO", "motivo": ingreso.get_motivo_sin_respaldo_display(),
                "url": None}
    try:
        disponible = bool(ingreso.imagen_ticket) and default_storage.exists(ingreso.imagen_ticket.name)
    except Exception:
        disponible = False
    if not disponible:
        return {"tipo": "NO_DISPONIBLE", "mensaje": m.RESPALDO_NO_DISPONIBLE, "url": None}
    return {"tipo": "IMAGEN", "url": f"/api/v1/consulta/ingresos/{ingreso.pk}/ticket/"}


def detalle(ingreso: Ingreso, request) -> dict:
    """HU-M07-02 CA04 a CA06 y CA12: cada bloque lo aporta su módulo; el que falta
    se indica, no se omite (RN-M07-08)."""
    from apps.ingresos.serializers import IngresoSerializer  # noqa: PLC0415
    from apps.reconocimiento.serializers import ReconocimientoSerializer  # noqa: PLC0415
    from apps.validacion.serializers import ResultadoValidacionSerializer  # noqa: PLC0415

    datos = IngresoSerializer(ingreso, context={"request": request}).data
    rec = getattr(ingreso, "reconocimiento", None) if hasattr(ingreso, "reconocimiento") else None
    reconocimiento = (
        {"disponible": True, **ReconocimientoSerializer(rec, context={"request": request}).data}
        if rec is not None and rec.exito
        else {"disponible": False, "mensaje": datos["reconocimiento"]["motivo"] or m.SIN_RECONOCIMIENTO}
    )
    filas = list(ResultadoValidacion.objects.filter(ingreso=ingreso).order_by("fecha_hora", "id"))
    validaciones = ({"disponible": True, "resultados": ResultadoValidacionSerializer(filas, many=True).data}
                    if filas else {"disponible": False, "mensaje": m.SIN_VALIDACIONES})
    recorrido = trazabilidad(ingreso)
    if recorrido["lote"] is None:
        recorrido["mensaje"] = m.MINERAL_EN_CANCHA  # HU-M07-01 CA11
    eventos = list(EventoRepository.historial_de_ingreso(ingreso.pk))
    return {
        **datos,
        "respaldo": respaldo(ingreso),
        "reconocimiento": reconocimiento,
        "validaciones": validaciones,
        "trazabilidad": recorrido,
        "historial": EventoSerializer(eventos, many=True, context={"referencias": referencias(eventos)}).data,
    }


def calendario(anio: int, mes: int, dia: int | None = None) -> dict:
    """HU-M07-03: un mes por día del pesaje; los anulados no cuentan ni suman y
    los En proceso cuentan sin sumar (RN-M07-11, RN-M07-12)."""
    if not 1 <= mes <= 12:
        raise ErrorDeValidacionDeDominio("Datos inválidos", codigo="ERROR_DE_VALIDACION", detalles={"mes": ["1 a 12"]})
    ultimo = calendar.monthrange(anio, mes)[1]
    desde, hasta = date(anio, mes, 1), date(anio, mes, ultimo)
    agregados = ConsultaRepository.por_dia(desde, hasta)
    dias = []
    for n in range(1, ultimo + 1):
        a = agregados.get(date(anio, mes, n), {})
        dias.append({
            "fecha": date(anio, mes, n), "ingresos": a.get("ingresos", 0),
            "toneladas": str(a.get("toneladas") or "0.00"),
            "con_en_proceso": bool(a.get("en_proceso")), "con_anulados": bool(a.get("anulados")),
        })
    resultado = {
        "anio": anio, "mes": mes, "dias": dias,
        "resumen": {
            "ingresos": sum(d["ingresos"] for d in dias),
            "toneladas": str(sum((a.get("toneladas") or 0) for a in agregados.values()) or "0.00"),
            "dias_con_llegadas": sum(1 for d in dias if d["ingresos"]),
            "en_proceso": sum(a.get("en_proceso", 0) for a in agregados.values()),
        },
    }
    if dia:
        elegido = date(anio, mes, int(dia))
        ingresos = (ConsultaRepository.base().filter(fecha_hora_pesaje__date=elegido)
                    .order_by("fecha_hora_pesaje", "id"))
        resultado["dia"] = {"fecha": elegido, "ingresos": [fila(i) for i in ingresos],
                            "mensaje": None if ingresos else m.DIA_SIN_LLEGADAS}
    return resultado


def cabecera(texto: str) -> dict:
    """HU-M07-02 CA16 y CA17: el código, completo o sus dígitos finales, abre el
    detalle; si no corresponde a ninguno, se toma como placa."""
    texto = (texto or "").strip()
    qs = Ingreso.objects.order_by("-fecha_hora_pesaje", "-id")
    encontrado = qs.filter(codigo__iexact=texto).first()
    if encontrado is None and texto.isdigit():
        encontrado = qs.filter(codigo__endswith=f"-{texto.zfill(5)[-5:]}").first()
    if encontrado is not None:
        return {"tipo": "INGRESO", "id": encontrado.pk, "codigo": encontrado.codigo}
    return {"tipo": "PLACA", "placa": texto}


def _enlace(usuario, roles, ruta):
    """HU-M07-04 CA11: la cifra enlaza solo si el rol tiene acceso a la pantalla."""
    return ruta if usuario.tiene_rol(*roles) else None


def inicio(usuario, hoy: date) -> dict:
    """HU-M07-04 CA01 a CA05, con el criterio del calendario (RN-M07-14)."""
    semana = ConsultaRepository.por_dia(hoy - timedelta(days=6), hoy)
    de_hoy = semana.get(hoy, {})
    ultimo = (ConsultaRepository.base().filter(fecha_hora_pesaje__date=hoy).exclude(estado=Ingreso.ANULADO)
              .order_by("-fecha_hora_pesaje").first())
    en_proceso_hoy = de_hoy.get("en_proceso", 0)
    pendientes_destare = list(ConsultaRepository.base().filter(estado=Ingreso.EN_PROCESO))
    lotes = list(LoteProceso.objects.exclude(estado=LoteProceso.CERRADO).prefetch_related(
        "partes", "pasos__etapa", "ingresos__repartos__parte"))
    en_proceso_lotes = [lo for lo in lotes if lo.estado == LoteProceso.ABIERTO or pendientes(lo)]
    ingresos_hoy = de_hoy.get("ingresos", 0)
    return {
        "fecha": hoy,
        "ingresos_hoy": {
            "cantidad": ingresos_hoy,
            "ultimo": {"hora": timezone.localtime(ultimo.fecha_hora_pesaje).strftime("%H:%M"),
                       "placa": ultimo.vehiculo.placa} if ultimo else None,
            "mensaje": None if ingresos_hoy else m.SIN_INGRESOS_HOY,
            "enlace": _enlace(usuario, TODOS, "/consulta/calendario"),
        },
        "toneladas_hoy": {
            "toneladas": str(de_hoy.get("toneladas") or "0.00"), "en_proceso": en_proceso_hoy,
            "mensaje": m.SIN_CONTAR_EN_PROCESO.format(n=en_proceso_hoy) if en_proceso_hoy else None,
            "enlace": _enlace(usuario, GESTION, "/consolidacion"),
        },
        "pendientes_destare": {
            "cantidad": len(pendientes_destare),
            "placas": sorted({i.vehiculo.placa for i in pendientes_destare}),
            "enlace": _enlace(usuario, TODOS, "/ingresos/destares"),
        },
        "lotes_en_proceso": {"cantidad": len(en_proceso_lotes), "enlace": _enlace(usuario, TODOS, "/lotes")},
        "ultimos_ingresos": [fila(i) for i in ConsultaRepository.base().order_by("-fecha_hora_pesaje", "-id")[:5]],
        "ultimos_siete_dias": [
            {"fecha": hoy - timedelta(days=d),
             "toneladas": str(semana.get(hoy - timedelta(days=d), {}).get("toneladas") or "0.00")}
            for d in range(6, -1, -1)
        ],
    }


def avisos(usuario, hoy: date) -> dict:
    """HU-M07-04 CA06 a CA10: se calculan al consultarse y solo muestran lo que
    el rol puede resolver (RN-M07-15). Textos de la maqueta."""
    lista = []
    for i in ConsultaRepository.base().filter(estado=Ingreso.EN_PROCESO).order_by("fecha_hora_pesaje"):
        lista.append({"tipo": "DESTARE", "titulo": m.AVISO_DESTARE.format(codigo=i.codigo),
                      "detalle": m.AVISO_DESTARE_DETALLE.format(placa=i.vehiculo.placa, bruto=i.peso_bruto_tn),
                      "enlace": "/ingresos/destares", "ingreso": i.pk})
    justificadas = (ResultadoValidacion.objects.select_related("ingreso")
                    .filter(regla="V4", resolucion=ResultadoValidacion.JUSTIFICADA, fecha_hora__date=hoy)
                    .exclude(ingreso__estado=Ingreso.ANULADO))
    vistos = set()
    for r in justificadas:
        if r.ingreso_id in vistos:
            continue
        vistos.add(r.ingreso_id)
        lista.append({"tipo": "V4_JUSTIFICADA", "titulo": m.AVISO_V4.format(codigo=r.ingreso.codigo),
                      "detalle": m.AVISO_V4_DETALLE.format(neto=r.ingreso.peso_neto_tn),
                      "enlace": f"/consulta/ingresos/{r.ingreso_id}", "ingreso": r.ingreso_id})
    lotes = (LoteProceso.objects.filter(estado=LoteProceso.EN_RECORRIDO)
             .prefetch_related("partes", "pasos__etapa", "ingresos__repartos__parte", "bigbags"))
    for lote in lotes:
        faltan = pendientes(lote)
        if faltan:
            lista.append({"tipo": "LOTE", "titulo": lote.nombre,
                          "detalle": m.AVISO_LOTE_DETALLE.format(pasos="; ".join(faltan)),
                          "enlace": f"/lotes/{lote.pk}", "lote": lote.pk})
        elif usuario.tiene_rol(*SOLO_ADMINISTRADOR):
            lista.append({"tipo": "LOTE_LISTO", "titulo": m.AVISO_LISTO.format(nombre=lote.nombre),
                          "detalle": m.AVISO_LISTO_DETALLE.format(
                              toneladas=toneladas(lote), bigbags=sum(b.cantidad for b in lote.bigbags.all())),
                          "enlace": f"/lotes/{lote.pk}/cerrar", "lote": lote.pk})
    if usuario.tiene_rol(*GESTION):
        sin_lote = list(Ingreso.objects.computables().filter(lote__isnull=True).values_list("codigo", flat=True))
        if sin_lote:
            plantilla = m.AVISO_SIN_LOTE if len(sin_lote) == 1 else m.AVISO_SIN_LOTE_VARIOS
            lista.append({"tipo": "SIN_LOTE", "titulo": plantilla.format(n=len(sin_lote)),
                          "detalle": ", ".join(sin_lote), "enlace": "/lotes"})
    return {"cantidad": len(lista), "avisos": lista, "mensaje": None if lista else m.NADA_PENDIENTE}


class ServicioExportacion:
    """HU-M07-02 CA13 y CA14: el conjunto filtrado completo, con su evento."""

    def __init__(self, auditoria: RegistradorDeEventos = registrador_por_defecto):
        self.auditoria = auditoria

    def exportar(self, filtros: Filtros, usuario, *, ip=None):
        from apps.consulta.exportadores import csv_listado  # noqa: PLC0415

        qs = ConsultaRepository.filtrar(filtros)
        cantidad = qs.count()
        if not cantidad:
            raise ErrorDeValidacionDeDominio(m.SIN_EXPORTAR, codigo="SIN_EXPORTAR")
        self.auditoria.registrar(
            accion=Accion.EXPORTAR, entidad="Ingreso", usuario=usuario, ip=ip,
            valores_nuevos={"exportacion": "LISTADO_INGRESOS", "cantidad": cantidad,
                            "filtros": {k: (str(v) if v is not None else None) for k, v in vars(filtros).items()}},
        )
        return csv_listado.filas(qs), cantidad
