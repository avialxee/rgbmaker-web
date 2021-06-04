# sky-rad
sky-rad is a python based flask app for #RADatHomeIndia with various aimed capabilities (in progress) which includes the astronomical archival data fetching service for different wavelength (aka RGBMaker Tool).

## What is IOU ROR and RGB?
_RAD-RGB images are false coloured images of the astronomical objects._

Astronomical study involves a multiwavelength analysis of the object from radio part of the spectrum to x-rays. Astronomers access these data from telescope through various archival data services which are [sky survey](https://en.wikipedia.org/wiki/Astronomical_survey) data on a particular wavelength. Each RGB image is a combination of these survey data in Red, Green and Blue colour channels, with their respective intensities at each pixel, resulting in a false coloured image. Usually the wavelength in each channel is in decreasing order _i.e_ survey in red channel has wavelength higher than green and green has wavelength greater than blue.

_The two widely used RAD-RGB images in our analysis are:_
+ #### IOU
  These are Infra Red - Optical - Ultra Violet, RAD-RGB images _i.e_ the red channel has infrared data (WISE 22) , green channel has optical data (DSS2 R) and blue channel has UV data (GalexNUV) at each pixel.
+ #### ROR
  These are Radio-Optical-Radio RAD-RGB images _i.e_ the red channel has radio data of higher wavelength (TGSS ADR1) , green channel has optical data (DSS2 R) and blue channel has radio data of lower wavelength (VLA NVSS) at each pixel.

## How to use the RAD-RGB Maker Tool:
RAD-RGB Maker Tool is very simple to use tool. All you need is the name of the astronomical object of interest or its coordinates, the radius of the image search scope, and what sort of images you would like to make.

_Here is a brief description of each labels provided in the form:_

+ #### Name (Optional)
  Your name, this will be displayed on the image enabling mentors, professors, fellow students to be able to recognize your work. Credit is important!

+ #### Position (Required)
  The catalogue name (Ex: M87, NGC1243, etc.) or the coordinates of the object in the FK5 (J2000) system (ex: 01 01 01, +01, 01 01).

+ #### Radius (Required)
  The size of the image in degrees, this size will be used for the [field of view](https://en.wikipedia.org/wiki/Field_of_view) in the resultant image. For reference, in the night sky, the moon is about 0.52 degrees across.

+ #### Images
  This dropdown gives you a choice of the composite images you want to create. 

  #### IOU ROR Optical
  
    _This option returns four images._
    + There are two [ROR](#what-is-iou-ror-and-rgb) _(Radio (TGSS ADR1) - Optical (DSS2Red) - Radio (NVSS))_ images. One with TGSS Contours and another with NVSS Contours. 
    + The third image is an [IOU](#what-is-iou-ror-and-rgb) _(Infrared (WISE 22) - Optical (DSS2 Red) - Ultraviolet (Galex Near UV))_ with TGSS Contours. 
    + The final RGB image is an optical image with _(DSS2IR - DSS2Red - DSS2Blue)_ with TGGSS Contours. 
  
  #### Composite Contours on DSS2R
  
    _This option returns two images._
    + The first is an ROR Image with TGSS contours. This image will however indicate TGSS and NVSS sources if they are seen by the Vizer catalogue. 
    + The second image is a composite image with DSS2Red background and contours of various radio surveys like TGSS, NVSS and VLA First (if available).

  
+ #### Archives 
  This dropdown currently offers access to the NVAS image archive. Selecting this option will return the top 5 results from NVAS (if exists). These can be downloaded as .imfits files (open with DS9) by using save as option when right clicked.

+ #### Query 
  You are now finally ready to make your RAD-RGB image! Just press the button, give it a few seconds, and you will have taken your first step in the RGB image analysis. The next and most important step is the analysis. All the best for that! 

> _Please check the RAD-RGB acknowledgement at the bottom of the page for further details_ : [RAD-RGB Maker Tool Acknowledgement](https://docs.google.com/document/d/1U5nkmCKOlgnDk4pO7d7HKj_OidH9IvXNfW9AojBc-s0/edit)