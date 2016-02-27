// StripFlaser.ino   Sketch to control a strip of NEO Pixels.
// and flash decartive LEDs.
//
// Writen for the EPIC Robot Team.
// Feb 16, 2016


#include <Adafruit_NeoPixel.h>
#define NEOPIN 9
#define NPIXELS 46
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NPIXELS, NEOPIN, NEO_GRB + NEO_KHZ800);

// Possilbe modes.  A mode is higher level logic for one type of display.
#define MODE_STEADY  0
#define MODE_BOUNCE  1   
#define MODE_FLASH   2
#define MODE_SWELL   3

// These are globals that maintain the mode and general parameters
// to each of the mode implementations.
int m_mode = 0;
int m_red = 255;
int m_blue = 255; 
int m_green = 255;

// ----------------------------------------------------------------------
// Helper fuctions:

// Helper function to set a pixels to the current color.
void pixel_on(int i)
{
  pixels.setPixelColor(i, pixels.Color(m_red, m_blue, m_green));
}

// Helper function to set a pixel to off.
void pixel_off(int i)
{
  pixels.setPixelColor(i, pixels.Color(0, 0, 0));
}

// -----------------------------------------------------------------------
// MODE STEADY
int steady_dly = 0;
int steady_num = 0;
void modestart_steady(int dly, int num)
{
  steady_dly = dly;
  steady_num = num;
}

int modeupdate_steady()
{
  if(steady_num <= 0) return 1;
  steady_num--;
  for(int i = 0; i < NPIXELS; i++) pixel_on(i);
  pixels.show();
  delay(steady_dly);
  return 0;
}


// -----------------------------------------------------------------------
// FLASH MODE.  Code below implements a flasher.
int flash_state = 0;
int flash_dly = 0;
int flash_num = 0;
int flash_dly_on = 0;
int flash_dly_off = 0;
void modestart_flash(int dly_on, int dly_off, int num)
{
  flash_state = 0;
  flash_dly_on = dly_on;
  flash_dly_off = dly_off;
  flash_num = num;
}

int modeupdate_flash()
{
  if(flash_num <= 0) return 1;
  flash_num--;
  for(int i = 0; i < NPIXELS; i++) pixel_on(i);
  pixels.show();
  delay(flash_dly_on);
  for(int i = 0; i < NPIXELS; i++) pixel_off(i);
  pixels.show();
  delay(flash_dly_off);
  return 0;
}

// ----------------------------------------------------------------------
// MODE BOUNCE

int bounce_num = 0;
int bounce_dly = 0;
int bounce_i = 0;
int bounce_dir = 1;

void modestart_bounce(int dly, int num)
{
  bounce_dly = dly;
  bounce_num = num;
  bounce_i = 1;
  bounce_dir = 1;
}

int modeupdate_bounce()
{
  if(bounce_i == 0) 
  {
    bounce_num--;
    if(bounce_num == 0) return 1;
  }
  pixel_off(bounce_i);
  if(bounce_dir) 
  { 
    bounce_i++;
    if(bounce_i >= NPIXELS) {
      bounce_i = NPIXELS - 1;
      bounce_dir = 0;
    }
  }
  else {
    bounce_i--;
    if(bounce_i < 0) {
      bounce_i = 0;
      bounce_dir = 1;
    }
  } 
  pixel_on(bounce_i);
  pixels.show();
  delay(bounce_dly);
  return 0;
}

//-----------------------------------------------------------------------
// Main loop code starts below.

// Setup. Is called once at startup by the system.
void setup() {
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(13, OUTPUT);
  pixels.begin(); 
}

// This function is responsible for changing the mode.  Its called
// each time a current mode finishs.
int pcnt = 0;
void changemode()
{
  pcnt++;
  if(pcnt > 8) pcnt = 0;
  switch(pcnt) {
    case 0: 
      m_mode = MODE_STEADY;
      m_red = 0; m_green= 0; m_blue =  0;
      modestart_steady(25, 200);
      return;
     case 1:
      m_mode = MODE_STEADY;
      m_red = 20; m_green=20; m_blue = 20;
      modestart_steady(25, 100);
      return;
     case 2:
      m_mode = MODE_FLASH;
      m_red = 255; m_green=255; m_blue = 0;
      modestart_flash(50, 50, 3);
      return;
     case 3:
      m_mode = MODE_FLASH;
      m_red = 0; m_green=255; m_blue = 0;
      modestart_flash(10, 20, 15);
      return;
     case 4:
      m_mode = MODE_BOUNCE;
      m_red = 255; m_green = 0; m_blue = 0;
      modestart_bounce(25, 1);
      return;
     case 5:
      m_mode = MODE_BOUNCE;
      m_red = 0; m_green = 255; m_blue = 0;
      modestart_bounce(25, 1);
      return;
     case 6:
      m_mode = MODE_BOUNCE;
      m_red = 255; m_green = 255; m_blue = 255;
      modestart_bounce(25, 3);
      return;
     case 7: 
      m_mode = MODE_FLASH;
      m_red = 255; m_green=0; m_blue = 0;
      modestart_flash(25, 25, 10);
      return;
     case 8:
      m_mode = MODE_STEADY;
      m_red = 255; m_green=255; m_blue = 255;
      modestart_steady(25, 100);
      return;
  }
}

// MAIN LOOP. Here we simplly call the update function for whatever
// mode we are in.  If the update function returns "true", then it
// is time to change modes.
void loop() {

  switch(m_mode)
  {
    case MODE_STEADY: if(modeupdate_steady()) changemode(); return;
    case MODE_BOUNCE: if(modeupdate_bounce()) changemode(); return;
    case MODE_FLASH:  if(modeupdate_flash()) changemode(); return;
    case MODE_SWELL:  changemode(); return;
  }
  changemode();
}



