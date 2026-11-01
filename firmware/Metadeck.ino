
#include <Keyboard.h>
const int buttonPins[] = {2,3,4,5,6,7,8,9,10,14,15,16,18,19,20,21,38,39,40,41};
const int NUM_BUTTONS = 20;
const int encoderLeft = A0;
const int encoderRight = A1;
const int encoderPress = A2;
unsigned long lastDebounce[20] = {0};
int lastState[20];
int btnState[20];
const unsigned long BTN_DEBOUNCE = 50;
unsigned long lastEncTime = 0;
const unsigned long ENC_REPEAT = 25;
void setup() {
  Keyboard.begin();
  for(int i=0;i<NUM_BUTTONS;i++){pinMode(buttonPins[i],INPUT_PULLUP);lastState[i]=HIGH;btnState[i]=HIGH;}
  pinMode(encoderLeft, INPUT_PULLUP);
  pinMode(encoderRight, INPUT_PULLUP);
  pinMode(encoderPress, INPUT_PULLUP);
}
void loop() {
  for(int i=0;i<NUM_BUTTONS;i++){
    int r=digitalRead(buttonPins[i]);
    if(r!=lastState[i]) lastDebounce[i]=millis();
    if((millis()-lastDebounce[i])>BTN_DEBOUNCE){
      if(r!=btnState[i]){
        btnState[i]=r;
        if(btnState[i]==LOW){
          int k=KEY_F13+i; if(k>KEY_F24) k=KEY_F13+(i%12);
          Keyboard.press(k); delay(10); Keyboard.release(k);
        }
      }
    }
    lastState[i]=r;
  }
  if(millis()-lastEncTime > ENC_REPEAT){
    if(digitalRead(encoderLeft)==LOW){
      Keyboard.press(KEY_F20); delay(5); Keyboard.release(KEY_F20);
      lastEncTime=millis();
    }
    if(digitalRead(encoderRight)==LOW){
      Keyboard.press(KEY_F21); delay(5); Keyboard.release(KEY_F21);
      lastEncTime=millis();
    }
  }
  static unsigned long lastPressDeb=0;
  static int lastPressSt=HIGH;
  static int pressSt=HIGH;
  int pr=digitalRead(encoderPress);
  if(pr!=lastPressSt) lastPressDeb=millis();
  if((millis()-lastPressDeb)>50){
    if(pr!=pressSt){
      pressSt=pr;
      if(pressSt==LOW){
        Keyboard.press(KEY_F22); delay(10); Keyboard.release(KEY_F22);
      }
    }
    lastPressSt=pr;
  }
}
