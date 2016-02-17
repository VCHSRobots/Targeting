// Does SPI communication in Slave Mode. 
//
// SPI pin numbers:
// SCK   13  // Serial Clock.
// MISO  12  // Master In Slave Out.
// MOSI  11  // Master Out Slave In.
// SS    10  // Slave Select

// Note that the SPI library does not support SPI slave mode.   That requires more work below.
#include <SPI.h>

void SlaveInit(void) {
  // Initialize SPI pins.
  pinMode(SCK, INPUT);
  pinMode(MOSI, INPUT);
  pinMode(MISO, INPUT);
  pinMode(SS, INPUT);
  // Enable SPI as slave.
  SPCR = (1 << SPE);
}

// SPI Transfer.
byte SPItransfer(byte value) {
  SPDR = value;
  while(!(SPSR & (1<<SPIF)));
  delay(10);
  return SPDR;
}

void setup() {
  Serial.begin(9600);
  SlaveInit();
  Serial.println("Slave Initialized");
}

char InBuf[5];
char OutBuf[5];


void loop() {
  if (!digitalRead(SS)) {
      pinMode(MISO, OUTPUT);  // Assert MSIO pin
      Serial.println("***Slave Enabled.");
      OutBuf[0] = 100; OutBuf[1] = 101; OutBuf[2] = 102; OutBuf[3] = 103; OutBuf[4] = 104;
      for(int i = 0; i < 1; i++) {
         InBuf[i] = SPItransfer(255);
         if(digitalRead(SS)) break;
      }
      Serial.println("Input: ");
      for(int i = 0; i < 5; i++) {
         Serial.print(InBuf[i], DEC); 
         Serial.print(" ");
      }
      Serial.print("\n");
  }
  else {
      pinMode(MISO, INPUT); 
      //Serial.println("Slave Disabled.");
  }
}

