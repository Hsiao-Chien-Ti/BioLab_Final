#include <SoftwareSerial.h>;   // 引用程式庫

// 定義連接藍牙模組的序列埠, UNO D8->BT TX, UNO D9->BT RX
SoftwareSerial BT(8, 9); // 接收腳, 傳送腳
char val;  // 儲存接收資料的變數

void setup() {
  Serial.begin(38400);   // 與電腦序列埠連線
  Serial.println("BT is ready!");

  // 設定藍牙模組的連線速率
  // 如果是HC-05，請改成38400
  // 如果是HC-06，請改成9600
  BT.begin(38400);
  delay(5000);   
  // BT.println( "AT" );
  BT.println( "AT+UART=115200,0,0" );
  // BT.println( "AT+UART" ); 
  // BT.println( "AT+NAME=adi" );
}

void loop() {
  // if (Serial.available()>0) {
  //   val = Serial.read();
    // BT.println( "AT+UART" );
  //   Serial.println(val);
  //   BT.println(val);
  // }
  if (BT.available()>0) {
    val = BT.read();
    Serial.print(val);
  }
}