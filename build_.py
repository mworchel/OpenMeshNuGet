import os

# Generate the includes for the autopkg
includes = []
index = 1
for root, dirs, files in os.walk("include"):
    if files :
        path, sub_dir = os.path.split(root)
        internal_path = sub_dir
        while path != "include":
            path, sub_dir = os.path.split(path)
            internal_path = sub_dir + "/" + internal_path
        includes.append("nested" + str(index) + "Include: { #destination = ${d_include}"+ internal_path +"; \"" + root + "\*\"};")
    index += 1

# Collect the build information from the filesystem if they haven't been built with this run
builds = []
for name, dirs, files in os.walk("build", topdown=False):
    if "bin" in dirs and "lib" in dirs:
        # Find the pivots by path name
        path, pivot = os.path.split(name)
        pivots = [pivot]
        while path != "build":
            path, pivot = os.path.split(path)
            pivots.append(pivot)

        lib_files = []
        for file in os.listdir(name + "/lib"):
            lib_files.append(name + "/lib/" + file) 


        bin_files = []
        for file in os.listdir(name + "/bin"):
            bin_files.append(name + "/bin/" + file)         
        
        builds.append({
            "pivots" : pivots,
            "lib_files" : lib_files,
            "bin_files" : bin_files,
        })
print(builds)

# Create the autopkg file
file = open("openmesh.autopkg", "w")
file.write('nuget {\n')
file.write('\tnuspec {\n')
file.write('\t\tid = openmesh;\n')
file.write('\t\tversion: 6.2;\n')
file.write('\t\ttitle: Open Mesh;\n)
file.write('\t\tauthors: {RWTH-Aachen University};\n')
file.write('\t\towners: {Markus Worchel};\n')
file.write('\t\tlicenseUrl: "https://www.openmesh.org/license/";\n')
file.write('\t\tprojectUrl: "https://www.openmesh.org/";\n')
file.write('\t\ticonUrl: "https://www.openmesh.org/static//OpenMesh_text_512.png";\n')
file.write('\t\trequireLicenseAcceptance: true;\n')
file.write('\t\tsummary: A generic and efficient polygon mesh data structure;\n')
file.write('\t\tdescription: @"OpenMesh is a generic and efficient data structure for representing and manipulating polygonal meshes.";\n')
file.write('\t\treleaseNotes: @"OpenMesh 6.2 is still fully backward compatible with the 2.x to 5.x branches. We marked some functions which should not be used anymore as deprecated and added hints which should be used instead. This release is a minor update to fix compilation errors with Visual Studio 2015 Update 3. We resolved some constructions causing internal compiler and compilation issues. ";\n')
file.write('\t\tcopyright: Copyright 2016;\n")
file.write('\t\ttags: {OpenMesh, native, Mesh, Half-Edge};\n")
file.write('\t}\n") #nuspec
file.write('\tfiles {\n") 
file.write('\t}\n") #files
file.write('}\n") #nuget