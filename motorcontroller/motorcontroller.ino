#define L_MOTOR 5
#define R_MOTOR 6

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.print("Hello");
}

void loop() {
  // put your main code here, to run repeatedly:
  int L_POWER = 0;
  int R_POWER = 0;
  int input = 0;
  
  while (Serial.available() == 0);
  input = Serial.read();
  
  while(input != 255){
    while (Serial.available() == 0);
    input = Serial.read();
//    Serial.print("CHECK is ");
//    Serial.println(input, DEC);
  }

  while (Serial.available() == 0);
  L_POWER = Serial.read();
//  Serial.print("L_POWER is ");
//  Serial.println(L_POWER, DEC);

  while (Serial.available() == 0);
  R_POWER = Serial.read();
//  Serial.print("R_POWER is ");
//  Serial.println(R_POWER, DEC);

    
//    if(input = 255){
//      L_POWER = Serial.read();
//      input = Serial.read();
//      Serial.println(input);
//      Serial.println("L POWER detected");
//    }
//    
//    if(input != 255){
//      R_POWER = Serial.read();
//      Serial.println(input);
//      Serial.println("R POWER detected");
//    }
  analogWrite(L_MOTOR, L_POWER);
  analogWrite(R_MOTOR, R_POWER);
  
}
