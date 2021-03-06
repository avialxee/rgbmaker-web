
from astropy.coordinates import Angle
from regions import PixCoord, EllipsePixelRegion
from matplotlib.collections import PatchCollection
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
#from scripts import vocalls
#import multipool
matplotlib.rcParams['font.size']=11
#import cProfile, pstats
#pr = cProfile.Profile()
#pr.enable()


## LIBRARY ==============================

#nbi:hide_in
def linear(inputArray, scale_min=None, scale_max=None):
    if not inputArray.max==0:
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
  if not inputArray.max == 0:
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


def log(inputArray, scale_min=None, scale_max=None,factor=2.0):
  if not inputArray.max == 0:
    imageData = np.array(inputArray, copy=True)


    if scale_min == None:
        scale_min = imageData.min()
    if scale_max == None:
      scale_max = imageData.max()
    #factor =math.log10(scale_max - scale_min)
    indices0 = np.where(imageData < 0)
    indices1 = np.where((imageData >= scale_min) & (imageData <= scale_max))
    indices2 = np.where(imageData > scale_max)
    imageData[indices0] = 0.0
    imageData[indices2] = 1.0
    try:
      imageData[indices1] = np.log10(imageData[indices1])/factor
    except:
      print ("Error on math.log10 ")
   
  return imageData

def overlayc (r,g,b,c,lvl,cmin) :
  ri = normals(r)
  gi = normals(g)
  bi = normals(b)
  if ri.max() != 0 and ri.min()!=0 :
    ri = sqrt(ri,scale_min=0.1*np.std(ri),scale_max=np.max(ri))
  if gi.max() != 0 and gi.min()!=0 :
    gi = sqrt(gi, scale_min=0.1*np.std(gi), scale_max=np.max(gi))
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


def overlayo(ri, gi, bi, kind = 'IOU'):
  if kind == 'IOU':
    ri = sqrt(ri, scale_min=np.percentile(np.unique(ri),1.), scale_max=np.percentile(np.unique(ri),100.))
    gi = sqrt(gi, scale_min=np.percentile(np.unique(gi),1.), scale_max=np.percentile(np.unique(gi),100.))
    #gi = log(gi, scale_min=np.percentile(np.unique(gi),0.), scale_max=np.percentile(np.unique(gi),100.),factor=2.85)
    bi = log(bi, scale_min=np.percentile(np.unique(bi),1.), scale_max=np.percentile(np.unique(bi),100.),factor=3.14)
    mul_factor = 255/ri.max()
    img = (np.transpose([(ri*mul_factor).astype(np.uint8),(gi*255/gi.max()).astype(np.uint8),(bi*255).astype(np.uint8)], (1, 2, 0)))

  if kind == 'Optical':
    #ri = log(ri, scale_min=np.percentile(np.unique(ri),1.), scale_max=np.percentile(np.unique(ri),100.),factor=0.3)
    ri = sqrt(ri, scale_min=np.min(ri), scale_max=np.percentile(np.unique(ri),100.))
    gi = sqrt(gi, scale_min=1.15*np.min(gi), scale_max=np.percentile(np.unique(gi),100.))
    #gi = log(gi, scale_min=np.percentile(np.unique(gi),0.), scale_max=np.percentile(np.unique(gi),100.),factor=7.85)
    #bi = log(bi, scale_min=np.percentile(np.unique(bi),1.), scale_max=np.percentile(np.unique(bi),100.),factor=3.15)
    bi = sqrt(bi, scale_min=np.min(bi), scale_max=np.percentile(np.unique(bi),100.))
    mul_factor = 255/ri.max()
    img = (np.transpose([(ri*mul_factor).astype(np.uint8),(gi*255.99).astype(np.uint8),(bi*256).astype(np.uint8)], (1, 2, 0)))
  #img = (np.dstack((ri,gi,bi))*255.99).astype(np.uint8)
  #img = np.stack([ri,gi,bi], axis=2)
  return img

def pl_RGB(rows,columns,i,wcs,svy,lvlc,img,fig,name) :
    ax = fig.add_subplot(rows, columns, i, projection=wcs)
    ax.axis( 'off')
    ax.imshow(img, origin='lower', interpolation='nearest')
    ax.annotate("#RADatHomeIndia",(10,10),color='white')
    ax.annotate("By " + str(name),(400-5*len(name),10),color='white')
    ax.set_autoscale_on(False)

    plt.contour(svy, lvlc, colors='white')
    if i==1 :
        ax.set_title("ROR-RGB-C: TGSS(GMRT)-DSS2-NVSS(VLA)-NVSS",
                     y=1, pad=-16, color="white")
        #ax.set_title("")
    if i==2 :
        ax.set_title("ROR-RGB-C: TGSS(GMRT)-DSS2-NVSS(VLA)-TGSS",
                     y=1, pad=-16, color="white")
    if i==3 :
        ax.set_title("IOU-RGB-C: WISE(22)-DSS2(red)-GALEX(NUV)-TGSS",
                     y=1, pad=-16, color="white")
    if i==4 :
        ax.set_title("Optical-RGB-C: DSS2(IR)-DSS2(Red)-DSS2(blue)-TGSS",
                     y=1, pad=-16, color="white")


# ------------ arcsec to pixel conversion ----------------------------#-#

def to_pixel(unit_inarcsec, r, px = 480):
    nvss_px_scale = px/(r)
    return np.round(((unit_inarcsec/3600) * ut.deg * nvss_px_scale), 2).value


## ====== Settings ========================
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
#VerifyWarning by astropy for NVSS in 2 
simplefilter('ignore', category=UserWarning)




## == MAIN CODE =============================================================================>




def query (name="",position="",radius=float(0.12),archives=1,imagesopt=2) :

  name = str(name)
  if len(name)<=2 :
    name = "Anonymous"
  if len(name)>15:
    name = name[:28]
  # initializing values
  pixels=480
  levelc=4
  start=perf_counter()
  c = None
  if float(str(radius)) > 2.0:
    r = 2.0
  r = float(str(radius))*ut.degree

  i=0
  uri=""
  info=""
  imglt=[]
  wcs=None
  status="info"
  otext=[]
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

      otext.append({'TGSSmin': str(tgss.min())})
      otext.append({'TGSSmax': str(tgss.max())})
      otext.append({'NVSSmin': str(nvss.min())})
      otext.append({'NVSSmax': str(nvss.max())})
      
      ######==== 1. PLOTTING RGBC ====#####

      # plots initialization
      img1, lvlc1 = overlayc(tgss,dss2r,nvss, nvss, levelc, 0.0015)
      img2, lvlc2 = overlayc(tgss,dss2r,nvss,tgss, levelc, 0.015)
      img3 = overlayo(w22,dss2r,gnuv, kind='IOU')
      img4 = overlayo(dss2i,dss2r,dss2b, kind='Optical')
      if lvlc1:
        otext.append({'TGSS_': (str(np.round(lvlc1, 3)))})
      if lvlc2:
        otext.append({'NVSS_': (str(np.round(lvlc2, 4)))})
      
      # plotting
      plt.ioff()
      fig = plt.figure(figsize=(20, 20))
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
      time_taken = perf_counter()-start
      info += ' Time taken:' + str(np.round(time_taken, 3))+". "
      uri = ""
      status = "warning"




  ##########=============######## 2. PLOTTING [SINGLE SURVEY] image with contour and RGBC #########=================#####

  if int(imagesopt) == 2 and c:
    # creating image list of the fits to retrieve
    

    try:  
      svys=[['TGSS ADR1'],['NVSS','VLA FIRST (1.4 GHz)'],['DSS2 Red']]
      rftsget, info = multipool.getdd(c,r,svys)
      #svys = ['tgss', 'nvss', 'first', 'dss2']
      #rftsget = vocalls.getdd(c, r, svys)
      

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

      otext.append({'TGSSmin': str(tgss.min())})
      otext.append({'TGSSmax': str(tgss.max())})
      otext.append({'NVSSmin': str(nvss.min())})
      otext.append({'NVSSmax': str(nvss.max())})
      otext.append({'FIRSTmin': str(first.min())})
      otext.append({'FIRSTmax': str(first.max())})
            ######==== 2. Vizier access for TGSS catalog ====#####
      nra,ndec,tra,tdec=([],)*4
      
      #print(nra,ndec)
            ######==== 2. PLOTTING SINGLE SURVEY====#####
      
      # plots initialization
      img1, lvlc1 = overlayc(tgss,dss2r,nvss, tgss, levelc, 0.015)
      if tgss.max() > 0.015 :
          lvlct = np.arange(0.015, tgss.max(),((tgss.max() - 0.015)/levelc))
          otext.append({'TGSS_': (str(np.round(lvlct, 3)))})
      else :
          lvlct=None
      if first.max() > 0.0005 :
          lvlcf = np.arange(0.0005, first.max(),((first.max() - 0.0005)/levelc))
          otext.append({'FIRST_': (str(np.round(lvlcf,4)))})    
      else :
          lvlcf=None
      if nvss.max() > 0.0015 :
          lvlcn = np.arange(0.0015, nvss.max(),((nvss.max() - 0.0015)/levelc))
          otext.append({'NVSS_': (str(np.round(lvlcn, 4)))})
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
      ax1.set_title('ROR-RGB-C: TGSS(GMRT)-DSS2-NVSS(VLA)-TGSS',
                    y=1, pad=-16, color="white")
      try:
        try:
        

          tviz = Vizier(columns=['RAJ2000','DEJ2000','Maj','Min','PA' ]).query_region(c,r, catalog='J/A+A/598/A78/table3')
          tra=tviz[0]['RAJ2000']*ut.deg
          tdec=tviz[0]['DEJ2000']*ut.deg
          ax1.scatter(tra, tdec, transform=ax1.get_transform('fk5'), s=300,
            edgecolor='yellow', color='gold', zorder=4, marker='1', alpha=1, label='TGSS Catalog')
          tra = tviz[0]['RAJ2000']  # *ut.deg
          tdec = tviz[0]['DEJ2000']  # *ut.deg
          tMaj = tviz[0]['Maj']
          tMin = tviz[0]['Min']
          tPA = tviz[0]['PA']

          center_tgss = coordinates.SkyCoord(ra=tra, dec=tdec)
          center_tgss_px = wcs.world_to_pixel(center_tgss)
          patch1 = []
          for i in range(len(center_tgss_px[0])):
              x, y = center_tgss_px[0][i], center_tgss_px[1][i]
              ce = PixCoord(x, y)
              a = to_pixel(tMaj[i],r)
              b = to_pixel(tMin[i], r)
              theta =Angle(tPA[i], 'deg') + 90*ut.deg

              reg = EllipsePixelRegion(center=ce, width=a, height=b, angle=theta)
              ellipse = reg.as_artist(facecolor='none', edgecolor='yellow', lw=2)
              patch1.append(ellipse)

          
          tgss_catalog = PatchCollection(
              patch1, edgecolor='yellow', facecolor='None')
          
          ax1.add_collection(tgss_catalog)
        finally:

          nviz = Vizier(columns=['RAJ2000','DEJ2000','MajAxis','MinAxis','PA' ]).query_region(c,
                                                     r, catalog='VIII/65/nvss')
          nra = coordinates.Angle(nviz[0]['RAJ2000'], unit=ut.hour)  # .deg
          ndec = coordinates.Angle(nviz[0]['DEJ2000'], unit=ut.deg)  # .deg
          nrad = coordinates.Angle(nviz[0]['RAJ2000'], unit=ut.hour).deg
          ndecd = coordinates.Angle(nviz[0]['DEJ2000'], unit=ut.deg).deg
          nMaj = nviz[0]["MajAxis"]
          nMin = nviz[0]["MinAxis"]
          if "PA" in nviz[0].columns:
              nPA = nviz[0]["PA"]
          else:
              nPA = 0

          cee2 = coordinates.SkyCoord(ra=nra, dec=ndec)
          center2 = wcs.world_to_pixel(cee2)
          patch2 = []
          for i in range(len(center2[0])):
            x, y = center2[0][i], center2[1][i]
            ce = PixCoord(x, y)
            a = to_pixel(nMaj[i],r)
            b = to_pixel(nMin[i],r)
            if nPA[i]!=0 and nPA[i]!= '--':
              theta = Angle(nPA[i], 'deg') + 90*ut.deg
            else:
              theta = 0*ut.deg + 90*ut.deg

            reg = EllipsePixelRegion(
                center=ce, width=a, height=b, angle=theta)
            ellipse = reg.as_artist(facecolor='none', edgecolor='cyan', lw=2)
            patch2.append(ellipse)
          nvss_catalog = PatchCollection(
              patch2, edgecolor='cyan', facecolor='None')
          ax1.add_collection(nvss_catalog)
        #cs=coordinates.SkyCoord(ra,dec,frame='fk5')
          ax1.scatter(nrad, ndecd, transform=ax1.get_transform('fk5'), s=300,
                      edgecolor='cyan', color='none', zorder=4, marker='.', label='NVSS Catalog')
      except:
        info=" Catalog data missing!"
      finally:
        ax1.legend(framealpha=0.0,labelcolor='white')
        
        # Single Survey plot
        dss2r = sqrt(dss2r, scale_min=np.percentile(
            np.unique(dss2r), 1.), scale_max=np.percentile(np.unique(dss2r), 100.))
        ax2 = fig.add_subplot(1,2,2, projection=wcs)
        ax2.axis( 'off')    
        ax2.imshow(dss2r, origin='lower', cmap='gist_gray') 
        ax2.annotate("#RADatHomeIndia",(10,10),color='white')
        ax2.annotate("By " + str(name),(400-5*len(name),10),color='white')
        ax2.set_autoscale_on(False)
        
        ax2.contour(nvss, lvlcn, colors='blue')
        ax2.contour(tgss, lvlct, colors='magenta')
        ax2.contour(first, lvlcf, colors='yellow')
        
        leg1 = mpatches.Patch(color='blue', label='NVSS')
        leg2 = mpatches.Patch(color='magenta', label='TGSS')
        leg3 = mpatches.Patch(color='yellow', label='FIRST')
        leg4 = mpatches.Patch(color='white', label='DSS2R')
        
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
      info = info or " No images found."
      uri = ""
      status = "warning"


  if archives and int(archives) == 2 and c:
      text=""
      #  NVAS
      try :
          nvas_urls = Nvas.get_image_list(c,radius=2*ut.arcsec)
          text += " " + str(len(nvas_urls)) + \
              " Image(s) found in NVAS: "
          i = 1
          for nvas in nvas_urls :
            if i<=5 :
              text += " <a href='" + str(nvas) + "' target='_blank' rel='noreferrer noopener'>[" + str(i) + "]</a>"
              i+=1

          otext.append({'NVAS': text})
      except :
          otext.append({'NVAS' : 'NVAS has no image'})
#  else :
#    #status=
#    uri=""
#    info="ERROR"
      
  return status, uri, info, otext

#  DEBUG :

#print(query(position="3c33.1"))
#pr.disable()
#s = io.StringIO()
#sortby = 'cumulative'
#ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#ps.print_stats()
#print( s.getvalue())
