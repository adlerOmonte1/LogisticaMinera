"""L7: ajuste fino de TrOCR con los recortes de los tickets.

  python 04_ajustar.py --validacion      Cinco entrenamientos; cada grupo se evalúa con el
                                         modelo que no lo vio. Nada se guarda en disco.
  python 04_ajustar.py --final           Un entrenamiento con todas las fotos; guarda el
                                         modelo candidato con el hash de sus pesos.
"""

import argparse
import hashlib
import json
import random
import time

import numpy as np
import torch
from PIL import Image, ImageFilter
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import v2 as T
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, get_linear_schedule_with_warmup

from lab import conjunto as C
from lab.evaluacion import evaluar, guardar, resumen
from lab.lector import LectorTrOCR

SEMILLA = 2026


class Aumentos:
    """Variaciones de foto que la planta producirá: inclinación, desenfoque,
    luz, contraste y encuadre del recorte."""

    def __init__(self):
        self.geometria = T.RandomAffine(degrees=4, translate=(0.03, 0.06), scale=(0.9, 1.08), shear=5, fill=255)
        self.color = T.ColorJitter(brightness=0.35, contrast=0.35, saturation=0.3, hue=0.04)

    def __call__(self, img: Image.Image) -> Image.Image:
        img = self.color(self.geometria(img))
        if random.random() < 0.3:
            img = img.filter(ImageFilter.GaussianBlur(random.uniform(0.3, 1.2)))
        if random.random() < 0.2:
            img = img.convert("L").convert("RGB")
        return img


class Muestras(Dataset):
    def __init__(self, muestras, procesador, aumentar: bool, repeticiones: int):
        self.m = muestras * repeticiones
        self.p = procesador
        self.aumentos = Aumentos() if aumentar else None

    def __len__(self):
        return len(self.m)

    def __getitem__(self, i):
        img, etiqueta, _zona = self.m[i]
        if self.aumentos:
            img = self.aumentos(img)
        pixeles = self.p(images=img, return_tensors="pt").pixel_values[0]
        ids = self.p.tokenizer(etiqueta, padding="max_length", max_length=32, truncation=True).input_ids
        ids = [t if t != self.p.tokenizer.pad_token_id else -100 for t in ids]
        return {"pixel_values": pixeles, "labels": torch.tensor(ids)}


def fijar_semilla(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)


def entrenar(base, archivos, epocas, lr, lote):
    fijar_semilla(SEMILLA)
    procesador = TrOCRProcessor.from_pretrained(base)
    modelo = VisionEncoderDecoderModel.from_pretrained(base).cuda()
    tok = procesador.tokenizer
    modelo.config.decoder_start_token_id = modelo.generation_config.decoder_start_token_id or tok.cls_token_id
    modelo.config.pad_token_id = tok.pad_token_id
    modelo.config.eos_token_id = tok.sep_token_id
    datos = Muestras(C.muestras(archivos), procesador, aumentar=True, repeticiones=4)
    cargador = DataLoader(datos, batch_size=lote, shuffle=True, num_workers=0)
    optim = torch.optim.AdamW(modelo.parameters(), lr=lr, weight_decay=0.01)
    pasos = epocas * len(cargador)
    plan = get_linear_schedule_with_warmup(optim, int(0.1 * pasos), pasos)
    modelo.train()
    for e in range(epocas):
        total = 0.0
        for b in cargador:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                perdida = modelo(pixel_values=b["pixel_values"].cuda(), labels=b["labels"].cuda()).loss
            perdida.backward()
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            optim.step()
            plan.step()
            optim.zero_grad()
            total += perdida.item()
        if (e + 1) % 5 == 0:
            print(f"  época {e + 1}/{epocas}: pérdida {total / len(cargador):.3f}", flush=True)
    modelo.eval()
    return procesador, modelo


def lector_desde(procesador, modelo):
    lector = LectorTrOCR.__new__(LectorTrOCR)
    lector.dispositivo, lector.procesador, lector.modelo, lector.haces = "cuda", procesador, modelo, 4
    lector._permitidos = {c: lector._tokens_permitidos(a) for c, a in __import__("lab.lector", fromlist=["ALFABETO"]).ALFABETO.items()}
    return lector


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="microsoft/trocr-base-handwritten")
    p.add_argument("--epocas", type=int, default=20)
    p.add_argument("--lr", type=float, default=3e-5)
    p.add_argument("--lote", type=int, default=8)
    p.add_argument("--validacion", action="store_true")
    p.add_argument("--final", action="store_true")
    p.add_argument("--nombre", default="trocr-ticket-v1")
    p.add_argument("--sufijo", default="", help="distingue una corrida de validación de otra")
    args = p.parse_args()
    particion = C.particion()
    etiqueta = f"{args.base.split('/')[-1]}-ajustado{args.sufijo}"

    if args.validacion:
        filas, tiempos, por_grupo = [], [], {}
        for g in sorted(set(particion.values())):
            inicio = time.time()
            entrena = sorted(a for a, k in particion.items() if k != g)
            prueba = sorted(a for a, k in particion.items() if k == g)
            print(f"Grupo {g}: entrena con {len(entrena)} fotos, evalúa {len(prueba)}", flush=True)
            proc, modelo = entrenar(args.base, entrena, args.epocas, args.lr, args.lote)
            f, t = evaluar(lector_desde(proc, modelo), prueba, etiqueta)
            por_grupo[g] = resumen(f, t)
            print(f"  {json.dumps(por_grupo[g], ensure_ascii=False)} ({time.time() - inicio:.0f} s)", flush=True)
            filas += f
            tiempos += t
            del modelo
            torch.cuda.empty_cache()
        guardar(filas, f"{etiqueta}-validacion-cruzada")
        total = resumen(filas, tiempos)
        (C.DATOS / "resultados" / f"{etiqueta}-validacion-cruzada.json").write_text(
            json.dumps({"total": total, "por_grupo": por_grupo, "parametros": vars(args)}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        print("TOTAL", json.dumps(total, ensure_ascii=False))

    if args.final:
        proc, modelo = entrenar(args.base, sorted(particion), args.epocas, args.lr, args.lote)
        destino = C.DATOS / "modelos" / args.nombre
        modelo.save_pretrained(destino)
        proc.save_pretrained(destino)
        pesos = next(destino.glob("*.safetensors"))
        huella = hashlib.sha256(pesos.read_bytes()).hexdigest()
        (destino / "VERSION").write_text(f"{args.nombre}+sha256:{huella[:12]}\n", encoding="utf-8")
        print(f"Modelo guardado en {destino} ({args.nombre}+sha256:{huella[:12]})")


if __name__ == "__main__":
    main()
