"""
Generic open image module for both Nanonis and Matrix files
Output should be in Spiepy format # https://pypi.org/project/SPIEPy/
Makes use of Nanonispy # https://pypi.org/project/nanonispy/
and Access2theMatrix  https://pypi.org/project/access2theMatrix/
Author: Koen
TODO: Check Nanonis import fw<>bw and up<>down
"""

# Do imports
import spiepy
import nanonispy as nap
import access2thematrix as a2m
from os import path



class OpenImage():
    """
    Class where the actual open image routines are kept
    """

    def __init__(self, trace=0, channel = "Z"):
        """ Init function takes scan direction and channel
        0 = forward, 1 = backward
        channel depends on Matrix vs Nanonis and what the user wants.
        It returns immediately the image as Spiepy object
        """


        # Store direction in self.trace  and channel in self.channel
        self.trace = trace
        self.channel = channel
        return None


    def open_image(self, filename):

        # First check which type of image it is
        # We can handle only Matrix and Nanonis files
        if not(path.exists(filename)):
            raise ValueError("File does not exist!")
        elif path.splitext(filename)[1][-5:] == "_mtrx":
            self.filetype = "Matrix"
        elif path.splitext(filename)[1][-3:] == "sxm":
            self.filetype = "Nanonis"
        else:
            raise TypeError("Filetype is not recognized")

        # Store filename in self.filename
        self.filename = filename

        # return the image
        return self.load_image()



    def load_image(self):
        """ Uses filetype and filename set in self.filetype and self.filename
        Then calls the apropriate routine to load the data and pack in a
        Spiepy object, which it returns.
        """
        # Load the data
        if self.filetype == "Matrix":
            image = self.read_matrix()
        elif self.filetype == "Nanonis":
            image = self.read_nanonis()
        # Convert to Spiepy
        image = self.convert_to_spiepy(image)
        # Add image name to make it unique
        image.name = self.filename
        image.trace = self.trace
        image.channel = self.channel
        # return image
        return image


    def read_matrix(self):
        """ Opens a Matrix file using access2theMatrix.
        Depends on self.filename, and self.trace.
        Channel is contained in filename for Matrix.
        Returns access2matrix object
        """
        # initialize a2m class
        mtrx_data = a2m.MtrxData()
        # Load correct trace using A2M functionality
        traces, message = mtrx_data.open(self.filename)
        im, message = mtrx_data.select_image(traces[self.trace])

        # Sometimes attributes are not handled well
        # specially in new a2m versions
        try:
            im.XY_width
        except:
            im.XY_width = im.width
        if im.XY_width < 0.01:
            im.XY_width *= 1E9

        try:
            im.XY_height
        except:
            im.XY_height = im.height
        if im.XY_height < 0.01:
            im.XY_height *= 1E9

        try:
            im.points
        except:
            im.points = im.data.shape[1]

        try:
            im.lines
        except:
            im.lines = im.data.shape[0]

        # Return A2M image
        return im


    def read_nanonis(self):
        """ Opens a Nanonis image file using nanonispy.
        Depends on self.filename, self.trace, and self.channel
        Returns custom created object unfortunately
        """
        # Load file
        image = nap.read.Scan(self.filename)

        # TODO: Check this
        if self.trace == 0:
            if image.header["scan_dir"] == "down":
                scan = np.flipud(image.signals[self.channel]["forward"])
            else:
                scan = (image.signals[self.channel]["forward"])
        else:
            if image.header["scan_dir"] == "down":
                scan = np.flip(image.signals[self.channel]["backward"])
            else:
                scan = np.fliplr(image.signals[self.channel]["backward"])

        # I have not found a better way to return data from nanonispy in a
        # reasonable similar format as access2theMatrix.
        # And I need those 2 to play nice.
        im = spiepy.Im()
        im.data = scan
        im.header = image.header
        # Return the constructed im object
        return im

    def convert_to_spiepy(self, image):
        """ Converts the objects that the load routines have created to SPIEPy
        instances with the same attributes.
        Not all attributes are implemented from the beginning under YAGNI rules.
        """
        if self.filetype == "Matrix":
            image.__class__ = spiepy.Im
        else:
            image.XY_height = image.header["scan_range"][1]
            image.XY_lines = image.header["scan_pixels"][1]
            image.XY_points = image.header["scan_pixels"][0]
            image.XY_width = image.header["scan_range"][0]
            image.XY_x_offset = image.header["scan_offset"][0]
            image.XY_y_offset = image.header["scan_offset"][1]
            image.angle = float(image.header["scan_angle"])
            image.voltage = image.header["bias"]
            image.current = float(image.header["Setpoint"][0].split(" ")[0])

        return image


if __name__ == '__main__':
    print("Test")
