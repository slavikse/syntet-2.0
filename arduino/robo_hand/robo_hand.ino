#include <SoftwareSerial.h>
#include <Servo.h>

// free pins: 7,8

#define TX_PIN 3
#define RX_PIN 2

#define LED_RED_PIN 4
#define LED_GREEN_PIN 5

#define SERVO_HOR_PIN 9
#define SERVO_VERT_LEFT_PIN 12
#define SERVO_VERT_RIGHT_PIN 13
#define SERVO_GRAB_LEFT_PIN 11
#define SERVO_GRAB_RIGHT_PIN 10

#define BUFFER_SIZE 128
#define BAUD 9600
#define PORT 80

#define WAITING_RESPONSE 5000
#define SETUP_DELAY 2000
#define PRINT_DELAY 1000

#define SERVO_HOR_CENTER 120
#define SERVO_STEP 10
#define SERVO_DELAY 200

SoftwareSerial ESP8266(TX_PIN, RX_PIN);

const String SSID = "cats2.4";
const String PASS = "Greeting_Style443";

Servo servoHor;
Servo servoVertLeft;
Servo servoVertRight;
Servo servoGrabLeft;
Servo servoGrabRight;

bool isBusy = true;

// > +IPD,0,358:GET /1 HTTP/1.1
// "%d,%d", &channelId, &packageLen
char buffer[BUFFER_SIZE];

void setup() {
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);

  digitalWrite(LED_RED_PIN, HIGH);

  Serial.begin(BAUD);
  Serial.setTimeout(WAITING_RESPONSE);
  serialsDebug();

  ESP8266.begin(BAUD);
  clearESP8266Buffer();
  configWiFi();

  servoHor.attach(SERVO_HOR_PIN);
  servoVertLeft.attach(SERVO_VERT_LEFT_PIN);
  servoVertRight.attach(SERVO_VERT_RIGHT_PIN);
  servoGrabLeft.attach(SERVO_GRAB_LEFT_PIN);
  servoGrabRight.attach(SERVO_GRAB_RIGHT_PIN);

  resetServo();
  delay(1000);

  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, HIGH);

  isBusy = false;
}

void loop() {
  processingRequests();
}

void clearESP8266Buffer() {
  while (ESP8266.available() > 0) {
    ESP8266.read();
  }
}

// https://esp8266.ru/esp8266-at-commands-v022
void configWiFi() {
  ESPCommand("AT+RST", WAITING_RESPONSE);
  // ESPCommand("AT+UART=" + String(BAUD) + ",8,1,0,0", SETUP_DELAY);
  // 1=Station (WiFi client), 2=SoftAP (WiFi hot spot), 3=Station+SoftAP | AT+CWMODE_DEF=1
  ESPCommand("AT+CWMODE=1", SETUP_DELAY);

  connectWiFi();

  ESPCommand("AT+CIPMODE=0", SETUP_DELAY);
  ESPCommand("AT+CIPMUX=1", SETUP_DELAY);
  ESPCommand("AT+CIPSERVER=1," + String(PORT), SETUP_DELAY);
  ESPCommand("AT+CIPSTO=2", SETUP_DELAY);
  Serial.println(ESPCommand("AT+CIFSR", SETUP_DELAY));
  // Serial.println(ESPCommand("AT+PING=\"ya.ru\"", SETUP_DELAY));
}

void connectWiFi() {
  String command = "AT+CWJAP=\"";
  command += SSID;
  command += "\",\"";
  command += PASS;
  command += "\"";

  Serial.println(ESPCommand(command, WAITING_RESPONSE));
}

String ESPCommand(String command, int wait) {
  ESP8266.println(command);
  delay(wait);

  String response = "";

  while (ESP8266.available() > 0) {
    char c = ESP8266.read();
    response += c;

    if (response.indexOf(command) > -1) {
      response = "";
    } else {
      response.trim();
    }
  }

  return response;
}

void processingRequests() {
  if (isBusy) {
    return;
  }

  char answer[] = "+IPD,";

  ESP8266.readBytesUntil('\n', buffer, BUFFER_SIZE);

  if (strncmp(buffer, answer, strlen(answer)) == 0) {
    int channelId;
    int packageLen;

    sscanf(buffer + strlen(answer), "%d,%d", &channelId, &packageLen);

    if (packageLen > 0) {
      char *pb = buffer + strlen(answer);

      while(*pb != ':') {
        pb++;
      }

      pb++;
      httpActions(channelId, answer, pb);
    }
  }

  clearBuffer();
}

void httpActions(int channelId, char answer[], char* pb) {
  if (strncmp(pb, "GET / ", strlen(answer) + 1) == 0) {
    isBusy = true;
    httpRequest(channelId, httpRespone());
    isBusy = false;
  } else if (strncmp(pb, "GET /1", strlen(answer) + 1) == 0) {
    isBusy = true;
    httpRequest(channelId, "1");

    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);

    servoTop();
    scenarioObject();
    delay(1000);
    scenarioGreen();
    delay(1000);

    isBusy = false;
    digitalWrite(LED_RED_PIN, LOW);
    digitalWrite(LED_GREEN_PIN, HIGH);
  } else if (strncmp(pb, "GET /2", strlen(answer) + 1) == 0) {
    isBusy = true;
    httpRequest(channelId, "2");

    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);

    servoTop();
    scenarioObject();
    delay(1000);
    scenarioWhite();
    delay(1000);

    isBusy = false;
    digitalWrite(LED_RED_PIN, LOW);
    digitalWrite(LED_GREEN_PIN, HIGH);
  } else {
    isBusy = false;
  }
}

void httpRequest(byte channelId, String content) {
  String headers = "HTTP/1.1 200 OK\r\n";
  // when sending a request to the server
  // "GET / HTTP/1.1\r\nHost: \"" + HOST + "\"\r\nConnection: close\r\n";
  headers += "Content-Type: text/html\r\n";
  headers += "Connection: close\r\n";
  headers += "Content-Length: " + content.length();
  headers += "\r\n\r\n";

  // ESP8266.print("AT+CIPSTART=\"TCP\",\"" + HOST + "\"," + PORT + "\r\n", PRINT_DELAY);
  ESP8266.print("AT+CIPSEND=");
  ESP8266.print(channelId);
  ESP8266.print(",");
  ESP8266.println(headers.length() + content.length());
  delay(20);

  char invitation[] = ">";

  if (ESP8266.find(invitation)) {
    ESP8266.print(headers);
    ESP8266.print(content);
    delay(200);
  }
}

String httpRespone() {
  String content = "<head>";
  content += "<meta name=viewport content=width=device-width>";
  content += "<meta charset=utf-8>";
  content += "<style>body{margin:2px;display:flex;flex-wrap:wrap;justify-content:center;gap:10px}button{font-size:80px}</style>";
  content += "<script>s=c=>fetch(c)</script>";
  content += "</head>";

  content += "<h1>Готов!</h1>";
  // content += "<button onclick=s(1)>👆</button>";

  return content;
}

void resetServo() {
  servoGrabRelease();
  delay(1000);
  servoTop();
  delay(1000);
  servoCenter();
}

void servoCenter() {
  servoHor.write(120);
}

void servoTop() {
  servoVertLeft.write(160);
  servoVertRight.write(25);
}

void servoBottom() {
  servoVertLeft.write(45);
  servoVertRight.write(135);
}

void servoLeft() {
  servoHor.write(180);
}

void servoRight() {
  servoHor.write(20);
}

void servoGrab() {
  servoGrabLeft.write(15);
  servoGrabRight.write(160);
}

void servoGrabRelease() {
  servoGrabLeft.write(120);
  servoGrabRight.write(70);
}

void scenarioObject() {
  servoCenter();
  delay(1000);
  servoBottom();
  delay(1000);
  servoGrab();
  delay(1000);
  servoTop();
}

void scenarioGreen() {
  servoLeft();
  delay(1000);
  servoDrop();
}

void scenarioWhite() {
  servoRight();
  delay(1000);
  servoDrop();
}

void servoDrop() {
  servoBottom();
  delay(1000);
  resetServo();
}

// void async() {
//   lastDebounceTime = millis();
//   if ((millis() - lastDebounceTime) > debounceDelay) {}
// }

void clearBuffer() {
  for (byte i = 0; i < BUFFER_SIZE; i++) {
    buffer[i] = 0;
  }
}

void serialsDebug() {
  if (ESP8266.available() > 0) {
    Serial.write(ESP8266.read());
  }

  if (Serial.available() > 0) {
    ESP8266.write(Serial.read());
  }
}
