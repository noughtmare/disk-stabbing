# disk-stabbing

To build this project you can run:

```
$ conda env create -f environment.yml
```

On windows this might produce an error about not being able to find Microsoft
Visual C++ 14. This can be installed seperately from the [Microsoft website](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
This will first install an installer which can then be used to install the build
tools. You need to install the C++ build tools with the optional MSVC and the
Windows 10 SDK. For me, creating the conda environment took about 5GB of RAM
which was during the compilation of CGAL.

This creates a `disk-stabbing` conda environment which can be activated to run
the gui (or to use the library in another way):

```
$ conda activate disk-stabbing
$ python gui.py
```

The GUI opens an empty window in which you can click to add disks that need to
be stabbed with a line. If there is no line that stabs all the disks then all
the disks are removed and you can click to add new disks again. During this
process the limiting lines and upper and lower hulls are shown as described in
the paper: "Approximating Polygons and Subdivisions with Minimum-Link Paths", by
Guibas, Hershberger, Mitchell and Snoeyink.
