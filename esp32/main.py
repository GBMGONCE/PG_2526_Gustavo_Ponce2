import uasyncio as asyncio
from machine import UART, Pin

# ==========================================
# CONFIGURACIÓN UART Y PINES
# ==========================================
# UART1 configurado en GPIO 17 (TX) y GPIO 16 (RX), a 9600 baudios.
# El TX del ESP32 debe ir conectado al RX (D0) del Arduino Nano.
uart = UART(1, baudrate=9600, tx=17, rx=16)

# LED indicador de actividad (suele ser GPIO 2 en el DevKit)
led = Pin(2, Pin.OUT)

# ==========================================
# INTERFAZ WEB HTML/CSS/JS (Responsiva)
# ==========================================
# Todo el HTML integrado como string para facilitar un servidor de archivo único
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Control Grúa Torre</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #ffffff;
            text-align: center;
            margin: 0;
            padding: 10px;
            touch-action: manipulation;
        }
        h1 { color: #00ADB5; margin-bottom: 5px; }
        .subtitle { color: #aaa; margin-bottom: 20px; font-size: 0.9rem; }
        
        .control-group {
            background-color: #1f2326;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
        }
        .control-group h2 {
            margin: 0 0 10px 0;
            font-size: 1.1rem;
            color: #eeeeee;
        }
        
        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            justify-content: center;
        }
        
        .btn {
            background-color: #393E46;
            border: none;
            border-radius: 12px;
            color: white;
            padding: 20px 10px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.1s;
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
        }
        .btn:active, .btn.active {
            background-color: #00ADB5;
            transform: scale(0.95);
        }
        
        .btn.stop {
            background-color: #FF2E63;
            grid-column: 2;
            grid-row: 2;
        }
        .btn.stop:active, .btn.stop.active {
            background-color: #D90429;
        }
        
        .empty { visibility: hidden; }
        
        .status-bar {
            margin-top: 10px;
            padding: 10px;
            background-color: #222831;
            border-radius: 8px;
            display: inline-block;
            min-width: 200px;
            font-family: monospace;
            color: #00ADB5;
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <h1>Grúa Torre</h1>
    <div class="subtitle">Panel de Control Dual (Web)</div>
    
    <div class="control-group">
        <h2>Elevación y Giro</h2>
        <div class="grid-container">
            <button class="btn empty"></button>
            <button class="btn" onmousedown="startCmd('U')" onmouseup="stopCmd()" ontouchstart="startCmd('U')" ontouchend="stopCmd()">Subir</button>
            <button class="btn empty"></button>
            
            <button class="btn" onmousedown="startCmd('L')" onmouseup="stopCmd()" ontouchstart="startCmd('L')" ontouchend="stopCmd()">Izq</button>
            <button class="btn stop" onmousedown="startCmd('S')" ontouchstart="startCmd('S')">STOP</button>
            <button class="btn" onmousedown="startCmd('R')" onmouseup="stopCmd()" ontouchstart="startCmd('R')" ontouchend="stopCmd()">Der</button>
            
            <button class="btn empty"></button>
            <button class="btn" onmousedown="startCmd('D')" onmouseup="stopCmd()" ontouchstart="startCmd('D')" ontouchend="stopCmd()">Bajar</button>
            <button class="btn empty"></button>
        </div>
    </div>

    <div class="control-group">
        <h2>Carro (Traslación)</h2>
        <div class="grid-container">
            <button class="btn empty"></button>
            <button class="btn" onmousedown="startCmd('F')" onmouseup="stopCmd()" ontouchstart="startCmd('F')" ontouchend="stopCmd()">Adelante</button>
            <button class="btn empty"></button>
            
            <button class="btn empty"></button>
            <button class="btn" onmousedown="startCmd('B')" onmouseup="stopCmd()" ontouchstart="startCmd('B')" ontouchend="stopCmd()">Atrás</button>
            <button class="btn empty"></button>
        </div>
    </div>

    <div class="status-bar" id="status">Comando: Listo</div>

    <script>
        let intervalId = null;
        
        // Función asíncrona para enviar comando al ESP32 sin recargar la página
        function sendRequest(cmd) {
            fetch('/cmd?action=' + cmd).catch(err => console.error("Error enviando:", err));
        }
        
        // Se ejecuta al presionar un botón
        function startCmd(cmd) {
            if(event) event.preventDefault();
            document.getElementById('status').innerText = 'Comando: ' + cmd;
            
            // 1. Enviar el primer comando inmediatamente
            sendRequest(cmd);
            
            // 2. Si hay un intervalo activo, limpiarlo
            if(intervalId) clearInterval(intervalId);
            
            // 3. Crear un ciclo repetitivo cada 200ms para evadir el "timeout" de seguridad del Arduino Nano
            if(cmd !== 'S') {
                intervalId = setInterval(() => {
                    sendRequest(cmd);
                }, 200);
            }
        }
        
        // Se ejecuta al soltar el botón
        function stopCmd() {
            if(event) event.preventDefault();
            if(intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
            document.getElementById('status').innerText = 'Comando: Stop';
            sendRequest('S'); // Enviar comando de parada
        }

        // Bloqueo del menú contextual en móviles al mantener pulsada la pantalla
        window.oncontextmenu = function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        };
    </script>
</body>
</html>
"""

# ==========================================
# GESTIÓN DE PETICIONES HTTP (uasyncio)
# ==========================================
async def handle_client(reader, writer):
    led.value(1) # Encender LED de actividad
    try:
        # Leer línea inicial (ej: GET /cmd?action=F HTTP/1.1)
        request_line = await reader.readline()
        if request_line == b"":
            return
            
        request_str = request_line.decode('utf-8').strip()
        
        # Leer resto de cabeceras hasta salto de línea doble, para limpiar el buffer
        while True:
            line = await reader.readline()
            if not line or line == b'\r\n':
                break
                
        # Parseo simple de URL
        if "GET /cmd?action=" in request_str:
            # Extraemos el comando de una letra (F, B, U, D, L, R, S)
            start_idx = request_str.find("action=") + 7
            cmd = request_str[start_idx:start_idx+1]
            
            # Enviar directamente por puerto Serial al Arduino Nano
            uart.write(cmd.encode())
            
            # Respuesta rápida para liberar el socket
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nOK"
            await writer.awrite(response.encode())
            
        elif "GET / " in request_str or "GET /index.html" in request_str:
            # Servir la interfaz gráfica al entrar a la IP
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                "Connection: close\r\n\r\n"
                + html_content
            )
            await writer.awrite(response.encode())
            
        else:
            # Cualquier otra petición
            response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n404 Not Found"
            await writer.awrite(response.encode())
            
    except Exception as e:
        print("Error en request:", e)
    finally:
        # Cerrar siempre la conexión para no agotar recursos del ESP32
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        led.value(0) # Apagar LED

# ==========================================
# BUCLE PRINCIPAL
# ==========================================
async def main():
    print("Iniciando servidor web asíncrono (uasyncio)...")
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Servidor activo en el puerto 80. Listo para operar la grúa.")
    
    while True:
        # Tarea en espera permanente, aquí pueden agregarse otros procesos concurrentes si fuera necesario.
        await asyncio.sleep(1)

# Iniciar rutina asíncrona
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Servidor detenido por usuario.")
