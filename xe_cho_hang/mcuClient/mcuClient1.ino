#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>
#include <Wire.h>
SoftwareSerial swSer(12, 14);
#define   LED0      2
#define   ssid      "FECT CLUB"
#define   pass      "666888999"
String host1 = "http://192.168.1.112:81/agv/";
String host2 = "http://192.168.1.112:81/agv/";
WiFiClient client;
HTTPClient http;
//String data = "", data_temp;
bool send_Request(byte stt, String data = "") {
  bool st = false;
  static String host = host1;
  Serial.println(host);
  for (int i = 0; i < 2; i++)
  {
    if (http.begin(client, host + "getvitri.php?stt=" + String(stt) + "&uid=" + data)) { // HTTP
      int httpCode = http.GET();
      if (httpCode > 0) {
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = http.getString();
          Serial.println(payload);
          st = 1;
          if (payload != "None")
          {
            swSer.println(payload);
          }
           break;
        }
      } else {
        if (host == host2)
        {
          host = host1;
        } else
        {
          host = host2;
        }
      }
      http.end();
    } else {
      if (host == host2)
      {
        host = host1;
      } else
      {
        host = host2;
      }
      Serial.printf("[HTTP} Unable to connect\n");
    }
  }
  return st;
}
void setup() {
  Serial.begin(115200);
  swSer.begin(9600);
//  ESP.eraseConfig();
//  WiFi.persistent(false);
//  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP(ssid, pass);
  delay(1000);
  pinMode(LED0, OUTPUT);
  Checkid_stop();
}
void Checkid_stop()
{
  while (!send_Request(4))
  {
    for (int i = 0; i < 4; i++)
    {
      digitalWrite(LED0, LOW);
      delay(250);
      digitalWrite(LED0, HIGH);
      delay(250);
    }
  }
  digitalWrite(LED0, LOW);
}
void readSerial() {
  if (swSer.available()) {
    delay(100);
    String data1 = "";
    while (swSer.available() > 0)
    {
      char b = (char)swSer.read();
      if (b != '\n')
      {
        data1 += b;
      } else {
        Serial.println(data1);
        int index1 = -1, index2 = -1;
        index1 = data1.indexOf("$");
        index2 = data1.indexOf("%");
        if (index1 >= 0 && index2 > index1)
        {
          String tam = data1.substring(index1 + 1, index2);
          Serial.println(tam);
          if (tam != "")
          {
            if (tam == "uid")
            {
              send_Request(3);
            }
            else if (tam == "stopid")
            {
              send_Request(4);
            }
            else
            {
              send_Request(5, tam);
            }
            delay(100);
          }
          break;
        }
      }
    }
  }
}
void loop () {
  readSerial();
}
