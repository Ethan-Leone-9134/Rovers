// Code takes a 6 digit input and converts it into gcode

void setup() {

  // Set up serial communication at 115200 baud rate
  Serial.begin(115200);
}

void loop() {
  // Read the GCODE from the Raspberry Pi over serial communtication 
  // and set the corresponding information
  if (Serial.available() > 0 ) {                              // Only run if there is something in the serial buffer 
    String GCODE = readFromSerial();                    // Custom function to convert the input into an "int"    
    Serial.println(GCODE);
  }
  delay(10);        // Wait for a short period to allow motor to respond
}



String readFromSerial() {
  // Function converts pi input into an int number
  // Inputs  - none
  // Outputs - result (int) - resultign three digit number

  while (Serial.available() == 0);      // wait for serial data to be available
  unsigned long startTime = millis();   // Get start time
  char input[6];                        // Initialize input variable
  for (int i = 0; i < 6; i++) {         // Set the three characters
    if (Serial.available() > 0){          // If the serial buffer has a character
      input[i] = Serial.read();             // Add the serial character to the "input" variable
    }
    else {                                // If the serial buffer is empty
      input[i] = 0;                         // Set the character to zero to push it along
    }
  }
  input[6]='\0';                        // Ending character
  String output = num2gCode(input);
  return output;                        // return the resultant integer value
}

String num2gCode(String comCode) {
  String firstChar;
  String secondChar;
  String command;

  switch (comCode.charAt(0)) {
    case '1':
      firstChar = "P";
      break;
    case '2':
      firstChar = "S";
      break;
    case '3':
      firstChar = "Q";
      break;
    case '4':
      firstChar = "M";
      break;
    case '5':
      firstChar = "R";
      break;
    case '6':
      firstChar = "K";
      break;
    case '7':
      firstChar = "H";
      break;
    case '8':
      firstChar = "E";
      break;
    default:
      firstChar = "";
      break;
  }

  secondChar = comCode.charAt(1);

  if (comCode.length() > 2) {
    String commandNum = comCode.substring(2);
    commandNum.replace("9", "-");
    int commandInt = commandNum.toInt();
    command = firstChar + secondChar + " " + String(commandInt);
  } else {
    command = firstChar + secondChar;
  }

  return command;
}
