#include <ICMPPing.h>
#include <util.h>
#include <Adafruit_SleepyDog.h>
#include <EEPROM.h>
#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>
#include <Adafruit_MCP9808.h>
#include <Adafruit_HTU21DF.h>
#include <SparkFunSX1509.h> // Include SX1509 library


//================ EEPROM Memory Map ================= 
// Address Byte       Data(8 bits)        Type                
//      0              ---- ----       MAC byte 0       
//      1              ---- ----       MAC byte 1       
//      2              ---- ----       MAC byte 2
//      3              ---- ----       MAC byte 3
//      4              ---- ----       MAC byte 4
//      5              ---- ----       MAC byte 5
//      6              ---- ----        Node ID 
//      7              ---- ----       Serial Number
//      8              ---- ----       unassigned
//      9              ---- ----       unassigned
//      10             ---- ----       unassigned
//      .              ---- ----       unassigned
//      ..             ---- ----       unassigned
//      ...            ---- ----       unassigned
//      1024           ---- ----       unassigned



// I2C addresses for the two MCP9808 temperature sensors
#define TEMP_TOP 0x1A
#define TEMP_MID 0x1B


IPAddress serverIp(10, 1, 1, 1); // Server ip address
EthernetUDP UdpRcv; // UDP object to receive packets
EthernetUDP UdpSnd; // UDP object to send packets
SOCKET pingSocket = 2; //Socket for pinging the server to monitor network connectivity; Socket 0 works for pinging but breaks the EthernetUDP
ICMPPing ping(pingSocket, (uint16_t)random(0, 255));
byte mac[6];
unsigned int rcvPort = 8888;  // Assign port to receive commands on
unsigned int sndPort = 8889;  // Assign port to send data on
unsigned long pokeTime; // Declare pokeTime variable that stores millis() value every time poke command is sent 

// Initializing buffer and data variables for receiving packets from the server
int packetSize;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
String command; // String for data


unsigned int EEPROM_SIZE = 1024;
unsigned int eeadr = 0; // MACburner.bin writes MAC addres to the first 6 addresses of EEPROM
unsigned int eeNodeAdr = 6; // EEPROM node ID address
unsigned int eeSerialAdr = 7;

// I2C digital i/o serial board
const byte SX1509_ADDRESS = 0x3E;
SX1509 io;


// Sensor objects
Adafruit_MCP9808 mcpTop = Adafruit_MCP9808(); 
Adafruit_MCP9808 mcpMid = Adafruit_MCP9808(); 
Adafruit_HTU21DF htu = Adafruit_HTU21DF();


// Wind Sensor
//#define analogPinForRV    1   // change to pins you the analog pins are using
//#define analogPinForTMP   0

// to calibrate your sensor, put a glass over it, but the sensor should not be
// touching the desktop surface however.
// adjust the zeroWindAdjustment until your sensor reads about zero with the glass over it. 

//const float zeroWindAdjustment =  .08; // negative numbers yield smaller wind speeds and vice versa.

//int TMP_Therm_ADunits;  //temp termistor value from wind sensor
//float RV_Wind_ADunits;    //RV output from wind sensor 
//float RV_Wind_Volts;
//int TempCtimes100;
//float zeroWind_ADunits;
//float zeroWind_volts;


// struct for a UDP packet
struct sensors {
  float nodeID;
  float mcpTempTop;
  float mcpTempMid;
  float htuTemp;
  float htuHumid;
//  float windSpeed_MPH;
//  float tempCAirflow;
  byte serial;
} sensorArray;



void setup() {

  Watchdog.disable(); // Disable Watchdog so it doesn't get into infinite reset loop
  
  // Initialize Serial port
  Serial.begin(57600);
  Serial.println("Running Setup..");
  

  // Setting pins appropriately. Very important to first deactivate the digital pins
  // because setting the pin as OUTPUT changes it's state and has caused problems with the reset pin 4 before
  // PSU that turns on White Rabbit is now hard wired to be turned on by the 5V Arduino signal, this prevents 
  // indefinite power cycle in case of a reset loop (which happens when ping/poke fail, the reset command was sent 
  // or all four sensors are off line.

  // Initialize and deactivate pins to avoid glitches
  // 8 way SNAP relay
  digitalWrite(2, LOW);
  pinMode(2, OUTPUT);
  digitalWrite(2, LOW);
   
  // FEM VAC pin: Active HIGH
  digitalWrite(5, LOW);
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);
  
  // PAM VAC pin: Active HIGH
  digitalWrite(6, LOW);
  pinMode(6, OUTPUT);
  digitalWrite(6, LOW);
  
  // SNAPv2_0_1: Active LOW so HIGH is off
  digitalWrite(3, HIGH);
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);

  // SNAPv2_2_3: Active LOW so HIGH is off
  digitalWrite(7, HIGH);
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);
  
  // Reset pin, Active LOW
  digitalWrite(4, HIGH);
  pinMode(4, OUTPUT); 
  digitalWrite(4, HIGH);
 
  // Find Digital IO card and initialize its pin modes 
  if (io.begin(SX1509_ADDRESS)) {
      Serial.println("Digital IO card found!");
      io.pinMode(0,INPUT);   // Serial
      io.pinMode(1,INPUT);   //   .
      io.pinMode(2,INPUT);   //   .
      io.pinMode(3,INPUT);   //   .
      io.pinMode(4,INPUT);   //   .
      io.pinMode(5,INPUT);   //   .
      io.pinMode(6,INPUT);   // Rev Number
      io.pinMode(7,INPUT);   //   .
      io.pinMode(8,INPUT);   // 1=production, 0=prototype
      io.pinMode(9,INPUT);   //  TBD
      io.pinMode(10,INPUT);  //   .
      io.pinMode(11,INPUT);  //   .
      io.pinMode(12,OUTPUT); //   .
      io.pinMode(13,OUTPUT); //   .
      io.pinMode(14,OUTPUT); //   .
      io.pinMode(15,OUTPUT); //   .
      
      for (int i=0; i<6; i++){
          sensorArray.serial |= io.digitalRead(i) << i; 
      }
      EEPROM.write(eeSerialAdr, sensorArray.serial);
  }
  else {
    Serial.println("Digital io card not found"); 
  }

  
  // Read MAC address from EEPROM (burned previously with MACburner.bin sketch)
  for (int i = 0; i < 6; i++){
    mac[i] = EEPROM.read(eeadr);
    ++eeadr;
    }
  // Read node ID from EEPROM (burned with MACburner.bin sketch) and assign it to struct nodeID member
  sensorArray.nodeID = EEPROM.read(eeNodeAdr);
  Serial.println("EEPROM contents:");
  for (int i = 0; i < 8; i++) {
    Serial.println("Address: ");
    Serial.print(i);
    Serial.print("\t");
    Serial.print("Data: ");
    Serial.print(EEPROM.read(i));
    Serial.print("\t");
  }
  
  // Enable Watchdog for 8 seconds
  Watchdog.enable(8000);
  
  // Start Ethernet connection, automatically tries to get IP using DHCP
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP, restarting sketch...");
    // Delay so the watchdog timer resets in case ethernet setup fails
    delay(10000);
  }
  Serial.println("Configured IP:");
  Serial.println(Ethernet.localIP());
  // Start UDP
  UdpRcv.begin(rcvPort);
  UdpSnd.begin(sndPort);
  delay(1500); // delay to give time for initialization
}

 
void loop() {
   
  ICMPEchoReply echoReply = ping(serverIp, 4); //takes about 7295 ms to fail
  Watchdog.reset();
 
  if (echoReply.status == SUCCESS){

    // Find top temp sensor and read its value
    if (mcpTop.begin(TEMP_TOP)) {
      sensorArray.mcpTempTop = mcpTop.readTempC();
      Watchdog.reset();
    }
    else {
      Serial.println("MCP9808 TOP not found");
    }

    
    // Find middle temp sensor and take read value
    if (mcpMid.begin(TEMP_MID)) {
      sensorArray.mcpTempMid = mcpMid.readTempC();
      Watchdog.reset();
    }
    else {
      Serial.println("MCP9808 MID not found"); 
    }
    Watchdog.reset();
    
    
    // Read humidity and temperature from HTU21DF sensor
    if (htu.begin()) {
      sensorArray.htuTemp = htu.readTemperature();
      sensorArray.htuHumid = htu.readHumidity();
    }
    else {
      Serial.println("HTU21DF not found!");
    }
    Watchdog.reset();


    // If none of the sensors are operating, shut down the powersupply to snaps, FEM and PAM.:
    //if (!mcpMid.begin(TEMP_MID) & !mcpTop.begin(TEMP_TOP) & !htu.begin()){
     // shutdownall();
      //bootReset();
    //}
//    // Wind Sensor
//    TMP_Therm_ADunits = analogRead(analogPinForTMP);
//    RV_Wind_ADunits = analogRead(analogPinForRV);
//    RV_Wind_Volts = (RV_Wind_ADunits *  0.0048828125);
//
//    // these are all derived from regressions from raw data as such they depend on a lot of experimental factors
//    // such as accuracy of temp sensors, and voltage at the actual wind sensor, (wire losses) which were unaccouted for.
//    TempCtimes100 = (0.005 *((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits)) - (16.862 * (float)TMP_Therm_ADunits) + 9075.4;  
//    sensorArray.tempCAirflow = TempCtimes100/100.0;
//    zeroWind_ADunits = -0.0006*((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits) + 1.0727 * (float)TMP_Therm_ADunits + 47.172;  //  13.0C  553  482.39
//
//    zeroWind_volts = (zeroWind_ADunits * 0.0048828125) - zeroWindAdjustment;  
//
//    // This from a regression from data in the form of 
//    // Vraw = V0 + b * WindSpeed ^ c
//    // V0 is zero wind at a particular temperature
//    // The constants b and c were determined by some Excel wrangling with the solver.
//    
//   
//    sensorArray.windSpeed_MPH =  pow(((RV_Wind_Volts - zeroWind_volts) /.2300) , 2.7265); 
//    Serial.println("Windspeed RAW:");
//    Serial.println(RV_Wind_Volts);
//    Serial.println("Windspeed_MPH");
//    Serial.println(sensorArray.windSpeed_MPH);
//    Serial.println("TempCairflow:");
//    Serial.println(sensorArray.tempCAirflow);   
//    //Serial.print("  TMP volts ");
//    //Serial.print(TMP_Therm_ADunits * 0.0048828125);
//    
//    //Serial.print(" RV volts ");
//    //Serial.print((float)RV_Wind_Volts);
//
//    //Serial.print("TempC");
//    //Serial.print(sensorArray.tempCAirflow);
//
//    //Serial.print("   ZeroWind volts ");
//    //Serial.print(zeroWind_volts);
//
//    //Serial.print("   WindSpeed MPH ");
//    //Serial.println(sensorArray.windSpeed_MPH);
      
    
    // Send UDP packet to the server ip address serverIp that's listening on port sndPort
    UdpSnd.beginPacket(serverIp, sndPort); // Initialize the packet send
    UdpSnd.write((byte *)&sensorArray, sizeof sensorArray); // Send the struct as UDP packet
    UdpSnd.endPacket(); // End the packet
    Serial.println("UDP packet sent...");
    Watchdog.reset();  
    
    // Clear UDP packet buffer before sending another packet
    memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE);
  
   
    // Check if request was sent to Arduino
    packetSize = UdpRcv.parsePacket(); // Reads the packet size
    
    if(packetSize>0) { //if packetSize is >0, that means someone has sent a request
  
      UdpRcv.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE); //Read the data request
      String command(packetBuffer); //Convert char array packetBuffer into a string called command
      
      if (command == "poke") {
          Serial.println("I've been poked!");
          pokeTime = millis();  
      }
      
      else if (command == "snapRelay_on") {
        digitalWrite(2, HIGH);
      }     
      
      else if (command == "snapRelay_off") {
        digitalWrite(2, LOW);
      }
      
      else if (command == "FEM_on") {
        digitalWrite(5, HIGH);
      }
      
      else if (command == "FEM_off") {
        digitalWrite(5, LOW);
      }
      
      else if (command == "PAM_on") {
        Serial.println("PAM on");
        delay(100);
        digitalWrite(6, HIGH);
      }
      
      else if (command == "PAM_off") {
        digitalWrite(6, LOW);
      }
      
      else if (command == "snapv2_0_1_on"){
        Serial.println("snapv2_0_1 on");
        digitalWrite(3, LOW);
        }
      else if (command == "snapv2_0_1_off"){
        Serial.println("snapv2_0_1 off");
        digitalWrite(3, HIGH);
        }
      else if (command == "snapv2_2_3_on"){
        Serial.println("snapv2_2_3 on");
        digitalWrite(7, LOW);
        }
      else if (command == "snapv2_2_3_off"){
        Serial.println("snapv2_2_3 off");
        digitalWrite(7, HIGH);
        }
        
      else if (command == "reset") {
        bootReset();
        }

      else if (command == "start") {
        startall();
          }
      
      else if (command == "shutdown") {
        shutdownall();
      }
     
    }

    //clear out the packetBuffer array
    memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE); 
    
    // Renew DHCP lease - times out eventually if this is removed
    Ethernet.maintain();

    // stroke the watchdog just in case
    Watchdog.reset();
   
    // Check the time elapsed since the last poke 
    // signal from the server. Reset bootloader 
    // in attempt to reestablish connection. 
    if ((millis()-pokeTime) > 10000){
      Serial.println("Haven't received a server poke in ");
      Serial.print(millis()-pokeTime);
      Serial.println("Resseting bootloader..");
      delay(200);
      bootReset();
    }  
   
   }
   else {
     
     Serial.println("Server ping unsuccessful. Restarting.");
     bootReset();
   
   }

   
  
}

void startall(){
  
  // Turn PAM on
  Serial.println("PAM on");
  digitalWrite(6, HIGH);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  
  // Turn FEM on
  digitalWrite(5, HIGH);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();

  // Turn 8 way snap relay on
  Serial.println("SNAP relay on");
  digitalWrite(2, HIGH);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  
  // Turn SNAPv2 0 and 1 on
  Serial.println("snapv2_0_1 on");
  digitalWrite(3, LOW);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();

  // Turn SNAPv2 2 and 3 on
  Serial.println("snapv2_2_3 on");
  digitalWrite(7, LOW);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  
  
}

void shutdownall(){

  Serial.println("Shutdown initiated"); 
  // Turn off FEM; inactive LOW
  digitalWrite(5, LOW);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  
  // Turn off PAM; inactive LOW
  digitalWrite(6, LOW);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();

  // Turn off snapv2_0_1; inactive HIGH
  digitalWrite(3, HIGH);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();

  // Turn off snapv2_2_3; inactive HIGH
  digitalWrite(7, HIGH);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();

  // Turn off 8 way snap relay; inactive LOW
  digitalWrite(2, LOW);
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
  delay(5000);
  Watchdog.reset();
   
  // When shutdown function is called, it turns off all 
  // controllable power supplies and precedes to bootloader
  // reset 
  //bootReset();

}

void bootReset(){
   Serial.println("Resetting Bootloader..");
   delay(500);
   digitalWrite(4, LOW);  
}



