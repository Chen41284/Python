"""Make a shadow of 2 meshes on the wall."""
from vtkplotter import *



def shadow(filepath):
    a = load(filepath)
    # a.normalize().rotateZ(-90).addShadow(x=-4, alpha=0.5)
    # a.normalize().addShadow(z=-2, alpha=1)
    # a.normalize().addShadow(x=-2, alpha=1)
    a.normalize().addShadow(y=-2, alpha=1)
    # s = Sphere(pos=[-0.4, 1.4, 0.3], r=0.3).addShadow(x=-4)
    # show(a, s, Text(__doc__), axes=1, viewup="z", bg="w")
    show(a, Text(__doc__), axes=1, viewup="z", bg="w")

if __name__=='__main__':
    datadir = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Recon\\"
    filename = "Armadillo4_meshlab_SSDRec.ply"
    shadow(datadir + filename)
