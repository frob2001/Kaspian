# Kaspian

Kaspian es un asistente personal visual para escritorio, pensado para funcionar primero en PC Linux y luego desplegarse en Raspberry Pi 5 con 8 GB de RAM. La primera versión de este repositorio es local-first, fullscreen, con UI tipo smart display, memoria persistente en SQLite, integración local con Ollama, cámara en vivo, modo texto manual y la arquitectura lista para voz continua y reconocimiento facial.

## Estado del proyecto

La base entregada prioriza una Fase 1 ejecutable:

- UI PySide6 fullscreen con reloj, fecha, calendario, estado global, transcripciones, cámara, panel de persona y panel musical.
- Persistencia SQLite con conversaciones, memorias, preferencias, personas, imágenes, embeddings, estado y comandos.
- Activación por nombre `Kaspian` usando una heurística sencilla.
- Integración con Ollama por HTTP local.
- Memoria básica con heurísticas conservadoras.
- Control local de Spotify con `playerctl`.
- Captura continua de cámara.
- Stubs funcionales para escucha continua, STT y TTS.
- Flujo visual preparado para registrar personas desconocidas.

## Arquitectura

```text
assistant_app/
  README.md
  requirements.txt
  .env.example
  .gitignore
  main.py
  launcher.py

  config/
  ui/
  voice/
  vision/
  brain/
  control/
  storage/
  services/
  data/
  assets/
  scripts/
  tests/
```

## Módulos principales

- `config/`: carga y validación de entorno, logging.
- `ui/`: ventana principal, dashboard y widgets.
- `voice/`: detector de activación, captura de audio, STT, TTS y escucha pasiva.
- `vision/`: cámara, detección de rostros, matching y registro de personas.
- `brain/`: prompts, contexto, memoria, cliente Ollama y orquestación.
- `control/`: Spotify, apps y acciones básicas del sistema.
- `storage/`: SQLite, modelos y migraciones.
- `services/`: reloj/fecha, almacenamiento de imágenes y bus de eventos.

## Requisitos del sistema

### PC Linux

- Python 3.11+
- `ffmpeg`
- `espeak-ng`
- `playerctl`
- dependencias de compilación para `face_recognition` si se desea reconocimiento facial completo

### Raspberry Pi 5

- Raspberry Pi OS 64-bit
- 8 GB RAM recomendados
- refrigeración activa sugerida si se usa cámara + Ollama + STT simultáneamente

## Instalación en PC

```bash
cd assistant_app
chmod +x scripts/setup_pc.sh scripts/run_dev.sh
./scripts/setup_pc.sh
```

## Instalación en Windows

Para una primera prueba local en Windows, usa PowerShell y una configuración ligera:

```powershell
cd assistant_app
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
.\scripts\run_windows.ps1
```

La preparación para Windows deja por defecto:

- `FULLSCREEN=false`
- `VOICE_ALWAYS_ON=false`
- `TTS_ENABLED=false`
- `FACE_RECOGNITION_ENABLED=false`

Así puedes validar UI, Ollama, SQLite, input manual, cámara básica y flujo general antes de pasar a Linux.

Si quieres soporte facial completo en Linux, instala también paquetes base para `dlib` y OpenCV:

```bash
sudo apt update
sudo apt install -y build-essential cmake python3-dev libopenblas-dev liblapack-dev
```

## Instalación en Raspberry Pi

```bash
cd assistant_app
chmod +x scripts/setup_pi.sh scripts/run_pi.sh
./scripts/setup_pi.sh
```

El script instala:

- Python y herramientas de build
- `ffmpeg`
- `espeak-ng`
- `playerctl`
- librerías de audio y OpenCV

## Instalación de Ollama

Consulta primero la guía oficial de Ollama para tu sistema, luego:

```bash
ollama serve
ollama pull gemma3:1b
ollama run gemma3:1b
```

Variables recomendadas:

```env
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:1b
```

En Raspberry Pi, empieza con un modelo pequeño y baja módulos pesados si hace falta.

## Configuración

Copia `.env.example` a `.env` si no existe y ajusta:

```env
APP_ENV=dev
FULLSCREEN=true
ALLOW_ESC_EXIT=true
LANGUAGE=es
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:1b
OLLAMA_TIMEOUT=120
DB_PATH=data/app.db
WHISPER_MODEL=small
TTS_ENABLED=true
VOICE_ALWAYS_ON=true
ACTIVATION_NAME=Kaspian
CAMERA_ENABLED=true
FACE_RECOGNITION_ENABLED=true
SPOTIFY_CONTROL_ENABLED=true
SAVE_UNKNOWN_FACES=true
```

## Ejecución

### Desarrollo en PC

```bash
cd assistant_app
./scripts/run_dev.sh
```

### Desarrollo en Windows

```powershell
cd assistant_app
.\scripts\run_windows.ps1
```

### Raspberry Pi

```bash
cd assistant_app
./scripts/run_pi.sh
```

## Uso

### Modo texto manual

Usa el campo inferior del dashboard y escribe frases como:

- `Kaspian, qué hora es`
- `Kaspian, abre Spotify`
- `Kaspian, pausa la música`
- `Kaspian, recuerda que me gusta el jazz`

La barra espaciadora enfoca el input manual. En desarrollo, `Esc` cierra la aplicación si `ALLOW_ESC_EXIT=true`.

### Activación por nombre

Kaspian distingue entre escucha pasiva y activación directa.

- No responde si no se detecta el nombre `Kaspian`.
- Si se detecta `Kaspian`, limpia la invocación y procesa la intención.

Ejemplos válidos:

- `Kaspian`
- `Oye Kaspian`
- `Kaspian, pon Spotify`
- `Kaspian, quién soy`

### Memoria

Kaspian guarda de forma conservadora:

- preferencias explícitas
- hechos personales útiles
- relaciones entre personas
- recordatorios

La heurística inicial vive en `brain/importance_analyzer.py`.

### Reconocimiento de personas

La app abre la cámara en un hilo separado. Si `face_recognition` está disponible:

- detecta rostros
- extrae embeddings
- compara contra embeddings guardados en SQLite

Si no está disponible:

- usa Haar cascades de OpenCV para detección visual básica
- deja el matching facial avanzado desactivado sin romper la UI

### Registro de personas nuevas

Cuando se detecta un rostro desconocido y luego hay interacción directa, la app puede abrir un diálogo con:

- imagen capturada
- campo de nombre
- botones guardar u omitir

Al guardar:

- crea la persona
- copia la imagen a `data/known_faces/<nombre>/`
- adjunta embedding si existe

### Control de Spotify

El control básico depende de `playerctl` en Linux:

- abrir Spotify
- play/pause
- siguiente
- anterior
- volumen

Ejemplos:

- `Kaspian, abre Spotify`
- `Kaspian, pausa la música`
- `Kaspian, siguiente canción`
- `Kaspian, volumen 40`

## Pruebas

```bash
cd assistant_app
source .venv/bin/activate
pytest
```

Cobertura incluida:

- memoria
- cliente Ollama con mocks
- activación por nombre
- matching facial simple
- smoke test de UI

## Rendimiento y despliegue en Raspberry Pi

Para Raspberry Pi 5 con 8 GB:

- usa `gemma3:1b` o un modelo pequeño equivalente
- considera desactivar `FACE_RECOGNITION_ENABLED` si el reconocimiento facial completo es costoso
- considera desactivar `VOICE_ALWAYS_ON` durante pruebas intensivas
- usa `CAMERA_FPS` moderado
- mantén STT en modelo pequeño

Variables útiles para recortar carga:

- `CAMERA_ENABLED=false`
- `FACE_RECOGNITION_ENABLED=false`
- `VOICE_ALWAYS_ON=false`
- `TTS_ENABLED=false`

## Notas de implementación

- La UI nunca debería bloquearse por Ollama, cámara o audio.
- El pipeline de voz está desacoplado para evolucionar hacia un wake word dedicado.
- El matching facial actual usa distancia euclídea simple sobre embeddings.
- La persistencia no depende de internet ni de servicios cloud.

## Próximos pasos sugeridos

- wake word dedicado offline
- Piper TTS como reemplazo de `espeak-ng`
- embeddings semánticos para memoria relevante
- integración real con calendario
- modo kiosk y arranque automático
- mejoras de identificación de hablante
- cola de tareas asíncronas para LLM/STT/TTS
