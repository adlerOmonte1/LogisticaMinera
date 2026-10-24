"""`Producto` pasa a ser `TipoMineral` (DR-03, modelo de datos 3.1).

Se renombra el modelo en lugar de crear uno nuevo para conservar las filas y
las claves foráneas que ya apuntaban a él. El código se acota a seis
caracteres, como fija el modelo de datos.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    # Después de la migración inicial de ingresos, que todavía crea su clave
    # foránea hacia `producto`: el renombre la actualiza en lugar de romperla.
    dependencies = [
        ("catalogo", "0002_retira_cliente"),
        ("ingresos", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(old_name="Producto", new_name="TipoMineral"),
        migrations.AlterModelOptions(
            name="tipomineral",
            options={
                "ordering": ["nombre"],
                "verbose_name": "Tipo de mineral",
                "verbose_name_plural": "Tipos de mineral",
            },
        ),
        migrations.AlterModelTable(name="tipomineral", table="tipo_mineral"),
        migrations.AlterField(
            model_name="tipomineral",
            name="codigo",
            field=models.CharField(max_length=6, unique=True, verbose_name="Código"),
        ),
    ]
