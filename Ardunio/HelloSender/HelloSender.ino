// Simple Program to send Hello over and over again.


void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

int counter = 0;
void loop() {
  counter++;
  Serial.print("Hello ");
  Serial.print(counter, DEC);
  Serial.print("\n");
  delay(50);
  digitalWrite(13, LOW);
  delay(100);
  digitalWrite(13, HIGH);
}


