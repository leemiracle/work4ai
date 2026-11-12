# Introduction

This is a custom version of texlive.
The purpose is to extend pdftex to generate machine learning OCR annotations for each PDF page.

The pipeline has an embedded Python >=3.10 interpreter and directly outputs markdown, you can find it on the `nvpdftex` branch.
This repository specifically adds python hooks to the pdflatex compiler.
The implementation of the hooks reside in the `nvtexpy` repository.

**NOTE**: The other engines like tex, luatex etc. have not been adapted!

The following image shows the modifications on a coarse level 
![images/nvpdftex-pipeline.png](images/nvpdftex-pipeline.png)


# Compilation

Installation should be easy in principle but it's hard to get it to run with your build environment. We recommend using our [Dockerfile](Dockerfile) for the build environment.

We provide simple scripts to support a quick error-reduced way to reconfigure / autoreconf / build pdflatex only.

```shell
# Only needed if new source files or dependencies were added / deleted.
# The resulting changes are already checked in!
# This is very sensitive to the autotools and libtool version.
# ./autoreconf-pdftex.sh

# Build dependent libraries and prepare the main web2c folder.
./configure-pdftex.sh

# Build the actual pdftex.
./build-pdftex.sh
```

# Installation

## Usage

The custom `pdftex` (and `pdflatex`, which is a symlink) depend on a python import of `nvtexpy`, which provides the `NVTexPyEngine` main class.

After installing, you can run `pdftex` just normally and it should not interfere with the normal PDF building.
In this default mode, no Python callbacks (except for init and exit) will be called. This is needed to make the format rebuilding work (see above).

To actually activate "nvtexpy" and generate markdown, you need to set the `-nvtexpy` option:

```shell
pdflatex -nvtexpy=2 example.tex  # Run with nvtexpy activated
pdflatex -nvtexpy=3 example.tex  # Run with nvtexpy and debugpy, to debug from vscode
```

The nvtexpy flag has bit flags, the first bit is the debugger, the second is the callback activation, hence 3 activates both.

All bits explained:
- `1`: Activate debugpy and wait for client
- `2`: Activate nvtexpy hooks
- `16`: If set, deactivate input_stack optimization of TeX. I.e. keep all intermediate levels. Careful!

## Development Usage

During development, you won't want to rebuild the formats after every little change to the binary.
In this case, you can run pdftex in the so-called `ini` mode, that means without loading any format files:

```shell
pdftex -ini -etex -nvtexpy=3 example.tex
```

You can use only plain TeX in this mode. If you want to use LaTeX, you will need to include it at the top of your TeX input file like this:
```
\let\primitivedump=\dump
\let\dump=\relax
\input pdflatex.ini
\let\dump=\primitivedump
```

After that you can use `\documentclass{...}` etc.

### Development Helpers and Debugging

Debugging:
- To debug `nvtexpy.py`, you can activate the flag as mentioned above.
- To debug the C-code including the Python bindings, you can attach `gdb` like `gdb -ex=r --args pdftex -nvtexpy=2 ...`

## About the C-code of pdftex
TeX is written in WEB (mixture of Pascal and comments), see `pdftex.web`. Normally this WEB file is composed of a main `tex.web` plus a lot of changesets (`*.ch` files).
To simplify things, we have merged those into one `pdftex.web` file.

During compilation some conversion happens:
- The WEB code is converted to compact Pascal code (`pdftex.p`)
- The Pascal code is converted to C code (`pdftex0.c`, `pdftexd.h`, `pdftexcoerce.h`, ...)
- `gcc` is used to compile this into the actual binary `pdftex`

If you want to debug the C-code, you should place breakpoints in `pdftex0.c`, or even easier in `nvtexpy.c` and the walk down the stack trace.


## Python Hooks Authors

- Lukas Vögtle ([@voegtlel](https://www.github.com/voegtlel))
- Philipp Fischer ([@philipp-fischer](https://www.github.com/philipp-fischer))

# Original Readme

$Id$
Public domain.  Originally written 2005 by Karl Berry.

For a high-level overview of building TeX Live, see
http://tug.org/texlive/build.html.  In brief:

- To configure and make the source tree, run ./Build.
  This builds in subdirectory Work/, and installs into subdirectory inst/.

- To build (mostly) without optimization, run ./Build --debug.

- If the make fails and you want to rebuild without starting from scratch:
  cd Work/whatever/subdir && make

Email tlbuild@tug.org if problems.

(Nearly everything the Build script does can be overridden via
environment variables; just take a look to see the names.)

Many more details about the TL build system, such as configuring to work
on a single program, adding new programs or libraries, documentation
about the many pieces of the system, etc., are in the doc/tlbuild*
document and the sibling README* files here (which are generated from
that document).


Build information for some of the platforms.
See also Master/tlpkg/bin/tl-update-bindir.

aarch64-linux:
  Built on contextgarden, see below, except for asy:
  aarch64 Debian GNU/Linux 10 (buster)
  gcc (Debian 8.3.0-6) 8.3.0
  ./Build --enable-arm-neon=on

armhf-linux:
  Built on contextgarden, see below.
  Raspbian/Raspberry Pi OS (Debian Buster)
  Previously, built by Simon Dales:
  gcc version 10.2.1 20210110 (Raspbian 10.2.1-6+rpi1)
  ./Build --enable-xindy CLISP=${BUILD_ROOT_DIR}/clisp/clisp-build/clisp}
  armhf-linux binaries are created and tested on RPi;
  they run on RPi, as well as ARMv7 CPUs, but are untested on non-RPi
  ARMv6 machines.

x86_64-cygwin: gcc-10.2.0, cygwin-3.1.7
  TL_CONFIGURE_ARGS="--enable-xindy --enable-shared CLISP=/path/to/clisp.exe
    LDFLAGS='-Wl,--no-insert-timestamp -Wl,--stack,0x800000'" \
  ./Build
  
i386-freebsd, amd64-freebsd:
  Built on contextgarden, see below.
  FreeBSD 11.4

i386-linux: see travis below.

i386-netbsd, amd64-netbsd:
  NetBSD/amd64 9.2
  gcc version 7.5.0 (nb4 20200810)
    TL_MAKE=gmake CC=gcc CXX=g++ \
    CFLAGS=-D_NETBSD_SOURCE \
    CXXFLAGS='-D_NETBSD_SOURCE -std=c++11' \
    LDFLAGS='-L/usr/X11R7/lib -Wl,-rpath,/usr/X11R7/lib' \
  ./Build --enable-xindy CLISP=/usr/local/bin/clisp

i386-solaris, x86_64-solaris:
  Built on contextgarden, see below.
  Solaris 10, gcc 5.5.  See doc/README.solaris.

universal-darwin: See Master/source/mactexdoc.tar.xz.

windows:
  Makefiles written by hand, see Master/source/windows-src.tar.xz.
  Visual Studio 2010 and Visual Studio 2015.

x86_64-darwinlegacy:
  Mac OS X 10.6, clang 5.0, libc++ required
  auxiliary installer binaries: Mac OS X 10.6, gcc -std=c99.
  https://github.com/TeXLive-M/texlive-buildbot
  http://build.contextgarden.net/waterfall?tag=c/texlive
  (These links have info on all platforms built by Mojca.)

i386-linux,
x86_64-linux,
x86_64-linuxmusl:
  CentOS 7 Docker image with musl libc 1.1.5, plus gcc10:
    yum -y install centos-release-scl-rh
    yum -y install devtoolset-9-gcc-c++
    yum install -y fontconfig-devel libX11-devel libXmu-devel libXaw-devel
  Binaries are taken from the CI testing via github;
  see the source/.github/* files for details on how to build,
  and tlpkg/bin/tl-update-bindir for updating binaries (in general).
