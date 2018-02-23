# --------------------------------File on client--------------------------------
# Reads

import ArmControlLib as ACL
import ftplib
import RoboPiLib_pwm as RPL
import time
RPL.RoboPiInit("/dev/ttyAMA0", 115200)
ftp = ftplib.FTP('192.168.21.213', 'jwrickman18',
                 'Heap!860')  # host computer info
# directory of repo on host
ftp.cwd('/Users/jwrickman18/Desktop/code/robo-control')
freq = 3000
## Motor 1 ##
motor1 = ACL.Motor(0, 1, 26, 20, 1000, 1000, 21848.88, freq)


## Motor2 ##
motor2 = ACL.Motor(2, 3, 19, 16, 1000, 1000, 11098.56, freq)

IKI = ACL.Inverse_Kinimatics(12.0, 12.0, motor1, motor2)

motor1CompletePrint = True
motor2CompletePrint = True
while True:
    gFile = open("ftpTemp.txt", "wb")
    ftp.retrbinary('RETR ftpTemp.txt', gFile.write)
    gFile.close()
    gFile = open("ftpTemp.txt", "r")
    buff = gFile.read()
    gFile.close()
    convertTxtArray = buff.split()
    motor1_count_request = float(convertTxtArray[0])
    motor2_count_request = float(convertTxtArray[1])
    IKI.runMotors(motor1_count_request, motor2_count_request)
