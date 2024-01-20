import paho.mqtt.client as mqtt
import mysql.connector
import RPi.GPIO as GPIO
import time
import logging
from datetime import datetime
from mfrc522 import SimpleMFRC522
from mysql.connector import Error
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont


logging.basicConfig(level=logging.INFO)

wait=time.sleep
state=0

#mqtt callbacks

def on_log(client, userdata, level, buf):
    logging.info(buf)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        logging.info("Client connected ok")
    else:
        logging.info("Bad connection returned code= "+str(rc))
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    logging.info("Client disconnected ok")

def on_subscribe():
    logging.info("Subscribed")

def on_publish(client, userdata, mid):
    logging.info("In on_publish callback mid=" +str(mid))

def on_message(client, userdata, message):
    topic=message.topic
    global state
    state=1
    rcv=str(message.payload.decode('utf-8'))
    pty(rcv)
    

def reset():
    ret=client1.publish('channel/main', '', 0, True)
    

#local mysql connection
def db_connect():
    try:
        global connection
        global cursor
        
        connection=mysql.connector.connect(host='localhost',
                                           database='attendance',
                                           user='root',
                                           password='password')
        if connection.is_connected():
            cursor=connection.cursor(buffered=True)
            logging.info("Database ready")

    except Error as e:
        logging.info("Error while connecting to mysql: ", e)


#I2C OLED display connected to Raspberry Pi and its functions
serial = i2c(port=1, address=0x3c)
device=ssd1306(serial)
FontTemp= ImageFont.truetype("./Unbounded-Regular.ttf", 18)

def ready():
    device.clear()
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline='white')
        draw.text((1,0), "Ready", font=FontTemp, fill="white")
        
def pty_display():
    device.clear()
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline='white')
        draw.text((1,0), "Admin", font=FontTemp, fill="white")
        
def logging_display():
    device.clear()
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline='white')
        draw.text((1,0), "Logging", font=FontTemp, fill="white")

def auth_display_y():
    device.clear()
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline='white')
        draw.text((1,0), "Authorized", font=FontTemp, fill="white")

def auth_display_n():
    device.clear()
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline='white')
        draw.text((1,0), "Not", font=FontTemp, fill="white")
        draw.text((1,20), "Authorized", font=FontTemp, fill="white")

#RFID-RC522 rfid card reader function to read
def c_read():
    try:
        uid, text = reader.read()
        print(uid)
    finally:
        GPIO.cleanup()
    return uid
        
#interaction with server when admin card is detected
def tp_lvl(uid):
    snd="0 Nil "+str(uid)
    print(snd)
    client1.publish('channel/main', snd, qos=2)
    while state==0:
        client1.on_message=on_message
        print(state)
        wait(2)
    logging.info("Priority mode ended")
    
#prioritymode or admin privileges given when admin card is detected
def pty(rcv):
    msg=rcv.split()
    print(msg[0])
    if msg[0]=='2':
        print("save")
        ad(msg)
    elif msg[0]=='3':
        print("dlt")
        dlt(msg)
    else:
        logging.info("Nothing is going to happen")

#check whether the card is registered in the database
def chck(UID):
    print(UID)
    sql="SELECT * FROM ID_INFO WHERE UID= %s" %(UID)
    print(sql)
    cursor.execute(sql)
    connection.commit()
    result=cursor.fetchall()
    return result

#log card to database and send the log to server
def log(msg):
    record=chck(msg)
    print(record)
    if record:
        sql="INSERT INTO ATT_LOG (ID, NAME, UID, TIME, DATE) VALUES (%s, %s, %s, %s, %s)"
        now = datetime.now()
        time=now.strftime("%H%M%S")
        date=now.strftime("%Y-%m-%d")
        values=(record[0][0],record[0][1], record[0][2], time, date,)
        cursor.execute(sql,values)
        connection.commit()
        logging.info("Authorized")
        auth_display_y()
        msg="1 "+str(record[0][0])+" "+record[0][2]+" "+record[0][1]+" "+time+" "+date
        client1.publish('channel/main', msg, qos=2)

    else:
        logging.info("Not Authorized")
        auth_display_n()

#add new card (admin control, card user info received from server)
def ad(msg):
    sql="INSERT INTO ID_INFO(NAME, UID) VALUES (%s, %s)"
    values=(msg[3], msg[2])
    cursor.execute(sql,values)
    connection.commit()
    logging.info("Entry added")

#delete card (admin control, card uid to be deleted received from the server)
def dlt(msg):
    UID=msg[2]
    sql="DELETE FROM ID_INFO WHERE UID= "+ UID
    cursor.execute(sql)
    connection.commit()
    sql="SELECT MAX(ID) FROM ID_INFO"
    result=cursor.execute(sql)
    connection.commit()
    if result==None:
        max_id=101
    else:
        max_id=result[0][0]
    sql="ALTER TABLE ID_INFO AUTO_INCREMENT=%s" %(max_id)
    cursor.execute(sql)
    connection.commit()
    logging.info("Entry deleted")
    sql="SELECT MAX(INDX) FROM ATT_LOG"
    result=cursor.execute(sql)
    connection.commit()
    if result==None:
        max_indx=1
    else:
        max_indx=result[0][0]
    sql="ALTER TABLE ATT_LOG AUTO_INCREMENT=%s" %(max_indx)
    cursor.execute(sql)
    connection.commit()


#main
db_connect()
Broker='165.232.183.7'
mqtt.Client.connected_flag=False
client1=mqtt.Client('Reader')
client1.username_pw_set('jp', password='startmqtt')
client1.on_log=on_log
client1.on_connect=on_connect
client1.on_disconnect=on_disconnect
client1.on_publish=on_publish
client1.connect(Broker)
client1.loop_start()

#when connection not established with the channel
while not client1.connected_flag:
    logging.info("In wait loop client1")
    wait(2)
wait(3)

client1.subscribe('channel/back', qos=2)

reader = SimpleMFRC522()

#main loop
while True:
    logging.info("Inside main while loop")
    ready()
    uid=c_read()
    #if admin card is scanned admin privileges are obtained
    if uid==786037433005:
        logging.info("Priority mode")
        pty_display()
        #uid='123'
        wait(2)
        tp_lvl(c_read())
        state=0
    #else the card that is read is checked with the database and logged
    else:
        logging.info("Logging")
        logging_display()
        result=log(uid)
        wait(3)

#closing all operations
device.clear()
client1.loop_stop()
client1.disconnect()
cursor.close()
connection.close()
