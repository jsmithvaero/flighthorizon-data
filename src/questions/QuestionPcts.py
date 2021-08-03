"""
file    : QuestionPercents.py
author  : Jesse Smith
authored: 20 July 2021
purpose : To answer questions about the data.
"""
import sys
import math

import argumentKeys as argKeys
from src.questions.Question import *
from src.radarData import RadarData
from src.Data import Data
from src.mathUtils import distanceKM
import statistics 

class QuestionPcts:

    metersToFeet = 3.281 # This could maybe go in MathUtils if used elsewhere

    def __init__(self):
        pass

    def getHZSpeedFromRadar(self, velX, velZ):
        self.velX = velX
        self.velZ = velZ
        return math.sqrt((self.velX**2) + (self.velZ**2)) # This can maybe go in MathUtils if needed elsewhere

    def getHZSpeedFromMAVLink(self, vx, vy):
        self.vx= vx
        self.vy= vy
        return math.sqrt(self.vx * self.vx + self.vy * self.vy);  # This can maybe go in MathUtils if needed elsewhere

    def invalidvsValidTracks(self, radarD):
        try: 
            minAltitude = RADAR_FILTER["minAltitude"]
            maxAltitude = RADAR_FILTER["maxAltitude"]
            minHorizontalSpeed = RADAR_FILTER["minHorizontalSpeed"]

            # Find number of unique tracks that are valid and nonvalid (given radar filter)
            validCnt = 0
            nonValidCnt = 0
            validConfSum = 0
            invalidConfSum = 0
            validDistSum = 0
            invalidDistSum = 0
            validArr = []
            invalidArr = []
            for key in radarD.points:
                points = radarD.points[key]
                for p in points:
                    p.altitude = p.altitude * self.metersToFeet  # convert to feet
                    hzSpeed = self.getHZSpeedFromRadar(p.xVelocity, p.yVelocity) 
                    if (p.altitude  > minAltitude and hzSpeed > minHorizontalSpeed):
                        if p.trackID not in validArr:
                            validArr.append(p.trackID)
                            validCnt += 1
                            validConfSum += p.confidence
                            validDistSum += p.distance

                    else:
                        if p.trackID not in invalidArr:
                            invalidArr.append(p.trackID)
                            nonValidCnt += 1
                            invalidConfSum += p.confidence
                            invalidDistSum += p.distance


            print("\n*********** (Echodyne) Invalid vs. Valid Tracks **************************************")
            print("Unique Invalid Tracks {invalid} (Confidence avg {invalidConfAvg}%) (Distance avg {invalidDistAvg})\nUnique Valid Tracks {valid} (Confidence avg {validConfAvg}%) (Distance avg {validDistAvg})\n".format(valid = validCnt, validDistAvg = round((validDistSum / validCnt),2), \
            invalid = nonValidCnt, invalidConfAvg = round((invalidConfSum / nonValidCnt),2), validConfAvg = round((validConfSum / validCnt),2), invalidDistAvg = round((invalidDistSum / nonValidCnt),2))) 
        
        except:
             print("No valid data found for valid vs invalid tracks")
             print("")

    def invalidvsValidTracksGroundAware(self, radarD):
        try: 
            minAltitude = RADAR_FILTER["minAltitude"]
            maxAltitude = RADAR_FILTER["maxAltitude"]
            minHorizontalSpeed = RADAR_FILTER["minHorizontalSpeed"]

            # Find number of unique tracks that are valid and nonvalid (given radar filter)
            validCnt = 0
            nonValidCnt = 0
            validConfSum = 0
            invalidConfSum = 0
            validDistSum = 0
            invalidDistSum = 0
            validArr = []
            invalidArr = []
            sampleCnt = 0
            for key in radarD.points:
                points = radarD.points[key]
                for p in points:
                    if (sampleCnt < 2000):
                        p.altitude = p.altitude* self.metersToFeet  # convert to feet
                        hzSpeed = p.speed
                        if (p.altitude> minAltitude and hzSpeed > minHorizontalSpeed):
                            if p.trackID not in validArr:
                                validArr.append(p.trackID)
                                validCnt += 1
                                validConfSum += p.confidence
                                validDistSum += p.distance

                        else:
                            if p.trackID not in invalidArr:
                                invalidArr.append(p.trackID)
                                nonValidCnt += 1
                                invalidConfSum += p.confidence
                                invalidDistSum += p.distance
                        sampleCnt += 1

            print("\n*********** (GroundAware) Invalid vs. Valid Tracks **************************************")
            print("Unique Invalid Tracks {invalid} (Confidence avg {invalidConfAvg}%) (Distance avg {invalidDistAvg})\nUnique Valid Tracks {valid} (Confidence avg {validConfAvg}%) (Distance avg {validDistAvg})\n".format(valid = validCnt, validDistAvg = round((validDistSum / validCnt),2), \
            invalid = nonValidCnt, invalidConfAvg = round((invalidConfSum / nonValidCnt),2), validConfAvg = round((validConfSum / validCnt),2), invalidDistAvg = round((invalidDistSum / nonValidCnt),2))) 
        
        except:
             print("No valid data found for valid vs invalid tracks")
             print("")

    def radarAccuracyByDistanceAltitude(self, mavlD, radarD):

        maxAltitude = RADAR_FILTER["maxAltitude"]
        minAltitude = RADAR_FILTER["minAltitude"]
        minHorizontalSpeed = RADAR_FILTER["minHorizontalSpeed"]
        maxHorizontalSpeed = RADAR_FILTER["maxHorizontalSpeed"]

        mavAltitude = []
        mavLat = []
        mavLon = []
        mavHZSpeed = []
        
        radarAltitude = []
        radarLat = []
        radarLon = []
        radarHZSpeed = []

        try: 
            sampleCnt = 0
            for key in radarD.points:
                points = radarD.points[key]

            for m in mavlD.getPoints():
                if (sampleCnt < 100):
                    m.altitude  = m.altitude  * self.metersToFeet  
                    hzSpeed =  self.getHZSpeedFromMAVLink(vx, vy)
                    if (m.altitude  < maxAltitude and m.altitude > minAltitude and hzSpeed > minHorizontalSpeed and hzSpeed < maxHorizontalSpeed):   
                        mavAltitude.append(m.altitude ) 
                        mavLat.append(m.latitude)  
                        mavLon.append(m.longitude) 
                        mavHZSpeed.append(hzSpeed)
  
                        for p in points:
                            if (abs(p.stamp.timestamp() * 1000 - m.stamp.timestamp() * 1000) < 103):
                                p.altitude = p.altitude * self.metersToFeet  
                                hzSpeed = self.getHZSpeedFromRadar(p.xVelocity, p.yVelocity) 

                            if (p.altitude< maxAltitude and p.altitude > minAltitude and hzSpeed > minHorizontalSpeed and hzSpeed < maxHorizontalSpeed):   
                                    radarAltitude.append(p.altitude) 
                                    radarLat.append(p.latitude)  
                                    radarLon.append(p.longitude)
                                    radarHZSpeed.append(hzSpeed) 
                sampleCnt += 1

            diffAlt = []
            for i in range(len(mavAltitude)):
                mav = mavAltitude[i]
                rad = radarAltitude[i]
                diff = abs(int(mav) - int(rad))
                diffAlt.append(diff)

            maxAlt = max(diffAlt)  
            minAlt = min(diffAlt)
            meanAlt = statistics.mean(diffAlt)  
            medianAlt = statistics.median(diffAlt) 

            print("")
            print("*********** (Echodyne) Spatial Correlation between Ownship and Mavlink tracks ********")
            print("")
            print("     Altitude (Avg) Feet")
            print("     -----------------------------")
            print("     " + str(round(meanAlt,2))) 

            diffHZSpeed = []
            for i in range(len(mavHZSpeed)):
                mav = mavHZSpeed[i]
                rad = radarHZSpeed[i]
                diff = abs(int(mav) - int(rad))
                diffHZSpeed.append(diff)

            maxHZSpeed = max(diffHZSpeed)  
            minHZSpeed = min(diffHZSpeed)
            meanHZSpeed = statistics.mean(diffHZSpeed)  
            medianHZSpeed = statistics.median(diffHZSpeed) 

            print("")
            print("")
            print("     HZSpeed (Avg) Knots")
            print("     -----------------------------")
            print("     " + str(round(meanHZSpeed,2)))             

            lat = []
            for i in range(len(mavLat)):
                mavlat = mavLat[i]
                radlat = radarLat[i]
                mavlon = round(mavLon[i], 7)
                radlon = round(radarLon[i], 7)
                diff = distanceKM(mavlat, mavlon, radlat, radlon)
                if (diff < .5):
                    lat.append(diff)
            try:
                maxLat  = max(lat)  
                meanLat = statistics.mean(lat)  

                print("")
                print("     Distance (Avg) feet")
                print("     -----------------------------")
                print("     " + str(round((meanLat * 1000) * self.metersToFeet,2))) 
                print("")
            except:
                pass
        except:
             print("No valid data found for spatial correlation between Mavlink and Radar Ownship")
             print("")

    def radarAccuracyByDistanceAltitudeGroundAware(self, mavlD, radarD):
    
        maxAltitude = RADAR_FILTER["maxAltitude"]
        minAltitude = RADAR_FILTER["minAltitude"]
        minHorizontalSpeed = RADAR_FILTER["minHorizontalSpeed"]
        maxHorizontalSpeed = RADAR_FILTER["maxHorizontalSpeed"]

        mavAltitude = []
        mavLat = []
        mavLon = []
        mavHZSpeed = []
        
        radarAltitude = []
        radarLat = []
        radarLon = []
        radarHZSpeed = []

        try: 
            sampleCnt = 0
            for key in radarD.points:
                points = radarD.points[key]
                
                if (sampleCnt < 100):
                    for m in mavlD.getPoints():
                        m.altitude = m.altitude * self.metersToFeet  
                        hzSpeed =  self.getHZSpeedFromMAVLink(m.xVelocity, m.yVelocity)
                        if (m.altitude < maxAltitude and m.altitude > minAltitude and hzSpeed > minHorizontalSpeed and hzSpeed < maxHorizontalSpeed):   
                            mavAltitude.append(m.altitude) 
                            mavLat.append(m.latitude)  
                            mavLon.appendm(m.longitude) 
                            mavHZSpeed.append(hzSpeed)
    
                            for p in points:
                                timev = m.stamp.timestamp()
                                timeDiff = abs(p.updateTime - timev); 
                                timeDiff = (timeDiff / 60) / 60
                                hours = int(timeDiff)
                                minutes = (timeDiff*60) % 60
                                seconds = (timeDiff*3600) % 60
                                if (seconds < .04):
                                    p.altitude = p.altitude * self.metersToFeet  
                                    hzSpeed = p.speed

                                if (p.altitude < maxAltitude and p.altitude > minAltitude and hzSpeed > minHorizontalSpeed and hzSpeed < maxHorizontalSpeed):   
                                        radarAltitude.append(p.altitude) 
                                        radarLat.append(p.latitude)  
                                        radarLon.append(p.longitude)
                                        radarHZSpeed.append(hzSpeed) 
                    sampleCnt += 1

            diffAlt = []
            for i in range(len(mavAltitude)):
                try:
                    mav = mavAltitude[i]
                    rad = radarAltitude[i]
                    diff = abs(int(mav) - int(rad))
                    diffAlt.append(diff)
                except:
                    pass

            maxAlt = max(diffAlt)  
            minAlt = min(diffAlt)
            meanAlt = statistics.mean(diffAlt)  
            medianAlt = statistics.median(diffAlt) 

            print("")
            print("*********** (GroundAware) Spatial Correlation between Ownship and Mavlink tracks ********")
            print("")
            print("     Altitude (Avg) Feet")
            print("     -----------------------------")
            print("     " + str(round(meanAlt,2))) 

            diffHZSpeed = []
            for i in range(len(mavHZSpeed)):
                try: 
                    mav = mavHZSpeed[i]
                    rad = radarHZSpeed[i]
                    diff = abs(int(mav) - int(rad))
                    diffHZSpeed.append(diff)
                except:
                    pass

            maxHZSpeed = max(diffHZSpeed)  
            minHZSpeed = min(diffHZSpeed)
            meanHZSpeed = statistics.mean(diffHZSpeed)  
            medianHZSpeed = statistics.median(diffHZSpeed) 

            print("")
            print("")
            print("     HZSpeed (Avg) Knots")
            print("     -----------------------------")
            print("     " + str(round(meanHZSpeed,2)))             

            lat = []
            for i in range(len(mavLat)):
                try:
                    mavlat = round(mavLat[i],7)
                    radlat = round(radarLat[i],7)
                    mavlon = round(mavLon[i], 7)
                    radlon = round(radarLon[i], 7)
                    diff = distanceKM(mavlat, mavlon, radlat, radlon)
                    if (diff < .18):
                        lat.append(diff)
                except:
                    pass
            try:
                maxLat  = max(lat)  
                meanLat = statistics.mean(lat)  

                print("")
                print("     Distance (Avg) feet")
                print("     -----------------------------")
                print("     " + str(round((meanLat * 1000) * self.metersToFeet,2))) 
                print("")
            except:
                pass
        except:
             print("No valid data found for spatial correlation between Mavlink and Radar Ownship")
             print("")             

RADAR_FILTER = {
  "minAltitude": 635,
  "maxAltitude": 1000,
  "minHorizontalSpeed": 3,
  "maxHorizontalSpeed": 1000,
  "minVerticalSpeed": 100,
  "maxVerticalSpeed": 3000,
}