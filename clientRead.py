# --------------------------------File on client--------------------------------
# Reads

import ArmControlLib as ACL
import ftplib
import RoboPiLib_pwm as RPL
import time
RPL.RoboPiInit("/dev/ttyAMA0", 115200)


def ftpSetup():
    gFile = open("IPinfo.txt", "r")
    buff = gFile.read()
    gFile.close()
    ip_info_array = buff.split()
    ipNum = ip_info_array[0]
    userName = ip_info_array[1]
    passWord = ip_info_array[2]
    return ftplib.FTP(ipNum, userName,
                      passWord)  # host computer info


def ftpInfoUpdate():
    print "Update FTP Info"
    gFile = open("IPinfo.txt", "r+")
    gFile.write(raw_input("IPAddress:"))
    gFile.write(" ")
    gFile.write(raw_input("UserName:"))
    gFile.write(" ")
    gFile.write(raw_input("PassWord"))
    gFile.close()


try:
    ftp = ftpSetup()
except:
    ftpInfoUpdate()
    ftp = ftpSetup()

ftp.cwd('/Users/jwrickman18/Desktop/code/robo-control')
freq = 3000
## Motor 1 ##
motor1 = ACL.Motor(0, 1, 26, 20, 1000, 1000, 21848.88, freq)


## Motor2 ##
motor2 = ACL.Motor(2, 3, 19, 16, 1000, 1000, 11098.56, freq)

IKI = ACL.Inverse_Kinimatics(12.0, 12.0, motor1, motor2)

motor1_count_request_old = 0
motor2_count_request_old = 0
while True:
    gFile = open("ftpTemp.txt", "wb")
    ftp.retrbinary('RETR ftpTemp.txt', gFile.write)
    gFile.close()
    gFile = open("ftpTemp.txt", "r")
    buff = gFile.read()
    gFile.close()
    convertTxtArray = buff.split()
    motor1_count_request_new, motor2_count_request_new = float(
        convertTxtArray[0]), float(convertTxtArray[1])
    timeStart = time.time()
    time.sleep(0.001)
    if time.time() - timeStart > 1:
        print "Motor1 rot count: %d Motor2 rot count: %d" % (
            motor1.encoder.Rotary_counter, motor2.encoder.Rotary_counter)
        timeStart = time.time()
    if motor1_count_request_new != motor1_count_request_old or motor2_count_request_new != motor2_count_request_old:
        print "New Command Recieved"
        if not IKI.moving:
            IKI.runMotors(int(motor1_count_request_new),
                          int(motor2_count_request_new))
            motor1_count_request_old = motor1_count_request_new
            motor2_count_request_old = motor2_count_request_new
