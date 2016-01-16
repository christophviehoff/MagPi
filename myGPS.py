import serial
import os


# track a valid fix on a position 
# and create a valid file name once
firstFixFlag = False
firstFixDate = ""

#set up serial connection object:
ser= serial.Serial(
	port='/dev/ttyUSB0',\
	baudrate=4800,\
	parity=serial.PARITY_NONE,\
	stopbits=serial.STOPBITS_ONE,\
	bytesize=serial.EIGHTBITS,\
	timeout=1)

def degress_to_decimal(data,hemisphere):
	""" 4529.8201,N,12245.1001,W
	idx 012345678   decimalPointPosition = 4
	fmt ddmm.mmmm
	
	"""

	try:
		decimalPointPosition = data.index('.')
		#slice
		degress = float(data[:decimalPointPosition-2])
		minutes = float(data[decimalPointPosition-2:])/60
	
		output= degress + minutes
		if hemisphere is 'N' or hemisphere is 'E':
			return output
		if hemisphere is 'S' or hemisphere is 'W':
			return -output	
	except:
		return""	
	

def parse_GPRMC(data):
	""" parse the following string:

	source NMEA reference manual

	Nema output messages GPxxx
	RMC time,data position,course and speed data
	GGA time ,position and fix time data
	GSA GPS reciver operation mode, satellites usde in position solution and DOP values
    
    RMC sentence example below
    
	$GPRMC,205625.000,A,4529.8201,N,12245.1001,W,0.00,185.57,160116,,,A*74
	$GPGGA,205626.000,4529.8201,N,12245.1001,W,1,08,1.3,125.4,M,-19.5,M,,0000*62
	$GPGSA,M,3,32,31,01,03,22,11,14,23,,,,,2.1,1.3,1.7*3C
	"""	
	data = data.split(',')
	dict ={
			'fix_time' : data[1],
			'validity' : data[2],
			'latitude' : data[3],
			'latitude_hemisphere' : data[4],
			'longitude' :data[5],
			'longitude_hemisphere' : data[6],
			'speed' : data[7],
			'true_course' : data[8],
			'fix_date' : data[9],
			'variation' : data [10],
			'variation_e_w' : data[11],
			'checksum' : data[12]
			}
	# converted from hhmm.ssxx to decimal
	dict['decimal_latitude']=degress_to_decimal(dict['latitude'],dict['latitude_hemisphere'])
	dict['decimal_longitude']=degress_to_decimal(dict['longitude'],dict['longitude_hemisphere'])
	
	return dict

#main program:
while True:
	line=ser.readline()
	if "$GPRMC" in line:
		#convert into python dictionary if data is a RMC sentence
		gpsData=parse_GPRMC(line)
		#print gpsData
		"""{'true_course': '107.23', 
 'fix_time': '213001.000',
 'variation': '',
 'latitude_hemisphere': 'N',
 'validity': 'A',
 'decimal_latitude': None,
 'speed': '0.32',
 'longitude_hemisphere': 'W',
 'variation_e_w': '',
 'checksum': 'A*70\r\n',
 'longitude': '12245.1007',
 'fix_date': '160116',
 'decimal_longitude': None,
            'latitude': '4529.8196'}
"""
		if gpsData['validity'] == 'A':
			#valid fix detected now log it
			if firstFixFlag is False:
				#create file name for first fix only once
				firstFixDate=gpsData['fix_date']+gpsData['fix_time']
				firstFixFlag = True
			else: #write data
				
				with open("/home/pi/Documents/gps_experimentation/"+firstFixDate+"-simple-log.txt","a") as myfile:
					myfile.write(gpsData['fix_date']+ ","+
								 gpsData['fix_time']+","+
							 str(gpsData['decimal_latitude']) +","+
							 str(gpsData['decimal_longitude'])+"\n")
							 
				with open("/home/pi/Documents/gps_experimentation/"+firstFixDate+"-gprmc-raw-log.txt","a") as myfile:
					myfile.write(line)
