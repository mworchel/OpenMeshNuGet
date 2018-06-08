import glob
import os
import shutil

def clear_directory(dir_path):
    if os.path.exists(dir_path):
        for file in os.listdir(dir_path):
            if os.path.isfile(dir_path + "/" + file):
                os.remove(dir_path + "/" + file)
            else:
                shutil.rmtree(dir_path + "/" + file)

# Create the build directory and set it as current working dir
build_dir = "./build"
os.makedirs("./build", exist_ok=True)
os.chdir(build_dir)

# Assemble list of used toolsets
toolsets = [
    ("Visual Studio 2013", "v120", {"x86" : "Visual Studio 12 2013", "x64" : "Visual Studio 12 2013 Win64"}),
    #("Visual Studio 2015", "v140", {"x86" : "Visual Studio 14 2015", "x64" : "Visual Studio 14 2015 Win64"}),
    #("Visual Studio 2017", "v150", {"x86" : "Visual Studio 15 2017", "x64" : "Visual Studio 15 2017 Win64"}),
    ]

platforms = [
    "x86", 
    #"x64"
    ]
configurations = [
    "debug", 
    "release"
    ]
linkages = [
    {
        "name" : "shared", 
        "flags" : "-DOPENMESH_BUILD_SHARED:BOOL=TRUE",
        "lib_files" : "lib/*.lib",
        "bin_files" : "*.dll",
    }, 
    # {
    #     "name" : "static", 
    #     "flags" : "-DOPENMESH_BUILD_SHARED:BOOL=FALSE",
    #     "lib_files" : "lib/*.lib",
    # }
    ]

builds = {}

install_dir = "./install"
autopkg_dir = "D:/openmesh-6.3"
os.makedirs(autopkg_dir, exist_ok=True)
for name, version, generators in toolsets:
    print("Building for " + name)

    for platform in platforms:
        # Clear the build directory
        clear_directory(".")
        for config in configurations:
            print("Building with generator " + generators[platform])

            for linkage in linkages:
                # Clear the install directory and make the build
                clear_directory(install_dir + "/")
                os.system('cmake ./.. ' + linkage["flags"] + ' -DCMAKE_INSTALL_PREFIX:PATH=' + install_dir + ' -G "' + generators[platform] + '"')
                os.system('cmake --build . --target INSTALL --config ' + config)

                # Create the meta info of this build
                pivots    = [version, platform, config, linkage]
                lib_files = []
                bin_files = []

                # Copy the created files into the right directory
                autopkg_relative_lib_dir = "build/" + version + "/" + platform + "/" + config + "/" + linkage["name"] + "/lib"
                autopkg_relative_bin_dir = "build/" + version + "/" + platform + "/" + config + "/" + linkage["name"] + "/bin"
                output_lib_dir = autopkg_dir + "/" + autopkg_relative_lib_dir
                output_bin_dir = autopkg_dir + "/" + autopkg_relative_bin_dir
                os.makedirs(output_lib_dir, exist_ok=True)
                os.makedirs(output_bin_dir, exist_ok=True)

                # Copy lib files
                if "lib_files" in linkage:
                    for lib_file in glob.glob(install_dir + "/" + linkage["lib_files"]):
                        filename = os.path.basename(lib_file)
                        lib_files.append(autopkg_relative_lib_dir + "/" + filename)
                        shutil.copy(lib_file, output_lib_dir + "/" + filename)

                # Copy bin files
                if "bin_files" in linkage:
                    for bin_file in glob.glob(install_dir + "/" + linkage["bin_files"]):
                        filename = os.path.basename(bin_file)                    
                        bin_files.append(autopkg_relative_bin_dir + "/" + filename)                    
                        shutil.copy(bin_file, output_bin_dir + "/" + filename)

                if not name in builds:
                    builds[name] = []

                builds[name].append ({
                    "pivots" : pivots,
                    "lib_files" : lib_files,
                    "bin_files" : bin_files
                })

                # Copy the include dir into the base directory
                if os.path.exists(install_dir + "/include") and not os.path.exists(autopkg_dir + "/include"):
                    shutil.copytree(install_dir + "/include", autopkg_dir + "/include")

                os.system("pause")

# # Change to the autopkg dir and go from there
# os.chdir(autopkg_dir)

# # Generate the includes for the autopkg
# includes = []
# index = 1
# for root, dirs, files in os.walk("include"):
# 	sub_root = root[8:]
# 	if files :
#         includes.append("nested" + str(index) + "Include: { #destination = ${d_include}"+ sub_root +"; \"" + root+ "\*\"};")
# index += 1

# # Collect the build information from the filesystem if they haven't been built with this run
# if not builds:
#     os.list

# # Create the autopkg file
# file = open("openmesh.autopkg", "w")
# file.write("nuget {\n")
# file.write("\tnuspec {\n")
# file.write("\t}\n") #nuspec
# file.write("}\n") #nuget