# Homework #3 of MENG25610 Winter 2021
  
Assignment:
- **Undergrads** and **Graduate students**: solve problem #1

Content:
- Problem #1 : open `Problem001.py` with a text editor

**Notes:**
 
The file contains code to compute the radial distribution function (RDF) for snapshots extracted from a molecular dynamics simulation of water, reported in directory `pbe400_128`. 
The code is not parallel and is split into four sections:
   - (1) INTRO
   - (2) GET LIST OF FILE NAMES
   - (3) COMPUTE RDF
   - (4) PLOT 

Use MPI to parallelize the computation of RDF in section 3, implementing the following strategy and running it on four cores: 
   - Let each MPI process work on a subset of the 128 snapshots, and compute partial average, minimum and maximum RDFs. Note that a snapshot may only be processed by one MPI process.
   - Use Reduce operations to collect in process 0 the total average, minimum, and maximum RDF for OO, OH, and HH. 
   - Let only process 0 plot the results and save them to file.

Please upload the parallel code and the resulting plot obtained by running the code on four cores.  
