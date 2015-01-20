#!/usr/bin/python

import sys,os
import gpxpy
import gpxpy.gpx
import math as mod_math
import gpxpy.utils as mod_utils
import itertools

def format_time(time_s):
    if not time_s:
        return 'n/a'
    minutes = mod_math.floor(time_s / 60.)
    hours = mod_math.floor(minutes / 60.)

    return '%s:%s:%s' % (str(int(hours)).zfill(2), str(int(minutes % 60)).zfill(2), str(int(time_s % 60)).zfill(2))

# Moyenne glissante d'ordre k
def moyenne_glissante(liste,ordre):
  sortedlist=[]

  n=0
  if ordre%2 == 0:
    n=ordre/2
  else :
    n=(ordre-1)/2

  for v in range(0,n) :
    sortedlist.append(liste[v])
   
  for v in range(n,len(liste)-n) :
    som=liste[v]
    for k in range(1,n+1) :
      som = som + (liste[v-k]) + (liste[v+k])
    sortedlist.append(som/(2*n + 1))

  for v in range(len(liste)-n,len(liste)) :
    sortedlist.append(liste[v])

  return sortedlist

def main(infile):
  
  home = gpxpy.gpx.GPXTrackPoint(48.883041, 2.1994429, time=None, elevation=62)

  #Set up blank lists for data
  x=[]
  y=[]
  elevation=[]
  distance=[]
  dip=[]
  velocity=[]
  
  smoothedvelocity=[]
  smootheddip=[]
  
  # recorded track stats
  validpt=0
  totalpt=0
  totaldistance=0
  totaltemps=0
  totalpositiveelevation=0
  totalnegativeelevation=0
  
  filename = os.path.splitext(infile)[0]
  
  gpx_file = open(infile, 'r')
  cvs_file=filename+".csv"

  # Parse GPX input file
  gpx=None
  try:
    gpx = gpxpy.parse(gpx_file)
  except Exception:
    print "File "+filename+" is invalid"
    sys.exit(0)
  
  
  for track in gpx.tracks:
      for segment in track.segments:
	  previous_point = None

          for point in segment.points:

	    # Remove points 100m from home
            distanceFromHome = point.distance_3d(home)
            if distanceFromHome < 100 :
	      continue
	      
	    temps=0
	    distance3D=0
	    pente=0
	    vitesse=0

	    if previous_point:
              distance2D = point.distance_2d(previous_point)
              distance3D = point.distance_3d(previous_point)
	      totaldistance=totaldistance+distance3D
	      
              if point.elevation and previous_point.elevation :
	        altitude_delta = point.elevation - previous_point.elevation
	      else :
	        altitude_delta = 0

	      if distance2D != 0:
	        pente = (100*altitude_delta)/distance2D
              else:
	        pente=0

              if pente > 0:
	        totalpositiveelevation=totalpositiveelevation+pente
              else:
	        totalnegativeelevation=totalnegativeelevation+abs(pente)	 

              if point.time and previous_point.time :
      	        time_delta = point.time - previous_point.time
                temps= mod_utils.total_seconds(time_delta)
      	        totaltemps=totaltemps+temps
		if mod_utils.total_seconds(time_delta) > 1 :
                  vitesse = (distance3D / 1000.) / (mod_utils.total_seconds(time_delta) / 60. ** 2)
	        else:
	          vitesse = 0
	      else :
	        time_delta = 0
		vitesse = 0
	      
            #		
            # Test data coherency
            #
	    # Distance bw two points need to be less than 200m to be considered
	    # At 40 km/h (11m/s) it means 1 record every 18s
	    #
	    
	    dataOK= True
	    # Detect if distance between two points is too long or too short (normaly bw 10 to 20 meters
	    if distance3D > 100 or distance3D <= 5 : dataOK=False

	    # In a city 10% dip is huge. So, more than 15% will certainly be an error. 
	    if pente > 15 or pente < -15: dataOK=False

	    # Detect if we stopped (v < 1 km/h)
	    if vitesse < 1 and temps !=0 : dataOK=False

            #print '{0},{1},{2},{3},{4},{5}'.format(point.longitude,point.latitude,point.elevation, distance3D, dip, velocity)
            #dataOK=True
	    if dataOK :
	      x.append(point.longitude)
	      y.append(point.latitude)
	      elevation.append(point.elevation)
	      distance.append(distance3D)
	      dip.append(pente)
	      velocity.append(vitesse)
              #print '{0},{1},{2},{3},{4},{5}'.format(point.longitude,point.latitude,point.elevation, distance3D, dip, velocity)
     
              validpt=validpt+1

	    previous_point = point
            totalpt=totalpt+1

  if validpt >= 7 :
    smoothedvelocity = moyenne_glissante(velocity,7)
    smootheddip = moyenne_glissante(dip,7)

    # Write CSV file
    with open(cvs_file,"w") as myfile:
      myfile.write('x,y,elevation,distance,pente,vitesse\n')  
      for j,k in enumerate(x):
        #print '{0},{1},{2},{3},{4},{5}'.format(k,y[j],elevation[j], distance[j], dip[j], velocity[j])
        #myfile.write('{0},{1},{2},{3},{4},{5}\n'.format(k,y[j],elevation[j], distance[j], smootheddip[j], velocity[j]))
        myfile.write('{0},{1},{2},{3},{4},{5}\n'.format(k,y[j],elevation[j], distance[j], smootheddip[j], smoothedvelocity[j]))
 
    print "File "+filename+" : "+str(validpt)+"/"+str(totalpt)+" waypoints."
    print "Distance enregistree "+str(totaldistance / 1000) +" km "
    print "Temps mouvement "+str(totaltemps / 60) +" min "
    if totaltemps != 0 :
      vit = 3.6 * (totaldistance/totaltemps)
      print "Vitesse moyenne "+str(vit) +" km/h "
    print "Denivele (positif/negatif) : " + str(totalpositiveelevation) + " m / -"+ str(totalnegativeelevation) + " m" 
  else :
    print "File "+filename+" contains no waypoints. "
  
if __name__ == "__main__":
  if len(sys.argv)>1:
    main(sys.argv[1])
  else:
    print "You forgot to include the filename!!!"
    print ""
    sys.exit()
