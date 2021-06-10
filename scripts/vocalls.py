import pyvo as vo
from astropy import coordinates, units as ut
from matplotlib import pyplot as plt
from astropy.io import fits
import numpy as np

c = coordinates.SkyCoord.from_name('speca', frame='fk5')
hdul=[]
svys=['tgss','nvss','first',]
def getdd_vo(c,svys,r=0.12):
    for i in range(len(svys)):
        if svys[i]=='tgssss':
            url = 'https://vo.astron.nl/tgssadr/q_fits/imgs/siap.xml'
            service = vo.dal.SIAService(url)

            coords = c
            r=0.12
            im_table = service.search(pos=coords,size=r, intersect='covers')
            im_table.to_table()
            url = im_table[0].getdataurl()
            #print(url)
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
            #hdul.append(fits.open(url))
    return hdul

#print(getdd_vo(c,svys,0.12))
#print(np.shape(hdul[0][0].data))

px=480
def get_imgl_pool(cals):
    c, svy, r, sam, sca, queue, ind, cach = cals
    # Some error in caching skyview at 600 px so using 480px
    try:
        #imglr = skv.get_images(c, svy, pixels=str(
        #    px), radius=r, scaling=sca, sampler=sam, cache=cach)
        url = 'http://skyview.gsfc.nasa.gov/cgi-bin/vo/sia.pl?survey=' + \
            svy+'&'
        service = vo.dal.SIAService(url)

        im_table = service.search(pos=c, size=r, intersect='covers')
        im_table.to_table()
        url = im_table[0].getdataurl()

        #print('Fetched %s from %s' % (len(imglr), ind))
        queue[ind] = fits.open(url)
    except:
        #print("inside error" + str(ind))
        pass
    return queue

def run_imgl(c, r, issvys, sam, sca, cache):
    result = [0]*len(issvys)
    error = None
    try:
        for ind in range(len(issvys)):
            imglt = get_imgl_pool(
                [c, issvys[ind], r, sam[ind], sca[ind], result, ind, cache])
    except Exception as e:
        error = e
    return imglt, error

imglt=[]
svys = ['tgss', 'nvss', 'first', 'dss2']
def getdd(c, r, svys):
    imgls = getdd_vo(c, svys, r)
    for i in range(len(imgls)):
        if imgls[i] == 0:
            imglt.insert(i, [np.zeros((px, px)), None])
        else:
            imglt.append([imgls[i][0].data, imgls[i][0].header])
    # returns [[hdulist], error]
    return imglt

#print(getdd(c,0.12,svys))

