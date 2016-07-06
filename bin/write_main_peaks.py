#!/usr/bin/env python

import numpy as np
import desispec.bootcalib
import argparse
import os.path
import sys

# convert air to vacuum, this is IDL routine airtovac for instance :
# http://idlastro.gsfc.nasa.gov/ftp/pro/astro/airtovac.pro
def convert_air_to_vacuum(air_wave) :
    # idl code :
    # for iter=0, 1 do begin
    # sigma2 = (1d4/double(wave_vac[g]) )^2.     ;Convert to wavenumber squared
    # ; Compute conversion factor
    # fact = 1.D +  5.792105D-2/(238.0185D0 - sigma2) + $
    #                        1.67917D-3/( 57.362D0 - sigma2)
    # wave_vac[g] = wave_air[g]*fact              ;Convert Wavelength
    # endfor
        
    sigma2 = (1e4/air_wave)**2
    fact = 1. +  5.792105e-2/(238.0185 - sigma2) +  1.67917e-3/( 57.362 - sigma2)
    vacuum_wave = air_wave*fact

    # comparison with http://www.sdss.org/dr7/products/spectra/vacwavelength.html
    # where : AIR = VAC / (1.0 + 2.735182E-4 + 131.4182 / VAC^2 + 2.76249E8 / VAC^4)
    # air_wave=numpy.array([4861.363,4958.911,5006.843,6548.05,6562.801,6583.45,6716.44,6730.82])
    # expected_vacuum_wave=numpy.array([4862.721,4960.295,5008.239,6549.86,6564.614,6585.27,6718.29,6732.68])
    # test ok
    return vacuum_wave

parser = argparse.ArgumentParser()

parser.add_argument('-o','--outfile', type = str, default = None, required=True, help="output ASCII file")
parser.add_argument('--air', action = "store_true", help="wavelength in air (default is vacuum)")
parser.add_argument('--subset', type = str, default = None, required=False, help="match with those lines")

args=parser.parse_args()

vacuum=True
if args.air :
    vacuum=False

nist_list=desispec.bootcalib.load_arcline_list(camera="all", vacuum=vacuum, lamps=None)
nist_ion=np.array(nist_list["Ion"])
nist_wave=np.array(nist_list["wave"])

if args.subset :
    subset_air_wave=[]
    subset_ion=[]
    ifile=open(args.subset)
    for line in ifile.readlines() :
        if line[0]=="#" :
            continue
        vals=line.strip().split()
        subset_air_wave.append(float(vals[0]))
        subset_ion.append((vals[1]))
    ifile.close()

    subset_air_wave=np.array(subset_air_wave)
    subset_ion=np.array(subset_ion)
    if args.air :
        subset_wave = subset_air_wave
    else :
        subset_wave = convert_air_to_vacuum(subset_air_wave)

    # match with NIST line list
    nist_subset_wave=[]
    nist_subset_ion=[]
    for wave,ion in zip(subset_wave,subset_ion) :
        ok=np.where(nist_ion==ion)[0]
        if ok.size==0 :
            print "no ",ion
            continue
        j=np.argmin(np.abs(wave-nist_wave[ok]))
        nwave=nist_wave[ok][j]
        delta=np.abs(nwave-wave)
        if delta>1. :
            print "error no good match of",wave,ion," delta=",delta
            continue
        nist_subset_wave.append(nwave)
        nist_subset_ion.append(ion)
    nist_subset_wave=np.array(nist_subset_wave)
    nist_subset_ion=np.array(nist_subset_ion)
    
    wave=nist_subset_wave
    ion=nist_subset_ion
else :
    wave=nist_wave
    ion=nist_ion

sort=np.argsort(wave)
ofile=open(args.outfile,"w")
ofile.write("# generated by %s , based on NIST\n"%sys.argv[0])
if args.subset :
    ofile.write("# using subsample of lines in %s\n"%args.subset)

if vacuum :
    ofile.write("# WAVE (A, IN VACUUM) ION\n")
else :
    ofile.write("# WAVE (A, IN AIR) ION\n")
for line in sort :
    ofile.write("%f %s\n"%(wave[line],ion[line]))
ofile.close()


