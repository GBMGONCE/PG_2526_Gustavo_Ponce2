# Requerimientos del Sistema - Grúa Torre Dual

Este documento detalla todos los requerimientos de hardware y software necesarios para replicar y operar el proyecto de la Grúa Torre, incluyendo las últimas funciones añadidas.

## Requerimientos de Hardware
- **ESP32 (Placa de Desarrollo):** Microcontrolador con conectividad Wi-Fi para alojar el servidor web.
- **Arduino Nano:** Microcontrolador principal para la lógica de los motores.
- **Módulos de Driver (TB6612FNG):** Para controlar la dirección y velocidad de los motores DC.
- **Driver DRV8825:** Para el control preciso del motor paso a paso.
- **Motor Paso a Paso (Nema 17):** Para el eje de rotación (Giro) de la grúa.
- **Motores DC con Reductora (N20):** Para los ejes de Carro (Traslación) y Elevación.
- **Módulos Joystick (x3):** Entradas analógicas para el control manual local.
- **Cables Jumper, Protoboard y Fuente de Alimentación:** Adecuados para la corriente requerida.

## Requerimientos de Software (Iniciales)
- **Arduino IDE:** Para compilar y subir el código C++ al Arduino Nano.
- **Thonny IDE:** Entorno recomendado para interactuar y programar el ESP32 con MicroPython.
- **MicroPython Firmware:** Instalado previamente en el ESP32.
- **Librería AccelStepper:** Instalada en el Arduino IDE para el control no bloqueante del motor Nema 17.

## Nuevas Funciones Añadidas (Actualizaciones)
Con las últimas actualizaciones, el software ahora cuenta con los siguientes requerimientos lógicos y nuevas capacidades:

1. **Interfaz Web Asíncrona (`uasyncio`):** El ESP32 gestiona un servidor web HTTP de forma concurrente en el puerto 80 sin trabar el sistema.
2. **Control Remoto vía Wi-Fi:** Conexión usando un dispositivo móvil o PC con una interfaz responsiva integrada en HTML/CSS/JS.
3. **Telemetría en Tiempo Real:** Logs en consola mostrando las peticiones web entrantes (`[HTTP]`) y los comandos enviados al Arduino (`[UART]`).
4. **IP Visible en Consola:** El ESP32 imprime su IP directamente en formato de enlace (`http://...`) facilitando el acceso al panel.
5. **Gestión de Wi-Fi Avanzada:** Cuenta con un timeout de seguridad de 10 segundos, impresión de estado e indicación visual usando el LED integrado de la placa (GPIO 2).
6. **Menú de Inicio Bypass (REPL):** Al arrancar el ESP32, otorga 5 segundos para pulsar "2" por consola y entrar en modo programación, evitando que el bucle de ejecución principal interfiera con Thonny IDE.
