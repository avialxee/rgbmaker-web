from astroquery.skyview import SkyView as skv
#import concurrent.futures
import numpy as np
imglt = []
px = 480
def get_imgl_pool(cals):
    c, svy, r,sam,sca,queue,ind,cach = cals
    # Some error in caching skyview at 600 px so using 480px
    try:
        imglr = skv.get_images(c, svy, pixels=str(px), radius=r, scaling=sca, sampler=sam, cache=cach)
        #print('Fetched %s from %s' % (len(imglr), ind))
        queue[ind] = imglr
    except :
        #print("inside error" + str(ind))
        pass
    return queue

#def run_imgl_pool(c,r,issvys,sam,sca,cache):
#    
#    try:
#        with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor:
#            result =[0]*len(issvys)
#            try :
#                imglt = [executor.submit(get_imgl_pool, [c, issvys[ind], r,sam[ind],sca[ind], result, ind, cache]) for ind in range(len(issvys))]
#            except Exception as e:
#                raise  e
#        return result, None
#    except Exception as e:
#        raise  e 

# ----------- removing use of thread pool concurrency -----------------#
def run_imgl(c,r,issvys,sam,sca,cache):
    result = [0]*len(issvys)
    error=None
    try : 
        for ind in range(len(issvys)):
            imglt= get_imgl_pool([c, issvys[ind], r,sam[ind],sca[ind], result, ind, cache])
    except Exception as e:
        error = e
    return imglt, error

def getdd(c,r,insvys) :
    # CONSTANTS
    sam=[None,"Lanczos3",None]
    sca=["Sqrt", "Sqrt", "loglog"] # --- astroquery: SkyView Log doesn't work --- #
    imglt=[]
    pool_svys=[]
    for s in range(len(insvys)):
        pool_svys+=insvys[s]
        sam += [sam[s]]*len(insvys[s])
        sca += [sca[s]]*len(insvys[s])
    imgls, error = run_imgl(c,r, pool_svys,sam,sca,"True")
    #if not error and len(imgls)==0:
    #    imgls, error = run_imgl_pool(c,r,pool_svys,sam,"False")
    # can also be included in run pool
    for i in range(len(imgls)) :
        if imgls[i]==0:
            imglt.insert(i,[np.zeros((px,px)),None])
        else:
            imglt.append([imgls[i][0][0].data, imgls[i][0][0].header])
    # returns [[hdulist], error]    
    return imglt, error

# DEBUG

#from astropy import coordinates, units as ut
#insvys=[['TGSS ADR1'],['NVSS','VLA FIRST (1.4 GHz)'],['DSS2 Red']]
#c = coordinates.SkyCoord.from_name("3c33.1", frame='fk5')
#print(np.shape(getdd(c, 0.12*ut.degree, insvys)[0][0][0]))
