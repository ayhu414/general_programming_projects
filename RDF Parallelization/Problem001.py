import numpy as np
import os 
import matplotlib.pyplot as plt
from mpi4py import MPI

############
# 1. INTRO #
############

class XYZfile:
    """This class loads an atomic structure from a XYZ file."""
    
    def __init__(self, filename):
        """Reads a XYZ file
        
        filename (str) : The name of the file
        """
        
        self.filename = filename
        with open(self.filename,'r') as file : 
            # number of atoms 
            self.np = int(file.readline()) 
            # comment 
            self.comment = file.readline() 
            # data 
            self.data = np.zeros(shape=(self.np,),dtype=[("element","U9"),("x","f8"),("y","f8"),("z","f8")])
            for i in range(self.np):
                parts = file.readline().strip().split(' ')
                self.data[i] = (parts[0],parts[1],parts[2],parts[3])

class CubicCell:
    
    def __init__(self, comment):
        """Reads a cubic cell from a comment contained in the xyz file
        
        comment (str) : The comment
        """
        self.L = np.zeros(shape=(3,),dtype="f8")
        parts = comment.strip().split(' ')
        self.L[0] = parts[1]  # period along x
        self.L[1] = parts[5]  # period along y 
        self.L[2] = parts[9]  # period along z
    
    def volume(self):
        """Computes the volume of the cell"""
        return self.L[0]*self.L[1]*self.L[2]  # volume of a cube
    
    def wrap(self,v):
        """Wraps the vector v into the unit cell
        
        v (3-dim ndarray) : vector
        """
        return np.remainder(v, self.L)  # wraps a vector into the cell 
    
    def pbc_distance(self,v1,v2):
        """Computes the distance between two vectors with PBC
        
        v1 (3-dim ndarray) : vector
        v2 (3-dim ndarray) : vector
        """
        d = np.array(v1,dtype="f8") - np.array(v2,dtype="f8") # general difference 
        d = np.remainder(d + self.L/2.0, self.L) - self.L/2.0  # minimum image difference 
        return np.linalg.norm(d) # norm of the minimum image difference

def sphere(r):
    return(4/3*np.pi*r**3)

def volume2(r,L):
    x = r/L
    return (-np.pi/12*(3-36*x**2+32*x**3))*L**3
           
def volume3(r,L):
    x = r/L
    return (-np.pi/4. + 3*np.pi*x**2 + np.sqrt(4*x**2-2) + (1-12*x**2)*np.arctan(np.sqrt(4*x**2-2)) + 2/3*x**2*8*x*np.arctan((2*x*(4*x**2-3))/(np.sqrt(4*x**2-2)*(4*x**2+1))) )*L**3 

def gauss1D(x,mu=0,sigma=1):
    return np.exp(-0.5*(x-mu)**2/sigma/sigma)/np.sqrt(2.*np.pi)/sigma

def rdf(f,Rmax,NRmax,element_center,element_distant) : 

    # get the cell 
    cell = CubicCell(f.comment)
    
    is_center = np.char.startswith(f.data[:]["element"],element_center)
    is_distant = np.char.startswith(f.data[:]["element"],element_distant)
    
    # count the number of center particles
    Np_center = np.sum(is_center)
    
    # count the number of distant particles
    Np_distant = np.sum(is_distant)
            
    bins = np.linspace(0,Rmax,NRmax+1,endpoint=True)
    radii = np.zeros(shape=(NRmax,),dtype="f8")
    hist = np.zeros(shape=(NRmax,),dtype="f8")
    volumes = np.zeros(shape=(NRmax,),dtype="f8")
    
    for i in range(NRmax):
        radii[i] = (bins[i]+bins[i+1])/2. # middle point between two bins
        if radii[i]<=cell.L[0]/2 : 
            volumes[i]=sphere(bins[i+1])-sphere(bins[i])
        elif radii[i]<=cell.L[0]*np.sqrt(2)/2  :
            volumes[i]=volume2(bins[i+1],cell.L[0])-volume2(bins[i],cell.L[0])
        elif radii[i]<=cell.L[0]*np.sqrt(3)/2 :
            volumes[i]=(volume3(bins[i+1],cell.L[0])-volume3(bins[i],cell.L[0]))
        else :
            volumes[i]=0
            
    # accumulate gaussians in hist 
    for i in range(f.np):
        if is_center[i]: #filter
            Ri = [f.data[i]["x"], f.data[i]["y"], f.data[i]["z"] ]
            for j in range(f.np):
                if is_distant[j] and (i!=j): #filter
                    Rj = [f.data[j]["x"], f.data[j]["y"], f.data[j]["z"] ]
                    d = cell.pbc_distance(Ri,Rj)
                    hist += gauss1D(radii,d,0.2)*Rmax/NRmax
            
    rho_avg = Np_distant / cell.volume()
    return np.divide(hist, volumes, out=np.zeros_like(hist), where=volumes!=0)/rho_avg/Np_center, radii

#############################
# 2. GET LIST OF FILE NAMES #
#############################

fnames = []

# We loop over all files that end with ".xyz"
for dirpath, dirnames, filenames in os.walk("pbe400_128", topdown=False):
    xyz_files = [f for f in filenames if f.endswith('.xyz')]
    for name in xyz_files:
        fnames.append(os.path.join(dirpath, name))

##################
# 3. COMPUTE RDF #
##################

Rmax = 9
NRmax = 100
no_files = len(fnames)

g_OO_avg = np.zeros(shape=(NRmax,),dtype="f8")
g_OH_avg = np.zeros(shape=(NRmax,),dtype="f8")
g_HH_avg = np.zeros(shape=(NRmax,),dtype="f8")
g_OO_max = np.zeros(shape=(NRmax,),dtype="f8")
g_OH_max = np.zeros(shape=(NRmax,),dtype="f8")
g_HH_max = np.zeros(shape=(NRmax,),dtype="f8")
g_OO_min = np.ones(shape=(NRmax,),dtype="f8")*100
g_OH_min = np.ones(shape=(NRmax,),dtype="f8")*100
g_HH_min = np.ones(shape=(NRmax,),dtype="f8")*100

#MPI IMPLEMENTATION

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

my_tasks = []

# distributes all files to n processors
for i, fname in enumerate(fnames):
    if rank == i % size:
        my_tasks.append(fname)

# LOOP that needs to be parallelized 
for i, fname in enumerate(my_tasks):
    print(f"processor {rank}, {i}/{len(my_tasks)-1}, Processing file: {fname}...")
    f = XYZfile(fname)
    g_OO, r_OO = rdf(f,Rmax,NRmax,"O","O")
    g_OH, r_OH = rdf(f,Rmax,NRmax,"O","H")
    g_HH, r_HH = rdf(f,Rmax,NRmax,"H","H")
    g_OO_avg += g_OO / no_files
    g_OH_avg += g_OH / no_files
    g_HH_avg += g_HH / no_files
    g_OO_max = np.maximum(g_OO,g_OO_max)
    g_OH_max = np.maximum(g_OH,g_OH_max)
    g_HH_max = np.maximum(g_HH,g_HH_max)
    g_OO_min = np.minimum(g_OO,g_OO_min)
    g_OH_min = np.minimum(g_OH,g_OH_min)
    g_HH_min = np.minimum(g_HH,g_HH_min)


#gathering for avg data at processor 0
sendbuff_OO_avg = np.array([g_OO_avg],dtype="f8")
sendbuff_OH_avg = np.array([g_OH_avg],dtype="f8")
sendbuff_HH_avg = np.array([g_HH_avg],dtype="f8")
recvbuff_OO_avg = np.zeros_like(sendbuff_OO_avg)
recvbuff_OH_avg = np.zeros_like(sendbuff_OH_avg)
recvbuff_HH_avg = np.zeros_like(sendbuff_HH_avg)
comm.Reduce(sendbuff_OO_avg,recvbuff_OO_avg,op=MPI.SUM,root=0)
comm.Reduce(sendbuff_OH_avg,recvbuff_OH_avg,op=MPI.SUM,root=0)
comm.Reduce(sendbuff_HH_avg,recvbuff_HH_avg,op=MPI.SUM,root=0)
g_OO_avg = recvbuff_OO_avg[0]
g_OH_avg = recvbuff_OH_avg[0]
g_HH_avg = recvbuff_HH_avg[0]


#gathering for max data at processor 0
sendbuff_OO_max = np.array([g_OO_max],dtype="f8")
sendbuff_OH_max = np.array([g_OH_max],dtype="f8")
sendbuff_HH_max = np.array([g_HH_max],dtype="f8")
recvbuff_OO_max = np.zeros_like(sendbuff_OO_max)
recvbuff_OH_max = np.zeros_like(sendbuff_OH_max)
recvbuff_HH_max = np.zeros_like(sendbuff_HH_max)
comm.Reduce(sendbuff_OO_max,recvbuff_OO_max,op=MPI.MAX,root=0)
comm.Reduce(sendbuff_OH_max,recvbuff_OH_max,op=MPI.MAX,root=0)
comm.Reduce(sendbuff_HH_max,recvbuff_HH_max,op=MPI.MAX,root=0)
g_OO_max = recvbuff_OO_max[0]
g_OH_max = recvbuff_OH_max[0]
g_HH_max = recvbuff_HH_max[0]

#gathering for min data at processor 0
sendbuff_OO_min = np.array([g_OO_min],dtype="f8")
sendbuff_OH_min = np.array([g_OH_min],dtype="f8")
sendbuff_HH_min = np.array([g_HH_min],dtype="f8")
recvbuff_OO_min = np.zeros_like(sendbuff_OO_min)
recvbuff_OH_min = np.zeros_like(sendbuff_OH_min)
recvbuff_HH_min = np.zeros_like(sendbuff_HH_min)
comm.Reduce(sendbuff_OO_min,recvbuff_OO_min,op=MPI.MIN,root=0)
comm.Reduce(sendbuff_OH_min,recvbuff_OH_min,op=MPI.MIN,root=0)
comm.Reduce(sendbuff_HH_min,recvbuff_HH_min,op=MPI.MIN,root=0)
g_OO_min = recvbuff_OO_min[0]
g_OH_min = recvbuff_OH_min[0]
g_HH_min = recvbuff_HH_min[0]

###########
# 4. PLOT #
###########

if rank == 0:
    file_name = "rdf.png"
    plt.plot(r_OO,g_OO_avg,marker="o",color="r",label="g_OO")
    plt.plot(r_OO,g_OO_min,color="r")
    plt.plot(r_OO,g_OO_max,color="r")
    plt.plot(r_OH,g_OH_avg,marker="o",color="b",label="g_OH")
    plt.plot(r_OH,g_OH_min,color="b")
    plt.plot(r_OH,g_OH_max,color="b")
    plt.plot(r_HH,g_HH_avg,marker="o",color="g",label="g_HH")
    plt.plot(r_HH,g_HH_min,color="g")
    plt.plot(r_HH,g_HH_max,color="g")
    plt.xlabel(r"r ($\AA$)")
    plt.xlim(0,Rmax)
    plt.ylim(0,4)
    plt.ylabel(r"g(r)")
    plt.legend()
    plt.savefig(file_name)
    print(f"File saved: {file_name}")