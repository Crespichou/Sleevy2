int emgPin = A0; // Broche analogique pour le capteur EMG
int emgValue = 0; // Valeur du capteur EMG

void setup() {
    Serial.begin(9600); // Initialisation de la communication série
}

void loop() {
    emgValue = analogRead(emgPin); // Lecture de la valeur du capteur EMG
    Serial.println(emgValue); // Impression de la valeur du capteur EMG sur le moniteur série
    delay(100); // Attente de 100ms
}
  