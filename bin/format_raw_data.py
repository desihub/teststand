#!/usr/bin/env python

import astropy.io.fits as pyfits
import argparse
import re
import sys

def parse_sec_keyword(value):
    m = re.search('\[(\d+):(\d+)\,(\d+):(\d+)\]', value)
    if m is None:
        raise ValueError, 'unable to parse {} as [a:b, c:d]'.format(value)
    return  map(int, m.groups())


parser=argparse.ArgumentParser(description="Reformat DESI raw data")
parser.add_argument('-i','--infile', type = str, default = None, required=True,
                    help = 'path to input DESI raw data file')
parser.add_argument('-o','--outfile', type = str, default = None, required=True,
                    help = 'path to output DESI raw data file')
parser.add_argument('-c','--camera', type = str, default = None, required=True,
                    help = 'camera')
parser.add_argument('--hdu', type = int, default = 0, required=False,
                    help = 'HDU to consider')

args = parser.parse_args()

ffile=pyfits.open(args.infile)
hdu=ffile[args.hdu]
header=hdu.header
header["EXTNAME"]=args.camera.upper()
header["CAMERA"]=args.camera.upper()

if args.camera.lower().find("r")==0: 
    
    print "tuned to first teststand image"
    
    
    
           
    
    
    header["DATASEC1"]='[10:2064,4:2065]'
    d1xmin,d1xmax,d1ymin,d1ymax = parse_sec_keyword(header["DATASEC1"])
    header["PRESEC1"]='[1:%d,%d:%d]'%(d1xmin-1,d1ymin,d1ymax)
    header["CCDSEC1"]='[1:%d,1:%d]'%(d1xmax-d1xmin+1,d1ymax-d1ymin+1)
    header["BIASSEC1"]='[%d:2100,%d:%d]'%(d1xmax+1,d1ymin,d1ymax)
    c1xmin,c1xmax,c1ymin,c1ymax = parse_sec_keyword(header["CCDSEC1"])
    p1xmin,p1xmax,p1ymin,p1ymax = parse_sec_keyword(header["PRESEC1"])
    b1xmin,b1xmax,b1ymin,b1ymax = parse_sec_keyword(header["BIASSEC1"])

    header["DATASEC2"]='[2137:4187,%d:%d]'%(d1ymin,d1ymax)
    d2xmin,d2xmax,d2ymin,d2ymax = parse_sec_keyword(header["DATASEC2"])
    header["PRESEC2"]='[%d:%d,%d:%d]'%(d2xmax,header["NAXIS1"],d2ymin,d2ymax)    
    header["BIASSEC2"]='[%d:%d,%d:%d]'%(b1xmax+1,d2xmin-1,d2ymin,d2ymax)    
    header["CCDSEC2"]='[%d:%d,%d:%d]'%(c1xmax+1,c1xmax+1+d2xmax-d2xmin,1,d2ymax-d2ymin+1)    
    c2xmin,c2xmax,c2ymin,c2ymax = parse_sec_keyword(header["CCDSEC2"])
    p2xmin,p2xmax,p2ymin,p2ymax = parse_sec_keyword(header["PRESEC2"])
    b2xmin,b2xmax,b2ymin,b2ymax = parse_sec_keyword(header["BIASSEC2"])
    
    header["DATASEC3"]='[%d:%d,2136:4197]'%(d1xmin,d1xmax)
    d3xmin,d3xmax,d3ymin,d3ymax = parse_sec_keyword(header["DATASEC3"])    
    header["PRESEC3"]='[%d:%d,%d:%d]'%(p1xmin,p1xmax,d3ymin,d3ymax)
    header["BIASSEC3"]='[%d:%d,%d:%d]'%(b1xmin,b1xmax,d3ymin,d3ymax)
    header["CCDSEC3"]='[%d:%d,%d:%d]'%(c1xmin,c1xmax,c1ymax+1,c1ymax+1+d3ymax-d3ymin)
    c3xmin,c3xmax,c3ymin,c3ymax = parse_sec_keyword(header["CCDSEC3"])
    
    header["DATASEC4"]='[%d:%d,%d:%d]'%(d2xmin,d2xmax,d3ymin,d3ymax)
    header["PRESEC4"]='[%d:%d,%d:%d]'%(p2xmin,p2xmax,d3ymin,d3ymax)
    header["BIASSEC4"]='[%d:%d,%d:%d]'%(b2xmin,b2xmax,d3ymin,d3ymax)
    header["CCDSEC4"]='[%d:%d,%d:%d]'%(c2xmin,c2xmax,c3ymin,c3ymax)
    
    if 1 :
        print "flip image !"
        hdu.data = hdu.data[::-1,:]
        print "now modify all SEC info"
        xmin,xmax,ymin,ymax = parse_sec_keyword(header["CCDSEC4"])        
        ny_ccd=ymax
        ny_input=header["NAXIS2"]
        
        header_copy=header.copy()
        newamps={1:3,2:4,3:1,4:2}
        for amp in range(1,5) :
            

            for sec in ["PRESEC","DATASEC","BIASSEC","CCDSEC"] :
                key="%s%d"%(sec,amp)
                xmin,xmax,ymin,ymax = parse_sec_keyword(header_copy[key])
                if sec == "CCDSEC" :
                    flipped_ymax=ny_ccd-ymin+1
                    flipped_ymin=ny_ccd-ymax+1
                else :
                    flipped_ymax=ny_input-ymin+1
                    flipped_ymin=ny_input-ymax+1
                key="%s%d"%(sec,newamps[amp])
                header[key]='[%d:%d,%d:%d]'%(xmin,xmax,flipped_ymin,flipped_ymax)
    
    for a in range(1,5) :
        key="GAIN%d"%a
        if not key in header :
            header[key]=1.
            print "WARNING !! MADE UP",key,header[key]
    
    #for k in ["DATASEC1","PRESEC1","CCDSEC1","BIASSEC1","DATASEC2","PRESEC2","CCDSEC2","BIASSEC2","DATASEC3","PRESEC3","CCDSEC3","BIASSEC3","DATASEC4","PRESEC4","CCDSEC4","BIASSEC4"]:
    for k in header.keys() :
        print k,"=",header[k]
    
    


else :
    print "not implemented yet for camera",args.camera
    sys.exit(12)



ffile.writeto(args.outfile,clobber=True)
print "wrote",args.outfile
print "done"