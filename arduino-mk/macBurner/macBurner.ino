#include <EEPROM.h>
#include <Ethernet.h>
#include <EthernetUdp.h>


//================ EEPROM Memory Map ================= 
// Address Byte       Data(8 bits)        Type                
//      0              ---- ----       MAC byte 0       
//      1              ---- ----       MAC byte 1       
//      2              ---- ----       MAC byte 2
//      3              ---- ----       MAC byte 3
//      4              ---- ----       MAC byte 4
//      5              ---- ----       MAC byte 5
//      6              ---- ----        Node ID 
//      7              ---- ----       unassigned
//      8              ---- ----       unassigned
//      9              ---- ----       unassigned
//      10             ---- ----       unassigned
//      .              ---- ----       unassigned
//      ..             ---- ----       unassigned
//      ...            ---- ----       unassigned
//      1024           ---- ----       unassigned


unsigned int nodeID = 0;

unsigned int eeadr = 0; 
unsigned int eeNodeAdr = 6; // EEPROM addres that will store node ID number

byte mac[] = {0x00, 0x08, 0xDC, 0x00, 0x00, 0x6A}; //Assign MAC address of the Arduino here

unsigned int localPort = 8888; // Assign a port to talk over
int packetSize;

EthernetUDP Udp; // UDP object

IPAddress serverIp(10, 1, 1, 1); // Server ip address
EthernetUDP UdpSer; // UDP object to print serial debug info

unsigned int serPort = 8890;  // Assign port to print debug statements



// For future use; initializing buffer and data variables for receiving packets from the server
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
String datReq; // String for data

void serialUdp(String);


void setup() {
  Serial.begin(9600);
  
  // burn MAC to first 6 EEPROM bytes
  for (int i = 0; i < 6; i++){
    EEPROM.write(eeadr, mac[i]);
    ++eeadr;
    }
    
  // burn node ID to the 7th EEPROM byte  
  EEPROM.write(eeNodeAdr, nodeID);

  // Zero all the other EEPROM cells - 255 is the default in each cell with an off the shelf Arduino
  for (int i = 7; i < 1024; i++){
    EEPROM.write(i,0);
  }  
 
  // Print out the contents of EEPROM
  for (int i = 0; i < 8; i++) {
    serialUdp("Printing the contents of EEPROM");
    serialUdp("Address: ");
    serialUdp(String(i));
    Serial.print("Data: ");
    Serial.print(String(EEPROM.read(i)));

  } 

  // Start Ethernet connection, automatically tries to get IP using DHCP
  if (Ethernet.begin(mac) == 0) {

    serialUdp("Failed to configure Ethernet using DHCP");
    for (;;)
      ;
  }
  serialUdp("IP address:");
  serialUdp(String(Ethernet.localIP()));
  
  // Start UDP
  Udp.begin(localPort);
  delay(1500); // delay to give time for initialization

  // Set Pin 4 as the reset pin
  pinMode(4, OUTPUT);
  digitalWrite(4, HIGH);

  
}




void loop() {
   // Check if request was sent to Arduino
    packetSize = Udp.parsePacket(); //Reads the packet size
    serialUdp("Waiting to receive the reset command..");
    
    if (packetSize>0) { //if packetSize is >0, that means someone has sent a request
  
      Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE); //Read the data request
      String datReq(packetBuffer); //Convert char array packetBuffer into a string called datReq
    
      if (datReq == "reset") {
        
        serialUdp("Resetting the microcontroller...");
        digitalWrite(4, LOW);
      }   
      
    }

}


void serialUdp(String message){
  UdpSer.beginPacket(serverIp, serPort);
  UdpSer.print(message);
  UdpSer.endPacket();
  memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE);
  }

