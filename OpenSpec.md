# Especificación de Arquitectura - Grúa Torre Dual (OpenSpec)

Este documento detalla la arquitectura de software y hardware para el proyecto de control dual (Web y Físico) de la Grúa Torre.

## 1. Topología del Sistema
El sistema se compone de dos microcontroladores operando de manera cooperativa:
- **ESP32 (MicroPython):** Actúa como interfaz de conectividad Wi-Fi y servidor web asíncrono. Sirve el panel de control HTML/JS y envía las órdenes del usuario vía UART.
- **Arduino Nano (C++):** Actuador principal. Lee los joysticks físicos, escucha el puerto UART y coordina el movimiento de los motores de forma no bloqueante.

---

## 2. Mapa de Conexiones (Pinout)

### Comunicación ESP32 <-> Arduino Nano
| Dispositivo A | Pin | Dispositivo B | Pin | Función |
|---------------|-----|---------------|-----|---------|
| **ESP32**     | GPIO 17 (TX) | **Arduino Nano** | D0 (RX) | Transmisión de comandos (UART 9600 bps) |
| **ESP32**     | GND | **Arduino Nano** | GND | Referencia de tierra común (Obligatoria) |

### Control de Motores y Entradas (Arduino Nano)
| Componente | Pin Arduino | Función |
|------------|-------------|---------|
| **Joystick Carro** | A0 | Control analógico del Carro (Adelante/Atrás) |
| **Joystick Elevación** | A1 | Control analógico de Elevación (Subir/Bajar) |
| **Joystick Giro** | A2 | Control analógico de Giro (Izquierda/Derecha) |
| **TB6612FNG (Motor A)** | D2 | AIN1 - Dirección Carro |
| | D4 | AIN2 - Dirección Carro |
| | D3 | PWMA - Velocidad Carro (PWM) |
| **TB6612FNG (Motor B)** | D7 | BIN1 - Dirección Elevación |
| | D8 | BIN2 - Dirección Elevación |
| | D5 | PWMB - Velocidad Elevación (PWM) |
| **TB6612FNG (STBY)** | 5V | Habilitación de driver (High) |
| **DRV8825 (Nema 17)**| D9 | STEP - Señal de pasos para Giro |
| | D10 | DIR - Señal de dirección para Giro |

---

## 3. Protocolo de Comunicación Serial

La comunicación fluye en una dirección del ESP32 al Arduino a **9600 baudios (8N1)**. Se basa en el envío de caracteres ASCII simples, lo que reduce la carga de procesamiento y hace más robusto el _parsing_.

| Carácter ASCII | Acción Web Correspondiente | Motor/Eje Afectado |
|:---:|---|---|
| `F` | Adelante (Forward) | Carro (DC) |
| `B` | Atrás (Backward) | Carro (DC) |
| `U` | Subir (Up) | Elevación (DC) |
| `D` | Bajar (Down) | Elevación (DC) |
| `L` | Izquierda (Left) | Giro (Stepper) |
| `R` | Derecha (Right) | Giro (Stepper) |
| `S` | Stop | Todos los motores (Comando Web) |

### Seguridad (Watchdog de Movimiento)
El Arduino implementa un *timeout* de 500 ms. Si no recibe un comando serial válido en ese tiempo, la orden web en curso se revierte internamente a `S` (Stop). 
Para evitar que el movimiento se detenga mientras el usuario presiona el botón sostenidamente en la web, la interfaz HTML envía el comando de forma activa cada 200 ms (*polling* persistente). En caso de desconexión Wi-Fi, el ESP32 deja de emitir UART y el Arduino detiene inmediatamente el movimiento sin dejar un motor activo de forma insegura.

---

## 4. Endpoints del Servidor Web (ESP32)

El ESP32 utiliza `uasyncio` para atender peticiones web sin bloquear el bucle del procesador.

### 1. Interfaz Principal
- **Endpoint:** `GET /` o `GET /index.html`
- **Descripción:** Entrega la interfaz de usuario en un archivo embebido (HTML, CSS y JS).
- **Respuesta:** `200 OK` (`text/html`).

### 2. Receptor de Comandos (API)
- **Endpoint:** `GET /cmd?action=<char>`
- **Descripción:** Recibe la intención de movimiento emitido por la web al presionar o soltar un botón. Implementado usando `fetch()` para evitar la recarga de página.
- **Parámetro `action`:** Uno de los caracteres del protocolo (ej. `F`, `B`, `S`).
- **Respuesta:** `200 OK` (`text/plain`).
- **Comportamiento:** El ESP32 retransmite inmediatamente el carácter recibido a través del GPIO 17 mediante la clase UART.

---

## 5. Lógica de Control Mixto (Joysticks + Web)

El programa del Arduino Nano está diseñado de forma **no bloqueante**.
1. **Lectura Asíncrona:** Constantemente procesa la posición de los joysticks (`analogRead`) y el buffer serial (`Serial.read()`).
2. **Suma de Intenciones:** Mapea el valor de cada joystick (con una zona muerta incorporada) a una velocidad que va desde un límite negativo a uno positivo. A esta velocidad base del joystick, se le suma vectorialmente la velocidad designada al comando web actual.
# Especificación de Arquitectura - Grúa Torre Dual (OpenSpec)

Este documento detalla la arquitectura de software y hardware para el proyecto de control dual (Web y Físico) de la Grúa Torre.

## 1. Topología del Sistema
El sistema se compone de dos microcontroladores operando de manera cooperativa:
- **ESP32 (MicroPython):** Actúa como interfaz de conectividad Wi-Fi y servidor web asíncrono. Sirve el panel de control HTML/JS y envía las órdenes del usuario vía UART.
- **Arduino Nano (C++):** Actuador principal. Lee los joysticks físicos, escucha el puerto UART y coordina el movimiento de los motores de forma no bloqueante.

---

## 2. Mapa de Conexiones (Pinout)

### Comunicación ESP32 <-> Arduino Nano
| Dispositivo A | Pin | Dispositivo B | Pin | Función |
|---------------|-----|---------------|-----|---------|
| **ESP32**     | GPIO 17 (TX) | **Arduino Nano** | D0 (RX) | Transmisión de comandos (UART 9600 bps) |
| **ESP32**     | GND | **Arduino Nano** | GND | Referencia de tierra común (Obligatoria) |

### Control de Motores y Entradas (Arduino Nano)
| Componente | Pin Arduino | Función |
|------------|-------------|---------|
| **Joystick Carro** | A0 | Control analógico del Carro (Adelante/Atrás) |
| **Joystick Elevación** | A1 | Control analógico de Elevación (Subir/Bajar) |
| **Joystick Giro** | A2 | Control analógico de Giro (Izquierda/Derecha) |
| **TB6612FNG (Motor A)** | D2 | AIN1 - Dirección Carro |
| | D4 | AIN2 - Dirección Carro |
| | D3 | PWMA - Velocidad Carro (PWM) |
| **TB6612FNG (Motor B)** | D7 | BIN1 - Dirección Elevación |
| | D8 | BIN2 - Dirección Elevación |
| | D5 | PWMB - Velocidad Elevación (PWM) |
| **TB6612FNG (STBY)** | 5V | Habilitación de driver (High) |
| **DRV8825 (Nema 17)**| D9 | STEP - Señal de pasos para Giro |
| | D10 | DIR - Señal de dirección para Giro |

---

## 3. Protocolo de Comunicación Serial

La comunicación fluye en una dirección del ESP32 al Arduino a **9600 baudios (8N1)**. Se basa en el envío de caracteres ASCII simples, lo que reduce la carga de procesamiento y hace más robusto el _parsing_.

| Carácter ASCII | Acción Web Correspondiente | Motor/Eje Afectado |
|:---:|---|---|
| `F` | Adelante (Forward) | Carro (DC) |
| `B` | Atrás (Backward) | Carro (DC) |
| `U` | Subir (Up) | Elevación (DC) |
| `D` | Bajar (Down) | Elevación (DC) |
| `L` | Izquierda (Left) | Giro (Stepper) |
| `R` | Derecha (Right) | Giro (Stepper) |
| `S` | Stop | Todos los motores (Comando Web) |

### Seguridad (Watchdog de Movimiento)
El Arduino implementa un *timeout* de 500 ms. Si no recibe un comando serial válido en ese tiempo, la orden web en curso se revierte internamente a `S` (Stop). 
Para evitar que el movimiento se detenga mientras el usuario presiona el botón sostenidamente en la web, la interfaz HTML envía el comando de forma activa cada 200 ms (*polling* persistente). En caso de desconexión Wi-Fi, el ESP32 deja de emitir UART y el Arduino detiene inmediatamente el movimiento sin dejar un motor activo de forma insegura.

---

## 4. Endpoints del Servidor Web (ESP32)

El ESP32 utiliza `uasyncio` para atender peticiones web sin bloquear el bucle del procesador.

### 1. Interfaz Principal
- **Endpoint:** `GET /` o `GET /index.html`
- **Descripción:** Entrega la interfaz de usuario en un archivo embebido (HTML, CSS y JS).
- **Respuesta:** `200 OK` (`text/html`).

### 2. Receptor de Comandos (API)
- **Endpoint:** `GET /cmd?action=<char>`
- **Descripción:** Recibe la intención de movimiento emitido por la web al presionar o soltar un botón. Implementado usando `fetch()` para evitar la recarga de página.
- **Parámetro `action`:** Uno de los caracteres del protocolo (ej. `F`, `B`, `S`).
- **Respuesta:** `200 OK` (`text/plain`).
- **Comportamiento:** El ESP32 retransmite inmediatamente el carácter recibido a través del GPIO 17 mediante la clase UART.

---

## 5. Lógica de Control Mixto (Joysticks + Web)

El programa del Arduino Nano está diseñado de forma **no bloqueante**.
1. **Lectura Asíncrona:** Constantemente procesa la posición de los joysticks (`analogRead`) y el buffer serial (`Serial.read()`).
2. **Suma de Intenciones:** Mapea el valor de cada joystick (con una zona muerta incorporada) a una velocidad que va desde un límite negativo a uno positivo. A esta velocidad base del joystick, se le suma vectorialmente la velocidad designada al comando web actual.
   - *Escenario de ejemplo:* Si el operador empuja el Joystick del Carro hacia adelante (+150 PWM) pero un comando remoto intenta retraer el carro hacia atrás (-200 PWM), la resultante será un leve retroceso de -50 PWM.
3. **Límites Físicos:** Se asegura la protección de los drivers y motores limitando los valores calculados usando la función matemática `constrain()`.
4. **Ejecución Stepper:** La llamada `stepper.runSpeed()` de la librería *AccelStepper* se ejecuta en cada repetición de la función `loop()`, asegurando así pasos calculados fluidos y consistentes sin utilizar retrasos artificiales (`delay()`).

---

## 6. Flujo de Inicio y Conectividad (boot.py)

El proceso de arranque del ESP32 está diseñado para ser robusto y amigable con el desarrollo:
1. **Menú de Inicio (REPL):** Durante los primeros 5 segundos del arranque, se presenta un menú interactivo por terminal serie. Si se selecciona la opción "2", se interrumpe la ejecución del código para liberar la consola REPL. Esto facilita enormemente la modificación y subida de archivos (como `main.py` o `boot.py`) sin que el bucle principal bloquee el puerto serie. Si no hay intervención en 5 segundos, avanza automáticamente.
2. **Conexión Wi-Fi Asistida:** Intenta conectarse a la red Wi-Fi configurada parpadeando el LED de estado (GPIO 2). 
3. **Manejo de Errores Wi-Fi:** Si tras 10 segundos no logra conectarse a la red Wi-Fi, el sistema detiene el intento y emite un mensaje de error por consola, esperando a que el usuario reinicie o revise sus credenciales, evitando la creación de redes no deseadas.

---

## 7. Historial de Cambios y Actualizaciones (Git Log)

A continuación, se documenta la evolución del proyecto organizando cada actualización por fecha y nombrando sus características clave basándonos en los commits realizados ese día:

### 📅 Actualización [2026-05-13]: Inicialización y Estructura Base
- **Commits asociados:** `Initial commit`, `I1`
- **Descripción:** Se creó el repositorio y se establecieron los cimientos del proyecto subiendo los primeros archivos en C++ para el Arduino Nano y en Python para el ESP32, definiendo la estructura de carpetas base.

### 📅 Actualización [2026-05-18]: Despliegue de Interfaz Web
- **Commits asociados:** `Update main.py`
- **Descripción:** Configuración inicial de la interfaz de usuario. Se integró el código HTML/CSS/JS embebido y se programó el socket asíncrono básico para recibir los comandos desde los botones de la grúa.

### 📅 Actualización [2026-05-19]: Telemetría y Monitorización
- **Commits asociados:** `TELEMETRIA Y IP EN LA CONSOLA`, `Merge branch 'main'`
- **Descripción:** **Nuevas Funciones.** Se implementaron los prints de telemetría HTTP y UART para permitir monitorear las peticiones en tiempo real. Además, se añadió la funcionalidad para que el ESP32 muestre su IP asignada en formato URL para un fácil acceso.

### 📅 Actualización [2026-05-20]: Implementación de Red Inalámbrica
- **Commits asociados:** `CONEXION A WIFI`, `Update boot.py`, `Merge branch 'main'`
- **Descripción:** **Nuevas Funciones.** Desarrollo del archivo `boot.py` para la gestión inteligente de la red Wi-Fi. Se refinó la lógica de conexión y se configuraron las temporizaciones de red de manera confiable.

### 📅 Actualización [2026-05-21]: Edición Final, Menú de Inicio y Correcciones
- **Commits asociados:** `EDICION FINAL FUNCIONAL`
- **Descripción:** **Versión Final Funcional.** Esta actualización integró un Menú Interactivo de 5 segundos al arrancar (Bypass REPL), indicación visual usando el LED (GPIO 2), y corrigió de forma definitiva el error de `Acceso Denegado` de Thonny IDE. También se implementó un cierre seguro para `asyncio` y se retiró el fallback del Punto de Acceso (AP).
