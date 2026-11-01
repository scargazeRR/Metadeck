#include <Keyboard.h>

const int buttonPins[] = {2,3,4,5,6,7,8,9,10,14,15,16,18,19,20,21,38,39,40,41};
const int encoderPins[] = {A0,A1,A2};
const int NUM_BUTTONS = 20;
unsigned long lastDebounceTime[23] = {0};
int lastButtonState[23];
int buttonState[23];
const unsigned long debounceDelay = 50;
bool lastEncoderState[3] = {HIGH,HIGH,HIGH};

void setup() {
  Keyboard.begin();
  for(int i=0;i<NUM_BUTTONS;i++){pinMode(buttonPins[i],INPUT_PULLUP);lastButtonState[i]=HIGH;buttonState[i]=HIGH;}
  for(int i=0;i<3;i++) pinMode(encoderPins[i],INPUT_PULLUP);
}

void loop() {
  for(int i=0;i<NUM_BUTTONS;i++){
    int reading=digitalRead(buttonPins[i]);
    if(reading!=lastButtonState[i]) lastDebounceTime[i]=millis();
    if((millis()-lastDebounceTime[i])>debounceDelay){
      if(reading!=buttonState[i]){
        buttonState[i]=reading;
        if(buttonState[i]==LOW){
          int key=KEY_F13+i; if(key>KEY_F24) key=KEY_F13+(i%12);
          Keyboard.press(key); delay(20); Keyboard.release(key);
        }
      }
    }
    lastButtonState[i]=reading;
  }
  for(int i=0;i<3;i++){
    int reading=digitalRead(encoderPins[i]);
    if(reading!=lastEncoderState[i]) lastDebounceTime[NUM_BUTTONS+i]=millis();
    if((millis()-lastDebounceTime[NUM_BUTTONS+i])>debounceDelay){
      if(reading==LOW && lastEncoderState[i]==HIGH){
        int key=KEY_F20+i; Keyboard.press(key); delay(20); Keyboard.release(key);
      }
      lastEncoderState[i]=reading;
    }
  }
}
