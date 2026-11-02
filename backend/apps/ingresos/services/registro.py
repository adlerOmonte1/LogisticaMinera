"""Casos de uso de M03: iniciar el registro, registrar, corregir, revertir la
última corrección, anular y registrar el destare. HU-M03-01 a HU-M03-04.

`ServicioIngreso` recibe sus dependencias (notas de M03): el reconocedor de M04,
el validador de M05, el generador del código, el reloj, la auditoría de M09 y el
puerto hacia M06. No importa ningún motor ni nombra ninguna regla: cambiar de
motor o añadir una regla no lo modifica (RNF-M03-12).

Cada escritura ocurre en una sola transacción, junto con su evento de
auditoría (RN-M03-15): o se persiste todo o no se persiste nada (CA12).
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Callable

from django.db import transaction
from django.utils import timezone

from apps.accounts.permissions import GESTION
from apps.catalogo.models import TipoMineral, Vehiculo
from apps.catalogo.services import vehiculos as servicio_vehiculos
from apps.ingresos.models import Ingreso
from apps.ingresos.repositories import CORRECCION, REVERSION, HistorialIngresoRepository, IngresoRepository
from apps.reconocimiento import services as reconocimiento
from apps.reconocimiento.dominio import FECHA, PESO_BRUTO, PLACA, ResultadoReconocimiento
from apps.validacion.models import ResultadoValidacion
from apps.validacion.reglas import DatosTicket
from apps.validacion.services import ResultadoValidacionDatos, ValidadorConsistencia, registrar_resultados
from common.correlativo import GeneradorCorrelativo
from common.eventos import Accion, RegistradorDeEventos
from common.excepciones import ConflictoDeConcurrencia, ErrorDeValidacionDeDominio
from common.reloj import Reloj

from . import borrador as borradores
from . import imagen as imagenes
from . import mensajes
from .lotes import PuertoLotes

CORRIGIBLES = ("placa", "fecha_hora_pesaje", "peso_bruto_tn", "tipo_mineral")
_DOS_DECIMALES = Decimal("0.01")


@dataclass(frozen=True)
class DatosConfirmados:
    """Lo que el usuario confirma en la revisión (HU-M03-01, detalles)."""

    placa: str | None = None
    fecha: date | None = None
    hora: time | None = None
    peso_bruto_tn: Decimal | None = None
    tipo_mineral: int | None = None
    justificaciones: dict | None = None


def _normalizar_placa(placa: str | None) -> str | None:
    return placa.strip().upper() if placa and placa.strip() else None


def _componer(fecha: date, hora: time) -> datetime:
    """La fecha reconocida del ticket con la hora que indica el usuario (DR-11)."""
    return timezone.make_aware(datetime.combine(fecha, hora.replace(second=0, microsecond=0)))


def _texto_peso(valor: Decimal | None) -> str | None:
    return None if valor is None else str(Decimal(valor).quantize(_DOS_DECIMALES))


def _rechazo_por_inconsistencias(
    evaluacion: ResultadoValidacionDatos, justificaciones: dict, *, mensaje_general: str | None
) -> None:
    """Rechaza si hay una regla bloqueante incumplida o una advertencia sin
    justificar (RN-M03-05, RN-M05-02, RN-M05-03), con todas las inconsistencias
    en los detalles (RN-M05-04).

    El mensaje principal: el de HU-M03-01 CA06 cuando hay una bloqueante o
    varias advertencias; el de la justificación que falta cuando es una sola
    (HU-M05-01 CA02 y CA10). En la corrección, `mensaje_general` es None y manda
    el mensaje literal de la regla incumplida (HU-M03-02 CA03). D-25 lo explica.
    """
    bloqueantes = evaluacion.bloqueantes
    sin_justificar = evaluacion.advertencias_sin_justificar(justificaciones)
    if not bloqueantes and not sin_justificar:
        return
    if bloqueantes:
        mensaje = mensaje_general or bloqueantes[0].mensaje
    elif len(sin_justificar) == 1 or mensaje_general is None:
        mensaje = sin_justificar[0].mensaje_justificacion
    else:
        mensaje = mensaje_general
    raise ErrorDeValidacionDeDominio(
        mensaje,
        codigo="INCONSISTENCIAS",
        detalles={
            "inconsistencias": [e.como_dict() for e in evaluacion.inconsistencias],
            "justificaciones_faltantes": [
                {"regla": e.regla, "mensaje": e.mensaje_justificacion} for e in sin_justificar
            ],
        },
    )


class ServicioIngreso:
    def __init__(
        self,
        *,
        fabrica_reconocedor: Callable,
        validador: ValidadorConsistencia,
        generador: GeneradorCorrelativo,
        reloj: Reloj,
        auditoria: RegistradorDeEventos,
        lotes: PuertoLotes,
    ):
        self.fabrica_reconocedor = fabrica_reconocedor
        self.validador = validador
        self.generador = generador
        self.reloj = reloj
        self.auditoria = auditoria
        self.lotes = lotes

    # ------------------------------------------------------------------ inicio

    def iniciar_registro(self, usuario, *, archivo=None, sin_foto: bool = False, motivo: str | None = None) -> dict:
        """HU-M03-01: recibe la imagen —o el motivo del registro sin foto—,
        asigna la hora de inicio y devuelve la propuesta sin persistir nada del
        ingreso (RN-M03-02, HU-M04-01 CA06)."""
        if archivo is None and not sin_foto:
            raise ErrorDeValidacionDeDominio(mensajes.SIN_IMAGEN, codigo="SIN_IMAGEN")
        motivos = dict(Ingreso.MOTIVOS_SIN_FOTO)
        if archivo is None and motivo not in motivos:
            raise ErrorDeValidacionDeDominio(
                mensajes.CAMPOS_OBLIGATORIOS,
                codigo="CAMPOS_OBLIGATORIOS",
                detalles={"campos": ["motivo_sin_respaldo"]},
            )

        if archivo is not None:
            contenido, extension = imagenes.leer_y_validar(archivo)
            inicio = self.reloj.ahora()  # al recibir la imagen (RS-M03-02)
            ruta = imagenes.guardar(contenido, extension, inicio)
            resultado = reconocimiento.reconocer(self.fabrica_reconocedor(), contenido)
        else:
            inicio = self.reloj.ahora()  # al elegir el registro sin foto
            ruta, resultado = None, None

        hora_propuesta = timezone.localtime(inicio).time().replace(second=0, microsecond=0)
        propuesta, evaluacion, vehiculo = self._propuesta(resultado, hora_propuesta, inicio)
        umbral = str(reconocimiento.umbral_vigente()) if resultado else None
        token = borradores.firmar(
            borradores.Borrador(
                usuario=usuario.pk,
                inicio=inicio,
                imagen=ruta,
                motivo_sin_respaldo=None if archivo is not None else motivo,
                reconocimiento=resultado.como_dict() if resultado else None,
                umbral=umbral,
                propuesta=[
                    {"regla": e.regla, "cumple": e.cumple, "detalle": e.detalle} for e in evaluacion.evaluadas
                ],
            )
        )
        return {
            "borrador": token,
            "hora_inicio_registro": inicio,
            "sin_respaldo_fotografico": archivo is None,
            "motivo_sin_respaldo": None if archivo is not None else motivo,
            "reconocimiento": reconocimiento.presentar(resultado) if resultado else None,
            "propuesta": {
                **propuesta,
                "hora": hora_propuesta.strftime("%H:%M"),
                "hora_es_propuesta": True,  # HU-M03-01 CA10
            },
            "vehiculo": self._vehiculo_breve(vehiculo),
            "aviso_placa": self._aviso_placa(propuesta["placa"], vehiculo),
            "inconsistencias": [e.como_dict() for e in evaluacion.inconsistencias],
            # Solo el Administrativo y el Administrador agregan un tipo de mineral
            # desde el registro (RN-M03-24); al Supervisor se le dice a quién pedirlo (CA15).
            "puede_agregar_tipo_mineral": usuario.tiene_rol(*GESTION),
            "aviso_tipo_mineral": None if usuario.tiene_rol(*GESTION) else mensajes.SUPERVISOR_SIN_ALTA_MINERAL,
        }

    def _propuesta(self, resultado: ResultadoReconocimiento | None, hora: time, momento: datetime):
        if resultado is None:
            vacio = {"placa": None, "fecha": None, "peso_bruto_tn": None}
            return vacio, ResultadoValidacionDatos(), None
        placa = _normalizar_placa(resultado.campo(PLACA).valor)
        fecha = self._fecha_o_none(resultado.campo(FECHA).valor)
        peso = self._decimal_o_none(resultado.campo(PESO_BRUTO).valor)
        vehiculo = Vehiculo.objects.filter(placa=placa).first() if placa else None
        datos = DatosTicket(
            momento_registro=momento,
            placa=placa,
            fecha_hora_pesaje=_componer(fecha, hora) if fecha else None,
            peso_bruto_tn=peso,
            tara_tn=vehiculo.tara_tn if vehiculo else None,
            capacidad_tn=vehiculo.capacidad_tn if vehiculo else None,
        )
        propuesta = {
            "placa": placa,
            "fecha": fecha.isoformat() if fecha else None,
            "peso_bruto_tn": _texto_peso(peso),
        }
        return propuesta, self.validador.validar(datos), vehiculo

    @staticmethod
    def _fecha_o_none(texto):
        try:
            return date.fromisoformat(texto) if texto else None
        except ValueError:
            return None

    @staticmethod
    def _decimal_o_none(texto):
        try:
            return Decimal(texto) if texto else None
        except Exception:
            return None

    @staticmethod
    def _vehiculo_breve(vehiculo):
        if vehiculo is None:
            return None
        return {
            "id": vehiculo.pk,
            "placa": vehiculo.placa,
            "titularidad": vehiculo.tipo_titularidad,
            "capacidad_tn": str(vehiculo.capacidad_tn),
            "tara_tn": None if vehiculo.tara_tn is None else str(vehiculo.tara_tn),
            "pendiente_destare": vehiculo.pendiente_destare,
            "activo": vehiculo.activo,
        }

    @staticmethod
    def _aviso_placa(placa, vehiculo):
        if not placa:
            return None
        if vehiculo is None:
            return mensajes.PLACA_NO_REGISTRADA.format(placa=placa)  # CA04
        if not vehiculo.activo:
            return mensajes.VEHICULO_DE_BAJA.format(placa=placa)  # CA13
        return None

    # ---------------------------------------------------------------- registro

    def registrar_ingreso(self, usuario, token: str | None, datos: DatosConfirmados, *, ip=None) -> Ingreso:
        """HU-M03-01: revalida en el servidor (RN-M05-01), asigna el código y la
        hora de fin, calcula el neto con la tara del vehículo o deja el ingreso
        En proceso, y persiste todo con su auditoría en una transacción."""
        b = borradores.leer(token, usuario)
        if b is None:
            raise ErrorDeValidacionDeDominio(mensajes.SIN_IMAGEN, codigo="SIN_IMAGEN")  # CA02

        placa = _normalizar_placa(datos.placa)
        faltan = [
            nombre
            for nombre, valor in (
                ("placa", placa),
                ("fecha", datos.fecha),
                ("hora", datos.hora),
                ("peso_bruto_tn", datos.peso_bruto_tn),
                ("tipo_mineral", datos.tipo_mineral),
            )
            if valor in (None, "")
        ]
        tipo = None
        if datos.tipo_mineral is not None:
            tipo = TipoMineral.objects.filter(pk=datos.tipo_mineral, activo=True).first()
            if tipo is None:
                faltan.append("tipo_mineral")  # inexistente o desactivado: no es elegible
        if faltan:
            raise ErrorDeValidacionDeDominio(
                mensajes.CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS", detalles={"campos": faltan}
            )

        if b.imagen:
            codigo_previo = IngresoRepository.imagen_ya_registrada(b.imagen)
            if codigo_previo:
                raise ConflictoDeConcurrencia(
                    mensajes.BORRADOR_YA_REGISTRADO.format(codigo=codigo_previo), codigo="BORRADOR_REGISTRADO"
                )

        momento = self.reloj.ahora()
        fecha_hora = _componer(datos.fecha, datos.hora)
        vehiculo = Vehiculo.objects.filter(placa=placa).first()
        evaluacion = self.validador.validar(
            DatosTicket(
                momento_registro=momento,
                placa=placa,
                fecha_hora_pesaje=fecha_hora,
                peso_bruto_tn=datos.peso_bruto_tn,
                tara_tn=vehiculo.tara_tn if vehiculo else None,
                capacidad_tn=vehiculo.capacidad_tn if vehiculo else None,
            )
        )
        justificaciones = datos.justificaciones or {}
        if vehiculo is None and not evaluacion.bloqueantes:
            raise ErrorDeValidacionDeDominio(
                mensajes.PLACA_NO_REGISTRADA.format(placa=placa),
                codigo="PLACA_NO_REGISTRADA",
                detalles={"campos": ["placa"]},
            )
        if vehiculo is not None and not vehiculo.activo:
            raise ErrorDeValidacionDeDominio(
                mensajes.VEHICULO_DE_BAJA.format(placa=placa), codigo="VEHICULO_DE_BAJA"
            )
        _rechazo_por_inconsistencias(evaluacion, justificaciones, mensaje_general=mensajes.INCONSISTENCIAS)

        with transaction.atomic():
            codigo = self.generador.siguiente(momento)
            tara = vehiculo.tara_tn
            ingreso = Ingreso(
                codigo=codigo,
                fecha_hora_pesaje=fecha_hora,
                hora_inicio_registro=b.inicio,
                hora_fin_registro=momento,
                vehiculo=vehiculo,
                tipo_mineral=tipo,
                peso_bruto_tn=datos.peso_bruto_tn,
                tara_tn=tara,
                peso_neto_tn=None if tara is None else datos.peso_bruto_tn - tara,
                usuario_registro=usuario,
                estado=Ingreso.EN_PROCESO if tara is None else Ingreso.REGISTRADO,
                sin_respaldo_fotografico=b.sin_foto,
                motivo_sin_respaldo=b.motivo_sin_respaldo or "",
            )
            if b.imagen:
                ingreso.imagen_ticket.name = b.imagen
            ingreso.save()

            if b.reconocimiento is not None:
                self._persistir_reconocimiento(ingreso, b, usuario, ip)
            registrar_resultados(
                ingreso,
                ResultadoValidacion.CONFIRMACION,
                evaluacion,
                fecha_hora=momento,
                justificaciones=justificaciones,
                propuesta=b.propuesta,
            )
            self.auditoria.registrar(
                accion=Accion.CREAR,
                entidad="Ingreso",
                id_entidad=ingreso.pk,
                usuario=usuario,
                ip=ip,
                valores_nuevos=self._instantanea(ingreso),
            )
        return ingreso

    def _persistir_reconocimiento(self, ingreso, b, usuario, ip):
        resultado = ResultadoReconocimiento.desde_dict(b.reconocimiento)
        confirmados = {
            PLACA: ingreso.vehiculo.placa,
            FECHA: timezone.localtime(ingreso.fecha_hora_pesaje).date().isoformat(),
            PESO_BRUTO: _texto_peso(ingreso.peso_bruto_tn),
        }
        rec = reconocimiento.persistir(
            ingreso, resultado, confirmados, fecha_proceso=b.inicio, umbral=Decimal(b.umbral)
        )
        self.auditoria.registrar(
            accion=Accion.RECONOCER,
            entidad="Ingreso",
            id_entidad=ingreso.pk,
            usuario=usuario,
            ip=ip,
            valores_nuevos={"reconocimiento": rec.pk, "motor": rec.motor, "version_motor": rec.version_motor,
                            "exito": rec.exito},
        )
        cambiados = {
            nombre: (resultado.campo(nombre).valor, valor)
            for nombre, valor in confirmados.items()
            if resultado.campo(nombre).valor != valor
        }
        if cambiados:
            # Una persona cambió lo que propuso el motor (modelo de datos, M09).
            self.auditoria.registrar(
                accion=Accion.CORREGIR_DATO,
                entidad="Ingreso",
                id_entidad=ingreso.pk,
                usuario=usuario,
                ip=ip,
                valores_anteriores={k: v[0] for k, v in cambiados.items()},
                valores_nuevos={k: v[1] for k, v in cambiados.items()},
            )

    @staticmethod
    def _instantanea(ingreso, campos=None) -> dict:
        valores = {
            "codigo": ingreso.codigo,
            "placa": ingreso.vehiculo.placa,
            "fecha_hora_pesaje": ingreso.fecha_hora_pesaje.isoformat(),
            "peso_bruto_tn": _texto_peso(ingreso.peso_bruto_tn),
            "tipo_mineral": ingreso.tipo_mineral_id,
            "tara_tn": _texto_peso(ingreso.tara_tn),
            "peso_neto_tn": _texto_peso(ingreso.peso_neto_tn),
            "estado": ingreso.estado,
            "sin_respaldo_fotografico": ingreso.sin_respaldo_fotografico,
        }
        return valores if campos is None else {k: valores[k] for k in campos}

    # -------------------------------------------------------------- corrección

    def corregir_ingreso(self, id_ingreso: int, cambios: dict, motivo: str, usuario, *,
                         justificaciones: dict | None = None, ip=None) -> Ingreso:
        """HU-M03-02. `cambios` admite solo los campos corregibles; lo demás que
        envíe el cliente no llega aquí (CA04, RS-M03-12)."""
        with transaction.atomic():
            ingreso = Ingreso.objects.select_for_update().select_related("vehiculo", "tipo_mineral").get(pk=id_ingreso)
            if ingreso.estado == Ingreso.ANULADO:
                raise ConflictoDeConcurrencia(mensajes.CORREGIR_ANULADO, codigo="INGRESO_ANULADO")
            if not (motivo or "").strip():
                raise ErrorDeValidacionDeDominio(mensajes.MOTIVO_CORRECCION, codigo="MOTIVO_OBLIGATORIO")
            nuevos = self._valores_corregidos(ingreso, cambios)
            if not nuevos:
                raise ErrorDeValidacionDeDominio(mensajes.SIN_CAMBIOS, codigo="SIN_CAMBIOS")
            return self._aplicar(ingreso, nuevos, motivo, usuario, justificaciones or {}, ip=ip,
                                 operacion=CORRECCION)

    def revertir_correccion(self, id_ingreso: int, motivo: str, usuario, *, correccion: int | None = None,
                            justificaciones: dict | None = None, ip=None) -> Ingreso:
        """HU-M03-02 CA12 a CA14: restaura los valores anteriores a la última
        corrección vigente, por el mismo camino y con la misma validación que una
        corrección (RN-M03-28), y deja un evento nuevo que la referencia (RN-M03-29)."""
        with transaction.atomic():
            ingreso = Ingreso.objects.select_for_update().select_related("vehiculo", "tipo_mineral").get(pk=id_ingreso)
            if ingreso.estado == Ingreso.ANULADO:
                raise ConflictoDeConcurrencia(mensajes.CORREGIR_ANULADO, codigo="INGRESO_ANULADO")
            if not (motivo or "").strip():
                raise ErrorDeValidacionDeDominio(mensajes.MOTIVO_CORRECCION, codigo="MOTIVO_OBLIGATORIO")
            ultima = HistorialIngresoRepository.ultima_correccion_vigente(ingreso.pk)
            if ultima is None:
                raise ConflictoDeConcurrencia(
                    mensajes.SIN_CORRECCION_VIGENTE.format(codigo=ingreso.codigo), codigo="SIN_CORRECCION"
                )
            if correccion is not None and correccion != ultima.pk:
                raise ConflictoDeConcurrencia(mensajes.SOLO_ULTIMA_CORRECCION, codigo="NO_ES_LA_ULTIMA")
            anteriores = ultima.valores_anteriores or {}
            restaurar = {
                "placa": anteriores.get("placa"),
                "fecha_hora_pesaje": datetime.fromisoformat(anteriores["fecha_hora_pesaje"])
                if "fecha_hora_pesaje" in anteriores else None,
                "peso_bruto_tn": Decimal(anteriores["peso_bruto_tn"]) if "peso_bruto_tn" in anteriores else None,
                "tipo_mineral": anteriores.get("tipo_mineral"),
            }
            nuevos = {k: v for k, v in restaurar.items() if k in anteriores}
            return self._aplicar(ingreso, nuevos, motivo, usuario, justificaciones or {}, ip=ip,
                                 operacion=REVERSION, revierte=ultima.pk)

    def _valores_corregidos(self, ingreso, cambios: dict) -> dict:
        """Solo lo que de verdad cambia. La fecha y la hora pueden llegar por
        separado: la que falta se toma del ingreso."""
        nuevos = {}
        placa = _normalizar_placa(cambios.get("placa"))
        if placa and placa != ingreso.vehiculo.placa:
            nuevos["placa"] = placa
        if cambios.get("fecha") or cambios.get("hora"):
            actual = timezone.localtime(ingreso.fecha_hora_pesaje)
            fecha_hora = _componer(cambios.get("fecha") or actual.date(), cambios.get("hora") or actual.time())
            if fecha_hora != ingreso.fecha_hora_pesaje:
                nuevos["fecha_hora_pesaje"] = fecha_hora
        peso = cambios.get("peso_bruto_tn")
        if peso is not None and Decimal(peso) != ingreso.peso_bruto_tn:
            nuevos["peso_bruto_tn"] = Decimal(peso)
        tipo = cambios.get("tipo_mineral")
        if tipo is not None and tipo != ingreso.tipo_mineral_id:
            nuevos["tipo_mineral"] = tipo
        return nuevos

    def _aplicar(self, ingreso, nuevos: dict, motivo: str, usuario, justificaciones: dict, *, ip,
                 operacion: str, revierte: int | None = None) -> Ingreso:
        antes = self._instantanea(ingreso)

        vehiculo = ingreso.vehiculo
        if "placa" in nuevos:
            vehiculo = Vehiculo.objects.filter(placa=nuevos["placa"]).first()
            if vehiculo is None:
                raise ErrorDeValidacionDeDominio(
                    mensajes.PLACA_NO_REGISTRADA.format(placa=nuevos["placa"]), codigo="PLACA_NO_REGISTRADA"
                )
            if not vehiculo.activo:
                raise ErrorDeValidacionDeDominio(
                    mensajes.VEHICULO_DE_BAJA.format(placa=vehiculo.placa), codigo="VEHICULO_DE_BAJA"
                )
        tipo = ingreso.tipo_mineral
        if "tipo_mineral" in nuevos:
            tipo = TipoMineral.objects.filter(pk=nuevos["tipo_mineral"], activo=True).first()
            if tipo is None:
                raise ErrorDeValidacionDeDominio(
                    mensajes.CAMPOS_OBLIGATORIOS, codigo="CAMPOS_OBLIGATORIOS", detalles={"campos": ["tipo_mineral"]}
                )
            lote = self.lotes.lote_del_ingreso(ingreso)
            if lote is not None and tipo.pk not in lote.minerales:  # RN-M03-25, DR-27
                raise ErrorDeValidacionDeDominio(
                    mensajes.MINERAL_FUERA_DEL_LOTE.format(mineral=tipo.nombre, lote=lote.nombre),
                    codigo="MINERAL_FUERA_DEL_LOTE",
                )

        # Con la misma placa se conserva la tara aplicada (D-17); con otra, la del
        # vehículo correcto, y si aún no la tiene, vuelve a En proceso (RN-M03-26).
        tara = vehiculo.tara_tn if "placa" in nuevos else ingreso.tara_tn
        fecha_hora = nuevos.get("fecha_hora_pesaje", ingreso.fecha_hora_pesaje)
        bruto = nuevos.get("peso_bruto_tn", ingreso.peso_bruto_tn)

        previas = self._justificaciones_vigentes(ingreso.pk)
        justificaciones = {**previas, **{k: v for k, v in justificaciones.items() if (v or "").strip()}}
        evaluacion = self.validador.validar(
            DatosTicket(
                momento_registro=ingreso.hora_fin_registro,
                placa=vehiculo.placa,
                fecha_hora_pesaje=fecha_hora,
                peso_bruto_tn=bruto,
                tara_tn=tara,
                capacidad_tn=vehiculo.capacidad_tn,
                excluir_ingreso=ingreso.pk,  # RN-M05-13
            )
        )
        _rechazo_por_inconsistencias(evaluacion, justificaciones, mensaje_general=None)

        ingreso.vehiculo = vehiculo
        ingreso.tipo_mineral = tipo
        ingreso.fecha_hora_pesaje = fecha_hora
        ingreso.peso_bruto_tn = bruto
        ingreso.tara_tn = tara
        ingreso.peso_neto_tn = None if tara is None else bruto - tara
        ingreso.estado = Ingreso.EN_PROCESO if tara is None else Ingreso.REGISTRADO
        ingreso.save()

        momento = self.reloj.ahora()
        registrar_resultados(
            ingreso, ResultadoValidacion.CONFIRMACION, evaluacion, fecha_hora=momento, justificaciones=justificaciones
        )
        despues = self._instantanea(ingreso)
        modificados = [k for k in despues if despues[k] != antes[k]]
        valores_nuevos = {k: despues[k] for k in modificados}
        valores_nuevos["operacion"] = operacion
        if revierte is not None:
            valores_nuevos["revierte"] = revierte
        self.auditoria.registrar(
            accion=Accion.MODIFICAR,
            entidad="Ingreso",
            id_entidad=ingreso.pk,
            usuario=usuario,
            ip=ip,
            valores_anteriores={k: antes[k] for k in modificados},
            valores_nuevos=valores_nuevos,
            motivo=motivo.strip(),
        )
        return ingreso

    @staticmethod
    def _justificaciones_vigentes(id_ingreso: int) -> dict:
        """La justificación ya dada a una advertencia sigue valiendo mientras la
        advertencia persista: corregir otro campo no obliga a escribirla otra vez."""
        vigentes = {}
        for r in ResultadoValidacion.objects.filter(
            ingreso_id=id_ingreso, resolucion=ResultadoValidacion.JUSTIFICADA
        ).order_by("id"):
            vigentes[r.regla] = r.justificacion
        return vigentes

    # --------------------------------------------------------------- anulación

    def anular_ingreso(self, id_ingreso: int, motivo: str, usuario, *, ip=None) -> Ingreso:
        """HU-M03-03. Nunca se borra (RN-M03-14): se anula con motivo y queda en
        el histórico, fuera de todo total. Si su lote todavía reúne ingresos, M06
        lo retira (RN-M03-27)."""
        with transaction.atomic():
            ingreso = Ingreso.objects.select_for_update().select_related("vehiculo").get(pk=id_ingreso)
            if ingreso.estado == Ingreso.ANULADO:
                raise ConflictoDeConcurrencia(mensajes.YA_ANULADO.format(codigo=ingreso.codigo), codigo="YA_ANULADO")
            if not (motivo or "").strip():
                raise ErrorDeValidacionDeDominio(mensajes.MOTIVO_ANULACION, codigo="MOTIVO_OBLIGATORIO")
            lote = self.lotes.lote_del_ingreso(ingreso)
            if lote is not None and lote.reune_ingresos:
                self.lotes.retirar(ingreso, usuario)
            estado_anterior = ingreso.estado
            ingreso.estado = Ingreso.ANULADO
            ingreso.motivo_anulacion = motivo.strip()
            ingreso.save(update_fields=["estado", "motivo_anulacion"])
            self.auditoria.registrar(
                accion=Accion.ANULAR,
                entidad="Ingreso",
                id_entidad=ingreso.pk,
                usuario=usuario,
                ip=ip,
                valores_anteriores={"estado": estado_anterior},
                motivo=ingreso.motivo_anulacion,
            )
        return ingreso

    # ----------------------------------------------------------------- destare

    def registrar_destare(self, id_vehiculo: int, tara_tn: Decimal | None, usuario, *,
                          fecha_destare: datetime | None = None, justificaciones: dict | None = None,
                          ip=None) -> tuple[Vehiculo, list[Ingreso]]:
        """HU-M03-04: la tara digitada (RN-M03-19) se guarda en el vehículo por el
        servicio de M02 y completa en la misma operación todos sus ingresos En
        proceso (CA07), con V2 y V4 evaluadas sobre cada uno (RN-M05-05).
        `justificaciones`: {código del ingreso: texto} para los fuera de rango."""
        if tara_tn is None:
            raise ErrorDeValidacionDeDominio(mensajes.TARA_OBLIGATORIA, codigo="TARA_OBLIGATORIA")
        ahora = self.reloj.ahora()
        fecha_destare = fecha_destare or ahora
        justificaciones = justificaciones or {}

        with transaction.atomic():
            vehiculo = Vehiculo.objects.select_for_update().get(pk=id_vehiculo)
            if vehiculo.tara_tn is not None:
                raise ConflictoDeConcurrencia(
                    servicio_vehiculos.MENSAJE_YA_TIENE_TARA.format(placa=vehiculo.placa), codigo="VEHICULO_CON_TARA"
                )
            if fecha_destare > ahora:  # RN-M03-23
                raise ErrorDeValidacionDeDominio(mensajes.DESTARE_FUTURO, codigo="DESTARE_FUTURO")
            # El bloqueo impide dos destares simultáneos del mismo vehículo con
            # taras distintas (notas de M03).
            pendientes = list(
                Ingreso.objects.select_for_update().filter(vehiculo=vehiculo, estado=Ingreso.EN_PROCESO).order_by("id")
            )
            if not pendientes:
                raise ErrorDeValidacionDeDominio(mensajes.SIN_PENDIENTES, codigo="SIN_PENDIENTES")

            evaluaciones = {}
            for ingreso in pendientes:
                evaluacion = self.validador.validar(
                    DatosTicket(
                        momento_registro=ahora,
                        placa=vehiculo.placa,
                        fecha_hora_pesaje=ingreso.fecha_hora_pesaje,
                        peso_bruto_tn=ingreso.peso_bruto_tn,
                        tara_tn=tara_tn,
                        capacidad_tn=vehiculo.capacidad_tn,
                    ),
                    solo_dependientes_de_tara=True,
                )
                evaluaciones[ingreso.pk] = evaluacion
                if evaluacion.bloqueantes:  # V2: la tara no es menor que el bruto (CA03)
                    raise ErrorDeValidacionDeDominio(
                        evaluacion.bloqueantes[0].mensaje,
                        codigo="INCONSISTENCIAS",
                        detalles={"ingreso": ingreso.codigo,
                                  "inconsistencias": [e.como_dict() for e in evaluacion.inconsistencias]},
                    )
            sin_justificar = [
                (i, e)
                for i in pendientes
                for e in evaluaciones[i.pk].advertencias_sin_justificar(
                    {e.regla: justificaciones.get(i.codigo, "") for e in evaluaciones[i.pk]}
                )
            ]
            if sin_justificar:  # V4 (CA04)
                raise ErrorDeValidacionDeDominio(
                    sin_justificar[0][1].mensaje_justificacion,
                    codigo="INCONSISTENCIAS",
                    detalles={"justificaciones_faltantes": [
                        {"ingreso": i.codigo, "regla": e.regla, "mensaje": e.mensaje_justificacion}
                        for i, e in sin_justificar
                    ]},
                )

            ids = [i.pk for i in pendientes]
            servicio_vehiculos.registrar_tara(vehiculo, tara_tn, fecha_destare, usuario, ingresos_relacionados=ids)
            for ingreso in pendientes:
                antes = self._instantanea(ingreso, ["tara_tn", "peso_neto_tn", "estado"])
                ingreso.tara_tn = tara_tn
                ingreso.peso_neto_tn = ingreso.peso_bruto_tn - tara_tn
                ingreso.estado = Ingreso.REGISTRADO
                ingreso.save(update_fields=["tara_tn", "peso_neto_tn", "estado"])
                registrar_resultados(
                    ingreso,
                    ResultadoValidacion.DESTARE,
                    evaluaciones[ingreso.pk],
                    fecha_hora=ahora,
                    justificaciones={e.regla: justificaciones.get(ingreso.codigo, "") for e in evaluaciones[ingreso.pk]},
                )
                self.auditoria.registrar(
                    accion=Accion.MODIFICAR,
                    entidad="Ingreso",
                    id_entidad=ingreso.pk,
                    usuario=usuario,
                    ip=ip,
                    valores_anteriores=antes,
                    valores_nuevos={**self._instantanea(ingreso, ["tara_tn", "peso_neto_tn", "estado"]),
                                    "operacion": "DESTARE"},
                )
        return vehiculo, pendientes
