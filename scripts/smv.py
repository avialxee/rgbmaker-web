
from astroquery.nvas import Nvas
from astroquery.vizier import Vizier

from warnings import simplefilter
from astropy.io import fits as fts
from astropy import coordinates, units as ut
from astropy.wcs import WCS
from time import perf_counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#from regions import EllipseSkyRegion as esr

import numpy as np
import math
import io
import urllib, base64
import matplotlib
from scripts import multipool
#import multipool
matplotlib.rcParams['font.size']=15
#import cProfile, pstats
#pr = cProfile.Profile()
#pr.enable()



## LIBRARY ==============================

#nbi:hide_in
def linear(inputArray, scale_min=None, scale_max=None):
    imageData=np.array(inputArray, copy=True)

    if scale_min == None:
        scale_min = imageData.min()
    if scale_max == None:
        scale_max = imageData.max()

    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = (imageData -scale_min) / (scale_max - scale_min)
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    indices = np.where(imageData > 1)
    imageData[indices] = 1.0

    return imageData

def sqrt(inputArray, scale_min=None, scale_max=None):
    imageData=np.array(inputArray, copy=True)

    if scale_min == None:
        scale_min = imageData.min()
    if scale_max == None:
        scale_max = imageData.max()

    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = imageData - scale_min
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    imageData = np.sqrt(imageData)
    imageData = imageData / math.sqrt(scale_max - scale_min)

    return imageData


def overlayc (r,g,b,c,lvl,cmin) :
  ri = normals(r)
  gi = normals(g)
  bi = normals(b)
  if ri.max() != 0 and ri.min()!=0 :
    ri = sqrt(ri,scale_min=0.1*np.std(ri),scale_max=np.max(ri))
  if gi.max() != 0 and gi.min()!=0 :
    gi = sqrt(gi,scale_min=0.1*np.std(gi),scale_max=np.max(gi))
  if bi.max() != 0 and bi.min()!=0 :
    bi = sqrt(bi,scale_min=0.1*np.std(bi),scale_max=np.max(bi))
  replace = bi > 1
  bi[replace] = 1
  replace = gi > 1
  gi[replace] = 1
  replace = ri > 1
  ri[replace] = 1
  #Stacking the Images and set up as 8-bit integers (highest value 2^8 = 256)
  img = (np.dstack((ri,gi,bi))*255.99).astype(np.uint8)
  if c.max() > cmin :
    lvlc = np.arange(cmin, c.max(),((c.max() - cmin)/lvl))
  else :
    lvlc = None
  return img, lvlc

def normals(o) :
  X_scaled =(o - np.median(o))
  if o.max()!=0 :
    X = X_scaled/o.max()
    return X
  else :
    return X_scaled

def overlayo(r, g, b) :
  ri = normals(r)
  gi = normals(g)
  bi = normals(b)
  if ri.max() != 0 and ri.min()!=0 :
    ri = linear(ri,scale_min=np.min(ri),scale_max=np.max(ri))
  if gi.max() != 0 and gi.min()!=0 :
    gi = linear(gi,scale_min=np.min(gi),scale_max=np.max(gi))
  if bi.max() != 0 and bi.min()!=0 :
    bi = linear(bi,scale_min=np.min(bi),scale_max=np.max(bi))  
  #Replace any value higher than 1 with 1 
  replace = bi > 1
  bi[replace] = 1
  replace = gi > 1
  gi[replace] = 1
  replace = ri > 1
  ri[replace] = 1
  #Stack the Images and set up as 8-bit integers (highest value 2^8 = 256)
  img = (np.dstack((ri,gi,bi))*255.99).astype(np.uint8)
  return img

def pl_RGB(rows,columns,i,wcs,svy,lvlc,img,fig,name) :
    ax = fig.add_subplot(rows, columns, i, projection=wcs)
    ax.axis( 'off')
    ax.imshow(img)
    ax.annotate("#RADatHomeIndia",(10,10),color='white')
    ax.annotate("By " + str(name),(400-5*len(name),10),color='white')
    ax.set_autoscale_on(False)

    plt.contour(svy, lvlc, colors='white')
    if i==1 :
        ax.set_title("ROR with NVSS contour ",y=1,pad=-16,color="white")
        #ax.set_title("")
    if i==2 :
        ax.set_title("ROR with TGSS contour ",y=1,pad=-16,color="white")
    if i==3 :
        ax.set_title("IOU with TGSS contour ",y=1,pad=-16,color="white")
    if i==4 :
        ax.set_title("Optical with TGSS contour ",y=1,pad=-16,color="white")



## ====== Settings ========================
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
#VerifyWarning by astropy for NVSS in 2 
simplefilter('ignore', category=UserWarning)




## == MAIN CODE =============================================================================>




def query (name="",position="",radius=float(0.12),archives=1,imagesopt=2) :

  name = str(name)
  if len(name)<=2 :
      name = "Anonymous"
  
  # initializing values
  pixels=480
  levelc=4
  start=perf_counter()
  c = None
  
  r = float(str(radius))*ut.degree
  i=0
  uri=""
  info=""
  imglt=[]
  wcs=None
  status="info"

##########=============######## 0. COORDINATES CHECK #########=================#####
  try :
    c = coordinates.SkyCoord.from_name(position, frame='fk5')
  except :
    info = " Please check coordinates"
    status="warning"
  


  ##########=============######## 1. PLOTTING  RGBC #########=================#####
  if int(imagesopt) == 1 and c:
    # 1. creating image list of the fits to retrieve
    try:  
      
      svys=[['TGSS ADR1'],['NVSS'],['DSS2 Red', 'DSS2 IR', 'DSS2 Blue', 'WISE 22', 'GALEX Near UV']]
      
      rftsget, info = multipool.getdd(c,r,svys)
      
      for result in rftsget :
        if not wcs :
          wcs = WCS(result[1])
    except:
      info=" issue fetching data from server"
    
    if wcs :
      
      tgss=rftsget[0][0]
      nvss=rftsget[1][0]
      dss2r=rftsget[2][0]
      dss2i = rftsget[3][0]
      dss2b = rftsget[4][0]
      w22 = rftsget[5][0]
      gnuv = rftsget[6][0]


      ######==== 1. PLOTTING RGBC ====#####

      # plots initialization
      img1, lvlc1 = overlayc(tgss,dss2r,nvss, nvss, levelc, 0.0015)
      img2, lvlc2 = overlayc(tgss,dss2r,nvss,tgss, levelc, 0.015)
      img3 = overlayo(w22,dss2r,gnuv)
      img4 = overlayo(dss2i,dss2r,dss2b)

      
      # plotting
      plt.ioff()
      fig = plt.figure(figsize=(20, 20))
      l6 = "images downloaded: drawing...."
      pl_RGB(2,2,1,wcs,nvss,lvlc1,img1,fig,name)
      pl_RGB(2,2,2,wcs,tgss,lvlc2,img2,fig,name)
      pl_RGB(2,2,3,wcs,tgss,lvlc2,img3,fig,name)
      pl_RGB(2,2,4,wcs,tgss,lvlc2,img4,fig,name)
      plt.subplots_adjust(wspace=0.01,hspace=0.01)
      ############ Saving final plot #####################
      buf = io.BytesIO()
      fig.savefig(buf, format='png',bbox_inches='tight', transparent=True, pad_inches=0)
      buf.seek(0)
      string = base64.b64encode(buf.read())
      plt.close()
      uri = 'data:image/png;base64,' + urllib.parse.quote(string)
      time_taken=perf_counter()-start
      info = 'completed in ' + str(np.round (time_taken,3))+". "
      status = "success"
    else :
      info = " No images found."
      uri = ""
      status = "warning"




  ##########=============######## 2. PLOTTING [SINGLE SURVEY] image with contour and RGBC #########=================#####

  if int(imagesopt) == 2 and c:
    # creating image list of the fits to retrieve
    

    try:  
      svys=[['TGSS ADR1'],['NVSS','VLA FIRST (1.4 GHz)'],['DSS2 Red']]
      rftsget, info = multipool.getdd(c,r,svys)
      
      for result in rftsget :
        if not wcs :
          wcs = WCS(result[1])
    except:
      info=" issue fetching data from server"
    
    
    if wcs :
      tgss=rftsget[0][0]
      nvss=rftsget[1][0]
      first=rftsget[2][0]
      dss2r=rftsget[3][0]

            ######==== 2. Vizier access for TGSS catalog ====#####
      nra,ndec,tra,tdec=([],)*4
      
      #print(nra,ndec)
            ######==== 2. PLOTTING SINGLE SURVEY====#####
      
      # plots initialization
      img1, lvlc1 = overlayc(tgss,dss2r,nvss, tgss, levelc, 0.015)
      if tgss.max() > 0.015 :
          lvlct = np.arange(0.015, tgss.max(),((tgss.max() - 0.015)/levelc))
      else :
          lvlct=None
      if first.max() > 0.0005 :
          lvlcf = np.arange(0.0005, first.max(),((first.max() - 0.0005)/levelc))
      else :
          lvlcf=None
      if nvss.max() > 0.0015 :
          lvlcn = np.arange(0.0015, nvss.max(),((nvss.max() - 0.0015)/levelc))
      else :
          lvlcn=None
          

      # plotting

      plt.ioff()
      fig = plt.figure(figsize=(20, 20))
      
      # RGBC plot
      ax1 = fig.add_subplot(1,2,1, projection=wcs) 
      ax1.axis('off')    
      ax1.imshow(img1) 
      ax1.annotate("#RADatHomeIndia",(10,10),color='white')
      ax1.annotate("By " + str(name),(400-5*len(name),10),color='white')
      ax1.set_autoscale_on(False)
      ax1.contour(tgss, lvlc1, colors='white')
      
      try:
        try:
        

          tviz = Vizier.query_region(c,r, catalog='J/A+A/598/A78/table3')
          tra=tviz[0]['RAJ2000']*ut.deg
          tdec=tviz[0]['DEJ2000']*ut.deg
          ax1.scatter(tra, tdec, transform=ax1.get_transform('fk5'), s=300,
            edgecolor='yellow', color='gold', zorder=4, marker='1', alpha=1, label='TGSS Catalog')
        
        finally:
          nviz = Vizier.query_region(c,r, catalog='VIII/65/nvss')
          nra=coordinates.Angle(nviz[0]['RAJ2000'], unit=ut.hour).deg
          ndec=coordinates.Angle(nviz[0]['DEJ2000'], unit=ut.deg).deg
          ax1.scatter(nra, ndec, transform=ax1.get_transform('fk5'), s=300,
            edgecolor='cyan', color='none', zorder=3, marker='.', label='NVSS Catalog')
        
        #cs=coordinates.SkyCoord(ra,dec,frame='fk5')
        
      except:
        info=" Catalog data missing!"
      finally:
        ax1.legend(framealpha=0.0,labelcolor='white')
        
        # Single Survey plot
        dss2r = sqrt(dss2r,scale_min=0.5*np.std(dss2r),scale_max=np.max(dss2r))
        ax2 = fig.add_subplot(1,2,2, projection=wcs)
        ax2.axis( 'off')    
        ax2.imshow(dss2r, origin='lower', cmap='gist_gray') 
        ax2.annotate("#RADatHomeIndia",(10,10),color='white')
        ax2.annotate("By " + str(name),(400-5*len(name),10),color='white')
        ax2.set_autoscale_on(False)
        
        ax2.contour(nvss, levels=lvlcn, colors='blue')
        ax2.contour(tgss, lvlct, colors='magenta')
        ax2.contour(first, lvlcf, colors='yellow')
        
        leg1 = mpatches.Patch(color='blue', label='NVSS')
        leg2 = mpatches.Patch(color='magenta', label='TGSS')
        leg3 = mpatches.Patch(color='yellow', label='FIRST')
        leg4 = mpatches.Patch(color='grey', label='DSS2R')
        
        ax2.legend(handles=[leg1,leg2,leg3,leg4], labelcolor='linecolor', framealpha=0.0,)
        ax2.autoscale(False)
        
        plt.subplots_adjust(wspace=0.01,hspace=0.01)
        #esky = esr(cs, height=blobM[0]*ut.arcsec, width=blobm[0]*ut.arcsec, angle=pa[0]*ut.arcsec)
        #sky_pix.plot()


        ############ Saving final plot #####################
        buf = io.BytesIO()
        fig.savefig(buf, format='png',bbox_inches='tight', transparent=True, pad_inches=0)
        buf.seek(0)
        string = base64.b64encode(buf.read())
        plt.close()
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        time_taken=perf_counter()-start
        info = 'completed in ' + str(np.round (time_taken,3))+". "
        status = "success"
    else :
      info = " No images found."
      uri = ""
      status = "warning"
  

  if archives and int(archives) == 2 and c:
      
      #  NVAS
      try :
          nvas_urls = Nvas.get_image_list(c,radius=2*ut.arcsec)
          info += " " + str(len(nvas_urls)) + " Image(s) found in NVAS: "
          i = 1
          for nvas in nvas_urls :
            if i<=5 :
              info += " <a href='" + str(nvas)+ "'>["+ str(i) + "]</a>"
              i+=1

          status = "success"
      except :
          status = "warning"
          info+=" NVAS has no image"
#  else :
#    #status=
#    uri=""
#    info="ERROR"
      
  return status, uri, info

#  DEBUG :

#print(query(position="speca"))
#pr.disable()
#s = io.StringIO()
#sortby = 'cumulative'
#ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#ps.print_stats()
#print( s.getvalue())