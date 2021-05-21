#!/usr/bin/env python
#from multiprocessing.pool import ThreadPool
from time import time as timer
from urllib.request import urlopen
from astropy import coordinates, units as ut
from astroquery.skyview import SkyView as skv
import numpy as np

import concurrent.futures
from astropy.io import fits as fts

start = timer()


def get_imgl_pool(cals):
  c, svy, r,sam,queue,ind = cals
  imglr = skv.get_image_list(c, svy, pixels="600", radius=r, scaling="Sqrt", sampler=sam, cache=False)
  print('Fetched %s from %s' % (len(imglr), ind))
  queue[ind] = imglr
def run_imgl_pool(c,r,svys,sam):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
            result =list(range(len(svys)))
            imglt = [executor.submit(get_imgl_pool, [c,svys[ind],r,sam[ind],result,ind]) for ind in list(range(len(svys)))]
        
        return result, None
    except Exception as e:
        return None, e 
def fetch_imgl_pool(c,r,svys,sam):
    result =list(range(len(svys)))
    #results = ThreadPool(20).imap_unordered(fetch_url, urls)

    
    try:
        #result = queue.Queue()
        result =list(range(len(svys)))
        imglt = [ThreadPool(1).starmap(get_imgl_pool, [(c,svys[ind],r,sam[ind],result,ind)]) for ind in list(range(len(svys)))]
        
        return result, None
    except Exception as e:
        return None, e 






def read_url(cals):
  url, queue, i_url = cals
  #print(url[i_url])
  data = urlopen(url, timeout=10)
  fget = fts.getdata(data, header=True)
  print('Fetched %s from %s' % (len(fget), i_url))
  queue[i_url] = fget
  #queue.task_done()
  #queue.put(fget)

def fetch_parallel(urls):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
            result =list(range(len(urls)))
            imglt = [executor.submit(read_url, [urls[i_url],result, i_url]) for i_url in list(range(len(urls)))]
        
        return result, None
    except Exception as e:
        return None, e 



svys=[['TGSS ADR1'],['NVSS'],['DSS2 Red', 'DSS2 IR', 'DSS2 Blue', 'WISE 22', 'GALEX Near UV']]
sam=[None,"Lanczos3",None]
radius = 0.12*ut.degree

imglt=[]
imgls, error = run_imgl_pool("speca",radius, svys,sam)
imglt.extend(imgls[0])
imglt.extend(imgls[1])
imglt.extend(imgls[2])
img, errs = fetch_parallel(imglt)
print([img, error])
#for future in concurrent.futures.as_completed(imgls):

#    print(future.result())


print(" fetched in %ss" % ( timer() - start))




#with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
#
#    future_to_url = {executor.submit(get_imgl_pool, url, 60): url for url in URLS}
#    for future in concurrent.futures.as_completed(future_to_url):
#        url = future_to_url[future]
#        try:
#            data = future.result()
#        except Exception as exc:
#            print('%r generated an exception: %s' % (url, exc))
#        else:
#            print('%r page is %d bytes' % (url, len(data)))
#
#
#

#urls = ["http://www.google.com", "http://www.apple.com", "http://www.microsoft.com", "http://www.amazon.com", "http://www.facebook.com"]
#
#def fetch_url(url):
#    try:
#        response = urlopen(url)
#        return url, response.read(), None
#    except Exception as e:
#        return url, None, e
#
#start = timer()
#results = ThreadPool(2).imap_unordered(fetch_url, urls)
#for url, html, error in results:
#    if error is None:
#        print("%r fetched in %ss" % (url, timer() - start))
#        print(html)
#    else:
#        print("error fetching %r: %s" % (url, error))
#print("Elapsed Time: %s" % (timer() - start))
