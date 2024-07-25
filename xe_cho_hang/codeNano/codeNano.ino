#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <SoftwareSerial.h>
Servo myservo;
SoftwareSerial ser(2, 3);
#define SS_PIN 10
#define RST_PIN 9
#define servo 8
#define b1 A1
#define b2 A0
#define b3 7
#define CB1 digitalRead(b1)   
#define CB2 digitalRead(b2)
#define CB3 digitalRead(b3)
#define ENA 5
#define ENB 6
#define vmax 150
#define vmin 40
#define deta vmax/3
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

MFRC522::MIFARE_Key key;
int vT = 0;
int vP = 0;
int st_start = 0;////////
int gocBD = 0, gocKT = 120;
String stop_id = "";
String dd_id = "";
unsigned long time_ = 0, time_1 = 0;
void setup() {
  ser.begin(9600);
  Serial.begin(115200);
  Serial.println("Start Arduino Nano");
  SPI.begin();
  Serial.println("Start Init RFID");
  rfid.PCD_Init();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  pinMode(b1, INPUT_PULLUP);
  pinMode(b2, INPUT_PULLUP);
  pinMode(b3, INPUT_PULLUP);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  myservo.attach(servo);
  myservo.write(gocBD);
  Serial.println("Init complete");
}

void DC()
{
  static unsigned int vtT = 0, vtP = 0;
  if (vtT != vT || vtP != vP)
  {
    vtT = vT;
    vtP = vP;
    analogWrite(ENA, vT);
    analogWrite(ENB, vP);
  }
}
void readSerial() {
  String a = "";
  if (ser.available()) {
    delay(30);
    while (ser.available()) {
      char b = (char)ser.read();
      if (b != '\n')
      {
        a += b;
      }
      else
      {
        Serial.println(a);
        int index1 = -1;
        int index2 = -1;
        index1 = a.indexOf('@');
        index2 = a.indexOf('#');
        if (index1 > -1 && index2 > index1 )
        {
          String tam = a.substring(index1 + 1, index2);
          if (tam != "")
          {
            stop_id = tam;
            Serial.println(tam);
          }

        } else {
          int index1 = -1;
          int index2 = -1;
          index1 = a.indexOf('$');
          index2 = a.indexOf('%');
          if (index1 > -1 && index2 > index1 )
          {
            dd_id = a.substring(index1 + 1, index2);
            Serial.println(dd_id);
            st_start = 1;
            time_ = millis();
          }
        }
        break;
      }
    }
  }
}
void Tien(bool run_)
{
  if (run_)
  {
    byte a[3] = {CB1, CB2, CB3};
    if (!a[0]  && a[2])
    {
      vT >= vmin + deta  ? vT -= deta : vT = vmin;
      vP <= vmax - deta - 10 ? vP += deta : vP = vmax - 10 ;
    }
    else if (a[0]  && !a[2])
    {
      vP >= vmin + deta ? vP -= deta : vP = vmin;
      vT <= vmax - deta - 10 ? vT += deta : vT = vmax - 10 ;
    }
    else if (a[0]  && !a[1] && a[2])
    {
      vT <= vmax - deta - 10 ? vT += deta : vT = vmax - 10 ;
      vP <= vmax - deta - 10 ? vP += deta : vP = vmax - 10 ;
    }
    else
    {
      vP = 0;
      vT = 0;
    }
  } else {
    vP = 0;
    vT = 0;
  }
  DC();
}
void checkRFID() {
  if (  rfid.PICC_IsNewCardPresent()) {
    if (  rfid.PICC_ReadCardSerial()) {
      ///////////////////////////////
      String uid = String(rfid.uid.uidByte[0]);
      uid += String(rfid.uid.uidByte[1]);
      uid += String(rfid.uid.uidByte[2]);
      uid += String(rfid.uid.uidByte[3]);
      ser.println("$" + uid + "%");
      Serial.println("$" + uid + "%");
      if (uid == stop_id)
      {
        vT = 0;
        vP = 0;
        DC();
        st_start = 0;
      } else if (uid == dd_id) {
        vT = 0;
        vP = 0;
        DC();
        DC_gat();
      }
    }
  }
  ///////////////////////////
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
void DC_gat()
{
  for (int i = gocBD; i <= gocKT; i++)
  {
    myservo.write(i);
    delay(2);
  }
  for (int i = gocKT; i >= gocBD; i--)
  {
    myservo.write(i);
    delay(10);
  }
}
void loop() {
  if (!st_start)
  {
    if (millis() - time_1 > 3000 )
    {
      if (stop_id == "")
      {
        ser.println("$stopid%");
        Serial.println("$stopid%");
      } else {
        ser.println("$uid%");
        Serial.println("$uid%");
      }
      time_1 = millis();
    }

    readSerial();
  } else {
    Tien(st_start);
    if (millis() - time_ > 2000 && st_start)
    {
      checkRFID();
    }
  }
//Tien(1);
}
