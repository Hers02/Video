# Video
## Hacer hablar una foto gratis

Guía: [`colab/COMO_USAR.md`](colab/COMO_USAR.md) — notebook de Google Colab con LivePortrait.

## Videos

- `videos/monito_copion_v2.mp4` — misma idea con voz humana de IA (Chatterbox, código abierto); audio en `videos/voz_monito_copion.mp3`.
- `videos/monito_copion.mp4` — el monito copión diciendo "¡Hola! ¿Qué tal? Soy el monito copión."
  Hecho gratis, sin APIs pagas: voz con `espeak-ng` (subida de tono con `ffmpeg`) y boca animada
  según el volumen del audio con `scripts/hablar_animal.py` (OpenCV).
- `videos/monito_copion_v3_liveportrait.mp4` — versión con LivePortrait (red neuronal, modo humano, en CPU):
  boca que se abre de forma realista con la voz, parpadeos y movimiento de cabeza.
  Script: `scripts/hablar_liveportrait.py` (se ejecuta dentro de una copia de
  [LivePortrait](https://github.com/KwaiVGI/LivePortrait)).

### Créditos de imágenes
- `videos/macaco_frente_fuente.jpg` y el video v3: foto "Macaca fascicularis looking at the observer front view
  at bust length" por **Basile Morin**, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), vía
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Macaca_fascicularis_looking_at_the_observer_front_view_at_bust_length.jpg).
  El video v3 es una obra derivada y se comparte bajo la misma licencia.
