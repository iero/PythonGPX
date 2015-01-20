#!/usr/bin/python

import sys,os
import shapefile as shp
import csv
import math

def main(path):

  #Set up shapefile point writer and create empty fields
  w = shp.Writer(shp.POINT)
  w.autoBalance = 1 #ensures gemoetry and attributes match
  w.field('X','F',10,8)
  w.field('Y','F',10,8)
  w.field('Elevation','F',10,8)
  w.field('Distance','F',10,8)
  w.field('Pente','F',10,8)
  w.field('Pente_Abs','F',10,8)
  w.field('Vitesse','F',10,8)

  w2 = shp.Writer(shp.POLYLINE)
  w2.autoBalance = 1 #ensures gemoetry and attributes match
  w2.field('Pente','F',10,8)
  w2.field('Vitesse','F',10,8)

  out_wp_file = path+"_all_wp.shp"
  out_poly_file = path+"_all_poly.shp"
  prj_wp_file = path+"_all_wp.prj"
  prj_poly_file = path+"_all_poly.prj"

  prj = open(prj_wp_file, "w")
  epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
  prj.write(epsg)
  prj.close()

  prj = open(prj_poly_file, "w")
  epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
  prj.write(epsg)
  prj.close()


  for f in os.listdir(path) :
    os.rename(os.path.join(path, f), os.path.join(path, f.replace(' ', '_')))

  for f in os.listdir(path) :
    if f.endswith(".csv") :
      csv_file = open(os.path.join(path,f), 'r')
      filename = os.path.splitext(f)[0]
      print filename

      #Set up blank lists for data
      x,y,elevation,distance,pente,abspente,velocity=[],[],[],[],[],[],[]

      #read data from csv file and store in lists
      r = csv.reader(csv_file, delimiter=',')
 
      for i,row in enumerate(r):
        if i > 0: #skip header
          x.append(float(row[0]))
          y.append(float(row[1]))
          if row[2] != 'None' :
	    elevation.append(float(row[2]))
	  else :
	    elevation.append(None)
          distance.append(float(row[3]))
          if row[4] != 'None':
	    pente.append(float(row[4]))
            abspente.append(abs(float(row[4])))
	  else :
	    pente.append(None)
	    abspente.append(None)
	  if row[5] != 'None' :
            velocity.append(float(row[5]))
	  else :
	    velocity.append(None)
	  
          #print'{0},{1},{2},{3},{4},{5},{6}\n'.format(x,y,elevation, distance, pente,abspente, velocity)

      #loop through the data and write the point shapefile
      for j,k in enumerate(x):
        #print'{0},{1},{2},{3},{4},{5},{6}\n'.format(k,y[j],elevation[j], distance[j], pente[j],abspente[j], velocity[j])
        w.point(k,y[j]) # write the geometry
        w.record(k,y[j],elevation[j], distance[j], pente[j], abspente[j], velocity[j]) # write the attributes

      print 'Added {0} points\n'.format(len(x))

      #loop through the data and write the polylines shapefile
      for j,k in enumerate(x):
        #print'{0},{1},{2},{3},{4},{5},{6}\n'.format(k,y[j],elevation[j], distance[j], pente[j],abspente[j], velocity[j])
        if j > 0 :
	  line = [[x[j-1],y[j-1]],[x[j],y[j]]]
	  w2.line(parts=([line])) # write the geometry
          w2.record(abspente[j], velocity[j]) # write the attributes

      #print 'Added {0} vectors\n'.format(len(x)-1)

  #Save shapefiles
  w.save(out_wp_file)
  w2.save(out_poly_file)

    
if __name__ == "__main__":
  if len(sys.argv)>1:
    main(sys.argv[1])
  else:
    print "You forgot to include the directory"
    print ""
    sys.exit()
