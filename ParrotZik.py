#!/usr/bin/env python

import sys
if sys.platform == "darwin":
	import lightblue
else:
	import bluetooth

import ParrotProtocol
import struct
from BeautifulSoup import BeautifulSoup

class ParrotZik(object):
	def __init__(self,addr=None):
		uuid = "" # Not used ...

		if sys.platform == "darwin":
			service_matches = lightblue.findservices( name = "Parrot RFcomm service", addr = addr )
		else:
			service_matches = bluetooth.find_service(name = "Parrot RFcomm service", address = addr )		


		if len(service_matches) == 0:
		    print "Failed to find Parrot Zik RFCOMM service"
		    self.sock =""
		    return

		if sys.platform == "darwin":
			first_match = service_matches[0]
			port = first_match[1]
			name = first_match[2]
			host = first_match[0]
		else:
			first_match = service_matches[0]
			port = first_match["port"]
			name = first_match["name"]
			host = first_match["host"]

		print "Connecting to \"%s\" on %s" % (name, host)

		if sys.platform == "darwin":
			self.sock=lightblue.socket()
		else:
			self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

		self.sock.connect((host, port))

		self.sock.send('\x00\x03\x00')
		data = self.sock.recv(1024)

		self.BatteryLevel = 100
		self.BatteryCharging = False
		print "Connected"

	def getBatteryState(self):
		data = self.sendGetMessage("/api/system/battery/get")
		return data.answer.system.battery["state"]

	def getBatteryLevel(self):
		data = self.sendGetMessage("/api/system/battery/get")	
		try:
			if data.answer.system.battery["percent"] <> '':
				self.BatteryLevel = data.answer.system.battery["percent"]
			if data.answer.system.battery["state"] == 'charging':
				self.BatteryCharging = True
			else:
				self.BatteryCharging = False
		except:
			pass

		try:
			print "notification received" + data.notify["path"]
		except:
			pass

		return self.BatteryLevel

	def getVersion(self):
                data = self.sendGetMessage("/api/software/version/get")
		return data.answer.software["sip6"]	

	def getFriendlyName(self):
		data = self.sendGetMessage("/api/bluetooth/friendlyname/get")
		return data.answer.bluetooth["friendlyname"]

	def getAutoConnection(self):
		data = self.sendGetMessage("/api/system/auto_connection/enabled/get")
		return data.answer.system.auto_connection["enabled"]

	def setAutoConnection(self,arg):
		data = self.sendSetMessage("/api/system/auto_connection/enabled/set",arg)
		return data

	def getAncPhoneMode(self):
		data = self.sendGetMessage("/api/system/anc_phone_mode/enabled/get")
		return data.answer.system.anc_phone_mode["enabled"]

	def getNoiseCancelStreet(self):
		data = self.sendGetMessage("/api/audio/equalizer/preset_value/get")
		return data.answer.audio.noise_cancellation["enabled"]

	def getNoiseCancel(self):
		data = self.sendGetMessage("/api/audio/noise_cancellation/enabled/get")
		return data.answer.audio.noise_cancellation["enabled"]

	def setNoiseCancel(self,arg):
		data = self.sendSetMessage("/api/audio/noise_cancellation/enabled/set",arg)
		return data

	def getLouReedMode(self):
		data = self.sendGetMessage("/api/audio/specific_mode/enabled/get")
		return data.answer.audio.specific_mode["enabled"]


        def getFlightMode(self):
                data = self.sendGetMessage("/api/flight_mode/get")
		return data.answer.flight_mode["enabled"]

        def unsetFlightMode(self):
                data = self.sendGetMessage("/api/flight_mode/disable")
                try:
			if data.answer["path"] <> '':
                                return data.answer["path"]                
                except:
                        pass

		try:
			print "notification received" + data.notify["path"]
		except:
			pass
                
        def setFlightMode(self):
                data = self.sendGetMessage("/api/flight_mode/enable")
		return data.answer["path"]


        def getSoundEffect(self):
		data = self.sendGetMessage("/api/audio/sound_effect/get")
		return data.answer.audio.sound_effect["room_size"]

        def getNoise(self):
		data = self.sendGetMessage("/api/audio/noise/get")
#		return data.answer.audio.noise["internal"]
		return data.answer.audio.noise["external"]

	def getRoom(self):
		data = self.sendGetMessage("/api/audio/sound_effect/room_size/get")
		return data.answer.audio.sound_effect["room_size"]

	def setRoom(self,arg):
		data = self.sendSetMessage("/api/audio/sound_effect/room_size/set",arg)
		return data

	def getAngle(self):
		data = self.sendGetMessage("/api/audio/sound_effect/angle/get")
		return data.answer.audio.sound_effect["angle"]

	def setAngle(self,arg):
		data = self.sendSetMessage("/api/audio/sound_effect/angle/set",arg)
		return data

        def getNoiseControl(self):
                data = self.sendGetMessage("/api/audio/noise_control/get")
#                return data.answer.audio.noise_control["type"] #// anc aoc
                return data.answer.audio.noise_control["value"] #// 1,2,3 ? 

	def setNoiseControl(self,arg):
		data = self.sendSetMessage("/api/audio/noise_control/set",arg)
		return data
         
        def getNoiseControlEnabled(self):
                data = self.sendGetMessage("/api/audio/noise_control/enabled/get")
                return data.answer.audio.noise_control["enabled"] 
       

	def getTest(self):
		data = self.sendGetMessage("/api/audio/noise_control/get")
		return data.answer.audio.specific_mode["enabled"]

	def setLouReedMode(self,arg):
		data = self.sendSetMessage("/api/audio/sound_effect/angle/get",arg)
		return data

	def getParrotConcertHall(self):
		data = self.sendGetMessage("/api/audio/sound_effect/enabled/get")
		return data.answer.audio.sound_effect["enabled"]

	def setParrotConcertHall(self,arg):
		data = self.sendSetMessage("/api/audio/sound_effect/enabled/set",arg)
		return data

	def sendGetMessage(self,message):
                print message
                message = ParrotProtocol.getRequest(message)
		
                return self.sendMessage(message)

	def sendSetMessage(self,message,arg):
		message = ParrotProtocol.setRequest(message,arg)
		return self.sendMessage(message)

	def sendMessage(self,message):
		try:
			self.sock.send(str(message))
		except:
			self.sock =""
			return
		if sys.platform == "darwin":
			data = self.sock.recv(30)
		else:
			data = self.sock.recv(7)
		data = self.sock.recv(1024)
		data=BeautifulSoup(data)
                print data
		return data

	def Close(self):
		self.sock.close()
