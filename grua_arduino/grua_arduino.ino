#include <AccelStepper.h>

// ==========================================
// PINES JOYSTICK
// ==========================================
#define JOY_X A0 // Carro
#define JOY_Y A1 // Elevación
#define JOY_Z A2 // Giro

// ==========================================
// PINES TB6612FNG - Motor A (Carro)
// ==========================================
#define AIN1 2
#define AIN2 4
#define PWMA 3

// ==========================================
// PINES TB6612FNG - Motor B (Elevación)
// ==========================================
#define BIN1 7
#define BIN2 8
#define PWMB 5

// ==========================================
// PINES DRV8825 - Motor Paso a Paso (Giro)
// ==========================================
#define STEP_PIN 9
#define DIR_PIN 10

// Inicializamos la clase AccelStepper para el Nema 17 usando los pines
// indicados
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// ==========================================
// VARIABLES DE CONTROL Y SEGURIDAD
// ==========================================
char webCmd = 'S';
unsigned long lastWebCmdTime = 0;
const unsigned long WEB_TIMEOUT = 500; // Timeout de 500ms para seguridad web

void setup() {
  // Comunicación serial a 9600 bps (RX = D0)
  Serial.begin(9600);

  // Configuración de pines para Motores DC
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);

  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  // (Nota: Asegúrate de conectar el pin STBY del TB6612FNG a 5V)

  // Configuración base para el Stepper (Giro)
  stepper.setMaxSpeed(1500.0);
  // Al usar runSpeed() la aceleración no interfiere, pero se define por buenas
  // prácticas
  stepper.setAcceleration(500.0);
}

// Función de control para Motor A (Carro) usando PWM y TB6612FNG
void controlMotorA(int speed) {
  if (speed > 0) {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
    analogWrite(PWMA, speed);
  } else if (speed < 0) {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
    analogWrite(PWMA, -speed);
  } else {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, LOW);
    analogWrite(PWMA, 0);
  }
}

// Función de control para Motor B (Elevación) usando PWM y TB6612FNG
void controlMotorB(int speed) {
  if (speed > 0) {
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
    analogWrite(PWMB, speed);
  } else if (speed < 0) {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
    analogWrite(PWMB, -speed);
  } else {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, LOW);
    analogWrite(PWMB, 0);
  }
}

void loop() {
  // 1. Escuchar Comandos Web (UART) de forma no bloqueante
  if (Serial.available() > 0) {
    char incoming = Serial.read();
    // Validar el comando recibido
    if (incoming == 'F' || incoming == 'B' || incoming == 'U' ||
        incoming == 'D' || incoming == 'L' || incoming == 'R' ||
        incoming == 'S') {
      webCmd = incoming;
      lastWebCmdTime = millis();
    }
  }

  // 2. Aplicar Timeout de Seguridad Web
  // Si en más de WEB_TIMEOUT ms no hemos recibido nada desde la web,
  // detenemos los comandos web para evitar movimientos fantasma en caso de
  // caída WiFi.
  if (millis() - lastWebCmdTime > WEB_TIMEOUT) {
    webCmd = 'S';
  }

  // 3. Leer Joysticks Analógicos
  int joyX = analogRead(JOY_X);
  int joyY = analogRead(JOY_Y);
  int joyZ = analogRead(JOY_Z);

  // Mapear señales del joystick a rangos de velocidad, añadiendo zonas muertas
  // para ruido. Rango PWM: -255 a 255.
  int speedX = map(joyX, 0, 1023, -255, 255);
  if (abs(speedX) < 40)
    speedX = 0;

  int speedY = map(joyY, 0, 1023, -255, 255);
  if (abs(speedY) < 40)
    speedY = 0;

  // Stepper necesita un rango mayor de velocidad. Rango: -1000 a 1000 pasos/seg
  int speedZ = map(joyZ, 0, 1023, -1000, 1000);
  if (abs(speedZ) < 60)
    speedZ = 0;

  // 4. Evaluar intenciones Web
  int webSpeedX = 0;
  int webSpeedY = 0;
  int webSpeedZ = 0;

  // Velocidades fijas asignadas a la web
  int motorPwmValue = 200;   // PWM (0-255)
  int stepperWebSpeed = 800; // Pasos/seg

  switch (webCmd) {
  case 'F':
    webSpeedX = motorPwmValue;
    break; // Adelante (Carro)
  case 'B':
    webSpeedX = -motorPwmValue;
    break; // Atrás (Carro)
  case 'U':
    webSpeedY = motorPwmValue;
    break; // Subir (Elevación)
  case 'D':
    webSpeedY = -motorPwmValue;
    break; // Bajar (Elevación)
  case 'L':
    webSpeedZ = -stepperWebSpeed;
    break; // Izquierda (Giro)
  case 'R':
    webSpeedZ = stepperWebSpeed;
    break; // Derecha (Giro)
  case 'S':
    break; // Stop (Sin efecto)
  }

  // 5. Lógica de Control Mixto (Suma Vectorial de Intenciones)
  // De esta forma si la web dice "F" y el Joystick dice Atrás, se contrarrestan
  // o permite un control simultáneo (ej. web sube, joystick mueve a la
  // derecha).
  int finalSpeedX = speedX + webSpeedX;
  int finalSpeedY = speedY + webSpeedY;
  int finalSpeedZ = speedZ + webSpeedZ;

  // Asegurar que no excedemos los rangos máximos de los actuadores
  finalSpeedX = constrain(finalSpeedX, -255, 255);
  finalSpeedY = constrain(finalSpeedY, -255, 255);
  finalSpeedZ = constrain(finalSpeedZ, -1500, 1500);

  // 6. Actuar Motores
  controlMotorA(finalSpeedX);
  controlMotorB(finalSpeedY);

  // Control no bloqueante del Stepper con AccelStepper
  if (finalSpeedZ != 0) {
    stepper.setSpeed(finalSpeedZ);
    stepper.runSpeed(); // Genera un pulso si corresponde al tiempo de velocidad
  } else {
    stepper.stop();
  }
}
