
from pickle import TRUE
from socket import timeout
from astroquery.skyview import SkyView
from astroquery.nvas import Nvas

from astropy.io import fits as fts
from astropy import coordinates, units as ut
from astropy.wcs import WCS
from time import perf_counter

import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import numpy as np
import math
import io
import urllib, base64
import requests
import matplotlib
matplotlib.rcParams['font.size']=15




#nbi:hide_in
def linear(inputArray, scale_min=None, scale_max=None):
    """
    Written by Min-Su Shin
    Department of Astrophysical Sciences, Princeton University
    """
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
    """
    Written by Min-Su Shin
    Department of Astrophysical Sciences, Princeton University
    """

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
    ri = sqrt(ri,scale_min=0.5*np.std(ri),scale_max=np.max(ri))
  if gi.max() != 0 and gi.min()!=0 :
    gi = sqrt(gi,scale_min=0.5*np.std(gi),scale_max=np.max(gi))
  if bi.max() != 0 and bi.min()!=0 :
    bi = sqrt(bi,scale_min=0.5*np.std(bi),scale_max=np.max(bi))
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

def pl_RGB(rows,columns,i,wcs,svy,lvlc,img,fig,pos,name) :
    ax = fig.add_subplot(rows, columns, i, projection=wcs)
    ax.axis( 'off')
    ax.imshow(img)
    ax.annotate("#RADatHomeIndia",(10,10),color='white')
    ax.annotate("By " + str(name),(470-5*len(name),10),color='white')
    ax.set_autoscale_on(False)

    plt.contour(svy, lvlc, colors='white')
    if i==1 :
        ax.set_title("ROR with NVSS contour of " + str(pos),y=1,pad=-16,color="white")
        #ax.set_title("")
    if i==2 :
        ax.set_title("ROR with TGSS contour of " + str(pos),y=1,pad=-16,color="white")
    if i==3 :
        ax.set_title("IOU with TGSS contour of " + str(pos),y=1,pad=-16,color="white")
    if i==4 :
        ax.set_title("Optical with TGSS contour of " + str(pos),y=1,pad=-16,color="white")
        


#nbi:hide_in

def query (name="Anonymous",position="",radius=0.12,archives=1,imagesopt=2) :
    
    start=perf_counter()
    pos = str(position)
    errorname = "check coordinates"
    name = str(name)
    if len(name)<=2 :
        name = "Anonymous"
    
    l5="using Name: " + name
    l6=""
    l4=""
    if int(archives) == 2 :
        
        #  NVAS
        try :
            c = coordinates.SkyCoord.from_name(pos, frame='fk5')
            nvas_urls = Nvas.get_image_list(c,radius=2*ut.arcsec)
            l5 = str(len(nvas_urls)) + " image(s) found in NVAS: "
            i = 1
            for nvas in nvas_urls :
                l5 += " <a href='" + str(nvas)+ "'>["+ str(i) + "]</a>"
                i+=1

            l5 +="<br>"
            l4 ="success"
        except :
            l4 ="NVAS "
        
    if int(imagesopt) == 2 :
        try :
          c = coordinates.SkyCoord.from_name(pos, frame='fk5')
          l4 = "fetching  "+ pos
          svy=['TGSS ADR1',  'NVSS', 'VLA FIRST (1.4 GHz)','DSS2 Red']
          r = radius*ut.degree
          levelc = 4
          i=0
          imgin=[]          
          try :
            imglt = SkyView.get_image_list(c, ['TGSS ADR1'], radius=r, pixels=600, scaling='Sqrt')
            imglr = SkyView.get_image_list(c, ['NVSS', 'VLA FIRST (1.4 GHz)'], radius=r, pixels=600, scaling='Sqrt',sampler='Lanczos3')
            imglv = SkyView.get_image_list(c, ['DSS2 Red'], radius=r, pixels=600, scaling='Sqrt')
            imglb = imglt + imglr + imglv
            i=i+1
          except :
            l4 = "survey data misbehaving for: " + svy[i]
          i=0
          l6 = "downloading images...."
          for imgl in imglb :
            try : 
              imd = fts.getdata(imgl, header=True)
              imgin.append(np.array(imd[0]))
              wcs=WCS(imd[1])
              i = i+1
            except :
              l4 = "no data fetched for "+ svy[i]
              imgin.append(np.zeros((600,600)))
              i += 1
              pass
          if wcs!= None :

            tgss = imgin[0]
            nvss = ndimage.gaussian_filter(imgin[1], sigma=4.0, order=0)
            first = imgin[2]
            ds2r = imgin[3]
            errorname = "while overlaying"
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
                
            img1, lvlc1 = overlayc(tgss,ds2r,nvss, tgss, levelc, 0.015)
            
            errorname = "while drawing"
            l6 = "images downloaded: drawing...."
            plt.ioff()
            fig = plt.figure(figsize=(20, 20))
            
            ax1 = fig.add_subplot(1,2,1, projection=wcs) 
            ax1.axis( 'off')    
            ax1.imshow(img1) 
            ax1.annotate("#RADatHomeIndia",(10,10),color='white')
            ax1.annotate("By " + str(name),(470-5*len(name),10),color='white')
            ax1.set_autoscale_on(False)
            ax1.contour(tgss, lvlc1, colors='white')
            
            dss2r = sqrt(ds2r,scale_min=0.5*np.std(ds2r),scale_max=np.max(ds2r))
            ax2 = fig.add_subplot(1,2,2, projection=wcs)
            ax2.axis( 'off')    
            ax2.imshow(dss2r, origin='lower', cmap='gist_gray') 
            ax2.annotate("#RADatHomeIndia",(10,10),color='white')
            ax2.annotate("By " + str(name),(470-5*len(name),10),color='white')
            ax2.set_autoscale_on(False)
            ax2.contour(nvss, levels=lvlcn, colors='blue')
            ax2.contour(tgss, lvlct, colors='magenta')
            ax2.contour(first, lvlcf, colors='yellow')
            
            leg1 = mpatches.Patch(color='blue', label='NVSS')
            leg2 = mpatches.Patch(color='magenta', label='TGSS')
            leg3 = mpatches.Patch(color='yellow', label='FIRST')
            plt.legend(handles=[leg1,leg2,leg3])
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png',bbox_inches='tight', transparent=True, pad_inches=0)
            buf.seek(0)
            string = base64.b64encode(buf.read())
            plt.close()
            uri = 'data:image/png;base64,' + urllib.parse.quote(string)
            htin = ("width:100%; height:auto;", uri)
            html = '<img style="%s" src = "%s" />' % htin 
            time_taken=perf_counter()-start
            l6 = "Image fetched in " + str(np.round (time_taken,3))
            l4 = ""
            l5+=html
          else :
            l4 ="No data available"
        except :
            l4 = "Error Occured: " + errorname + " " + pos
            l5 = ""
    
    if int(imagesopt) == 1 :    
        
        try:
          c = coordinates.SkyCoord.from_name(pos, frame='fk5')
          l4 = "fetching  "+ pos
          svy=['TGSS ADR1',  'NVSS', 'DSS2 Red','DSS2 IR', 'DSS2 Blue', 'WISE 22', 'GALEX Near UV']
          r = radius*ut.degree
          levelc = 5
          i=0
          imglb=[]
          try :
    
            imglt = SkyView.get_image_list(position=c, survey=['TGSS'], coordinates="J2000", projection=None, pixels="600", scaling="Sqrt", sampler=None, resolver=None, deedger=None, lut=None, grid=None, gridlabels=None, radius=r, width=None, height=None, cache=False)
            imglr = SkyView.get_image_list(position=c, survey=['NVSS', 'VLA FIRST (1.4 GHz)'], coordinates="J2000", projection=None, pixels="600", scaling="Sqrt", sampler=None, resolver=None, deedger=None, lut=None, grid=None, gridlabels=None, radius=r, width=None, height=None, cache=False)
            imglv = SkyView.get_image_list(position=c, survey=['DSS2 Red', 'DSS2 IR', 'DSS2 Blue', 'WISE 22', 'GALEX Near UV'], coordinates="J2000", projection=None, pixels="600", scaling="Sqrt", sampler=None, resolver=None, deedger=None, lut=None, grid=None, gridlabels=None, radius=r, width=None, height=None, cache=False)
            imglb.append(np.array([imglt ,imglr ,imglv]))
            #l4 = "survey " + str(imglt)
            
            i=i+1
          except :
            l4 = "survey data misbehaving for: " 
          print(imglb)
          i=0
          imgin = []
          l6 = "downloading images...."  
          errorname = str(np.shape(imglb))
          wcs=[]
          for imgl in imglb :
            #res= urllib.request.urlopen(imgl[0], timeout=300)
              
            try : 
              
              #res = requests.get(str(imgl))
              imd = fts.getdata(imgl, header=True)
              #errorname = "while downloading 1 " + str(np.shape(imd))
              imgin.append(np.array(imd[0]))
              wcs=WCS(imd[1])
              #errorname = "while downloading " + str(wcs)
              i = i+1
            except :
              l4 = "no data fetched for "+ svy[i]
              imgin.append(np.zeros((600,600)))
              i += 1
              pass
          if wcs!= None :
            #errorname=str(imgin[1].shape)
            l6 = "overlaying images...." 
            #errorname = "while ovl 1 " + str(np.shape(imgin))
              
            tgss = imgin[0]
            nvss = imgin[1]
            nvss = ndimage.gaussian_filter(nvss, sigma=4.0, order=0)
            ds2r = imgin[2]
            ds2i = imgin[3]
            ds2b = imgin[4]
            w22 = imgin[5]
            gnuv = imgin[6]
            errorname = "while overlaying"

            img1, lvlc1 = overlayc(tgss,ds2r,nvss, nvss, levelc, 0.0015)
            img2, lvlc2 = overlayc(tgss,ds2r,nvss,tgss, levelc, 0.015)
            img3 = overlayo(w22,ds2r,gnuv)
            img4 = overlayo(ds2i,ds2r,ds2b)

            errorname = "while drawing"
            plt.ioff()
            fig = plt.figure(figsize=(20, 20))
            l6 = "images downloaded: drawing...."
            pl_RGB(2,2,1,wcs,nvss,lvlc1,img1,fig,pos,name)
            pl_RGB(2,2,2,wcs,tgss,lvlc2,img2,fig,pos,name)
            pl_RGB(2,2,3,wcs,tgss,lvlc2,img3,fig,pos,name)
            pl_RGB(2,2,4,wcs,tgss,lvlc2,img4,fig,pos,name)

            buf = io.BytesIO()
            fig.savefig(buf, format='png',bbox_inches='tight', transparent=True, pad_inches=0)
            buf.seek(0)
            string = base64.b64encode(buf.read())
            plt.close()
            uri = 'data:image/png;base64,' + urllib.parse.quote(string)
            htin = ("width:100%; height:auto;", uri)
            html = '<img style="%s" src = "%s" />' % htin 
            time_taken=perf_counter()-start
            l6 = "Image fetched in " + str(np.round (time_taken,3))
            l4 = ""
            l5+=html
            l5 = uri
          else :
            l4 ="No data available"

        except Exception as e:
            l4 = "Error Occured: " + errorname + " for " + pos 
            #raise e
            l5 = ""
    if int(archives) == 1 and int(imagesopt) == 3:
        l4 = "Nothing to Show"
    return l4, l5, l6


#a=query(position="speca")
#print(a)

