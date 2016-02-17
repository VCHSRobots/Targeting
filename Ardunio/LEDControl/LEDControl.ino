// LED Control -- Ardunio Program to accept command from Raspberry PI
// and control the color of NEO Pixels arranged in a ring.
//
// Writen for the EPIC Robot Team.
// Feb 16, 2016


#include <Adafruit_NeoPixel.h>
#define NEOPIN 9
#define NUMPIXELS 12
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, NEOPIN, NEO_GRB + NEO_KHZ800);

void set_ring(int r, int g, int b, int w);
void ChangeColor(int c, int brightness);

void setup() {
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  
  pinMode(13, OUTPUT);
  Serial.begin(9600);
  pixels.begin();
  
}

int counter = 0;
int lastColor = -1;
int lastPot = -1;
int potvalue = 0;
int c = 0;
void loop() {
  c = digitalRead(3) + 2*digitalRead(4) + 4*digitalRead(5);
  potvalue = analogRead(A0);
  if(c != lastColor || potvalue != lastPot) {
    lastColor = c;
    lastPot = potvalue;
    Serial.print("Color = ");
    Serial.print(lastColor, DEC);
    Serial.print("\n");
    ChangeColor(c, potvalue);
  }
  
  counter++;
  if(counter > 10) {
    counter = 0;   
    Serial.print("Color Output Program. V1\n");
    //c++;
    //if (c >= 8) c = 0;
  }
  delay(50);
  digitalWrite(13, LOW);
  delay(100);
  digitalWrite(13, HIGH);

  int potvalue = analogRead(A0);
  //Serial.print("Pot = ");
  //Serial.print(potvalue, DEC);
  //Serial.print("\n");
}


// ChangeColor() function.  Input is c, a number between 0-7 that
// is the color selector, and brightness, a number between 0 and 1024
// that gives the brightness of the light.
void ChangeColor(int c, int brightness)
{
  int s = brightness / 4;  // Should yeild a num between 0-255.
    
  if(c == 0) {set_ring(0, 0, 0, 0); return; }
  if(c == 1) {set_ring(s, 0, 0, 0); return; }
  if(c == 2) {set_ring(0, s, 0, 0); return; }
  if(c == 3) {set_ring(0, 0, s, 0); return; }
  if(c == 4) {set_ring(s, s, s, 0); return; }
  if(c == 5) {set_ring(s, s, 0, 0); return; }
  if(c == 6) {set_ring(s, 0, s, 0); return; }
  if(c == 7) {set_ring(0, s, s, 0); return; }
}

void set_ring(int r, int g, int b, int w)
{
  for(int i=0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
    pixels.show();
  }
}


