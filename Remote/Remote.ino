#define L_PIN 1
#define R_PIN 2
#define Q_PIN 3

void setup() {
  pinMode(L_PIN, INPUT_PULLUP);
  pinMode(R_PIN, INPUT_PULLUP);
  pinMode(Q_PIN, INPUT_PULLUP);
  pinMode(13, OUTPUT);
}

void loop() {
  int L_VAL = digitalRead(L_PIN);
  int R_VAL = digitalRead(R_PIN);
  int Q_VAL = digitalRead(Q_PIN);

  if(L_VAL == HIGH){
    digitalWrite(13, LOW);
  }
  else{
    digitalWrite(13, HIGH);
  }
}
