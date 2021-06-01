import pyvo as vo
from astropy import coordinates, units as ut
from matplotlib import pyplot as plt
from astropy.io import fits
import numpy as np

c = coordinates.SkyCoord.from_name('speca', frame='fk5')
hdul=[]
svys=['tgss','nvss','first',]
for i in range(len(svys)):

    if svys[i]=='tgss':
        url = 'https://vo.astron.nl/tgssadr/q_fits/imgs/siap.xml'
        service = vo.dal.SIAService(url)

        coords = c
        r=0.12
        im_table = service.search(pos=coords,size=r, intersect='covers')
        im_table.to_table()
        url = im_table[0].getdataurl()
        print(url)
        ra= str(c.ra.deg)
        dec=str(c.dec.deg)
        suffixurl='?sdec='+str(r)+'&dec='+dec+'&ra='+ra+'&sra='+str(r)
        download = url + str(suffixurl)
        hdul.append( fits.open(download))
        #hdul = fits.open(download)
        
        #plt.show()
    else :
        url= 'http://skyview.gsfc.nasa.gov/cgi-bin/vo/sia.pl?survey='+svys[i]+'&'
        service=vo.dal.SIAService(url)

        im_table = service.search(pos=c,size=r,intersect='covers')
        im_table.to_table()     
        url = im_table[0].getdataurl()
        hdul.append( fits.open(url))
        print(url)

print(np.shape(hdul[0][0].data))

