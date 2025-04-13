#define LIGHT_PIN 7  // Light LED on Pin 7
#define FAN_PIN 8    // Fan LED on Pin 8

void setup() {
    Serial.begin(9600);   // Initialize serial communication
    pinMode(LIGHT_PIN, OUTPUT);
    pinMode(FAN_PIN, OUTPUT);
    digitalWrite(LIGHT_PIN, LOW); // Ensure LEDs start OFF
    digitalWrite(FAN_PIN, LOW);
}

void loop() {
    if (Serial.available() >= 2) {  // Ensure at least 2 bytes are available
        char device = Serial.read();  // Read device type (L or F)
        char state = Serial.read();   // Read state (0 or 1)

        if (device == 'L') {  // Light Control
            digitalWrite(LIGHT_PIN, state == '1' ? HIGH : LOW);
            Serial.println(state == '1' ? "Light ON" : "Light OFF");
        }
        else if (device == 'F') {  // Fan Control
            digitalWrite(FAN_PIN, state == '1' ? HIGH : LOW);
            Serial.println(state == '1' ? "Fan ON" : "Fan OFF");
        }
    }
}

