import network
import time

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
            print(".", end="")
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        print("\n¡Conexión Wi-Fi exitosa!")
        print("Configuración de red (IP, Subnet, Gateway, DNS):", wlan.ifconfig())
    else:
        print("\nError: No se pudo conectar a la red Wi-Fi.")
        print("Iniciando Modo Punto de Acceso (Access Point)...")
        wlan.active(False) # Desactivar modo cliente para ahorrar energía
        
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        # Nombre de la red Wi-Fi que emitirá el ESP32
        ap.config(essid="GRUA_TORRE", password="password123")
        
        print("\n==========================================")
        print("¡Punto de Acceso creado con éxito!")
        print("Por favor, desde tu teléfono o PC conéctate a:")
        print("Red Wi-Fi: GRUA_TORRE")
        print("Contraseña: password123")
        print("IP asignada:", ap.ifconfig()[0])
        print("==========================================\n")

# ----------------------------------------------------
# CREDENCIALES WI-FI - Reemplazar por las redes reales
# ----------------------------------------------------
WIFI_SSID = "DESKTOP-L8DNB2E 0462"
WIFI_PASSWORD = "J4284o1!"

# Ejecutar la conexión al encender
connect_wifi(WIFI_SSID, WIFI_PASSWORD)

