# Portable-RFID-card-reader-using-MQTT    
Portable RFID Card reader  
Card reader console - Raspberry Pi  
Card Reader - RFID-RC522  
Display - 0.96 inch SSD1306 128x64 resolution OLED display  
Database - MySQL  
Connection protocol - MQTT  
MQTT Broker - Ubuntu 22.04 Desktop  

The project is about creating a portable RFID card reader for attendance marking that saves the attendance to the server using MQTT protocol. The entire project uses Python for the code base. Python is used to handle saving of data to the MySQL database using MySQL connector, handling MQTT services like sending and receiving messages through specific channels, interfacing 0.96 inch SSD1306 128x64 resolution OLED display and RFID-RC522 card reader with the Raspberry Pi in the client side code, and also the user interaction during privileged mode to add new card data or delete existing card data from the database in the server side. In both server and client the data is saved in MySQL database. The server here is Ubuntu 22.04 Desktop. Here MQTT protocol is used to send the data to the server. The server acts as the broker for the MQTT services. When a recognized card is detected the data is saved locally in th Raspberri Pi device, used as card reader, and also it is sent to the server using via selected MQTT channel.

![photo_6260373223350845226_y](https://github.com/ca11mejp/Portable-RFID-card-reader-using-MQTT/assets/13674947/fee8e4dd-9b8f-4f5e-aca9-78c6a901a47a)

![photo_6260373223350845222_y](https://github.com/ca11mejp/Portable-RFID-card-reader-using-MQTT/assets/13674947/b08971b9-2f94-4764-b9da-90421d49ac5e)
