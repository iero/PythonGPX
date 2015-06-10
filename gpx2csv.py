#!/usr/bin/python

import sys,os
import gpxpy
import gpxpy.gpx
import math as mod_math
import gpxpy.utils as mod_utils
import itertools
import collections

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
  #os.rename(infile,infile.replace(' ','_'))
  
  gpx_file = open(infile, 'r')
  #cvs_file=filename+".csv"
  #summary_file=filename+".sum"

  # Parse GPX input file
  gpx=None
  try:
    gpx = gpxpy.parse(gpx_file)
  except Exception:
    print "File "+filename+" is invalid"
    sys.exit(0)

  datetrack=""  
  
  for track in gpx.tracks:
      for segment in track.segments:
	  previous_point = None

          for point in segment.points:
	    datetrack=point.time

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

              #if pente > 0:
	      #  totalpositiveelevation=totalpositiveelevation+pente
              #else:
	      #  totalnegativeelevation=totalnegativeelevation+abs(pente)	 

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
    smoothedelev = moyenne_glissante(elevation,7)

    originalname=filename
    filename=str(datetrack).split()[0]
    filepath=os.path.dirname(os.path.realpath(infile))

    newfile=originalname
    for v in range(0,9) :
        newfile = filepath+"/"+filename+"_"+str(v)
        if not os.path.isfile(newfile+".gpx") : break
    
    os.rename(infile,newfile+".gpx")
    cvs_file=newfile+".csv"
    summary_file=newfile+".sum"

    # Write CSV file
    with open(cvs_file,"w") as myfile:
      myfile.write('x,y,elevation,distance,pente,vitesse\n')  
      for j,k in enumerate(x):

        if j > 0:
	  difelev = smoothedelev[j] - smoothedelev[j-1]
	  if (difelev > 0) :
	    totalpositiveelevation=totalpositiveelevation+difelev
	  else :
	    totalnegativeelevation=totalnegativeelevation+abs(difelev)
	  
        myfile.write('{0},{1},{2},{3},{4},{5}\n'.format(k,y[j],elevation[j], distance[j], smootheddip[j], smoothedvelocity[j]))
 
	# format : fichier, date heure, distance (km), temps (h:min:sec), elevation
	dt=str(datetrack).split()[0]

	dist="%.2f" % (totaldistance/1000)

	m, s = divmod(totaltemps,60)
	h, m = divmod(m,60)
	tps="%d:%02d:%02d" % (h, m, s)
	
	deniv="%i" % totalpositiveelevation

    with open(summary_file,"w") as sumfile:
        sumfile.write('{0},{1},{2},{3},{4}\n'.format(filename, dt, dist, tps, deniv))

    print "File "+filename+" : "+str(validpt)+"/"+str(totalpt)+" waypoints."
    print "Date  "+dt
    print "Distance enregistree "+ dist +" km "
    print "Temps mouvement "+ tps
    if totaltemps != 0 :
      vit = 3.6 * (totaldistance/totaltemps)
      print "Vitesse moyenne "+str(vit) +" km/h "
    print "Denivele (positif/negatif) : " + str(totalpositiveelevation) + " m / -"+ str(totalnegativeelevation) + " m" 

    result=[]
    result.append(dt)
    result.append(dist)
    result.append(totaltemps)
    result.append(totalpositiveelevation)
  else :
    result=[]
    print "File "+filename+" contains no waypoints. "

  return result


if __name__ == "__main__":

  dict_nb = {'Total':'0'};
  dict_deniv = {'Total':'0'};
  dict_dist = {'Total':'0'};
  dict_time = {'Total':'0'};

  if len(sys.argv)>1:
    fname=sys.argv[1]
    if (os.path.isfile(fname)) :
      main(fname)
    elif (os.path.isdir(fname)) :
      for f in os.listdir(fname) :
	#if not os.path.splitext(f)[0].endwith('.gpx'): continue
	if not f.endswith('.gpx'): continue
        result = main(fname+"/"+f)
	if not result : continue 
	
	dt=result[0]
	dist=result[1]
	tps=result[2]
	deniv=result[3]

        # Nb trips
        if dt in dict_dist :
          dict_nb[dt] = int(dict_nb[dt]) + 1
        else :
          dict_nb[dt] = 1
        dict_nb['Total'] = int(dict_nb['Total']) + 1

        # Distance by day
        if dt in dict_dist :
          dict_dist[dt] = float(dict_dist[dt]) + float(dist)
        else :
          dict_dist[dt] = dist
        dict_dist['Total'] = float(dict_dist['Total']) + float(dist)
  
        # Time by day
        if dt in dict_time :
          dict_time[dt] = float(dict_time[dt]) + float(tps)
        else :
          dict_time[dt] = tps
        dict_time['Total'] = float(dict_time['Total']) + float(tps)

        # Positive deniv by day
        if dt in dict_deniv :
          dict_deniv[dt] = float(dict_deniv[dt]) + float(deniv)
        else :
          dict_deniv[dt] = deniv
        dict_deniv['Total'] = float(dict_deniv['Total']) + float(deniv)

	#dist="%.2f" % (totaldistance/1000)
    
    print("{0}".format(dict_nb['Total'])+" trips recorded")
    print("{0}".format(dict_dist['Total'])+" km")
    print("{0}".format(dict_time['Total'])+" min")
    print("{0}".format(dict_deniv['Total'])+" m deniv")

    print("date,nb,dist,time,deniv")
    for i in dict_nb :
      m, s = divmod(dict_time[i],60)
      h, m = divmod(m,60)
      tps="%d:%02d:%02d" % (h, m, s)
      deniv="%i" % dict_deniv[i]
      print("{0},{1},{2},{3},{4}".format(i,dict_nb[i],dict_dist[i],tps,deniv))


  else:
    print "You forgot to include the filename!!!"
    print ""
    sys.exit()
