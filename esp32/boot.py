import network
import time

def connect_wifi(ssid, password):
    print("Iniciando conexión Wi-Fi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Conectando a la red {ssid}...")
        wlan.connect(ssid, password)
        
        timeout = 15 # Timeout de 15 segundos
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        print("\n¡Conexión Wi-Fi exitosa!")
        print("Configuración de red (IP, Subnet, Gateway, DNS):", wlan.ifconfig())
    else:
        print("\nError: No se pudo establecer conexión a la red Wi-Fi en el tiempo esperado.")

# ----------------------------------------------------
# CREDENCIALES WI-FI - Reemplazar por las redes reales
# ----------------------------------------------------
WIFI_SSID = "TU_SSID_AQUI"
WIFI_PASSWORD = "TU_PASSWORD_AQUI"

# Ejecutar la conexión al encender
connect_wifi(WIFI_SSID, WIFI_PASSWORD)
