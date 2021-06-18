import numpy as np
import math

from astropy import units as ut
from matplotlib import pyplot as plt


# -- below are slight modifications of 
# original author: Min-Su Shin , University of Michigan ----- #-#

def linear(inputArray, scale_min=None, scale_max=None):
    """
    Performs linear scaling of the input numpy array.
	@type inputArray: numpy array
	@param inputArray: image data array
	@type scale_min: float
	@param scale_min: minimum data value
	@type scale_max: float
	@param scale_max: maximum data value
	@rtype: numpy array
	@return: image data array

	"""
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
    """
    Performs sqrt scaling of the input numpy array.
	@type inputArray: numpy array
	@param inputArray: image data array
	@type scale_min: float
	@param scale_min: minimum data value
	@type scale_max: float
	@param scale_max: maximum data value
	@rtype: numpy array
	@return: image data array

	"""		
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
    """
    Performs log10 scaling of the input numpy array.
	@type inputArray: numpy array
	@param inputArray: image data array
	@type scale_min: float
	@param scale_min: minimum data value
	@type scale_max: float
	@param scale_max: maximum data value
	@rtype: numpy array
	@return: image data array
	
	"""
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

# ---------- author : @avialxee ---------#-#

def overlayc (r,g,b,c,lvl,cmin) :
  """
  Returns RGB stacked image and contour levels to be overlayed.
  @input: 
    r/g/b:(2-D array) survey 2-D array data in 
    c :   (2-D array) survey data for contour
    lvl : (int) number of levels to draw
    cmin: (float) minimum value selected for the contour
  @return:
    Img : (np array) dimension: (px,px,3)
    lvlc: (list) dimension: None or of length len(lvl)
  """
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

  # Stacking the Images and set up as 8-bit integers (highest value 2^8 = 256)
  img = (np.dstack((ri,gi,bi))*255.99).astype(np.uint8)
  if c.max() > cmin :
    lvlc = np.arange(cmin, c.max(),((c.max() - cmin)/lvl))
  else :
    lvlc = None
  return img, lvlc

def normals(o) :
  """
  normalizing before scaling, 
  @input:   (2D array) input survey
  @return:  (2D array) dimension same as input survey

  """
  X_scaled =(o - np.median(o))
  if o.max()!=0 :
    X = X_scaled/o.max()
    return X
  else :
    return X_scaled


def overlayo(ri, gi, bi, kind = 'IOU'):
  """
  Returns RGB stacked image.
  @Input: 
    ri/gi/bi: (2-D array) survey 2-D array data in 
    kind  :   (string) either IOU or Optical
  @return:
    Img : (np array) dimension: (px,px,3)
  """
  if kind == 'IOU':
    ri = sqrt(ri, scale_min=np.percentile(np.unique(ri),1.), scale_max=np.percentile(np.unique(ri),100.))
    gi = sqrt(gi, scale_min=np.percentile(np.unique(gi),1.), scale_max=np.percentile(np.unique(gi),100.))
    #gi = log(gi, scale_min=np.percentile(np.unique(gi),0.), scale_max=np.percentile(np.unique(gi),100.),factor=2.85)
    bi = log(bi, scale_min=np.percentile(np.unique(bi), 5.),
             scale_max=np.percentile(np.unique(bi), 100.), factor=3.15)
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
    """
    @input:
        rows    : (int) Total number of rows.
        columns : (int) Total number of columns.
        i       : (int) current number of the cell.
        wcs     : (astropy wcs) world coordinate system fetched from header of fits
        svy     : (np array) 2-D array
        lvlc    : (list) list of float
        img     : (np array) dimension = (px,px,3)
        fig     : (maplotlib.pyplot.figure)
        name    : (string) input name to be show on figure
    @return:
        None
    """
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
    """
    convert arcsec into pixel.
    @input:
        unit_inarcsec: input magnitude (unitless) data in arcsec
        r   :   length of square image in deg
        px  :   total pixels in one length
    @return:
        input data converted to be used onto pixel length rounded upto 2 decimal places.
    """
    nvss_px_scale = px/(r)
    return np.round(((unit_inarcsec/3600) * ut.deg * nvss_px_scale), 2).value

