
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
   Serial.begin(9600);
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
    char str[100];
    receivedString.toCharArray(str, 100);
    // Print the received string to the serial monitor

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
    dmd.clearScreen( true );
    dmd.selectFont(Arial_Black_16);

    dmd.drawMarquee("AMITY INNOVATION DESIGN AND RESEARCH CENTRE",43,(32*DISPLAYS_ACROSS)-1,9);
    long start=millis();
    long timer=start;
    boolean ret=false;
    while(!ret){
      if (Serial.available() > 0) {
        break;
      }
      if ((timer) < millis()) {
        ret=dmd.stepMarquee(-1,0);
        timer=millis();
      }
    }
   }
   delay( 200 );      
   
}

