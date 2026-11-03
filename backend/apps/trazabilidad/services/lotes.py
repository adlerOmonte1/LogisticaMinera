"""Casos de uso de M06: ciclo del lote, composición, recorrido, división, bigbags
y cierre. HU-M06-01, HU-M06-02, HU-M06-04 y HU-M06-05.

Cada operación bloquea el lote (`select_for_update`) y registra su evento en la
misma transacción (RNF-M06-04). Los eventos del lote llevan los ingresos que
afecta en `ingresos_relacionados`, con la entidad `Lote`, para que el historial
de cada ingreso los reúna (RS-M09-13, HU-M09-02 CA03).
"""

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from django.db import transaction
from django.utils import timezone

from apps.catalogo.models import TipoMineral
from apps.ingresos.models import Ingreso
from apps.trazabilidad.dominio import ENSACADO, MOLIENDA, NOMBRE_ETAPA, SECADO, Destino, Ruta
from apps.trazabilidad.models import (
    Bigbag,
    ContadorLote,
    EtapaProceso,
    LoteMineral,
    LoteProceso,
    ParteLote,
    PasoEtapa,
    RepartoIngreso,
)
from common.correlativo import GeneradorCorrelativoPorAnio
from common.eventos import Accion, RegistradorDeEventos, registrador_por_defecto
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio
from common.reloj import Reloj, reloj_del_sistema

from . import mensajes as m
from .recorrido import (
    Carga,
    ensacado_aproximado,
    es_tardio,
    pendientes,
    requiere_secado_propio,
    resumen,
    texto_fraccion,
    toneladas,
    toneladas_de,
    ya_transformado,
)

ENTIDAD = "Lote"
_DOS = Decimal("0.01")
generador_codigo = GeneradorCorrelativoPorAnio(ContadorLote, "LOT")


def leer_fraccion(valor) -> Fraction:
    """Acepta «1/3», «0.5» o «50%» y la convierte en fracción exacta (notas de M06)."""
    texto = str(valor).strip().replace(",", ".")
    try:
        if texto.endswith("%"):
            return Fraction(texto[:-1].strip()) / 100
        return Fraction(texto)
    except (ValueError, ZeroDivisionError):
        raise ErrorDeValidacionDeDominio(m.FRACCION_INVALIDA.format(fraccion=valor), codigo="FRACCION_INVALIDA")


class ServicioLote:
    def __init__(self, *, reloj: Reloj = reloj_del_sistema, auditoria: RegistradorDeEventos = registrador_por_defecto,
                 generador=generador_codigo):
        self.reloj = reloj
        self.auditoria = auditoria
        self.generador = generador

    # ---------------------------------------------------------------- comunes

    def _bloquear(self, id_lote: int) -> LoteProceso:
        return (LoteProceso.objects.select_for_update().prefetch_related(
            "partes", "pasos__etapa", "ingresos__repartos__parte", "bigbags", "lista_minerales__tipo_mineral")
            .get(pk=id_lote))

    @staticmethod
    def _no_cerrado(lote: LoteProceso) -> None:
        if lote.estado == LoteProceso.CERRADO:  # RN-M06-21
            raise ConflictoDeConcurrencia(m.LOTE_CERRADO.format(codigo=lote.codigo), codigo="LOTE_CERRADO")

    def _evento(self, lote, usuario, operacion: str, *, valores=None, anteriores=None, motivo="", ingresos=None,
                accion=Accion.MODIFICAR):
        if ingresos is None:
            ingresos = list(Ingreso.objects.filter(lote=lote).values_list("pk", flat=True))
        self.auditoria.registrar(
            accion=accion, entidad=ENTIDAD, id_entidad=lote.pk, usuario=usuario,
            valores_anteriores=anteriores, valores_nuevos={"operacion": operacion, **(valores or {})},
            motivo=motivo, ingresos_relacionados=ingresos,
        )

    @staticmethod
    def _minerales_vigentes(lote) -> dict[int, LoteMineral]:
        return {lm.tipo_mineral_id: lm for lm in lote.lista_minerales.all() if lm.fecha_retiro is None}

    # --------------------------------------------------------------- apertura

    def abrir(self, datos: dict, usuario) -> LoteProceso:
        """HU-M06-01 CA01 a CA03."""
        nombre = (datos.get("nombre") or "").strip()
        tipo = TipoMineral.objects.filter(pk=datos.get("tipo_mineral"), activo=True).first()
        apertura: date | None = datos.get("fecha_apertura")
        faltan = [c for c, v in (("nombre", nombre), ("tipo_mineral", tipo), ("fecha_apertura", apertura)) if not v]
        if faltan:
            raise ErrorDeValidacionDeDominio(m.CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS",
                                             detalles={"campos": faltan})
        if LoteProceso.objects.filter(nombre__iexact=nombre).exists():  # RN-M06-14
            raise ErrorDeValidacionDeDominio(m.NOMBRE_DUPLICADO.format(nombre=nombre), codigo="NOMBRE_DUPLICADO")
        ahora = self.reloj.ahora()
        if apertura > timezone.localtime(ahora).date():  # el día de la planta, no el de UTC
            raise ErrorDeValidacionDeDominio(m.APERTURA_FUTURA, codigo="APERTURA_FUTURA")
        with transaction.atomic():
            lote = LoteProceso.objects.create(
                codigo=self.generador.siguiente(ahora), nombre=nombre, tipo_mineral=tipo, fecha_apertura=apertura,
                usuario_registro=usuario, fecha_registro=ahora,
            )
            LoteMineral.objects.create(lote=lote, tipo_mineral=tipo, fecha_hora=ahora, usuario_registro=usuario)
            self._evento(lote, usuario, "ABRIR", accion=Accion.CREAR, ingresos=[],
                         valores={"codigo": lote.codigo, "nombre": nombre, "tipo_mineral": tipo.codigo,
                                  "fecha_apertura": apertura.isoformat()})
        return lote

    # ------------------------------------------------------------- minerales

    def agregar_mineral(self, id_lote: int, id_tipo, usuario, *, autorizacion: str = "") -> LoteProceso:
        """HU-M06-01 CA17 y CA18 (DR-27)."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._no_cerrado(lote)
            tipo = TipoMineral.objects.filter(pk=id_tipo, activo=True).first()
            if tipo is None:
                raise ErrorDeValidacionDeDominio(m.CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS",
                                                 detalles={"campos": ["tipo_mineral"]})
            if tipo.pk in self._minerales_vigentes(lote):
                raise ConflictoDeConcurrencia(m.MINERAL_YA_EN_LOTE.format(mineral=tipo.nombre), codigo="MINERAL_REPETIDO")
            self._sumar_mineral(lote, tipo, usuario, autorizacion)
        return lote

    def _sumar_mineral(self, lote, tipo, usuario, autorizacion=""):
        LoteMineral.objects.create(lote=lote, tipo_mineral=tipo, autorizacion=autorizacion,
                                   fecha_hora=self.reloj.ahora(), usuario_registro=usuario)
        self._evento(lote, usuario, "AGREGAR_MINERAL", valores={"tipo_mineral": tipo.codigo}, motivo=autorizacion)

    def quitar_mineral(self, id_lote: int, id_tipo: int, usuario) -> TipoMineral:
        """HU-M06-01 CA19 y RN-M06-23: baja lógica de la fila (D-22)."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._no_cerrado(lote)
            if lote.estado != LoteProceso.ABIERTO:
                raise ConflictoDeConcurrencia(m.QUITAR_SOLO_ABIERTO, codigo="LOTE_NO_ABIERTO")
            vigentes = self._minerales_vigentes(lote)
            fila = vigentes.get(int(id_tipo))
            if fila is None:
                raise LoteMineral.DoesNotExist
            tipo = fila.tipo_mineral
            if Ingreso.objects.filter(lote=lote, tipo_mineral=tipo).exists():
                raise ConflictoDeConcurrencia(m.MINERAL_CON_INGRESOS.format(mineral=tipo.nombre),
                                              codigo="MINERAL_CON_INGRESOS")
            if len(vigentes) == 1:
                raise ConflictoDeConcurrencia(m.CONSERVAR_UN_MINERAL, codigo="ULTIMO_MINERAL")
            fila.fecha_retiro = self.reloj.ahora()
            fila.usuario_retiro = usuario
            fila.save(update_fields=["fecha_retiro", "usuario_retiro"])
            self._evento(lote, usuario, "QUITAR_MINERAL", anteriores={"tipo_mineral": tipo.codigo})
        return tipo

    # ------------------------------------------------------------ asignación

    def asignar(self, id_lote: int, ids: list[int], usuario, *, autorizacion: str = "") -> LoteProceso:
        """HU-M06-01 CA04 a CA09, CA12, CA13, CA20 y CA21. Valida todo antes de
        escribir: o se asignan todos o ninguno."""
        if not ids:
            raise ErrorDeValidacionDeDominio(m.SELECCIONE_INGRESOS, codigo="SIN_SELECCION")
        autorizacion = (autorizacion or "").strip()
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._no_cerrado(lote)
            ingresos = list(Ingreso.objects.select_for_update().select_related("tipo_mineral").filter(pk__in=ids))
            if len(ingresos) != len(set(ids)):
                raise Ingreso.DoesNotExist
            vigentes = self._minerales_vigentes(lote)
            otros_minerales = {}
            origenes = {}
            for ingreso in ingresos:
                if ingreso.estado == Ingreso.ANULADO:  # RN-M06-03
                    raise ConflictoDeConcurrencia(m.INGRESO_ANULADO, codigo="INGRESO_ANULADO")
                if ingreso.estado == Ingreso.EN_PROCESO:  # RN-M06-13
                    raise ConflictoDeConcurrencia(m.INGRESO_EN_PROCESO.format(codigo=ingreso.codigo),
                                                  codigo="INGRESO_EN_PROCESO")
                if ingreso.lote_id and ingreso.lote_id != lote.pk:
                    origenes[ingreso.pk] = self._puede_salir(ingreso, ingreso.lote_id, [i.pk for i in ingresos])
                if ingreso.tipo_mineral_id not in vigentes:
                    otros_minerales[ingreso.tipo_mineral_id] = ingreso.tipo_mineral
            if otros_minerales and not autorizacion:  # RN-M06-02
                raise ErrorDeValidacionDeDominio(m.FALTA_AUTORIZACION, codigo="FALTA_AUTORIZACION")

            for tipo in otros_minerales.values():
                self._sumar_mineral(lote, tipo, usuario, autorizacion)
            ahora = self.reloj.ahora()
            asignados = [i for i in ingresos if i.lote_id != lote.pk]
            for ingreso in asignados:
                origen = origenes.get(ingreso.pk)
                if origen is not None:  # CA08: traslado, con constancia en ambos lotes
                    self._evento(origen, usuario, "TRASLADAR", ingresos=[ingreso.pk],
                                 valores={"ingreso": ingreso.codigo, "destino": lote.codigo})
                ingreso.lote = lote
                ingreso.fecha_asignacion_lote = ahora
                ingreso.save(update_fields=["lote", "fecha_asignacion_lote"])
            if asignados:
                self._evento(lote, usuario, "ASIGNAR", ingresos=[i.pk for i in asignados], motivo=autorizacion,
                             valores={"ingresos": [i.codigo for i in asignados],
                                      "tardios": lote.estado == LoteProceso.EN_RECORRIDO,
                                      "otro_mineral": [t.codigo for t in otros_minerales.values()],
                                      **({"origen": {i.codigo: origenes[i.pk].codigo for i in asignados
                                                     if i.pk in origenes}} if origenes else {})})
        return lote

    def _puede_salir(self, ingreso, id_origen: int, salen: list[int]) -> LoteProceso:
        """RN-M06-04: retiro o traslado solo antes del zarandeo o la molienda, y
        un lote En recorrido conserva al menos un ingreso."""
        origen = self._bloquear(id_origen)
        self._no_cerrado(origen)
        if ya_transformado(ingreso, origen):
            raise ConflictoDeConcurrencia(m.YA_TRANSFORMADO.format(codigo=ingreso.codigo), codigo="YA_TRANSFORMADO")
        if origen.estado == LoteProceso.EN_RECORRIDO:
            quedan = Ingreso.objects.filter(lote=origen).exclude(estado=Ingreso.ANULADO).exclude(pk__in=salen)
            if not quedan.exists():
                raise ConflictoDeConcurrencia(m.CONSERVAR_UN_INGRESO.format(codigo=origen.codigo),
                                              codigo="CONSERVAR_UN_INGRESO")
        return origen

    def retirar(self, id_lote: int, id_ingreso: int, usuario) -> Ingreso:
        """HU-M06-01 CA22 y CA23 (DR-29): vuelve a cancha. No se borra ningún paso:
        el secado registrado describe lo que ocurrió (D-07)."""
        with transaction.atomic():
            ingreso = Ingreso.objects.select_for_update().get(pk=id_ingreso, lote_id=id_lote)
            lote = self._puede_salir(ingreso, id_lote, [ingreso.pk])
            ingreso.lote = None
            ingreso.fecha_asignacion_lote = None
            ingreso.save(update_fields=["lote", "fecha_asignacion_lote"])
            self._evento(lote, usuario, "RETIRAR", ingresos=[ingreso.pk], valores={"ingreso": ingreso.codigo})
        return ingreso

    def retirar_por_anulacion(self, ingreso, usuario) -> None:
        """RN-M03-27 y RN-M06-03: el anulado sale del lote que todavía reúne
        ingresos. Lo invoca M03 dentro de la transacción de la anulación."""
        lote = self._bloquear(ingreso.lote_id)
        ingreso.lote = None
        ingreso.fecha_asignacion_lote = None
        ingreso.save(update_fields=["lote", "fecha_asignacion_lote"])
        self._evento(lote, usuario, "RETIRAR", ingresos=[ingreso.pk], motivo="Anulación del ingreso",
                     valores={"ingreso": ingreso.codigo})

    # -------------------------------------------------------------- recorrido

    def iniciar_recorrido(self, id_lote: int, usuario) -> LoteProceso:
        """HU-M06-01 CA10 y CA11 (RN-M06-10)."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._no_cerrado(lote)
            if lote.estado != LoteProceso.ABIERTO:
                raise ConflictoDeConcurrencia(m.YA_INICIADO.format(nombre=lote.nombre), codigo="YA_INICIADO")
            if not Ingreso.objects.filter(lote=lote).exclude(estado=Ingreso.ANULADO).exists():
                raise ConflictoDeConcurrencia(m.SIN_INGRESOS, codigo="SIN_INGRESOS")
            lote.estado = LoteProceso.EN_RECORRIDO
            lote.fecha_inicio_recorrido = self.reloj.ahora()
            lote.save(update_fields=["estado", "fecha_inicio_recorrido"])
            self._evento(lote, usuario, "INICIAR_RECORRIDO", anteriores={"estado": LoteProceso.ABIERTO},
                         valores={"estado": lote.estado, "fecha_inicio_recorrido": lote.fecha_inicio_recorrido.isoformat()})
        return lote

    def registrar_etapa(self, id_lote: int, datos: dict, usuario) -> tuple[PasoEtapa, Carga, dict]:
        """HU-M06-02. `datos`: etapa, fecha_hora, ruta, parte, ingreso, horas_molienda,
        observacion, bigbags. Devuelve el paso, su carga y lo calculado."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._exige_recorrido(lote)
            parte = self._parte(lote, datos.get("parte"))
            ingreso = None
            if datos.get("ingreso"):
                ingreso = lote.ingresos.get(pk=datos["ingreso"])
                if not requiere_secado_propio(ingreso, lote):
                    raise ErrorDeValidacionDeDominio(m.SECADO_CON_EL_LOTE.format(codigo=ingreso.codigo),
                                                     codigo="SECADO_CON_EL_LOTE")
            carga = Carga(lote, parte, ingreso)
            if carga.parte is None and carga.ingreso is None and carga.dividido and SECADO in carga.pasos():
                raise ErrorDeValidacionDeDominio(m.INDIQUE_PARTE, codigo="INDIQUE_PARTE")

            ruta = datos.get("ruta") or None
            etapa = datos.get("etapa")
            if carga.necesita_ruta() and etapa not in carga.pasos():
                # La ruta la elige el lote después del secado (RN-M06-15); la porción
                # de un ingreso tardío la sigue, no la elige.
                if carga.ingreso is not None or ruta not in Ruta.values:
                    raise ErrorDeValidacionDeDominio(m.ELIJA_RUTA, codigo="SIN_RUTA")
                etapa = etapa or carga.secuencia(ruta)[1]
            else:
                ruta = None
            etapa = etapa or carga.siguiente()
            paso = self._validar_y_guardar_paso(lote, carga, etapa, ruta, datos, usuario)
            if ruta:
                lote.ruta = ruta
                lote.save(update_fields=["ruta"])

            calculado = {}
            if etapa == MOLIENDA and paso.horas_molienda:
                tn = toneladas_de(lote, parte)
                calculado["toneladas_por_hora"] = str((tn / paso.horas_molienda).quantize(_DOS))
            if etapa == ENSACADO and datos.get("bigbags"):
                calculado["bigbags"] = self._crear_bigbags(lote, parte, datos["bigbags"], usuario)
            self._evento(lote, usuario, "ETAPA", valores={
                "etapa": etapa, "carga": carga.nombre, "fecha_hora": paso.fecha_hora.isoformat(),
                **({"ruta": ruta} if ruta else {}),
                **({"horas_molienda": str(paso.horas_molienda)} if paso.horas_molienda else {}),
            }, ingresos=[ingreso.pk] if ingreso else None)
        return paso, carga, calculado

    def _exige_recorrido(self, lote):
        self._no_cerrado(lote)
        if lote.estado == LoteProceso.ABIERTO:  # RN-M06-05
            raise ConflictoDeConcurrencia(m.LOTE_NO_INICIADO, codigo="LOTE_NO_INICIADO")

    @staticmethod
    def _parte(lote, id_parte):
        if not id_parte:
            return None
        return next(p for p in lote.partes.all() if p.pk == int(id_parte))

    def _validar_y_guardar_paso(self, lote, carga: Carga, etapa: str, ruta, datos, usuario) -> PasoEtapa:
        """RN-M06-06 a RN-M06-08: orden de la ruta, una vez por carga y fechas
        coherentes. La etapa previa se busca en la secuencia de la carga."""
        hechos = carga.pasos()
        if etapa in hechos:
            raise ConflictoDeConcurrencia(
                m.ETAPA_REPETIDA.format(etapa=NOMBRE_ETAPA[etapa], nombre=carga.nombre), codigo="ETAPA_REPETIDA")
        secuencia = carga.secuencia(ruta)
        if not any(e not in hechos for e in secuencia):
            raise ConflictoDeConcurrencia(m.SIN_ETAPAS_PENDIENTES, codigo="SIN_ETAPAS_PENDIENTES")
        if carga.lleva_secado and SECADO not in hechos and etapa != SECADO:
            raise ErrorDeValidacionDeDominio(m.ETAPA_PREVIA.format(etapa=NOMBRE_ETAPA[SECADO]), codigo="ETAPA_PREVIA")
        if etapa not in secuencia:
            raise ErrorDeValidacionDeDominio(
                m.ETAPA_FUERA_DE_RUTA.format(etapa=NOMBRE_ETAPA.get(etapa, etapa), nombre=carga.nombre),
                codigo="ETAPA_FUERA_DE_RUTA")
        posicion = secuencia.index(etapa)
        previo = hechos.get(secuencia[posicion - 1]) if posicion else carga.paso_previo_externo()
        nombre_previa = NOMBRE_ETAPA[secuencia[posicion - 1]] if posicion else NOMBRE_ETAPA[SECADO]
        if previo is None and (posicion or not carga.lleva_secado):
            raise ErrorDeValidacionDeDominio(m.ETAPA_PREVIA.format(etapa=nombre_previa), codigo="ETAPA_PREVIA")

        ahora = self.reloj.ahora()
        fecha: datetime = datos.get("fecha_hora") or ahora
        if fecha > ahora:
            raise ErrorDeValidacionDeDominio(m.ETAPA_FUTURA, codigo="ETAPA_FUTURA")
        if previo is not None and fecha < previo.fecha_hora:
            raise ErrorDeValidacionDeDominio(m.ETAPA_ANTES_DE_PREVIA.format(etapa=nombre_previa),
                                             codigo="ETAPA_ANTES_DE_PREVIA")
        if previo is None and fecha < lote.fecha_inicio_recorrido:
            raise ErrorDeValidacionDeDominio(m.ETAPA_ANTES_DEL_INICIO, codigo="ETAPA_ANTES_DEL_INICIO")
        horas = datos.get("horas_molienda")
        if horas is not None and (etapa != MOLIENDA or horas <= 0):
            raise ErrorDeValidacionDeDominio(m.HORAS_INVALIDAS, codigo="HORAS_INVALIDAS")
        return PasoEtapa.objects.create(
            lote=lote, parte=carga.parte, ingreso_tardio=carga.ingreso, etapa=EtapaProceso.objects.get(codigo=etapa),
            fecha_hora=fecha, horas_molienda=horas, observacion=datos.get("observacion") or "",
            usuario_registro=usuario, fecha_registro=ahora,
        )

    def registrar_secado_propio(self, id_lote: int, id_ingreso: int, datos: dict, usuario) -> PasoEtapa:
        """HU-M06-02 CA14 y HU-M06-04 CA09: el tardío que llegó después del secado
        del lote se seca aparte y, si el lote está dividido, se reparte entre sus
        partes con fracciones que suman la unidad (DR-20)."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._exige_recorrido(lote)
            ingreso = lote.ingresos.get(pk=id_ingreso)
            if not requiere_secado_propio(ingreso, lote):
                raise ErrorDeValidacionDeDominio(m.SECADO_CON_EL_LOTE.format(codigo=ingreso.codigo),
                                                 codigo="SECADO_CON_EL_LOTE")
            partes = list(lote.partes.all())
            reparto = []
            if partes:
                reparto = self._reparto(partes, datos.get("fracciones"))
            paso = self._validar_y_guardar_paso(lote, Carga(lote, None, ingreso), SECADO, None, datos, usuario)
            for parte, fraccion in reparto:
                RepartoIngreso.objects.create(ingreso=ingreso, parte=parte, numerador=fraccion.numerator,
                                              denominador=fraccion.denominator)
            self._evento(lote, usuario, "SECADO_PROPIO", ingresos=[ingreso.pk], valores={
                "ingreso": ingreso.codigo, "fecha_hora": paso.fecha_hora.isoformat(),
                **({"reparto": {p.nombre: texto_fraccion(f) for p, f in reparto}} if reparto else {})})
        return paso

    @staticmethod
    def _reparto(partes, fracciones) -> list:
        """Por defecto, las fracciones del lote (DR-20)."""
        if not fracciones:
            return [(p, p.fraccion) for p in partes]
        por_parte = {int(f["parte"]): leer_fraccion(f["fraccion"]) for f in fracciones}
        reparto = [(p, por_parte[p.pk]) for p in partes if por_parte.get(p.pk)]
        suma = sum((f for _, f in reparto), Fraction(0))
        if suma != 1:
            raise ErrorDeValidacionDeDominio(m.REPARTO_NO_SUMA.format(suma=texto_fraccion(suma)), codigo="REPARTO_NO_SUMA")
        return reparto

    # --------------------------------------------------------------- división

    def dividir(self, id_lote: int, partes: list[dict], usuario) -> list[ParteLote]:
        """HU-M06-04 (RN-M06-16, DR-18), en el orden de las notas de M06."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._no_cerrado(lote)
            if lote.partes.all():
                raise ConflictoDeConcurrencia(m.YA_DIVIDIDO, codigo="YA_DIVIDIDO")
            if lote.ruta or any(p.etapa.codigo != SECADO for p in lote.pasos.all()):
                raise ConflictoDeConcurrencia(m.YA_AVANZO, codigo="YA_AVANZO")
            if len(partes) > 6:
                raise ErrorDeValidacionDeDominio(m.MAXIMO_SEIS, codigo="MAXIMO_SEIS")
            if len(partes) < 2:
                raise ErrorDeValidacionDeDominio(m.MINIMO_DOS, codigo="MINIMO_DOS")
            if any(not (p.get("nombre") or "").strip() or not p.get("fraccion") or p.get("ruta") not in Ruta.values
                   for p in partes):
                raise ErrorDeValidacionDeDominio(m.CAMPOS_DE_CADA_PARTE, codigo="CAMPOS_DE_CADA_PARTE")
            nombres = [p["nombre"].strip().lower() for p in partes]
            if len(set(nombres)) != len(nombres):
                raise ErrorDeValidacionDeDominio(m.NOMBRES_REPETIDOS, codigo="NOMBRES_REPETIDOS")
            fracciones = [leer_fraccion(p["fraccion"]) for p in partes]
            if any(f <= 0 for f in fracciones):
                raise ErrorDeValidacionDeDominio(m.CAMPOS_DE_CADA_PARTE, codigo="CAMPOS_DE_CADA_PARTE")
            suma = sum(fracciones, Fraction(0))
            if suma != 1:  # exacta, sin redondeo (RNF-M06-11)
                raise ErrorDeValidacionDeDominio(m.FRACCIONES_NO_SUMAN.format(suma=texto_fraccion(suma)),
                                                 codigo="FRACCIONES_NO_SUMAN")
            creadas = [
                ParteLote.objects.create(lote=lote, nombre=p["nombre"].strip(), numerador=f.numerator,
                                         denominador=f.denominator, ruta=p["ruta"])
                for p, f in zip(partes, fracciones)
            ]
            # Un tardío que ya se secó aparte antes de la división se reparte con
            # las fracciones del lote (DR-20).
            for ingreso in lote.ingresos.all():
                if requiere_secado_propio(ingreso, lote) and not ingreso.repartos.exists():
                    for parte in creadas:
                        RepartoIngreso.objects.create(ingreso=ingreso, parte=parte, numerador=parte.numerador,
                                                      denominador=parte.denominador)
            self._evento(lote, usuario, "DIVIDIR", valores={"partes": [
                {"nombre": c.nombre, "fraccion": texto_fraccion(c.fraccion), "ruta": c.ruta} for c in creadas]})
        return creadas

    # ---------------------------------------------------------------- bigbags

    def asociar_bigbags(self, id_lote: int, datos: dict, usuario) -> dict:
        """HU-M06-02 CA11 a CA13 (RN-M06-19)."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            self._exige_recorrido(lote)
            parte = self._parte(lote, datos.get("parte"))
            if parte is None and lote.partes.all():
                raise ErrorDeValidacionDeDominio(m.INDIQUE_PARTE, codigo="INDIQUE_PARTE")
            if ENSACADO not in Carga(lote, parte).pasos():
                raise ErrorDeValidacionDeDominio(m.BIGBAGS_SIN_ENSACADO, codigo="SIN_ENSACADO")
            registro = self._crear_bigbags(lote, parte, datos, usuario)
            self._evento(lote, usuario, "BIGBAGS", valores={"carga": Carga(lote, parte).nombre, **registro})
        return registro

    def _crear_bigbags(self, lote, parte, datos: dict, usuario) -> dict:
        """El peso estimado reparte lo pendiente de ensacar; con Recalcular se
        guarda el que indica el usuario (notas de M06). Es una estimación."""
        cantidad = int(datos.get("cantidad") or 0)
        if cantidad <= 0:
            raise ErrorDeValidacionDeDominio(m.CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS",
                                             detalles={"campos": ["cantidad"]})
        recalcular = bool(datos.get("recalcular"))
        if recalcular:
            peso = datos.get("peso_aproximado_tn")
            if not peso or Decimal(str(peso)) <= 0:
                raise ErrorDeValidacionDeDominio(m.CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS",
                                                 detalles={"campos": ["peso_aproximado_tn"]})
            peso = Decimal(str(peso)).quantize(_DOS)
        else:
            pendiente = toneladas_de(lote, parte) - ensacado_aproximado(lote, parte)
            if pendiente <= 0:
                raise ErrorDeValidacionDeDominio(m.YA_ENSACADO, codigo="YA_ENSACADO")
            peso = (pendiente / cantidad).quantize(_DOS, rounding=ROUND_HALF_UP)
        Bigbag.objects.create(lote=lote, parte=parte, cantidad=cantidad, peso_aproximado_tn=peso,
                              recalculado=recalcular, fecha_hora=self.reloj.ahora(), usuario_registro=usuario)
        return {"cantidad": cantidad, "peso_aproximado_tn": str(peso), "recalculado": recalcular,
                "es_estimacion": True}

    # ----------------------------------------------------------------- cierre

    def cerrar(self, id_lote: int, destino: str | None, usuario, *, observacion: str = "") -> LoteProceso:
        """HU-M06-05 (RN-M06-20, DR-14). El permiso lo comprueba la vista."""
        with transaction.atomic():
            lote = self._bloquear(id_lote)
            if lote.estado == LoteProceso.CERRADO:
                raise ConflictoDeConcurrencia(m.YA_CERRADO, codigo="YA_CERRADO")
            if destino not in Destino.values:
                raise ErrorDeValidacionDeDominio(m.SIN_DESTINO, codigo="SIN_DESTINO")
            faltan = pendientes(lote)
            if faltan:
                raise ConflictoDeConcurrencia(m.PENDIENTES.format(pendientes="; ".join(faltan)),
                                              codigo="PENDIENTES", detalles={"pendientes": faltan})
            datos_resumen = resumen(lote)
            lote.estado = LoteProceso.CERRADO
            lote.destino = destino
            lote.observacion_cierre = (observacion or "").strip()
            lote.fecha_cierre = self.reloj.ahora()
            lote.usuario_cierre = usuario
            lote.save(update_fields=["estado", "destino", "observacion_cierre", "fecha_cierre", "usuario_cierre"])
            self._evento(lote, usuario, "CERRAR", anteriores={"estado": LoteProceso.EN_RECORRIDO},
                         valores={"estado": lote.estado, "destino": destino, "resumen": {
                             k: v for k, v in datos_resumen.items() if k not in ("pendientes", "ultimo_ensacado")}},
                         motivo=lote.observacion_cierre)
        return lote


servicio_lote = ServicioLote()

__all__ = ["ServicioLote", "es_tardio", "leer_fraccion", "servicio_lote", "toneladas"]
