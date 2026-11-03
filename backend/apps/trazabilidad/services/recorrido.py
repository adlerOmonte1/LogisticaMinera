"""Cálculos de lectura del lote: sus cargas, la etapa que sigue, los pendientes
del cierre, el resumen y la trazabilidad de un ingreso. No escriben.

Una **carga** es lo que recorre etapas: el lote —su secado común y, sin dividir,
su ruta—, cada parte, el secado propio de un ingreso tardío y la porción de ese
ingreso en cada ruta (D-26). La etapa que sigue se busca en la secuencia de la
carga, no contando pasos: los huecos son justamente lo que la regla impide
(notas de M06).
"""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from django.db.models import Sum
from django.utils import timezone

from apps.ingresos.models import Ingreso
from apps.trazabilidad.dominio import ENSACADO, ETAPAS_POR_RUTA, MOLIENDA, NOMBRE_ETAPA, SECADO, TRANSFORMAN, Ruta
from apps.trazabilidad.models import LoteProceso, ParteLote, PasoEtapa

_DOS = Decimal("0.01")


def texto_fraccion(f: Fraction) -> str:
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


@dataclass
class Carga:
    lote: LoteProceso
    parte: ParteLote | None = None
    ingreso: Ingreso | None = None

    @property
    def nombre(self) -> str:
        """Como la planta identifica la carga (RN-M06-14): el lote o la parte; la
        de un ingreso tardío, por su código."""
        if self.ingreso is not None:
            return f"{self.ingreso.codigo} → {self.parte.nombre}" if self.parte else self.ingreso.codigo
        return self.parte.nombre if self.parte else self.lote.nombre

    @property
    def dividido(self) -> bool:
        return bool(self.lote.partes.all())

    @property
    def ruta(self) -> str | None:
        if self.parte is not None:
            return self.parte.ruta
        return None if self.dividido else (self.lote.ruta or None)

    @property
    def lleva_secado(self) -> bool:
        """El secado es del lote (común) o del ingreso tardío (propio), nunca de una parte."""
        return self.parte is None

    def secuencia(self, ruta: str | None = None) -> list[str]:
        ruta = ruta or self.ruta
        return ([SECADO] if self.lleva_secado else []) + (list(ETAPAS_POR_RUTA[Ruta(ruta)]) if ruta else [])

    def pasos(self) -> dict[str, PasoEtapa]:
        return {
            p.etapa.codigo: p
            for p in self.lote.pasos.all()
            if p.parte_id == (self.parte.pk if self.parte else None)
            and p.ingreso_tardio_id == (self.ingreso.pk if self.ingreso else None)
        }

    def paso_previo_externo(self) -> PasoEtapa | None:
        """Para una parte o una porción, la etapa anterior a su ruta es el secado
        del que proviene: el común del lote o el propio del ingreso tardío."""
        if self.lleva_secado:
            return None
        return Carga(self.lote, None, self.ingreso).pasos().get(SECADO)

    def siguiente(self) -> str | None:
        hechos = self.pasos()
        return next((e for e in self.secuencia() if e not in hechos), None)

    def necesita_ruta(self) -> bool:
        """Secado hecho, lote sin dividir y sin ruta: la planta debe decidirla (RN-M06-15)."""
        return self.lleva_secado and not self.dividido and not self.lote.ruta and SECADO in self.pasos()


def secado_comun(lote: LoteProceso) -> PasoEtapa | None:
    return Carga(lote).pasos().get(SECADO)


def requiere_secado_propio(ingreso: Ingreso, lote: LoteProceso) -> bool:
    """El ingreso tardío que llegó después del secado del lote tiene el suyo (RN-M06-18)."""
    secado = secado_comun(lote)
    return bool(secado and ingreso.fecha_asignacion_lote and ingreso.fecha_asignacion_lote > secado.fecha_registro)


def es_tardio(ingreso: Ingreso, lote: LoteProceso) -> bool:
    return bool(lote.fecha_inicio_recorrido and ingreso.fecha_asignacion_lote
                and ingreso.fecha_asignacion_lote > lote.fecha_inicio_recorrido)


def ingresos_vigentes(lote: LoteProceso):
    return [i for i in lote.ingresos.all() if i.estado != Ingreso.ANULADO]


def cargas(lote: LoteProceso) -> list[Carga]:
    partes = list(lote.partes.all())
    resultado = [Carga(lote)] + [Carga(lote, p) for p in partes]
    for ingreso in ingresos_vigentes(lote):
        if requiere_secado_propio(ingreso, lote):
            resultado.append(Carga(lote, None, ingreso))
            for reparto in ingreso.repartos.all():
                if reparto.parte.lote_id == lote.pk:
                    resultado.append(Carga(lote, reparto.parte, ingreso))
    return resultado


def ya_transformado(ingreso: Ingreso, lote: LoteProceso) -> bool:
    """RN-M06-04: el mineral pasó por zarandeo o molienda en alguna parte del lote
    o, si el ingreso tiene secado propio, en alguna de sus porciones."""
    if requiere_secado_propio(ingreso, lote):
        return any(p.etapa.codigo in TRANSFORMAN and p.ingreso_tardio_id == ingreso.pk for p in lote.pasos.all())
    return any(p.etapa.codigo in TRANSFORMAN and p.ingreso_tardio_id is None for p in lote.pasos.all())


def pendientes(lote: LoteProceso) -> list[str]:
    """Lo que falta para cerrar el lote (HU-M06-05 CA02). La misma lista la ve la
    pantalla y la usa el cierre, para que no discrepen (notas de M06)."""
    if lote.estado == LoteProceso.ABIERTO:
        return ["el lote sigue abierto"]

    def falta(carga: Carga) -> str | None:
        if carga.necesita_ruta():
            return f"{carga.nombre}: definir la ruta"
        etapa = carga.siguiente()
        return None if etapa is None else f"{carga.nombre}: falta {NOMBRE_ETAPA[etapa].lower()}"

    resultado = []
    comun = Carga(lote)
    if SECADO not in comun.pasos():
        resultado.append("falta el secado del lote")
    elif not comun.dividido:
        resultado.append(falta(comun))
    for parte in lote.partes.all():
        resultado.append(falta(Carga(lote, parte)))
    for ingreso in ingresos_vigentes(lote):
        if not requiere_secado_propio(ingreso, lote):
            continue
        propio = Carga(lote, None, ingreso)
        if SECADO not in propio.pasos():
            resultado.append(f"{ingreso.codigo}: falta su secado")
        elif not propio.dividido:
            # Sin ruta del lote, el pendiente ya figura en el lote.
            resultado.append(falta(propio) if lote.ruta else None)
        else:
            for reparto in ingreso.repartos.all():
                resultado.append(falta(Carga(lote, reparto.parte, ingreso)))
    return [p for p in resultado if p]


def toneladas(lote: LoteProceso) -> Decimal:
    """RN-M06-24 y RNF-M06-03: una consulta agregada sobre los ingresos no
    anulados del lote, calculada al consultarse."""
    total = Ingreso.objects.computables().filter(lote=lote).aggregate(t=Sum("peso_neto_tn"))["t"]
    return total or Decimal("0.00")


def toneladas_de(lote: LoteProceso, parte: ParteLote | None, total: Decimal | None = None) -> Decimal:
    """Estimación (RN-M06-17): fracción por las toneladas netas del lote."""
    total = toneladas(lote) if total is None else total
    if parte is None:
        return total
    return (total * parte.numerador / parte.denominador).quantize(_DOS)


def ensacado_aproximado(lote: LoteProceso, parte: ParteLote | None = None) -> Decimal:
    total = Decimal("0.00")
    for b in lote.bigbags.all():
        if parte is None or b.parte_id == parte.pk:
            total += b.cantidad * b.peso_aproximado_tn
    return total


def resumen(lote: LoteProceso) -> dict:
    """HU-M06-05 CA06: lo estimado se señala como estimación."""
    total = toneladas(lote)
    lineas = list(lote.partes.all()) or [None]
    ensacados = [p.fecha_hora for p in lote.pasos.all() if p.etapa.codigo == ENSACADO]
    ultimo = max(ensacados) if ensacados else None
    apertura = timezone.make_aware(timezone.datetime.combine(lote.fecha_apertura, timezone.datetime.min.time()))
    partes = []
    for parte in lineas:
        carga = Carga(lote, parte)
        molienda = carga.pasos().get(MOLIENDA)
        tn = toneladas_de(lote, parte, total)
        horas = molienda.horas_molienda if molienda else None
        partes.append({
            "nombre": carga.nombre,
            "ruta": carga.ruta,
            "fraccion": texto_fraccion(parte.fraccion) if parte else "1",
            "toneladas_aproximadas": str(tn),
            "horas_molienda": None if horas is None else str(horas),
            "toneladas_por_hora": None if not horas else str((tn / horas).quantize(_DOS)),
        })
    ensacado = ensacado_aproximado(lote)
    return {
        "pendientes": pendientes(lote),
        "toneladas_registradas": str(total),
        "bigbags": sum(b.cantidad for b in lote.bigbags.all()),
        "ensacado_aproximado_tn": str(ensacado),
        "diferencia_tn": str((ensacado - total).quantize(_DOS)),
        "es_estimacion": True,
        "partes": partes,
        "horas_desde_apertura": _horas(apertura, ultimo),
        "horas_desde_inicio": _horas(lote.fecha_inicio_recorrido, ultimo),
        "ultimo_ensacado": ultimo,
    }


def _horas(desde, hasta):
    if not desde or not hasta:
        return None
    return round((hasta - desde).total_seconds() / 3600, 1)


def trazabilidad(ingreso: Ingreso) -> dict:
    """HU-M06-03: el recorrido del ingreso es el de su lote o el de las partes en
    que se repartió (RN-M06-11); la proporción se calcula sobre las etapas de su
    ruta o la unión de las rutas de sus partes, y no se calcula sin ruta
    (RN-M06-22)."""
    lote = ingreso.lote
    base = {"ingreso": ingreso.codigo, "anulado": ingreso.estado == Ingreso.ANULADO}
    if lote is None:
        return {**base, "lote": None, "mensaje": "El ingreso aún no tiene lote y no ha recorrido ninguna etapa",
                "lineas": [], "etapas_recorridas": 0, "etapas_totales": 0, "ruta_por_decidir": False,
                "proceso_completo": False}

    propio = requiere_secado_propio(ingreso, lote)
    origen = Carga(lote, None, ingreso if propio else None)
    partes = list(lote.partes.all())
    if partes:
        if propio:
            repartos = {r.parte_id for r in ingreso.repartos.all()}
            lineas = [Carga(lote, p, ingreso) for p in partes if p.pk in repartos]
        else:
            lineas = [Carga(lote, p) for p in partes]
    else:
        lineas = [origen]

    secado = origen.pasos().get(SECADO)
    detalle = []
    union: dict[str, list[bool]] = {SECADO: [secado is not None]}
    for linea in lineas:
        hechos = linea.pasos()
        etapas = []
        for codigo in ([SECADO] if not partes else []) + (list(ETAPAS_POR_RUTA[Ruta(linea.ruta)]) if linea.ruta else []):
            paso = secado if codigo == SECADO else hechos.get(codigo)
            etapas.append({"codigo": codigo, "nombre": NOMBRE_ETAPA[codigo], "completada": paso is not None,
                           "fecha_hora": paso.fecha_hora if paso else None,
                           "usuario": paso.usuario_registro.username if paso else None})
            if codigo != SECADO:
                union.setdefault(codigo, []).append(paso is not None)
        detalle.append({"nombre": linea.nombre, "ruta": linea.ruta, "etapas": etapas})

    sin_ruta = any(linea.ruta is None for linea in lineas)
    recorridas = sum(1 for marcas in union.values() if all(marcas))
    return {
        **base,
        "lote": {"id": lote.pk, "codigo": lote.codigo, "nombre": lote.nombre, "estado": lote.estado,
                 "destino": lote.destino or None, "fecha_cierre": lote.fecha_cierre},
        "secado": {"propio": propio, "completado": secado is not None,
                   "fecha_hora": secado.fecha_hora if secado else None,
                   "usuario": secado.usuario_registro.username if secado else None},
        "lineas": detalle,
        "ruta_por_decidir": sin_ruta,
        "etapas_recorridas": recorridas,
        "etapas_totales": None if sin_ruta else len(union),
        "proceso_completo": not sin_ruta and recorridas == len(union),
    }
