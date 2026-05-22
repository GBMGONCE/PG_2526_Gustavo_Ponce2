import uasyncio as asyncio
from machine import UART, Pin
import network

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
html_content = """<!DOCTYPE html>

<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" name="viewport"/>
<title>CRANE_OS Dashboard</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
        body {
            font-family: 'JetBrains Mono', monospace;
            background-color: #000000;
            color: #e2e2e2;
            overflow: hidden;
            touch-action: manipulation;
        }
        .hazard-pattern {
            background: repeating-linear-gradient(
                45deg,
                #ffd700,
                #ffd700 20px,
                #000000 20px,
                #000000 40px
            );
        }
        .gauge-container {
            position: relative;
            width: 200px;
            height: 200px;
        }
        .gauge-svg {
            transform: rotate(-90deg);
        }
        .custom-scrollbar::-webkit-scrollbar {
            width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #131313;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #ffd700;
        }
        
        /* Prevenir selección de texto en botones móviles */
        button {
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
        }
    </style>
<script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: {
            extend: {
              "colors": {
                      "surface-bright": "#393939",
                      "on-surface": "#e2e2e2",
                      "primary-container": "#ffd700",
                      "surface-container": "#1f1f1f",
                      "surface": "#131313",
              },
            },
          },
        }
    </script>
</head>
<body class="h-screen flex flex-col">
<!-- TopAppBar -->
<header class="bg-surface text-primary-container border-b-4 border-primary-container docked full-width top-0 flex justify-between items-center w-full px-8 h-16 z-50">
<div class="flex items-center gap-4">
<span class="font-headline-lg text-headline-lg font-black text-primary-container tracking-tighter uppercase">CRANE_OS</span>
<span class="bg-primary-container text-black px-2 py-0.5 font-label-bold text-label-bold rounded-sm">V4.2.0</span>
</div>
<div class="flex items-center gap-6">
<div class="flex items-center gap-2 text-primary-container">
<span class="material-symbols-outlined text-xl">wifi</span>
<span class="font-label-bold text-label-bold uppercase">LINK: STABLE</span>
</div>
<div class="flex items-center gap-4 border-l border-outline-variant pl-6">
<button class="material-symbols-outlined hover:bg-surface-container-highest hover:text-primary-container p-2 transition-all">settings</button>
<button class="material-symbols-outlined hover:bg-surface-container-highest hover:text-primary-container p-2 transition-all">notifications</button>
<button class="material-symbols-outlined hover:bg-surface-container-highest hover:text-primary-container p-2 transition-all text-red-500">power_settings_new</button>
</div>
</div>
</header>
<div class="flex flex-1 overflow-hidden pt-0">
<!-- SideNavBar -->
<nav class="bg-surface-container border-r-2 border-outline-variant flex flex-col h-full w-64 z-40">
<div class="p-6 border-b border-outline-variant">
<div class="font-headline-lg text-headline-lg text-primary-container leading-none">OPERATOR_01</div>
<div class="font-label-bold text-label-bold uppercase text-gray-400 opacity-70">SECTOR_7G</div>
</div>
<div class="flex-1 mt-4">
<a class="bg-primary-container text-black border-y-2 border-primary-container flex items-center px-6 py-4 w-full font-label-bold text-label-bold uppercase gap-3" href="#">
<span class="material-symbols-outlined">settings_remote</span>
                    Control
                </a>
</div>
<div class="p-4 mt-auto">
<button onmousedown="startCmd('S')" ontouchstart="startCmd('S')" class="w-full hazard-pattern h-24 border-4 border-black group relative overflow-hidden active:scale-95 transition-transform">
<div class="absolute inset-0 flex items-center justify-center bg-black/10 group-hover:bg-transparent">
<span class="bg-black text-primary-container font-black px-3 py-1 text-xl border-2 border-primary-container">EMERGENCY STOP</span>
</div>
</button>
</div>
</nav>
<!-- Main Content Area -->
<main class="flex-1 overflow-y-auto p-8 flex flex-col gap-8 bg-black custom-scrollbar">
<!-- Controls Row -->
<div class="grid grid-cols-2 gap-8">
<!-- GIRO CONTROL -->
<div class="bg-surface-container border-2 border-outline-variant p-6 flex flex-col items-center">
<div class="w-full flex justify-between items-center mb-6">
<h2 class="font-label-bold text-label-bold uppercase bg-surface-bright px-3 py-1">GIRO (NEMA 17)</h2>
<span class="text-primary-container font-bold">STATUS: ACTIVE</span>
</div>
<div class="w-full flex justify-between gap-4 mt-4">
<button onmousedown="startCmd('L')" onmouseup="stopCmd()" ontouchstart="startCmd('L')" ontouchend="stopCmd()" class="flex-1 border-2 border-primary-container py-6 text-2xl font-bold text-primary-container hover:bg-primary-container hover:text-black transition-colors">CCW (Izquierda)</button>
<button onmousedown="startCmd('R')" onmouseup="stopCmd()" ontouchstart="startCmd('R')" ontouchend="stopCmd()" class="flex-1 border-2 border-primary-container py-6 text-2xl font-bold text-primary-container hover:bg-primary-container hover:text-black transition-colors">CW (Derecha)</button>
</div>
</div>
<!-- CARRO CONTROL -->
<div class="bg-surface-container border-2 border-outline-variant p-6 flex flex-col">
<div class="w-full flex justify-between items-center mb-6">
<h2 class="font-label-bold text-label-bold uppercase bg-surface-bright px-3 py-1">CARRO (DC MOTOR)</h2>
<span class="text-primary-container font-bold">ACTIVE</span>
</div>
<div class="flex gap-8 flex-1 justify-center">
<div class="flex flex-col justify-center gap-4">
<button onmousedown="startCmd('F')" onmouseup="stopCmd()" ontouchstart="startCmd('F')" ontouchend="stopCmd()" class="w-32 h-20 border-2 border-primary-container flex items-center justify-center text-primary-container hover:bg-primary-container hover:text-black">
<span class="material-symbols-outlined text-4xl">add</span> (Adelante)
</button>
<button onmousedown="startCmd('B')" onmouseup="stopCmd()" ontouchstart="startCmd('B')" ontouchend="stopCmd()" class="w-32 h-20 border-2 border-primary-container flex items-center justify-center text-primary-container hover:bg-primary-container hover:text-black">
<span class="material-symbols-outlined text-4xl">remove</span> (Atrás)
</button>
</div>
</div>
</div>
</div>

<!-- ELEVACIÓN CONTROL (Added as it was missing from design) -->
<div class="bg-surface-container border-2 border-outline-variant p-6 flex flex-col items-center mt-2">
<div class="w-full flex justify-between items-center mb-6">
<h2 class="font-label-bold text-label-bold uppercase bg-surface-bright px-3 py-1">ELEVACIÓN (GANCHO)</h2>
<span class="text-primary-container font-bold">STATUS: ACTIVE</span>
</div>
<div class="w-full flex justify-between gap-4 mt-4">
<button onmousedown="startCmd('U')" onmouseup="stopCmd()" ontouchstart="startCmd('U')" ontouchend="stopCmd()" class="flex-1 border-2 border-primary-container py-6 text-2xl font-bold text-primary-container hover:bg-primary-container hover:text-black transition-colors">SUBIR</button>
<button onmousedown="startCmd('D')" onmouseup="stopCmd()" ontouchstart="startCmd('D')" ontouchend="stopCmd()" class="flex-1 border-2 border-primary-container py-6 text-2xl font-bold text-primary-container hover:bg-primary-container hover:text-black transition-colors">BAJAR</button>
</div>
</div>

</main>
<!-- Right Sidebar - Telemetry Log -->
<aside class="w-80 bg-surface-container border-l-2 border-outline-variant flex flex-col p-4 custom-scrollbar overflow-y-auto hidden md:flex">
<h3 class="font-label-bold text-label-bold uppercase border-b-2 border-primary-container pb-2 mb-4 text-primary-container">REAL-TIME TELEMETRY</h3>
<div class="flex flex-col gap-2 font-code-sm text-primary-container" id="logContainer">
<div class="p-2 bg-black/40 border-l-2 border-primary-container"><span class="opacity-50">CRANE_OS</span> INICIADO</div>
</div>
</aside>
</div>

<script>
        // LOGICA DE CONTROL DE LA GRUA (ESP32)
        let intervalId = null;
        
        function addLog(msg) {
            const logContainer = document.getElementById('logContainer');
            if(!logContainer) return;
            const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
            const newLog = document.createElement('div');
            newLog.className = 'p-2 bg-black/40 border-l-2 border-primary-container';
            newLog.innerHTML = `<span class="opacity-50">[${time}]</span> CMD_SEND: ${msg}`;
            logContainer.prepend(newLog);
            if (logContainer.children.length > 20) logContainer.lastElementChild.remove();
        }
        
        function sendRequest(cmd) {
            fetch('/cmd?action=' + cmd).catch(err => console.error("Error enviando:", err));
        }
        
        function startCmd(cmd) {
            if(event) event.preventDefault();
            addLog(cmd);
            sendRequest(cmd);
            if(intervalId) clearInterval(intervalId);
            if(cmd !== 'S') {
                intervalId = setInterval(() => { sendRequest(cmd); }, 200);
            }
        }
        
        function stopCmd() {
            if(event) event.preventDefault();
            if(intervalId) { clearInterval(intervalId); intervalId = null; }
            addLog('STOP');
            sendRequest('S');
        }

        window.oncontextmenu = function(e) {
            e.preventDefault(); e.stopPropagation(); return false;
        };

        // UI Interactions
        document.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('mousedown', () => { btn.style.transform = 'scale(0.98)'; });
            btn.addEventListener('mouseup', () => { btn.style.transform = 'scale(1)'; });
            btn.addEventListener('touchstart', () => { btn.style.transform = 'scale(0.98)'; });
            btn.addEventListener('touchend', () => { btn.style.transform = 'scale(1)'; });
        });
</script>
</body></html>
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
        
        # --- TELEMETRÍA DE RED ---
        if "GET /cmd?action=" in request_str:
            pass # Se imprime más abajo junto con el UART para ser más limpio
        elif "GET / " in request_str or "GET /index.html" in request_str:
            print("[HTTP] Cliente ha solicitado la interfaz web.")
            
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
            
            print(f"Interacción Web: Comando recibido -> '{cmd}'")
            
            # Enviar directamente por puerto Serial al Arduino Nano
            uart.write(cmd.encode())
            
            # --- TELEMETRÍA UART ---
            print(f"[TELEMETRÍA] Petición HTTP recibida. Enviando por UART -> '{cmd}'")
            
            # Respuesta rápida para liberar el socket
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nOK"
            await writer.awrite(response.encode())
            
        elif "GET / " in request_str or "GET /index.html" in request_str:
            print("Interacción Web: Interfaz gráfica (HTML) solicitada.")
            # Servir la interfaz gráfica al entrar a la IP
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n" + html_content
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
    
    # Obtener la IP actual para mostrar el enlace de acceso
    wlan = network.WLAN(network.STA_IF)
    ip = wlan.ifconfig()[0] if wlan.active() else "IP_Desconocida"
    
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Servidor activo en el puerto 80. Listo para operar la grúa.")
    
    while True:
        # Tarea en espera permanente, aquí pueden agregarse otros procesos concurrentes si fuera necesario.
        await asyncio.sleep(1)

# Ejecutar el servidor al final de main.py de manera segura
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nServidor web detenido desde el teclado.")
