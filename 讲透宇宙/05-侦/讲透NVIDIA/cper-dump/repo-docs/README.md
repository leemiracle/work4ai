Kernel module to read CPERs stored in the R/W Flash of Grace CPU

Cper-dump kernel module uses a specific DSM call to dump the CPERs from the SPI flash to a binary file. To build the module,

Download the repo.

Untar it using 'tar zvf <cper_dump_package>.tgz

cd <cper_dump_directory>

make clean

make

To deploy the module once it is build,

insmod ./cper_dump.ko
