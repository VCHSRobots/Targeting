void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  Serial.print("Color Maker Program");
}

int lstcolor = -1;
void loop() {
  int v = digitalRead(3) + 2*digitalRead(4) + 4*digitalRead(5);
  if(v != lstcolor) {
    Serial.print("Color = ");
    Serial.print(v, DEC);
    Serial.print("\n");
    lstcolor = v;
  }
}
