#!/usr/bin/python

import sys,os
import shapefile as shp
import csv
import math

def main(infile):
 
  csv_file = open(infile, 'r')
  filename = os.path.splitext(infile)[0]
  out_file = filename+".shp"
  prj_file = filename+".prj"


  #Set up blank lists for data
  x,y,elevation,distance,pente,abspente,velocity=[],[],[],[],[],[],[]

  #read data from csv file and store in lists
  r = csv.reader(csv_file, delimiter=',')
 
  for i,row in enumerate(r):
    if i > 0: #skip header
      x.append(float(row[0]))
      y.append(float(row[1]))
      elevation.append(float(row[2]))
      distance.append(float(row[3]))
      pente.append(float(row[4]))
      abspente.append(abs(float(row[4])))
      velocity.append(abs(float(row[5])))
      #print'{0},{1},{2},{3},{4},{5},{6}\n'.format(x,y,elevation, distance, pente,abspente, velocity)
      
  #Set up shapefile writer and create empty fields
  w = shp.Writer(shp.POINT)
  w.autoBalance = 1 #ensures gemoetry and attributes match
  w.field('X','F',10,8)
  w.field('Y','F',10,8)
  w.field('Elevation','F',10,8)
  w.field('Distance','F',10,8)
  w.field('Pente','F',10,8)
  w.field('Pente_Abs','F',10,8)
  w.field('Vitesse','F',10,8)

  #loop through the data and write the shapefile
  for j,k in enumerate(x):
    #print'{0},{1},{2},{3},{4},{5},{6}\n'.format(k,y[j],elevation[j], distance[j], pente[j],abspente[j], velocity[j])
    w.point(k,y[j]) #write the geometry
    w.record(k,y[j],elevation[j], distance[j], pente[j], abspente[j], velocity[j]) #write the attributes

  print 'File contains {0} points\n'.format(len(x))

  nblines=len(x)
  if nblines < 3 : 
    print "File "+filename+" is empty"
    sys.exit(0)

  #Save shapefile
  w.save(out_file)

  prj = open(prj_file, "w")
  epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
  prj.write(epsg)
  prj.close()

    
if __name__ == "__main__":
  if len(sys.argv)>1:
    main(sys.argv[1])
  else:
    print "You forgot to include the filename!!!"
    print ""
    sys.exit()
