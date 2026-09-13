# PROJECT DOMUS — Guía de construcción de la maqueta

## Alcance obligatorio

Este paquete sirve únicamente para fabricar la **maqueta física en crudo**. Los compañeros deben cortar, perforar, ensamblar y acabar las piezas descritas en los planos. No deben instalar sensores, cableado, bombas, tuberías, placas, relés, iluminación funcional ni conexiones eléctricas.

La integración posterior elegida usa un relé individual y un módulo de cuatro
relés. Esta decisión no cambia las cotas estructurales ni autoriza perforaciones
adicionales: medir módulos y conectores antes de abrir el gabinete o las fachadas.

Los agujeros H01–H05 son pasos mecánicos vacíos y se entregan con tapones removibles. H06 y H07 pertenecen a cierres y acceso físico. H08 es solamente una marca de centro: **no se perfora** hasta medir el sensor real.

## Medida rectora

- Base total: **800 × 520 mm**.
- Escala aplicada respecto al planteamiento inicial: **80 % uniforme**.
- Todas las cotas de los planos y CSV están en milímetros.
- Ante cualquier diferencia visual, mandan las cotas del PDF y los CSV, no la perspectiva del render.

## Orden de fabricación

1. Cortar la base, faldón frontal y paneles principales.
2. Marcar los ejes X/Y desde la esquina frontal izquierda de la base.
3. Marcar y abrir solamente H01–H07; dejar H08 sin perforar.
4. Construir por separado casa, porche, invernadero, módulo Jarvis y gabinete.
5. Fabricar bancales y jardineras con insertos removibles e impermeables.
6. Presentar todos los módulos en seco y verificar posiciones antes de pegar.
7. Fijar estructura, colocar tapas/tapones y hacer control dimensional final.

## Piezas que sí forman parte de la maqueta

- Base 800 × 520 mm y faldón frontal colgante 800 × 75 × 3 mm.
- Casa abierta: piso, pared trasera, dos laterales, techo removible, divisiones y mobiliario simplificado.
- Porche: plataforma, techo, cuatro postes, pasarela, barandas y dos jardineras.
- Invernadero: marco, postes, cumbrera, dos faldones transparentes, paredes transparentes y dos bancales.
- Carcasa vacía del módulo Jarvis y gabinete transparente vacío.
- Canal técnico vacío, pasos mecánicos, tapas ciegas, insertos y zonas de corte futuro marcadas.

## Piezas que no se instalan en esta fase

- Sensores y actuadores.
- Placas electrónicas, relés, fuentes y baterías.
- Cables, conectores y soldaduras.
- Bombas, depósito funcional y mangueras.
- Paneles solares funcionales y luces funcionales.

## Tierra y recipientes

- Cada bancal del invernadero: exterior **60.8 × 224 × 42 mm**, interior útil **56.8 × 220 × 38 mm**, profundidad de tierra recomendada **30 mm**, volumen aproximado **0.375 L**.
- Cada jardinera del porche: exterior **30.4 × 108 × 26 mm**, interior útil **26.4 × 104 × 22 mm**, profundidad de tierra recomendada **18 mm**, volumen aproximado **45–50 mL**.
- Usar insertos impermeables removibles. Marcar drenajes, pero no abrirlos hasta decidir la bandeja de recuperación.

## Archivos rectores

- `PLANOS_ULTIMATE_CONSTRUCCION_MAQUETA.pdf`: diez láminas A3 de fabricación.
- `lista_corte_ultimate.csv`: piezas y cantidades.
- `materiales_ultimate.csv`: materiales, espesores y uso.
- `perforaciones_y_accesos.csv`: diámetro, posición y estado de cada abertura.
- `PLANOS_ULTIMATE_MASTER_8K.png`: imagen maestra de la implantación general.
- `PLANOS_ULTIMATE_PNG_300DPI/`: diez láminas rasterizadas para impresión.
- `modelo_3d_interactivo.html`: comprobación visual del volumen; no sustituye las cotas.

## Control antes de entregar

- Verificar base 800 × 520 mm y escuadra de diagonales.
- Confirmar casa 344 × 260 mm con frente completamente abierto.
- Confirmar invernadero 200 × 280 mm, cumbrera a Z225 y faldones de 108.1 mm a 22.3°.
- Confirmar porche 200 × 156 mm.
- Confirmar carcasas Jarvis 84 × 94.4 mm y gabinete 88 × 120 mm.
- Confirmar que los insertos de tierra salen sin desmontar la estructura.
- Confirmar que no hay componentes eléctricos instalados.
