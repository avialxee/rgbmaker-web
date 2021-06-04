
## What are IOU ROR and RGB?
_RAD-RGB images are false-colored images of astronomical objects._

The astronomical study involves a multiwavelength analysis of the object from the radio part of the spectrum to x-rays. Astronomers access these data from various archival data services which are [sky survey](https://en.wikipedia.org/wiki/Astronomical_survey) data on a particular wavelength of a telescope. Each RGB image is a combination of these survey data in Red, Green, and Blue color channels, with their respective intensities at each pixel, resulting in a false-colored image. Usually, the surveys are selected so that the wavelength of each channel is in decreasing order i.e survey in the red channel has a wavelength higher than green and green has a wavelength greater than blue.

_The two widely used RAD-RGB images in our analysis are:_
+ #### IOU
  These are Infrared - Optical - Ultraviolet, RAD-RGB images _i.e_ the red channel has IR data (WISE 22), the green channel has data at the optical visible wavelength (DSS2 R) and the blue channel has UV data (GalexNUV) at each pixel.
+ #### ROR
  These are Radio-Optical-Radio RAD-RGB images _i.e_ the red channel has radio data of higher wavelength (TGSS ADR1), the green channel has optical data (DSS2 R) and the blue channel has radio data of lower wavelength (VLA NVSS) at each pixel.

## How to use the RAD-RGB Maker Tool:
RAD-RGB Maker Tool is a very simple to use tool. All you need is the name of the astronomical object of interest or its coordinates, the radius of the image search scope, and what sort of images you would like to make.

_Here is a brief description of each label provided in the form:_

+ #### Name (Optional)
  Your name will be displayed on the image enabling mentors, professors, fellow students to be able to recognize your work. Credit is important!

+ #### Position (Required)
  The object name or the coordinates of the object in the FK5 (J2000) system. Ex: "14 09 48.86 -03 02 32.6", M87, NGC1243, without quotes.

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
    + The first is a [ROR](#what-is-iou-ror-and-rgb) Image with TGSS contours. The various symbol seen on the image is the [catalog](https://en.wikipedia.org/wiki/Astronomical_catalog) data of the respective survey.
    + The second image is a composite image with DSS2Red background and contours of various radio surveys like TGSS, NVSS, and VLA First (if available).

  
+ #### Archives 
  This dropdown currently offers access to the NVAS image archive. Selecting this option will return the top 5 results from NVAS (if exists). These can be downloaded as .imfits files (open with DS9) by using save as an option when right-clicked.

+ #### Query 
  You are now finally ready to make your RAD-RGB image! Just press the button, give it a few seconds, and you will have taken your first step in the RGB image analysis. The next and most important step in the analysis. All the best for that! 

> _Please check the RAD-RGB acknowledgment at the bottom of the page for further details_ : [RAD-RGB Maker Tool Acknowledgement](https://docs.google.com/document/d/1U5nkmCKOlgnDk4pO7d7HKj_OidH9IvXNfW9AojBc-s0/edit)