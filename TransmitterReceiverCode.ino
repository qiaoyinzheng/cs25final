/*
   Using the nRF24L01 radio module to communicate
   between two Arduinos with much increased reliability following
   various tutorials, conversations, and studying the nRF24L01 datasheet
   and the library reference.

   Transmitter is
   https://github.com/michaelshiloh/resourcesForClasses/tree/master/kicad/Arduino_Shield_RC_Controller

  Receiver is
  https://github.com/michaelshiloh/resourcesForClasses/blob/master/kicad/nRF_servo_Mega

   This file contains code for both transmitter and receiver.
   Transmitter at the top, receiver at the bottom.
   One of them is commented out, so you need to comment in or out
   the correct section. You don't need to make changes to this 
   part of the code, just to comment in or out depending on
   whether you are programming your transmitter or receiver

   You need to set the correct address for your robot.

   Search for the phrase CHANGEHERE to see where to 
   comment or uncomment or make changes.

   These sketches require the RF24 library by TMRh20
   Documentation here: https://nrf24.github.io/RF24/index.html

   change log

   11 Oct 2023 - ms - initial entry based on
                  rf24PerformingRobotsTemplate
   26 Oct 2023 - ms - revised for new board: nRF_Servo_Mega rev 2
   28 Oct 2023 - ms - add demo of NeoMatrix, servo, and Music Maker Shield
	 20 Nov 2023 - as - fixed the bug which allowed counting beyond the limits
   22 Nov 2023 - ms - display radio custom address byte and channel
   12 Nov 2024 - ms - changed names for channel and address allocation for Fall 2024            
   31 Oct 2025 - ms - changed names for channel and address allocation for Fall 2024            
                    - listed pin numbers for servo/NeoPixel connections
                      https://github.com/michaelshiloh/resourcesForClasses/blob/master/kicad/nRF_servo_Mega    
                      https://github.com/michaelshiloh/resourcesForClasses/blob/master/kicad/nRFControlPanel
*/


// Common code
//

// Common pin usage
// Note there are additional pins unique to transmitter or receiver
//

// nRF24L01 uses SPI which is fixed
// on pins 11, 12, and 13 on the Uno
// and on pins 50, 51, and 52 on the Mega

// It also requires two other signals
// (CE = Chip Enable, CSN = Chip Select Not)
// Which can be any pins:

// CHANGEHERE
// For the transmitter
// const int NRF_CE_PIN = A4, NRF_CSN_PIN = A5;

// CHANGEHERE
// for the receiver
const int NRF_CE_PIN = A11, NRF_CSN_PIN = A15;

// nRF 24L01 pin   name
//          1      GND
//          2      3.3V
//          3      CE
//          4      CSN
//          5      SCLK
//          6      MOSI/COPI
//          7      MISO/CIPO

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(NRF_CE_PIN, NRF_CSN_PIN);  // CE, CSN

//#include <printf.h>  // for debugging

// See note in rf24Handshaking about address selection
//

// Channel and address allocation:
// Torico and Sarah: Channel 30, addr = 0x76
// Sudiksha and Aysha: Channel 40, addr = 0x73
// Mariam and Joy:  Channel 50, addr = 0x7C
// Ghadir and Mustafa: Channel 60, addr = 0xC6
// Clara and Jiho:  Channel 70, addr = 0xC3
// Victor and Meera: Channel 80, addr = 0xCC
// Ali and Hari: Channel 90, addr = 0x33

// CHANGEHERE
const int CUSTOM_CHANNEL_NUMBER = 50;   // change as per the above assignment
const byte CUSTOM_ADDRESS_BYTE = 0x7C;  // change as per the above assignment

// Do not make changes here
const byte xmtrAddress[] = { CUSTOM_ADDRESS_BYTE, CUSTOM_ADDRESS_BYTE, 0xC7, 0xE6, 0xCC };
const byte rcvrAddress[] = { CUSTOM_ADDRESS_BYTE, CUSTOM_ADDRESS_BYTE, 0xC7, 0xE6, 0x66 };

const int RF24_POWER_LEVEL = RF24_PA_LOW;

// global variables
uint8_t pipeNum;
unsigned int totalTransmitFailures = 0;

struct DataStruct {
  uint8_t stateNumber;
};
DataStruct data;

void setupRF24Common() {

  // RF24 setup
  if (!radio.begin()) {
    Serial.println(F("radio  initialization failed"));
    while (1)
      ;
  } else {
    Serial.println(F("radio successfully initialized"));
  }

  radio.setDataRate(RF24_250KBPS);
  radio.setChannel(CUSTOM_CHANNEL_NUMBER);
  radio.setPALevel(RF24_POWER_LEVEL);
}

// CHANGEHERE

/*
// Start of Transmitter code
// Choose Arduino Uno port

// Transmitter pin usage
const int LCD_RS_PIN = 3, LCD_EN_PIN = 2, LCD_D4_PIN = 4, LCD_D5_PIN = 5, LCD_D6_PIN = 6, LCD_D7_PIN = 7;
const int SW1_PIN = 8, SW2_PIN = 9, SW3_PIN = 10, SW4_PIN = A3, SW5_PIN = A2;

// LCD library code
#include <LiquidCrystal.h>

// initialize the library with the relevant pins
LiquidCrystal lcd(LCD_RS_PIN, LCD_EN_PIN, LCD_D4_PIN, LCD_D5_PIN, LCD_D6_PIN, LCD_D7_PIN);


const int NUM_OF_STATES = 32;
char* theStates[] = {
  "0 backstage mode",
  "1 dance mode",
  "2 dance to normal mode",
  "3 they always are",
  "4 dance to normal mode",
  "5 close face black out",
  "6 face on light on",
  "7 so disco night",
  "8 feeling fly",
  "9 overreacting",
  "10 you're supposed",
  "11 Ohhhhh here ",
  "12 knife mode angry face",
  "13 go to bed",
  "14 put down mode",
  "15 you know what",
  "16 see if",
  "17 knife mode",
  "18 filing for",
  "19 put down",
  "20 black out face",
  "21 face light on",
  "22 of course",
  "23 your coffee",
  "24 and gain a",
  "25 black out face",
  "26 light on face",
  "27 and saul don't",
  "28 we were",
  "29 honestly",
  "30 we discussed this",
  "31 this isn't",
  "32 she understood",
  "33 angry face",
  "34 normal face",
  "35 dance move",
  "36 close face"
};



void updateLCD() {

  lcd.clear();
  lcd.print(theStates[data.stateNumber]);
  lcd.setCursor(0, 1);  // column, line (from 0)
  lcd.print("not transmitted yet");
}

void countDown() {
  data.stateNumber = (data.stateNumber > 0) ? (data.stateNumber - 1) : 0;
  updateLCD();
}

void countUp() {
  if (++data.stateNumber >= NUM_OF_STATES) {
    data.stateNumber = NUM_OF_STATES - 1;
  }
  updateLCD();
}


void spare1() {}
void spare2() {}

void rf24SendData() {

  radio.stopListening();  // go into transmit mode
  // The write() function will block
  // until the message is successfully acknowledged by the receiver
  // or the timeout/retransmit maxima are reached.
  // Returns 1 if write succeeds
  // Returns 0 if errors occurred (timeout or FAILURE_HANDLING fails)
  int retval = radio.write(&data, sizeof(data));
  
  lcd.clear();
  lcd.setCursor(0, 0);  // column, line (from 0)
  lcd.print("transmitting");
  lcd.setCursor(14, 0);  // column, line (from 0)
  lcd.print(data.stateNumber);

  Serial.print(F(" ... "));
  if (retval) {
    Serial.println(F("success"));
    lcd.setCursor(0, 1);  // column, line (from 0)
    lcd.print("success");
  } else {
    totalTransmitFailures++;
    Serial.print(F("failure, total failures = "));
    Serial.println(totalTransmitFailures);

    lcd.setCursor(0, 1);  // column, line (from 0)
    lcd.print("error, total=");
    lcd.setCursor(13, 1);  // column, line (from 0)
    lcd.print(totalTransmitFailures);
  }
}

class Button {
  int pinNumber;
  bool previousState;
  void (*buttonFunction)();
public:

  // Constructor
  Button(int pn, void* bf) {
    pinNumber = pn;
    buttonFunction = bf;
    previousState = 1;
  }

  // update the button
  void update() {
    bool currentState = digitalRead(pinNumber);
    if (currentState == LOW && previousState == HIGH) {
      Serial.print("button on pin ");
      Serial.print(pinNumber);
      Serial.println();
      buttonFunction();
    }
    previousState = currentState;
  }
};

const int NUMBUTTONS = 5;
Button theButtons[] = {
  Button(SW1_PIN, countDown),
  Button(SW2_PIN, rf24SendData),
  Button(SW3_PIN, countUp),
  Button(SW4_PIN, spare1),
  Button(SW5_PIN, spare2),
};

void setupRF24() {

  setupRF24Common();

  // Set us as a transmitter
  radio.openWritingPipe(xmtrAddress);
  radio.openReadingPipe(1, rcvrAddress);

  // radio.printPrettyDetails();
  Serial.println(F("I am a transmitter"));

  data.stateNumber = 0;
}

void setup() {
  Serial.begin(9600);
  Serial.println(F("Setting up LCD"));

  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  lcd.clear();
  // Print a message to the LCD.
  lcd.print("Radio setup");

  // Display the address in hex
  lcd.setCursor(0, 1);
  lcd.print("addr 0x");
  lcd.setCursor(7, 1);
  char s[5];
  sprintf(s, "%02x", CUSTOM_ADDRESS_BYTE);
  lcd.print(s);

  // Display the channel number
  lcd.setCursor(10, 1);
  lcd.print("ch");
  lcd.setCursor(13, 1);
  lcd.print(CUSTOM_CHANNEL_NUMBER);

  Serial.println(F("Setting up radio"));
  setupRF24();

  // If setupRF24 returned then the radio is set up
  lcd.setCursor(0, 0);
  lcd.print("Radio OK state=");
  lcd.print(theStates[data.stateNumber]);

  // Initialize the switches
  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  pinMode(SW3_PIN, INPUT_PULLUP);
  pinMode(SW4_PIN, INPUT_PULLUP);
  pinMode(SW5_PIN, INPUT_PULLUP);
}



void loop() {
  for (int i = 0; i < NUMBUTTONS; i++) {
    theButtons[i].update();
  }
  delay(50);  // for testing
}


void clearData() {
  // set all fields to 0
  data.stateNumber = 0;
}

// End of transmitter code
// CHANGEHERE
*/


// Start of Receiver Code
// Choose Arduino Mega
// CHANGEHERE

// Additional libraries for music maker shield
#include <Adafruit_VS1053.h>
#include <SD.h>

// Servo library
#include <Servo.h>

// Additional libraries for graphics on the Neo Pixel Matrix
#include <Adafruit_NeoPixel.h>
#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#ifndef PSTR
#define PSTR // Make Arduino Due happy
#endif

// Additional pin usage for receiver

// Adafruit music maker shield
#define SHIELD_RESET -1  // VS1053 reset pin (unused!)
#define SHIELD_CS 7      // VS1053 chip select pin (output)
#define SHIELD_DCS 6     // VS1053 Data/command select pin (output)
#define CARDCS 4         // Card chip select pin
// DREQ should be an Int pin, see http://arduino.cc/en/Reference/attachInterrupt
#define DREQ 3  // VS1053 Data request, ideally an Interrupt pin
Adafruit_VS1053_FilePlayer musicPlayer = Adafruit_VS1053_FilePlayer(SHIELD_RESET, SHIELD_CS, SHIELD_DCS, DREQ, CARDCS);

// Connectors for NeoPixels and Servo Motors are labeled
// on the circuit board
// and use pins 16, 17, 18, 19, 20, and 21 

// Connectors for NeoPixels and Servo Motors are labeled
// M1 - M6 which is not very useful. Here are the pin
// assignments:
// M1 = 19
// M2 = 21 
// D20 = 20
// M4 = 16 // left arm
// M5 = 18 // right arm
// M6 = 17 // neopixel

// Servo motors
const int RIGHT_EAR_PIN = 20;
// D20 = 20  (Right Ear)
const int RIGHT_ARM_PIN = 18;
// M5 = 18  (Right hand)
const int LEFT_ARM_PIN = 16;
// M4 = 16  (Left hand)
//const int TAIL_SERVO_PIN = 17;
//const int GRABBER_SERVO_PIN = 18;
// Change Later

// Neopixel
const int NEOPIXELPIN = 17;
const int NUMPIXELS = 192;
// 64 LEDs for each 8x8 matrix, so 192 in total
//#define NEOPIXELPIN 18
//#define NUMPIXELS 64  // change to fit
//Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXELPIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoMatrix matrix = Adafruit_NeoMatrix(8, 8, 3, 1, NEOPIXELPIN,
                            NEO_MATRIX_TOP     + NEO_MATRIX_RIGHT +
                            NEO_MATRIX_COLUMNS + NEO_MATRIX_PROGRESSIVE,
                            NEO_GRB            + NEO_KHZ800);

// Array defining 8x8 grid layout for both matrices
int pixelMap0[8][8] = {
  { 0, 1, 2, 3, 4, 5, 6, 7 },
  { 8, 9, 10, 11, 12, 13, 14, 15 },
  { 16, 17, 18, 19, 20, 21, 22, 23 },
  { 24, 25, 26, 27, 28, 29, 30, 31 },
  { 32, 33, 34, 35, 36, 37, 38, 39 },
  { 40, 41, 42, 43, 44, 45, 46, 47 },
  { 48, 49, 50, 51, 52, 53, 54, 55 },
  { 56, 57, 58, 59, 60, 61, 62, 63 }
};

int pixelMap1[8][8] = {
  { 64, 65, 66, 67, 68, 69, 70, 71 },
  { 72, 73, 74, 75, 76, 77, 78, 79 },
  { 80, 81, 82, 83, 84, 85, 86, 87 },
  { 88, 89, 90, 91, 92, 93, 94, 95 },
  { 96, 97, 98, 99, 100, 101, 102, 103 },
  { 104, 105, 106, 107, 108, 109, 110, 111 },
  { 112, 113, 114, 115, 116, 117, 118, 119 },
  { 120, 121, 122, 123, 124, 125, 126, 127 }
};

int pixelMap2[8][8] = {  
  { 128, 129, 130, 131, 132, 133, 134, 135 },
  { 136, 137, 138, 139, 140, 141, 142, 143 },
  { 144, 145, 146, 147, 148, 149, 150, 151 },
  { 152, 153, 154, 155, 156, 157, 158, 159 },
  { 160, 161, 162, 163, 164, 165, 166, 167 },
  { 168, 169, 170, 171, 172, 173, 174, 175 },
  { 176, 177, 178, 179, 180, 181, 182, 183 },
  { 184, 185, 186, 187, 188, 189, 190, 191 }
};

Servo LeftArm;  // change names to describe what's moving
Servo RightArm;
Servo RightEar;
// Servo tail;
// Servo grabber;
// Servo disk;
// Change Later

// change as per your robot
const int RIGHT_ARM_RELAX = 20;
const int LEFT_ARM_RELAX = 50;
const int RIGHT_EAR_RELAX = 160;
// const int NOSE_WRINKLE = 45;
// const int NOSE_TWEAK = 90;
// const int TAIL_ANGRY = 0;
// const int TAIL_HAPPY = 180;
// const int GRABBER_RELAX = 0;
// const int GRABBER_GRAB = 180;

 // vairables for testing slow down servo example, delete if doesn't work
int currentLeftAngle = 120; 
int currentRightAngle = 60;
int stepSize = 3;
int moveDelay = 20;

void setup() {
  Serial.begin(9600);
  // printf_begin();

  // Set up all the attached hardware
  setupMusicMakerShield();
  setupServoMotors();
  setupNeoPixels();

  setupRF24();

  // Brief flash to show we're done with setup()
  flashNeoPixels();
}

void setupRF24() {
  setupRF24Common();

  // Set us as a receiver
  radio.openWritingPipe(rcvrAddress);
  radio.openReadingPipe(1, xmtrAddress);

  // radio.printPrettyDetails();
  Serial.print(F("I am a receiver on channel "));
  Serial.print(CUSTOM_CHANNEL_NUMBER);
  Serial.print (" and at address 0x");
  Serial.print (CUSTOM_ADDRESS_BYTE, HEX);
  Serial.println("");
}

void setupMusicMakerShield() {
  if (!musicPlayer.begin()) {  // initialise the music player
    Serial.println(F("Couldn't find VS1053, do you have the right pins defined?"));
    while (1)
      ;
  }
  Serial.println(F("VS1053 found"));

  if (!SD.begin(CARDCS)) {
    Serial.println(F("SD card failed or not present"));
    while (1)
      ;  // don't do anything more
  }

  // Set volume for left, right channels. lower numbers == louder volume!
  musicPlayer.setVolume(20, 20);

  // Timer interrupts are not suggested, better to use DREQ interrupt!
  //musicPlayer.useInterrupt(VS1053_FILEPLAYER_TIMER0_INT); // timer int

  // If DREQ is on an interrupt pin (on uno, #2 or #3) we can do background
  // audio playing
  musicPlayer.useInterrupt(VS1053_FILEPLAYER_PIN_INT);  // DREQ int
}

void setupServoMotors() {
  LeftArm.attach(LEFT_ARM_PIN);
  RightArm.attach(RIGHT_ARM_PIN);
  RightEar.attach(RIGHT_EAR_PIN);
  // resting position
  LeftArm.write(LEFT_ARM_RELAX);
  RightArm.write(RIGHT_ARM_RELAX);
  RightEar.write(RIGHT_EAR_RELAX);
  delay(1000);
  //  antenna.attach(ANTENNA_SERVO_PIN);
  //  tail.attach(TAIL_SERVO_PIN);
  //  grabber.attach(GRABBER_SERVO_PIN);
  // Change Later
  //  tail.write(TAIL_HAPPY);
}

void setupNeoPixels() {
  //  pixels.begin();
  //  pixels.clear();
  //  pixels.show();
  matrix.begin();
  matrix.setTextWrap(false);
  matrix.setBrightness(5);
  matrix.setTextColor(matrix.Color(200, 30, 40));
}

void flashNeoPixels() {

  // Using the Matrix library
  matrix.fillScreen(matrix.Color(0, 255, 0));
  matrix.show();
  delay(500);
  matrix.fillScreen(0);
  matrix.show();

  //  // all on
  //  for (int i = 0; i < NUMPIXELS; i++) {  // For each pixel...
  //    pixels.setPixelColor(i, pixels.Color(0, 100, 0));
  //  }
  //  pixels.show();
  //  delay(500);
  //
  //  // all off
  //  pixels.clear();
  //  pixels.show();
}

// customized neopixel functions start



const int FACE_WIDTH  = 8;
const int FACE_HEIGHT = 24;
const int PIXELS_PER_FACE = FACE_WIDTH * FACE_HEIGHT;  // 192


const uint8_t openMouth[PIXELS_PER_FACE * 3] = { 
  128, 86, 33, 93, 46, 0, 126, 57, 0, 128, 60, 0, 132, 76, 6, 132, 76, 6, 128, 60, 0, 128, 86, 33, 128, 86, 33, 93, 46, 0, 128, 60, 0, 132, 76, 6, 132, 76, 6, 128, 60, 0, 126, 57, 0, 127, 56, 1, 127, 83, 34, 104, 52, 0, 133, 74, 5, 135, 70, 0, 131, 64, 0, 128, 60, 0, 131, 64, 0, 132, 79, 12, 128, 53, 1, 132, 79, 12, 135, 70, 0, 133, 74, 3, 128, 61, 0, 132, 79, 12, 135, 70, 0, 135, 70, 0, 126, 57, 0, 130, 82, 23, 132, 79, 12, 128, 60, 0, 125, 74, 55, 130, 82, 23, 132, 76, 6, 132, 76, 6, 126, 74, 53, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 130, 82, 23, 129, 64, 1, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 126, 57, 0, 130, 82, 23, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 127, 71, 52, 126, 57, 0, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 75, 52, 126, 57, 0, 125, 74, 55, 126, 74, 53, 125, 74, 55, 93, 46, 0, 93, 46, 0, 93, 46, 0, 125, 74, 55, 125, 74, 55, 125, 75, 55, 93, 46, 0, 127, 71, 50, 125, 74, 55, 125, 74, 55, 125, 74, 55, 93, 46, 0, 126, 74, 55, 125, 74, 55, 125, 74, 55, 127, 71, 50, 125, 74, 55, 126, 48, 33, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 103, 74, 110, 3, 12, 71, 0, 0, 0, 3, 12, 71, 103, 74, 110, 126, 48, 33, 125, 74, 55, 125, 74, 55, 59, 65, 116, 103, 112, 159, 93, 46, 0, 59, 65, 116, 3, 12, 71, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 122, 30, 8, 125, 74, 55, 125, 72, 54, 125, 72, 54, 125, 72, 54, 125, 74, 53, 125, 74, 55, 125, 74, 55, 122, 30, 8, 126, 63, 45, 125, 74, 55, 125, 74, 55, 125, 74, 54, 125, 72, 54, 125, 74, 55, 125, 74, 55, 0, 0, 0, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 74, 55, 125, 72, 54, 125, 74, 55, 125, 74, 55, 0, 0, 0, 110, 38, 26, 118, 54, 40, 125, 74, 54, 125, 72, 54, 125, 72, 54, 125, 74, 55, 127, 63, 42, 35, 2, 0, 106, 4, 3, 115, 29, 20, 125, 74, 54, 125, 72, 54, 125, 74, 55, 128, 64, 43, 63, 7, 1, 105, 41, 0, 110, 38, 26, 118, 54, 40, 125, 74, 54, 125, 72, 54, 130, 61, 41, 128, 29, 7, 35, 2, 0, 93, 47, 0, 125, 74, 55, 125, 74, 55, 125, 74, 55, 128, 64, 43, 128, 29, 7, 128, 64, 43, 0, 0, 0, 129, 52, 0, 125, 74, 55, 125, 74, 55, 125, 74, 55, 126, 29, 8, 128, 64, 43, 125, 74, 55, 0, 0, 0, 128, 55, 1

  }; 

const uint8_t closedMouth[PIXELS_PER_FACE * 3] = {
  129, 85, 27, 93, 42, 0, 127, 54, 0, 129, 57, 0, 133, 75, 1, 133, 75, 1, 129, 57, 0, 129, 85, 27, 129, 85, 27, 93, 42, 0, 129, 57, 0, 133, 75, 1, 133, 75, 1, 129, 57, 0, 127, 54, 0, 128, 53, 0, 129, 82, 28, 104, 49, 0, 134, 73, 0, 136, 68, 0, 132, 62, 0, 129, 57, 0, 132, 62, 0, 133, 77, 4, 129, 51, 0, 133, 77, 4, 136, 68, 0, 134, 73, 0, 129, 58, 0, 133, 77, 4, 136, 68, 0, 136, 68, 0, 127, 54, 0, 131, 81, 16, 133, 77, 4, 129, 57, 0, 126, 73, 52, 131, 81, 16, 133, 75, 1, 133, 75, 1, 127, 71, 50, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 131, 81, 16, 131, 61, 0, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 127, 54, 0, 131, 81, 16, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 128, 69, 49, 127, 54, 0, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 74, 49, 127, 54, 0, 126, 73, 52, 127, 71, 50, 126, 73, 52, 93, 42, 0, 93, 42, 0, 93, 42, 0, 126, 73, 52, 126, 73, 52, 126, 74, 52, 93, 42, 0, 128, 69, 46, 126, 73, 52, 126, 73, 52, 126, 73, 52, 93, 42, 0, 127, 71, 52, 126, 73, 52, 126, 73, 52, 128, 69, 46, 126, 73, 52, 127, 44, 27, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 104, 73, 110, 0, 5, 69, 0, 0, 0, 0, 5, 69, 104, 73, 110, 127, 44, 27, 126, 73, 52, 126, 73, 52, 56, 63, 116, 104, 113, 160, 93, 42, 0, 56, 63, 116, 0, 5, 69, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 123, 24, 2, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 74, 49, 126, 73, 52, 126, 73, 52, 123, 24, 2, 127, 44, 27, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 0, 0, 0, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 0, 0, 0, 125, 75, 54, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 126, 73, 52, 129, 60, 37, 28, 0, 0, 115, 0, 0, 115, 0, 0, 126, 73, 52, 126, 73, 52, 126, 73, 52, 130, 61, 39, 61, 1, 0, 105, 36, 0, 125, 75, 54, 126, 73, 52, 126, 74, 52, 126, 73, 52, 131, 58, 36, 130, 23, 1, 28, 0, 0, 93, 43, 0, 126, 73, 52, 126, 73, 52, 126, 73, 52, 130, 61, 39, 130, 23, 1, 130, 61, 39, 0, 0, 0, 130, 49, 0, 126, 73, 52, 126, 73, 52, 126, 73, 52, 127, 23, 2, 130, 61, 39, 126, 73, 52, 0, 0, 0, 129, 52, 0
  };

const uint8_t angry[PIXELS_PER_FACE * 3] = {
  0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 94, 50, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 252, 49, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 254, 184, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 94, 50, 0, 0, 0, 255, 255, 255, 255, 255, 255, 254, 184, 50, 255, 94, 50, 254, 184, 50, 0, 0, 0, 254, 184, 50, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 252, 49, 254, 184, 50, 255, 252, 49, 255, 94, 50, 255, 252, 49, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 252, 49, 255, 252, 49, 255, 252, 49, 255, 252, 49, 255, 252, 49, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 252, 49, 255, 252, 49, 255, 252, 49, 255, 252, 49, 255, 252, 49, 0, 0, 0, 255, 255, 255, 255, 255, 255, 212, 27, 25, 154, 21, 22, 223, 87, 27, 223, 87, 27, 223, 87, 27, 0, 0, 0, 255, 255, 255, 255, 255, 255, 212, 27, 25, 212, 27, 25, 212, 27, 25, 212, 27, 25, 212, 27, 25, 212, 27, 25, 0, 0, 0, 255, 255, 255, 212, 27, 25, 154, 21, 22, 154, 21, 22, 154, 21, 22, 154, 21, 22, 154, 21, 22, 0, 0, 0, 255, 255, 255, 154, 21, 22, 0, 0, 0, 223, 87, 27, 255, 255, 255, 255, 255, 255, 154, 21, 22, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 154, 21, 22, 0, 0, 0, 255, 255, 255, 212, 27, 25, 212, 27, 25, 154, 21, 22, 154, 21, 22, 154, 21, 22, 212, 27, 25, 0, 0, 0, 255, 255, 255, 222, 210, 210, 0, 0, 0, 212, 27, 25, 212, 27, 25, 212, 27, 25, 223, 87, 27, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 212, 27, 25, 212, 27, 25, 223, 87, 27, 223, 87, 27, 0, 0, 0, 255, 255, 255, 212, 27, 25, 212, 27, 25, 212, 27, 25, 212, 27, 25, 154, 21, 22, 222, 210, 210, 0, 0, 0, 255, 255, 255, 212, 27, 25, 212, 27, 25, 154, 21, 22, 222, 210, 210, 222, 210, 210, 222, 210, 210, 170, 158, 158, 0, 0, 0, 222, 210, 210, 222, 210, 210, 170, 158, 158, 170, 158, 158, 170, 158, 158, 222, 210, 210, 222, 210, 210, 0, 0, 0, 170, 158, 158, 170, 158, 158, 222, 210, 210, 222, 210, 210, 222, 210, 210, 170, 158, 158, 222, 210, 210, 1, 1, 1, 0, 0, 0, 0, 0, 0, 129, 64, 62, 0, 0, 0, 0, 0, 0, 170, 158, 158, 222, 210, 210, 1, 0, 0, 95, 41, 41, 95, 41, 41, 95, 41, 41, 95, 41, 41, 95, 41, 41, 154, 21, 22, 212, 27, 25, 1, 0, 0, 95, 41, 41, 95, 41, 41, 129, 64, 62, 129, 64, 62, 95, 41, 41, 154, 21, 22, 154, 21, 22, 1, 0, 0, 129, 64, 62, 129, 64, 62, 129, 64, 62, 129, 64, 62, 129, 64, 62, 0, 0, 0, 0, 0, 0, 0, 0, 0
};  



// Map a single face pixel (index in 0..191) to the LED strip and set its color
void setFacePixelFromRGB(int faceIndex, const uint8_t* rgbData) {
  // 1. Get RGB from the array
  uint8_t r = rgbData[faceIndex * 3 + 0];
  uint8_t g = rgbData[faceIndex * 3 + 1];
  uint8_t b = rgbData[faceIndex * 3 + 2];

  // 2. Convert flat index to face (x, y) in 8×24
  int y = faceIndex / FACE_WIDTH;  // 0..23
  int x = faceIndex % FACE_WIDTH;  // 0..7

  // 3. Which 8×8 panel is this row in?
  int panel   = y / 8;    // 0 = top, 1 = middle, 2 = bottom
  int localY  = y % 8;    // row inside that panel (0..7)

  // 4. Look up LED index using the appropriate pixel map
  int ledIndex;

  if (panel == 0) {
    ledIndex = pixelMap0[localY][x];          // top panel
  } else if (panel == 1) {
    ledIndex = pixelMap1[localY][x];          // middle panel
  } else {
    ledIndex = pixelMap2[localY][x];   // bottom panel
  }

  // 5. Set that LED's color (NeoPixel style)
  matrix.setPixelColor(ledIndex, r, g, b);
}

void drawFace(const uint8_t* rgbData) {
  matrix.clear();  // turn everything off before drawing

  for (int i = 0; i < PIXELS_PER_FACE; i++) {
    setFacePixelFromRGB(i, rgbData);
  }

  matrix.show();
}

// Talking effect globals
bool        isTalking        = false;
bool        mouthOpen        = false;
unsigned long lastTalkFlipMs = 0;
unsigned long talkIntervalMs = 200;  // time between open/close
unsigned long talkEndTimeMs  = 0;

// Pointers to current faces for talking
const uint8_t* currentOpenFace   = nullptr;
const uint8_t* currentClosedFace = nullptr;
unsigned long bufferTimeMs = 500;


void startTalkingEffect(const uint8_t* openFace,
                        const uint8_t* closedFace,
                        unsigned long durationMs) {
  currentOpenFace   = openFace;
  currentClosedFace = closedFace;

  lastTalkFlipMs    = millis();
  talkEndTimeMs     = millis() + durationMs + bufferTimeMs;

  isTalking         = true;
  mouthOpen         = false;  // start closed
  drawFace(currentClosedFace);
}


void stopTalkingEffect() {
  isTalking = false;
  // Optionally: draw neutral face here
  drawFace(currentOpenFace); 
}


void updateTalkingEffect() {
  unsigned long now = millis();
  Serial.print(isTalking);
  Serial.print("\t");
  Serial.print(now);
  Serial.print("\t");
  Serial.print(talkEndTimeMs);
  Serial.print("\t");
  Serial.print(lastTalkFlipMs);
  Serial.print("\t");
  Serial.print(talkIntervalMs);
  Serial.print("\n");
  delay(200);
  if (!isTalking) return;
  // Stop after duration
  if (now >= talkEndTimeMs) {
    stopTalkingEffect();
    return;
  }
  // Time to flip?
  if (now - lastTalkFlipMs >= talkIntervalMs) {
    mouthOpen = !mouthOpen;
    if (mouthOpen) {
      drawFace(currentOpenFace);
    } else {
      drawFace(currentClosedFace);
    }
    lastTalkFlipMs = now;
  }
}

void resetPixels() {
  matrix.clear();
  matrix.show();
}

// end of neopixel customized functions

// start of customized servo functions
void moveRightTo(int targetAngle) {

  while (currentRightAngle != targetAngle) {
    if (currentRightAngle < targetAngle) {
      currentRightAngle += stepSize;
      if (currentRightAngle > targetAngle) currentRightAngle = targetAngle; 
    } else {
      currentRightAngle -= stepSize;
      if (currentRightAngle < targetAngle) currentRightAngle = targetAngle; 
    }
    RightArm.write(currentRightAngle); 
    delay(moveDelay);
  }
}


void moveLeftTo(int targetAngle) {
  while (currentLeftAngle != targetAngle) {
    if (currentLeftAngle < targetAngle) {
      currentLeftAngle += stepSize;
      if (currentLeftAngle > targetAngle) currentLeftAngle = targetAngle;
    } else {
      currentLeftAngle -= stepSize;
      if (currentLeftAngle < targetAngle) currentLeftAngle = targetAngle;
    }
    LeftArm.write(currentLeftAngle);
    delay(moveDelay);
  }
}

void moveRightEarTo(int targetAngle) {

  while (currentRightAngle != targetAngle) {
    if (currentRightAngle < targetAngle) {
      currentRightAngle += stepSize;
      if (currentRightAngle > targetAngle) currentRightAngle = targetAngle; 
    } else {
      currentRightAngle -= stepSize;
      if (currentRightAngle < targetAngle) currentRightAngle = targetAngle; 
    }
    RightEar.write(currentRightAngle); 
    delay(moveDelay);
  }
}

void resetArms() {

  moveRightTo(RIGHT_ARM_RELAX);
  moveLeftTo(LEFT_ARM_RELAX);
  moveRightEarTo(RIGHT_EAR_RELAX);
}

void danceMove() {
  for (int i = 1; i <= 6; i++) {

    moveRightTo(110);
    moveLeftTo(50);
    moveRightTo(90);
    moveLeftTo(20);
    for (int j = 0; j < 2; j++) {
      RightEar.write(160);
      delay(120);
      RightEar.write(130);
      delay(120);
    }
    
  }
}




// end of customized servo functions





void loop() {
  // If there is data, read it,
  // and do the needfull
  // Become a receiver
  radio.startListening();
  if (radio.available(&pipeNum)) {
    radio.read(&data, sizeof(data));
    Serial.print(F("message received Data = "));
    Serial.print(data.stateNumber);
    Serial.println();

    switch (data.stateNumber) {
      case 0:

        matrix.clear();
        drawFace(openMouth);
        resetArms();        
        
        
                
        break;
      case 1:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/Smirking.mp3");
        danceMove();
        
        
        
        
        break;
      case 2:
        danceMove();
        
        resetArms();
        
        break;
      case 3:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        Serial.println(musicPlayer.playingMusic);
        musicPlayer.startPlayingFile("/01TheyAl.mp3");
        startTalkingEffect(openMouth, closedMouth, 1000);
      
        // comment out printing
        // the audio always stop round case 12, where I set the brightness to 10
        // comment out neo matrix, leave the audio
        break;
      case 4:
        danceMove();
        
        resetArms();
      
        break;
      case 5:
        resetPixels();
        break;
      case 6:
        drawFace(openMouth);
        break;
      case 7:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/02SoDisc.mp3");
        startTalkingEffect(openMouth, closedMouth, 7000);
        break;

      case 8:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/03Feelin.mp3");
        startTalkingEffect(openMouth, closedMouth, 9000);
        break;
      case 9:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/04Overre.mp3");
        startTalkingEffect(openMouth, closedMouth, 7000);
        break;
      case 10:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/05You're.mp3");
        startTalkingEffect(openMouth, closedMouth, 3000);
        break;
      
        
        

        
      case 11:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/06Ohhhhh.mp3");
        startTalkingEffect(openMouth, closedMouth, 21000);
        break;
      
        
          // I tried to comment this out, the audio still stopped
        
        // after this case the audio stopped
        // this is also the point the audio stopped in today's rehearsal
        // this is  the cause the audio stopping
        // this might be too long?
        // see video

        
        break;
      case 12:
        // if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        // musicPlayer.startPlayingFile("/AngryKni.mp3");
      
        RightArm.write(110);
        // matrix.setBrightness(5);
        // this might steal too much power?
        
        // without serial printing, when I start this case, it flash to angry 1 sec and turn back to normal face
          // stopTalkingEffect: this might be the flipping flag for this
        // but the second time I called it it works well


        drawFace(angry);
        break;
      case 13:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/07GOTOBE.mp3");
        // startTalkingEffect(openMouth, closedMouth, 3000);
        break;

      case 14:
        resetArms();
        break;

      case 15:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/08YouKno.mp3");
        // startTalkingEffect(openMouth, closedMouth, 10000);
        break;

      case 16:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/09SeeIfI.mp3");
        // startTalkingEffect(openMouth, closedMouth, 10000);
        break;

      case 17:
        // if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        // musicPlayer.startPlayingFile("/AngryKni.mp3");
        RightArm.write(110);
        // drawFace(angry);
        break;

      case 18:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/10Filing.mp3");
        // startTalkingEffect(openMouth, closedMouth, 10000);
        break;

      case 19:
        resetArms();
        break;

      case 20:
        resetPixels();
        break;

      case 21:
        drawFace(openMouth);
        break;

      case 22:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        // musicPlayer.startPlayingFile("/Typinggg.mp3");
        musicPlayer.startPlayingFile("/15OfCour.mp3");
        startTalkingEffect(openMouth, closedMouth, 2000);
        break;

      case 23:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        // musicPlayer.startPlayingFile("/Typinggg.mp3");
        musicPlayer.startPlayingFile("/16YourCo.mp3");
        startTalkingEffect(openMouth, closedMouth, 2000);
        break;

      case 24:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        // musicPlayer.startPlayingFile("/Typinggg.mp3");
        musicPlayer.startPlayingFile("/17AndGai.mp3");
        startTalkingEffect(openMouth, closedMouth, 2000);
        break;

      case 25:
        resetPixels();
        break;

      case 26:
        drawFace(openMouth);
        break;

      case 27:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/AndSaulD.mp3");
        startTalkingEffect(openMouth, closedMouth, 7000);
        break;

      case 28:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/19WeWere.mp3");
        startTalkingEffect(openMouth, closedMouth, 2000);
        break;

      case 29:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/20Honest.mp3");
        startTalkingEffect(openMouth, closedMouth, 4000);
        break;

      case 30:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/21Wedisc.mp3");
        startTalkingEffect(openMouth, closedMouth, 5000);
        break;

      case 31:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/22ThisIs.mp3");
        startTalkingEffect(openMouth, closedMouth, 1000);
        break;

      case 32:
        if (musicPlayer.playingMusic) musicPlayer.stopPlaying();
        musicPlayer.startPlayingFile("/23SheUnd.mp3");
        startTalkingEffect(openMouth, closedMouth, 3000);
        break;

      case 33:
        drawFace(angry);
        break;

      case 34:
        drawFace(openMouth);
        break;

      case 35:
        danceMove();
        resetArms();
        break;

      case 36:
        resetPixels();
        break;

      default:
        Serial.println(F("Invalid option"));
    }



  }
  updateTalkingEffect();
  if (isTalking && musicPlayer.stopped()) {
    stopTalkingEffect();
  }
}  
// end of loop()
// end of receiver code
// CHANGEHERE
