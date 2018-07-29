import argparse
import glob
import os
import shutil
import subprocess

def clear_directory(dir_path):
    if os.path.exists(dir_path):
        for file in os.listdir(dir_path):
            if os.path.isfile(dir_path + "/" + file):
                os.remove(dir_path + "/" + file)
            else:
                shutil.rmtree(dir_path + "/" + file, ignore_errors=True)

# Get the necessary directories from the command line
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--use-existing', dest='use_existing', action='store_true')
parser.add_argument('-s', '--source-dir', dest='source_dir', metavar='OpenMesh source directory')
parser.add_argument('-b', '--build-dir', dest='build_dir', metavar='OpenMesh build directory')
parser.add_argument('-o', '--output-dir', dest='output_dir', metavar='Autopkg output directory', required=True)
parser.add_argument('-v', '--version', dest='version', required=True)
parser.add_argument('-r', '--release_notes', dest='release_notes', default='')
parser.add_argument('-y', '--copyright-year', dest='copyright_year', default='2018')
args = parser.parse_args()

# Transform the paths into absolute paths
use_existing = args.use_existing
source_dir   = '.'
build_dir    = '.'
if not use_existing:
    if args.source_dir is None:
        parser.error("If no existing build is used, the source dir has to be set")
    
    source_dir = os.path.abspath(args.source_dir)

    if args.build_dir is None:
        args.build_dir = args.source_dir + '/build'
    build_dir = os.path.abspath(args.build_dir)
    
output_dir = os.path.abspath(args.output_dir)
openmesh_version = args.version

# Validate the given paths
if not os.path.exists(source_dir):
    raise ValueError('Source directory does not exist.')

# Make sure the build directory and output directory exist
os.makedirs(build_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

print('Creating autopkg file for OpenMesh {:s}\nSourceDir: {:s}\nBuildDir: {:s}\nOutputDir: {:s}'.format(openmesh_version, source_dir, build_dir, output_dir))

# Assemble list of available toolset, platforms, configurations and linkages
toolsets = [
    ('Visual Studio 2013', 'v120', {'x86' : 'Visual Studio 12 2013', 'x64' : 'Visual Studio 12 2013 Win64'}),
    ('Visual Studio 2015', 'v140', {'x86' : 'Visual Studio 14 2015', 'x64' : 'Visual Studio 14 2015 Win64'}),
    ('Visual Studio 2017', 'v141', {'x86' : 'Visual Studio 15 2017', 'x64' : 'Visual Studio 15 2017 Win64'}),
    ]

platforms = [
    'x86', 
    'x64'
    ]

configurations = [
    'debug',
    'release'
    ]

linkages = [
    {
        'name' : 'static', 
        'flags' : 
        [
            '-DOPENMESH_BUILD_SHARED:BOOL=FALSE', 
            # '-DCMAKE_C_FLAGS_DEBUG:STRING=/D_DEBUG /MTd /Zi  /Ob0 /Od /RTC1',
            # '-DCMAKE_C_FLAGS_MINSIZEREL:STRING=/MT /O1 /Ob1 /D NDEBUG',
            # '-DCMAKE_C_FLAGS_RELEASE:STRING=/MT /O2 /Ob2 /D NDEBUG',
            # '-DCMAKE_C_FLAGS_RELWITHDEBINFO:STRING=/MT /Zi /O2 /Ob1 /D NDEBUG',
            # '-DCMAKE_CXX_FLAGS_DEBUG:STRING=/D_DEBUG /MTd /Zi /Ob0 /Od /RTC1',
            # '-DCMAKE_CXX_FLAGS_MINSIZEREL:STRING=/MT /O1 /Ob1 /D NDEBUG',
            # '-DCMAKE_CXX_FLAGS_RELEASE:STRING=/MT /O2 /Ob2 /D NDEBUG',
            # '-DCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING=/MT /Zi /O2 /Ob1 /D NDEBUG',
            # '-DCMAKE_C_FLAGS_DEBUG:STRING=/D_DEBUG /MTd /Zi  /Ob0 /Od /RTC1', 
            # '-DCMAKE_CXX_FLAGS_DEBUG:STRING=/D_DEBUG /MTd /Zi /Ob0 /Od /RTC1'
        ],
        'lib_files' : 'lib/*.lib',
    },
    {
        'name' : 'shared', 
        'flags' : ['-DOPENMESH_BUILD_SHARED:BOOL=TRUE'],
        'lib_files' : 'lib/*.lib',
        'bin_files' : '*.dll',
    }
    ]

cmake_to_coapps_linkage = {
    'static' : 'static',
    'shared' : 'dynamic'
}

install_dir = build_dir + '/install'
output_include_dir = os.path.join(output_dir, 'include')
output_build_dir = os.path.join(output_dir, 'build')
if not use_existing:
    # Clear the intermediate output directories
    if os.path.exists(output_include_dir):
        shutil.rmtree(output_include_dir)
    if os.path.exists(output_build_dir):
        shutil.rmtree(output_build_dir)
    for name, version, generators in toolsets:
        print("Building for {0:s} ({1:s})".format(name, version))
        for platform in platforms:
            generator = generators[platform]

            for linkage in linkages:
                # Try to create the solution
                clear_directory(build_dir)
                if subprocess.call(['cmake', source_dir, *linkage['flags'], '-DCMAKE_INSTALL_PREFIX:PATH={:s}'.format(install_dir), '-G', generator, '-DBUILD_APPS:BOOL=FALSE'], cwd=build_dir) > 0:
                    print("Solution creation failed. Continuing...")
                    continue

                for config in configurations:
                    print("Building platform {0:s} with configuration {1:s} ({2:s})".format(platform, config, linkage["name"]))

                    # Clear the install directory and make the build
                    clear_directory(install_dir)
                    if subprocess.call(['cmake', '--build', '.', '--target', 'INSTALL', '--config', config], cwd=build_dir) > 0:
                        print("Building configuration {:s} failed. Continuing...".format(config))
                        continue

                    # Copy the binary files into the output dir
                    output_lib_dir = output_build_dir + '/' + version + '/' + platform + '/' + config + '/' + cmake_to_coapps_linkage[linkage['name']] + '/lib'
                    output_bin_dir = output_build_dir + '/' + version + '/' + platform + '/' + config + '/' + cmake_to_coapps_linkage[linkage['name']] + '/bin'
                    os.makedirs(output_lib_dir, exist_ok=True)
                    os.makedirs(output_bin_dir, exist_ok=True)

                    # Copy lib files
                    if "lib_files" in linkage:
                        for lib_file in glob.glob(install_dir + '/' + linkage["lib_files"]):
                            filename = os.path.basename(lib_file)
                            shutil.copy(lib_file, output_lib_dir + '/' + filename)

                    # Copy bin files
                    if "bin_files" in linkage:
                        for bin_file in glob.glob(install_dir + '/' + linkage["bin_files"]):
                            filename = os.path.basename(bin_file)                                    
                            shutil.copy(bin_file, output_bin_dir + '/' + filename)

                    # Copy the include dir into the base directory
                    if os.path.exists(install_dir + '/include') and not os.path.exists(output_include_dir):
                        shutil.copytree(install_dir + '/include', output_include_dir)


# Generate the includes for the autopkg
print("Collecting include directories...")
include_paths = []
index = 1
for root, dirs, files in os.walk(output_include_dir):
    # Search a directory with (include) files
    if files :
        include_paths.append(os.path.relpath(root, output_include_dir).replace('\\', '/'))

# Collect the binary files from the filesystem
print("Collecting binary directories...")
builds = []
for root, dirs, files in os.walk(output_build_dir, topdown=False):
    if "bin" in dirs and "lib" in dirs:
        relative_path = os.path.relpath(root, output_build_dir).replace('\\', '/')
        pivots = relative_path.split('/')

        lib_files = []
        for file in os.listdir(root + '/lib'):
            lib_files.append('build/' + relative_path + '/lib/' + file) 

        bin_files = []
        for file in os.listdir(root + '/bin'):
            bin_files.append('build/' + relative_path + '/bin/' + file) 

        builds.append({
            "pivots" : pivots,
            "lib_files" : lib_files,
            "bin_files" : bin_files,
        })

print("Writing autopkg file...")
def write_line(f, tab_count, text):
    f.write('\t' * tab_count + text + '\n')

# Create the autopkg file
file = open(os.path.join(output_dir, 'openmesh-{:s}.autopkg'.format(openmesh_version)), "w")
write_line(file, 0, 'configurations')
write_line(file, 0, '{')
write_line(file, 1, 'Toolset')
write_line(file, 1, '{')
write_line(file, 2, 'key : "PlatformToolset";')
write_line(file, 2, 'choices: { v141, v140, v120, v110 };')
write_line(file, 1, '};') # Toolset
write_line(file, 0, '}') # configurations
write_line(file, 0, '')
write_line(file, 0, 'nuget')
write_line(file, 0, '{')
write_line(file, 1, 'nuspec')
write_line(file, 1, '{')
write_line(file, 2, 'id = openmesh;')
write_line(file, 2, 'version: {:s};'.format(openmesh_version))
write_line(file, 2, 'title: Open Mesh;')
write_line(file, 2, 'authors: {RWTH-Aachen University};')
write_line(file, 2, 'owners: {Markus Worchel};')
write_line(file, 2, 'licenseUrl: "https://www.openmesh.org/license/";')
write_line(file, 2, 'projectUrl: "https://www.openmesh.org/";')
write_line(file, 2, 'iconUrl: "https://www.openmesh.org/static//OpenMesh_text_512.png";')
write_line(file, 2, 'requireLicenseAcceptance: true;')
write_line(file, 2, 'summary: A generic and efficient polygon mesh data structure;')
write_line(file, 2, 'description: @"OpenMesh is a generic and efficient data structure for representing and manipulating polygonal meshes.";')
write_line(file, 2, 'releaseNotes: @"{:s}";'.format(args.release_notes))
write_line(file, 2, 'copyright: Copyright {:s};'.format(args.copyright_year))
write_line(file, 2, 'tags: {OpenMesh, native, Mesh, Half-Edge};')
write_line(file, 1, '}') # nuspec
write_line(file, 0, '')
write_line(file, 1, 'files')
write_line(file, 1, '{')
for i, p in enumerate(include_paths):
    write_line(file, 2, 'nested{0:d}Include: {{ #destination = ${{d_include}}{1:s}; "include/{1:s}/*"}};'.format(i + 1, p))
write_line(file, 0, '')
for b in builds:
    # Write the pivot
    write_line(file, 2, '[{:s}]'.format(', '.join(b['pivots'])))
    write_line(file, 2, '{')
    if len(b['lib_files']) > 0: 
        write_line(file, 3, 'lib: {{ {:s} }};'.format(', '.join(b['lib_files'])))
    if len(b['bin_files']) > 0: 
        write_line(file, 3, 'bin: {{ {:s} }};'.format(', '.join(b['bin_files'])))
    write_line(file, 2, '}')
    write_line(file, 2, '')
write_line(file, 1, '}') #files
write_line(file, 1, 'targets')
write_line(file, 1, '{')
write_line(file, 2, 'Defines += { HAS_OPENMESH, _USE_MATH_DEFINES};')
write_line(file, 2, '[debug, static]')
write_line(file, 2, '{')
write_line(file, 3, 'RuntimeLibrary = MultiThreadedDebugDLL;')
write_line(file, 2, '}')
write_line(file, 2, '[release, static]')
write_line(file, 2, '{')
write_line(file, 3, 'RuntimeLibrary = MultiThreadedDLL;')
write_line(file, 2, '}')
write_line(file, 1, '}') #targets
write_line(file, 0, '}') #nuget    
print("Done.")