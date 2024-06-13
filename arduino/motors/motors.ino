#include <SoftwareSerial.h>

// free pins: 0,1,2,9,10,11,12,13

#define TX_PIN 6
#define RX_PIN 3
#define BUFFER_SIZE 128
#define BAUD 9600
#define PORT 80

#define M1_DIR_PIN 4
#define M2_DIR_PIN 7
#define M1_SPEED_PIN 5
#define M2_SPEED_PIN 8 // jumper 6 -> 8
#define POWER_MAX 255
#define POWER_MIN 0
#define TRAVEL_TIME 300 // 9v
#define TURN_TIME 100 // ~45deg (9v)

#define WAITING_RESPONSE 5000
#define SETUP_DELAY 300
#define PRINT_DELAY 1000

SoftwareSerial ESP8266(TX_PIN, RX_PIN);

const String SSID = "cats2.4";
const String PASS = "Greeting_Style443";
// const String HOST = "";

// Motors pins: M1 M2
const byte MOTORS_PINS[] = {
  M1_DIR_PIN,
  M2_DIR_PIN,
  M1_SPEED_PIN,
  M2_SPEED_PIN,
};

// > +IPD,0,358:GET /1 HTTP/1.1
// "%d,%d", &channelId, &packageLen
char buffer[BUFFER_SIZE];

void setup() {
  Serial.begin(BAUD);
  Serial.setTimeout(WAITING_RESPONSE);

  for (byte i = 0; i < sizeof(MOTORS_PINS) / sizeof(byte); i++) {
    pinMode(MOTORS_PINS[i], OUTPUT);
  }

  serialsDebug();

  ESP8266.begin(BAUD);
  clearESP8266Buffer();
  configWiFi();
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
    httpRequest(channelId, httpRespone());
  } else if (strncmp(pb, "GET /1", strlen(answer) + 1) == 0) {
    httpRequest(channelId, "1");
    executeTask("top");
  } else if (strncmp(pb, "GET /2", strlen(answer) + 1) == 0) {
    httpRequest(channelId, "2");
    executeTask("bottom");
  } else if (strncmp(pb, "GET /3", strlen(answer) + 1) == 0) {
    httpRequest(channelId, "3");
    executeTask("left");
  } else if (strncmp(pb, "GET /4", strlen(answer) + 1) == 0) {
    httpRequest(channelId, "4");
    executeTask("right");
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
  content += "<style>body{margin:.5rem;display:grid;gap:.5rem}button{font-size:5rem}</style>";
  content += "<script>s=c=>fetch(c)</script>";
  content += "</head>";

  content += "<button onclick=s(1)>👆</button>";
  content += "<button onclick=s(2)>👇</button>";
  content += "<button onclick=s(3)>👈</button>";
  content += "<button onclick=s(4)>👉</button>";

  return content;
}

void executeTask(String command) {
  if (command == "stop") {
    stopMachine();
  } else if (command == "top") {
    motorsControl(LOW, HIGH, POWER_MAX, POWER_MAX);
    delay(TRAVEL_TIME);
    stopMachine();
  } else if (command == "bottom") {
    motorsControl(HIGH, LOW, POWER_MAX, POWER_MAX);
    delay(TRAVEL_TIME);
    stopMachine();
  } else if (command == "left") {
    motorsControl(LOW, LOW, POWER_MAX, POWER_MAX);
    delay(TURN_TIME);
    stopMachine();
  } else if (command == "right") {
    motorsControl(HIGH, HIGH, POWER_MAX, POWER_MAX);
    delay(TURN_TIME);
    stopMachine();
  }
}

void stopMachine() {
  motorsControl(LOW, LOW, POWER_MIN, POWER_MIN);
}

void motorsControl(byte direction1, byte direction2, byte power1, byte power2) {
  digitalWrite(M1_DIR_PIN, direction1);
  digitalWrite(M2_DIR_PIN, direction2);

  analogWrite(M1_SPEED_PIN, power1);
  analogWrite(M2_SPEED_PIN, power2);
}

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
