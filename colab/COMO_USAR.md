# Cómo hacer hablar al monito gratis (Google Colab + LivePortrait)

No necesitas una GPU propia: Google te presta una gratis (con límite de tiempo diario).

## Lo que necesitas
1. Una cuenta de Google.
2. **La foto** del mono, lo más grande y nítida posible.
3. **Un video tuyo** grabado con el celular, de 5 a 10 segundos, diciendo:
   *"Hola, ¿qué tal? Soy el monito copión"*.
   - Cara de frente, buena luz, cabeza quieta.
   - Empieza con la boca cerrada, mirando a la cámara.
   - Exagera un poco la boca y las cejas: el mono va a copiar tus gestos.

## Pasos
1. Abre el notebook en Colab de una de estas dos formas:
   - **Directo:** https://colab.research.google.com/github/Hers02/video/blob/main/colab/monito_copion_liveportrait.ipynb
     (si el repo es privado, Colab te pedirá autorizar GitHub).
   - **Manual:** descarga `monito_copion_liveportrait.ipynb` de esta carpeta y en
     Colab ve a **Archivo → Subir notebook**.
2. Menú **Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU → Guardar**.
3. Ejecuta las celdas **en orden** con el botón ▶. El Paso 2 tarda 5–10 minutos.
4. En el Paso 3 sube la foto y tu video juntos.
5. Prueba el Paso 4 (modo animales). Si falla o se ve raro, usa el Paso 5 (modo humano).
6. El Paso 6 te muestra el video y lo descarga.

## Qué esperar
- LivePortrait está entrenado con caras humanas y, en modo animales, con perros y gatos.
  Con un mono **puede salir bien o regular**; no hay garantía.
- En modo animales el resultado sale recortado alrededor de la cara.
- El video final lleva **tu voz** (la del video que grabaste).
