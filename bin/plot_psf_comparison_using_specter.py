#!/usr/bin/env python

import numpy as np
import astropy.io.fits as pyfits
import pylab
import specter.psf
import sys
import argparse
import string
import os.path
def readpsf(filename) :
    try :
        psftype=pyfits.open(filename)[0].header["PSFTYPE"]
    except KeyError :
        psftype=""
    print("PSF Type=",psftype)
    if psftype=="GAUSS-HERMITE" :
        return specter.psf.GaussHermitePSF(filename)
    elif psftype=="SPOTGRID" :
        return specter.psf.SpotGridPSF(filename)

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--psf1', type = str, default = None, required = True,
                    help = 'path of psf file')
parser.add_argument('--psf2', type = str, default = None, required = True,
                    help = 'path of psf second file')
parser.add_argument('--fiber', type = int, default = None, required = True,
                    help = 'fiber for psf1')
parser.add_argument('--fiber2', type = int, default = None, required = False,
                    help = 'fiber for psf2 (default=fiber1)')
parser.add_argument('--wavelength', type = float, default = 6000., required = False,
                    help = 'wavelength')
parser.add_argument('-o','--output', type = str, default = None, required = False,
                    help = 'path to output image (png) file')


args        = parser.parse_args()

if args.fiber2 is None :
    fiber2=args.fiber
else :
    fiber2=args.fiber2

psf1=readpsf(args.psf1)
psf2=readpsf(args.psf2)
xy1=psf1.xy(args.fiber,args.wavelength)
xy2=psf2.xy(fiber2,args.wavelength)
print("for psf1, xy=",xy1)
print("for psf2, xy=",xy2)


pylab.figure()
hw=5.
n1d=51
x=np.tile(np.linspace(-hw,hw,51),(n1d,1))
y=x.T
fpix1=psf1._value(x+xy1[0],y+xy1[1],args.fiber,args.wavelength)
fpix2=psf2._value(x+xy2[0],y+xy2[1],fiber2,args.wavelength)
fpix1 /= np.sum(fpix1)
fpix2 /= np.sum(fpix2)

mx1=np.sum(fpix1*x)
my1=np.sum(fpix1*y)
sigx1=np.sqrt(np.sum(fpix1*(x-mx1)**2))
sigy1=np.sqrt(np.sum(fpix1*(y-my1)**2))
mx2=np.sum(fpix2*x)
my2=np.sum(fpix2*y)
sigx2=np.sqrt(np.sum(fpix2*(x-mx2)**2))
sigy2=np.sqrt(np.sum(fpix2*(y-my2)**2))

print("psf1 sigx=%f sigy=%f"%(sigx1,sigy1))
print("psf2 sigx=%f sigy=%f"%(sigx2,sigy2))
print("sigx1/sigx2=%f sigy1/sigy2=%f"%(sigx1/sigx2,sigy1/sigy2))


a=pylab.subplot(2,2,1,title=os.path.basename(args.psf1))
pylab.imshow(fpix1,origin=0,interpolation="nearest",extent=(-hw,hw,-hw,hw))
pylab.text(-hw+0.3,-hw+0.8,"fiber #%d lambda=%dA"%(args.fiber,args.wavelength),fontsize=10,color="white")
pylab.text(-hw+0.3,-hw+0.1,"(x,y)=(%4.1f,%4.1f)"%(xy1[0],xy1[1]),fontsize=10,color="white")
pylab.subplot(2,2,2,title=os.path.basename(args.psf2))
pylab.imshow(fpix2,origin=0,interpolation="nearest",extent=(-hw,hw,-hw,hw))
pylab.text(-hw+0.3,-hw+0.8,"fiber #%d lambda=%dA"%(fiber2,args.wavelength),fontsize=10,color="white")
pylab.text(-hw+0.3,-hw+0.1,"(x,y)=(%4.1f,%4.1f)"%(xy2[0],xy2[1]),fontsize=10,color="white")
a=pylab.subplot(2,2,3,title="x prof.")
pylab.plot(x[n1d//2,:],fpix1[n1d//2,:],c="b")
pylab.plot(x[n1d//2,:],fpix2[n1d//2,:],c="r")
pylab.xlabel("x ccd")
a=pylab.subplot(2,2,4,title="y prof.")
pylab.plot(y[:,n1d//2],fpix1[:,n1d//2],c="b")
pylab.plot(y[:,n1d//2],fpix2[:,n1d//2],c="r")
pylab.xlabel("y ccd")

# do the ratio of psf2 integrals

ratio = np.sum(fpix1**2)/np.sum(fpix2**2)
print("single line photometric error=%f"%np.abs(ratio-1.))



pylab.show()

#pyfits.writeto(args.output,image,clobber=True)
