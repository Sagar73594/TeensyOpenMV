void send_odometry(){
    //===  Telemetry section =========
    //if(telem_timer > defaultTelemTime) {

      //DateTime time = rtc.now();
      //telem << time.timestamp(DateTime::TIMESTAMP_TIME);
      //telem << utc << ",";

      telem << etm_millis.elapsed()/1000. << ",";
           
      // IMU
      compass_update();
      telem << (float) -roll << "," << (float) -pitch << "," << (float) yar_heading << ",";

      //Wheel Encoders
      get_ticks_noreset();

      /********************************************************************/
      /*                                                                  */
      /*        Begin odometry                                            */
      /*                                                                  */
      /********************************************************************/  

      int left_encoder_count = 0;
      int right_encoder_count = 0;

	    switch (gDirection){
        case DIRECTION_STOP:
          {
            left_encoder_count = 0;
            right_encoder_count = 0;
            break;
          }
        case DIRECTION_FORWARD:
          left_encoder_count = ticksLR;
          right_encoder_count = ticksRR;
          break;
        case DIRECTION_REVERSE:
			    left_encoder_count = -ticksLR;
			    right_encoder_count = -ticksRR;
			    break;
		    case DIRECTION_ROTATE_LEFT:
			    left_encoder_count = -ticksLR;
			    right_encoder_count = ticksRR;
			    break;
		    case DIRECTION_ROTATE_RIGHT:
			    left_encoder_count = ticksLR;
			    right_encoder_count = -ticksRR;
			    break;			
		    default:
			    left_encoder_count = 0;
			    right_encoder_count = 0;
			    break;
	    }

      // zeros out encoder counts and reads encoders zero value
      //encA.write(0); encB.write(0); encC.write(0); encD.write(0);
      
      float Displacement = (left_encoder_count + right_encoder_count)*ENCODER_SCALE_FACTOR/2.0;
      //float Rotation = (left_encoder_count - right_encoder_count)*ENCODER_SCALE_FACTOR/TRACK;

      pos_x = pos_x + Displacement * cos(yar_heading-init_heading);
      pos_y = pos_y + Displacement * sin(yar_heading-init_heading);

      telem << pos_x << "," << pos_y  << endl;

      init_ticks_counter();
      //telem_timer = 0;
    //}
}

void odometry(){
 interrupts();
 ENCODER_SCALE_FACTOR = WHEEL_DIA*PI/CLICKS_PER_REV;
 float odo_start_distance = 0;
 //int odo_start = 0;

 telem << "Avaialbe Commands: [f, b, l, r, o]. " << endl;
 telem << "Follow direction commands with number of incdhes, f5 for forward 5 inches" << endl;
 telem << " o - to exit odometry mode" << endl;
 
 while(odo_mode_toggle == 1){
  while (telem.available() > 0) {
    int val = telem.read();  //read telem input commands

    turn_time_mult = telem.parseInt();
    turn_time_mult = turn_time_mult + odo_start_distance;  

    if(turn_time_mult == 0)
                turn_time_mult = 0;          

    //if(odo_start == 0){
    //  odo_start = 1;
    //}
    
    odo_start_distance = turn_time_mult;
    
    runODO(val, turn_time_mult);
  }
 }
}

void runODO(int val, int turn_time_mult)
{

    switch(val)
    {
      case 'f' : 
        odo_timer = 0;
        set_speed(speed);
        gDirection = DIRECTION_FORWARD;
        telem << "Rolling Forward!" << endl;
        telem << turn_time_mult << endl;

        //compass_update();
        init_heading = yar_heading;
        etm_millis.start();
        send_odometry();
        mForward();
        
       while(pos_x < turn_time_mult){
        //currentTime = millis();
        if (odo_timer > defaultOdoTime){
          //compass_update();
          send_odometry();
          odo_timer = 0;
        }
        mForward();
       }
      etm_millis.stop(); 
      etm_millis.reset();
      pos_x = pos_y = 0;
      mStop(); 
      break;
      
    case 'l' :
      telem.println("Turning to New Heading");
      set_speed(turnSpeed);
      
      //compass_update();
      new_heading = yar_heading - turn_time_mult;
      
      if(new_heading < 0){
        new_heading = 360. - new_heading;
      }

      //telem << turn_time_mult << "," << yar_heading << endl;
      
      pivotToOdo(new_heading, yar_heading);
           
      mStop();
      break;

    case 'r' :
      telem.println("Turning to New Heading");
      set_speed(turnSpeed);
      
      //compass_update();
      new_heading = turn_time_mult + yar_heading;

      if(new_heading > 360.){
        new_heading = new_heading - 360.;
      }

      telem << turn_time_mult << "," << (float) yar_heading << endl;
      
      pivotToOdo(new_heading, yar_heading);
           
      mStop();
      break;

    case 'b' :
        odo_timer = 0;
        set_speed(speed);
        gDirection = DIRECTION_REVERSE;        
        telem.println("Rolling Backward!");

        mBackward();
        etm_millis.start();
        send_odometry();
        
       while(abs(pos_x) < turn_time_mult){
        //currentTime = millis();
        if (odo_timer > defaultOdoTime){
          //compass_update();
          send_odometry();
          odo_timer = 0;
        }
        mBackward();
       }
      mStop();
      etm_millis.stop();
      etm_millis.reset();
      pos_x = pos_y = 0;
      motorRevTime = 0;
      break;
      
    case 's' :      
      telem.println("Stop!");
      mStop();
      break;

    case 'o' :
      telem.println("Toggle Odometry!");
      toggleOdo();
      mStop();
      break;
    }

    telem << "Avaialbe Commands: [f, b, l, r, o]. " << endl;
}


void pivotToOdo(int target, int currentAngle){

  //int currentAngle = yar_heading;
  int diff = target - currentAngle;
  
  etm_millis.start();
  
  while(abs(diff) > HEADING_TOLERANCE){
    //telem << "Compass Control: " << endl;
    //telem << "\t" << currentAngle << ", " << target << ", " << diff << endl;
    //if (odo_timer > defaultOdoTime){
      //compass_update();
    //  send_odometry();
    //  odo_timer = 0;
    //}
    
    if(diff > 0) {
      throttleRight = turnSpeed;
      throttleLeft = turnSpeed;
      mRight();//right
    } else {
      throttleRight = turnSpeed;
      throttleLeft = turnSpeed;
      mLeft();//left
    }
    
    //if (odo_timer > defaultOdoTime){
    //   send_odometry();
    //   odo_timer = 0;
    //}

    compass_update();
    currentAngle = yar_heading;
    diff = target - currentAngle;
  }
  
  etm_millis.stop();
  etm_millis.reset(); 
  mStop();
  return;
}

 



