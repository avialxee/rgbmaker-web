# sky-rad
Sky tool for #RADatHomeIndia will have RGB Maker tool and FIR submission forms


# How to use the RAD-RGB Maker Tool:

The process to use the RAD RGB Maker tool is very simple. All you need are - your name, the name of the object you want to image or its coordinates, the radius of the image search scope, and what sort of images you would like to make.

Let us go through the fields:
+ Name: Your name, so we know who made the image. Credits are important.
+ Object: The catalogue name (Ex: M87, NGC1243, etc.) or the coordinates of the object in the J2000 system (ex: 01 01 01, +01, 01 01).
+ Size (Degrees): The size of the image in degrees. For reference, in the night sky, the moon is 0.25 degrees across.
+ Images: This dropdown gives you a choice of the composite images you want to create. 
                    IOU ROR Optical: This option returns four images. 
                              1. There are two ROR (Radio (TGSS) - Optical (DSS2Red) - Radio (NVSS)) images. One with TGSS Contours and another with NVSS Contours. 
                              2. The third image is an IOU (Infrared (Wise 22) - Optical (DSS2Red) - Galex Near UV) with TGSS Contours. 
                              3. The final image is an optical image with (DSS2IR - DSS2Red - DSS2Blue) with TGGSS Contours. 
                    Composite Contours on DSS2R: This option returns two images. 
                              1. The first is an ROR Image with TGSS contours. This image will however indicate TGSS and NVSS sources if they are seen by the Vizer                                  catalogue. 
                              2. The second image is a composite image with DSS2Red background and contours of various radio surveys like TGSS, NVSS and VLA First                                    (if available).
  Please check the RAD-RGB acknowledgement at the bottom of the page for further details.
+ Archives: This dropdown currently offers access to the NVAS image archive. Selecting this option will return the object's NVAS image stamp, if it exists.
+ Query: You are now finally ready to make your RAD-RGB image! Just press the button, give it a few seconds, and you will have taken your first step in the RGB       image analysis. The next and most important step is the analysis. Good luck with that! 

