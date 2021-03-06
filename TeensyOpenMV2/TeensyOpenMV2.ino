#include <Wire.h>
#include <EEPROM.h>
#include <StopWatch.h>
#include <elapsedMillis.h>
#include <Streaming.h>
#include <StopWatch.h>
#include <PWMServo.h>
#include <vector>
#include <string.h>

#include <FastLED.h>

#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <VL53L0X.h>

#include "Constants.h"
#include "IOpins.h"
#include "init.h"
#include "initrcduino.h"

//Create VL53L0X instance
VL53L0X sensor;

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *lMotor = AFMS.getMotor(1);
Adafruit_DCMotor *rMotor = AFMS.getMotor(2);

/* Set the delay between fresh samples for BNO055*/
#define BNO055_SAMPLERATE_DELAY_MS (100)
Adafruit_BNO055 bno = Adafruit_BNO055(55);

//TSL2561 config
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);


PWMServo panServo;
PWMServo tiltServo;

// Set elapsed timers
elapsedMillis motorFwd;
elapsedMillis motorFwdRunTime;
elapsedMillis motorTurnTime;
elapsedMillis motorRevTime;
elapsedMillis turn_timer;
elapsedMillis odo_timer;

StopWatch etm_millis;

void setup() {
	telem.begin(57600);
  Wire.begin();
  telem2.begin(115200);

  sensor.init();
  sensor.setTimeout(500);
  //sensor.startContinuous();
  telem << "VL53L0X Initialized" << endl;

  BNO055_Init();

  //setup TSL2561 lux sensor
  /* Initialise the sensor */
  if(!tsl.begin())
  {
    /* There was a problem detecting the TSL2561 ... check your connections */
    telem << "Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!" << endl;
    while(1);
  }
  /* Setup the sensor gain and integration time */
  TSL2561_configureSensor();
  TSL2561_displaySensorDetails();
  
  //Setup motor shield  
	AFMS.begin();  // create with the default frequency 1.6KHz
  telem.println("Adafruit Motorshield v2 - Initialized!");

  //LED Setup
  delay(2000);
  FastLED.addLeds<WS2811, DATA_PIN, RGB>(leds, NUM_LEDS);
  FastLED.setBrightness(  BRIGHTNESS );
  
	// Set the speed to start, from 0 (off) to 255 (max speed)
	lMotor->setSpeed(150);
	rMotor->setSpeed(150);

	attachInterrupt(THROTTLE_IN_PIN, calcThrottle, CHANGE);
	attachInterrupt(STEERING_IN_PIN, calcSteering, CHANGE);
	attachInterrupt(RCMODE_IN_PIN, togRCMode, CHANGE);
	throttleLeft = throttleRight = speed;

    panServo.attach(23, 450, 2350); // some motors need min/max setting
    panServo.write(panZero);
    tiltServo.attach(38, 450, 2350); // some motors need min/max setting
    tiltServo.write(tiltZero);
  
    //Enable pull ups on encoders
    pinMode(l_encoder, INPUT_PULLUP);
    pinMode(r_encoder, INPUT_PULLUP);
    //Attach interrupts for encoders
    init_ticks_counter();
    attach_encoders();

    //Calculate Encoder Scale factor
    ENCODER_SCALE_FACTOR = WHEEL_DIA*PI/CLICKS_PER_REV;

    telem.println("I'm Ready to receive telem Commands![m, o, c, t]"); // Tell us I"m ready

}

void loop()
{
/*	#if defined SingleShot
		Serial.print(sensor.readRangeSingleMillimeters());
		if (sensor.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
	#else 
		Serial.print(sensor.readRangeContinuousMillimeters());
		if (sensor.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  #endif */
  
	//Serial.println();

  if (telem.available() > 0)
  {
    int val = telem.read();	//read telem input commands        

    int valMod = telem.parseInt();
    if(valMod == 0)
                valMod = 3; 
    
    switch(val)
    {
      case 'M':
        telem2.println(valMod);
        break;
      
      case 'm':
        telem << "Toggle Manual Mode ON" << endl;
        goManual();
        break;
        
      case 't' :      
        telem.println("toggle Roam Mode"); 
        set_speed(speed);
        toggleRoam();
        break;
	  
      case 'c' :
        telem.println("toggle RC control mode");
        toggleRC();
        break;

      case 'o' :
        telem << "Odometry Activated" << endl;
        toggleOdo();
        break;

      case 'g' :
        telem.println("Read Sensors and turn");
        readSensors();
        break;

      case 'L' :
        telem.println("Turn Lights On");
        for(int whiteLed = 0; whiteLed < NUM_LEDS; whiteLed = whiteLed + 1) {
          // Turn our current led on to white, then show the leds
          leds[whiteLed] = CRGB::White;
          // Show the leds (only one of which is set to white, from above)
        }
        FastLED.show();
        break;
      
      case 'O' :
        telem.println("Turn Lights Off");
        for(int blkLed = 0; blkLed < NUM_LEDS; blkLed = blkLed + 1) {
          // Turn our current led back to black for the next loop around
          leds[blkLed] = CRGB::Black;
        }
        FastLED.show();
        break;
    }
          
    delay(1);  
    //telem.println("I'm Ready to receive Mode Commands![m, o, c, t]"); // Tell us I"m ready
  }

  if(manual == 0){ 
      //just listen for telem commands and wait
      }
  else if(manual == 1){  //If roam active- drive autonomously
    goManual();
    }

  if(roam == 0){ 
      //just listen for telem commands and wait
      }
  else if(roam == 1){  //If roam active- drive autonomously
    goRoam();
    }

  if(odo_mode_toggle == 0){ 
      //just listen for telem commands and wait
     }
  else if(odo_mode_toggle == 1) {  //If roam active- drive autonomously
    toggleOdo();
    }
	
  if(rc_mode_toggle == 0){ 
      //just listen for telem commands and wait
      }
  else if(rc_mode_toggle == 1) {  //If roam active- drive autonomously
    goRC();
    }
  
  if(unRCInShared > RC_MODE_TOGGLE && rc_mode_toggle == 0) {
        telem << "toggle RC Mode On via SW" << endl; 
        rc_sw_on = 1;
        toggleRC();
     }
}

void toggleRoam(){
  // This method chooses to make the robot roam or else use the telem command input.
  if(roam == 0){
   roam = 1;
   etm_millis.start();
   telem.println("Activated Roam Mode");
  } else {
    etm_millis.stop();
    etm_millis.reset();
    roam = 0;
    mStop();
    telem.println("De-activated Roam Mode");
    telem.println("I'm Ready to receive Mode Commands![m, o, c, t]"); // Tell us I"m ready
  }
}

void goRoam() {  
  Roam();
}

void toggleRC(){
  // This method chooses to make the robot roam or else use the telem command input.
  if(rc_mode_toggle == 0){
   rc_mode_toggle = 1;
   telem << "Activated RC Mode" << endl;
   etm_millis.start();
  } else {
    rc_mode_toggle = 0;
    throttleLeft = throttleRight = speed;
    mStop();
    etm_millis.stop();
    etm_millis.reset();
    telem << endl << "De-activated RC Mode" << endl;
    telem << "I'm Ready to receive Mode Commands![m, o, c, t]" << endl; // Tell us I"m ready
  }
}

void goRC() {  
	rc_control();   
}

void toggleManual(){
  // This method chooses to make the robot roam or else use the telem command input.
  if(manual_toggle == 0){
   manual_toggle = 1;
   telem << "Manual Mode Activated" << endl;
  } else {
    manual_toggle = 0;
    mStop();
    telem << "De-activated Manual Mode" << endl << endl;
    telem.println("I'm Ready to receive Mode Commands![m, o, c, t]"); // Tell us I"m ready
  }
}

void goManual(){
  modeManual();
}


void toggleOdo(){
  if(odo_mode_toggle == 0) {
    odo_mode_toggle = 1;
    telem << "Odometry Nav Activated" << endl;
    //telem.println("I'm Ready to receive telem Commands![f (inches), b (inches), r (degs), l (degs), s, o]");
    pos_x = pos_y = 0;
    init_ticks_counter();
    odometry();
  } else {
    odo_mode_toggle = 0;
    mStop();
    telem << "Odometry Nav De-activated" << endl;
    telem << "I'm Ready to receive Mode Commands![m, o, c, t]" << endl; // Tell us I"m ready
  }
}


static void smartDelay2(unsigned long ms)
{
  unsigned long start = millis();
  do 
  {
    //getTicks();
    //send_telemetry();
  } while (millis() - start < ms);
}








