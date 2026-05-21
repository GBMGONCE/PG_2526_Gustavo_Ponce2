import network
import time
import machine
import sys
import uselect

# Configuración del LED de estado (GPIO 2)
led = machine.Pin(2, machine.Pin.OUT)
led.value(0)

def connect_wifi(ssid, password):
    print("Iniciando conexión Wi-Fi...")
    wlan = network.WLAN(network.STA_IF)
    
    # Limpiar estado interno del Wi-Fi para evitar "Wifi Internal State Error"
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(0.5)
    
    if not wlan.isconnected():
        print(f"Conectando a la red {ssid}...")
        wlan.connect(ssid, password)
        
        timeout = 10 # Timeout de 10 segundos
        while not wlan.isconnected() and timeout > 0:
            led.value(not led.value()) # Parpadear LED mientras conecta
            print(".", end="")
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        led.value(1) # LED encendido fijo si está conectado
        print("\n¡Conexión Wi-Fi exitosa!")
        print("Configuración de red (IP, Subnet, Gateway, DNS):", wlan.ifconfig())
    else:
        led.value(0)
        print("\nError: No se pudo conectar a la red Wi-Fi. Revisa tus credenciales.")

def menu_inicio(timeout_segundos=5):
    """
    Muestra un menú en la terminal. Avanza automáticamente si no hay respuesta.
    """
    print("\n" + "="*40)
    print("      SISTEMA DE CONTROL - GRÚA TORRE")
    print("="*40)
    print("1. Iniciar sistema normalmente (Modo Ejecución)")
    print("2. Detener en modo programación (Liberar REPL)")
    print(f"Selecciona una opción (Avanza a opción 1 en {timeout_segundos}s)...")
    
    # Configurar la terminal para escuchar la entrada del usuario sin bloquear
    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)
    
    tiempo_inicio = time.time()
    while (time.time() - tiempo_inicio) < timeout_segundos:
        # Revisar si hay datos en la terminal (espera hasta 100ms por ciclo)
        if poller.poll(100):
            caracter = sys.stdin.read(1)
            if caracter == '1':
                print("\n-> Opción 1 seleccionada. Iniciando...")
                return True
            elif caracter == '2':
                print("\n-> Opción 2 seleccionada. Modo programación activo.")
                print("Consola REPL liberada. Puedes subir o modificar archivos.")
                return False
    
    # Si se agota el tiempo sin respuesta, asumimos que está corriendo en la grúa de forma autónoma
    print("\n-> Tiempo de espera agotado. Iniciando de forma automática...")
    return True

# ----------------------------------------------------
# CREDENCIALES WI-FI - Reemplazar por las redes reales
# ----------------------------------------------------
WIFI_SSID = "DESKTOP-L8DNB2E 0462"
WIFI_PASSWORD = "J4284o1!"

# --- FLUJO DE INICIO ---
# Ejecutamos el menú ANTES de conectar al WiFi o cargar el main
if menu_inicio(timeout_segundos=5):
    # Ejecutar la conexión al encender
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
else:
    # Forzar la detención del script del sistema operativo para liberar REPL
    sys.exit()
