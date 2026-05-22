# Grúa Torre de Control Dual (Físico y Web)

Bienvenido al repositorio oficial del proyecto **Grúa Torre**, un sistema electrónico y de software que permite operar una grúa en escala a través de joysticks físicos o mediante un panel de control accesible vía Wi-Fi desde cualquier navegador (PC o Teléfono móvil).

## 🚀 Cómo funciona
El sistema está compuesto por el trabajo en equipo de dos microcontroladores:
- **Arduino Nano:** Actúa como el músculo. Lee tres joysticks analógicos y controla directamente el movimiento de los motores (2x DC y 1x Stepper) mediante los drivers de potencia. 
- **ESP32:** Actúa como el cerebro en red. Se conecta a tu Wi-Fi y levanta una página web con botones interactivos. Cuando oprimes un botón web, el ESP32 envía un carácter simple (como 'F', 'B', 'U') a través de un cable serial (UART) al Arduino, quien de inmediato ejecuta la orden en el motor correspondiente.

Todo el código está diseñado de forma **no bloqueante**, permitiendo operar varios motores a la vez de forma muy fluida.

---

## 💻 Instrucciones de Ejecución (Puesta en Marcha)

### 1. Configurar el Arduino Nano
- Abre la carpeta `grua_arduino` y ejecuta el archivo `.ino` en **Arduino IDE**.
- Revisa el menú *Herramientas > Gestor de Librerías* y asegúrate de tener instalada la librería `AccelStepper`.
- Conecta el Arduino, compila el proyecto y súbelo.

### 2. Configurar el ESP32
- Abre **Thonny IDE** y conecta tu ESP32.
- Abre el archivo `boot.py`. Busca las variables `WIFI_SSID` y `WIFI_PASSWORD` y reemplázalas por el nombre y contraseña real de tu red de internet.
- Sube los archivos `boot.py` y `main.py` a la memoria interna del ESP32.

### 3. Operación en el Mundo Real
Debido a que hemos implementado un menú inteligente en `boot.py` para protección de desarrollo, **no uses el botón verde "Run" (Reproducir)** en Thonny para operar la grúa (esto tirará un error de "Acceso Denegado"). Sigue estos pasos:
1. **Desconecta** la placa de Thonny IDE usando el botón "Stop/Restart Backend".
2. Presiona el pequeño botón físico **EN (Reset)** en el ESP32. También puedes usar un enchufe o batería portátil y funcionará de manera autónoma.
3. Si estás viendo la consola (Monitor Serie), verás el menú de 5 segundos, y luego de conectarse te dará la IP de tu servidor, por ejemplo: `http://192.168.1.15`.
4. Abre esa IP en el navegador de tu computadora o teléfono móvil, ¡y controla tu grúa!

---

## 📜 Historial de Cambios y Documentación Técnica
Para conocer la topología técnica, qué hace cada Pin, cómo funciona el protocolo Serial y revisar el registro completo de qué implementé, qué días y en qué consistió cada fase y *commit* de Git a lo largo del proyecto, por favor ingresa al archivo OpenSpec:

👉 **[Ver OpenSpec.md (Arquitectura y Registro de Commits)](OpenSpec.md)**

👉 **[Ver Requirements.md (Componentes Hardware y Software Adicionado)](Requirements.md)**
