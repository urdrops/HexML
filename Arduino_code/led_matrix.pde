/*--------------------------------------------------------------------------------------

 dmd_test.cpp 
   Demo and example project for the Freetronics DMD, a 512 LED matrix display
   panel arranged in a 32 x 16 layout.

 Copyright (C) 2011 Marc Alexander (info <at> freetronics <dot> com)

 See http://www.freetronics.com/dmd for resources and a getting started guide.

 Note that the DMD library uses the SPI port for the fastest, low overhead writing to the
 display. Keep an eye on conflicts if there are any other devices running from the same
 SPI port, and that the chip select on those devices is correctly set to be inactive
 when the DMD is being written to.

 USAGE NOTES
 -----------

 - Place the DMD library folder into the "arduino/libraries/" folder of your Arduino installation.
 - Get the TimerOne library from here: http://code.google.com/p/arduino-timerone/downloads/list
   or download the local copy from the DMD library page (which may be older but was used for this creation)
   and place the TimerOne library folder into the "arduino/libraries/" folder of your Arduino installation.
 - Restart the IDE.
 - In the Arduino IDE, you can open File > Examples > DMD > dmd_demo, or dmd_clock_readout, and get it
   running straight away!

 * The DMD comes with a pre-made data cable and DMDCON connector board so you can plug-and-play straight
   into any regular size Arduino Board (Uno, Freetronics Eleven, EtherTen, USBDroid, etc)
  
 * Please note that the Mega boards have SPI on different pins, so this library does not currently support
   the DMDCON connector board for direct connection to Mega's, please jumper the DMDCON pins to the
   matching SPI pins on the other header on the Mega boards.

 This example code is in the public domain.
 The DMD library is open source (GPL), for more see DMD.cpp and DMD.h

--------------------------------------------------------------------------------------*/

/*--------------------------------------------------------------------------------------
  Includes
--------------------------------------------------------------------------------------*/
#include <SPI.h>        //SPI.h must be included as DMD is written by SPI (the IDE complains otherwise)
#include <DMD.h>        //
#include <TimerOne.h>   //
#include "SystemFont5x7.h"
#include "Arial_black_16.h"

//Fire up the DMD library as dmd
#define DISPLAYS_ACROSS 3
#define DISPLAYS_DOWN 2
DMD dmd(DISPLAYS_ACROSS, DISPLAYS_DOWN);

/*--------------------------------------------------------------------------------------
  Interrupt handler for Timer1 (TimerOne) driven DMD refresh scanning, this gets
  called at the period set in Timer1.initialize();
--------------------------------------------------------------------------------------*/
void ScanDMD()
{ 
  dmd.scanDisplayBySPI();
}

/*--------------------------------------------------------------------------------------
  setup
  Called by the Arduino architecture before the main loop begins
--------------------------------------------------------------------------------------*/
void setup(void)
{

   //initialize TimerOne's interrupt/CPU usage used to scan and refresh the display
   Timer1.initialize( 1000 );           //period in microseconds to call ScanDMD. Anything longer than 5000 (5ms) and you can see flicker.
   Timer1.attachInterrupt( ScanDMD );   //attach the Timer1 interrupt to ScanDMD which goes to dmd.scanDisplayBySPI()

   //clear/init the DMD pixels held in RAM
   dmd.clearScreen( true );   //true is normal (all pixels off), false is negative (all pixels on)

}

/*--------------------------------------------------------------------------------------
  loop
  Arduino architecture main loop
--------------------------------------------------------------------------------------*/
void loop(void)
{  
   byte b;
   if (Serial.available() > 0) { // Check if data is available to read
    String receivedString = Serial.readStringUntil('\n'); // Read the incoming string until newline character '\n'
    int stringLength = receivedString.length(); 
    char str[20];
    receivedString.toCharArray(str, 20);
    // Print the received string to the serial monitor
    Serial.print("Received: ");
    Serial.println(receivedString);

    // You can add your logic here based on the received string
    
    // 10 x 14 font clock, including demo of OR and NOR modes for pixels so that the flashing colon can be overlayed
    dmd.clearScreen( true );
    dmd.selectFont(Arial_Black_16);

    dmd.drawMarquee(str,stringLength,(32*DISPLAYS_ACROSS)-1,8);
    long start=millis();
    long timer=start;
    boolean ret=false;
    while(!ret){
      if ((timer) < millis()) {
        ret=dmd.stepMarquee(-1,0);
        timer=millis();
      }
    }
   } else {
    // default code
   }
   delay( 200 );      
   
}

