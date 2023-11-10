# ARC and ROM Builder

Copyright (c) 2023, kounch

All rights reserved.

---

Select your desired language / Elija idioma:

- Click [this link for English](#english)

- Pulse [este enlace para Castellano](#castellano)

---

## English

### Features

This is a tool that creates ARC and ROM files. It is main focus is the [ZXTRES family](https://github.com/zxtres/) of FPGA devices, but it may also be useful for others like MiST, MiSTica or SiDi.

These are the main features:

- Uses the [MiSTer Update All](https://github.com/theypsilon/Update_All_MiSTer) databases (Arcades DB and JTCores DB) to obtain download information
- Downloads ZIP and MRA files from the sources in the obtained metadata
- Downloads [mra tool](https://github.com/kounch/mra-tools-c/tree/master/release) for the current OS (Mac, Windows or Linux)
- Builds ARC and ROM files structure for using with Jotego cores

### Software Requirements

- **Python (version 3.9 or later)**. Docs, downloads, etc. [here](https://www.python.org/)

### Installation and Use

Install Python 3. On Windows, it's recommended that `py launcher` is selected as an install option.

Copy the files `ARC_ROM_Builder.py` and `cores.json` to a directory with enough available space (3.5GB, at least, if using the default `cores.json` file), and execute the script:

     python3 ARC_ROM_Builder.py

On Windows

     py -3 ARC_ROM_Builder.py

Or

    ..python.exe ARC_ROM_Builder.py

This will create the following file and directory structure

     <AC_ROM_Builder directory/
       |
       +--cache/
       |     +--bin/
       |     |    +-mra(.exe)
       |     |
       |     +--mra/
       |     |    +-(..).mra
       |     |    (..)
       |     |
       |     +--roms/
       |     |    +-(..).zip
       |     |    (..)
       |     |
       |     +--arcade_roms_db.json.zip
       |     +--jtbindb.json.zip
       |
       +--JOTEGO/
             +--(...).arc
             +--(...).rom
             (...)

Once the process is finished, if there wer no errors, copy the entire `JOTEGO` directory to the root of a microSD card to use with the Arcade cores.

If something happens that interrupts the download of files, it is recommended to execute the script again, which will try to continue from that last failure.

### Advanced use

The script has the following parameters:

    -v, --version         Show program's version number and exit
    -C CACHE_DIR, --cache_dir CACHE_DIR
                          Change the directory location of the Cache
    -c CORES_DB, --cores_db CORES_DB
                          Change the name and location of the Cores DB JSON file
    -O OUTPUT_DIR, --output_dir OUTPUT_DIR
                          Change the Output directory name and location
    -a, --force_arcade_db
                          Force to download again the cached Arcade DB
    -m, --force_mra_db    Force to download again the cached MRA DB
    -i INCLUDE, --include INCLUDE
                          Names of cores to include, separated by commas
    -e EXCLUDE, --exclude EXCLUDE
                          Names of cores to exclude, separated by commas
    -n, --no_arc_rom      Do not build ARC and ROM files
    -f, --force           Force to download again cached ZIP and MRA files

#### Core database

The `cores.json` file defines the criteria by which the zip and mra files to be downloaded will be searched for, as well as, in cases where a core supports several of them, to indicate one to be used by default. Its structure is as follows:

    {
        "<core 1 name>": {
            "default_arc":"<default arc name>",
            "default_mra": "<default mra name>"
        },
        "<core 2 name>": {
            "default_arc":"<default arc name>",
            "default_mra":"<default mra name>"
        },

        (...)
    }

Where:

- `<core n name>` indicates the name to look up in the ROM and MRA DBs to identify the ZIP and MRA files to use. Examples: `jt1942`, `jtcps2`, `jtcps1`, `jtcps2`, `jtcps2`.
- `<default arc name>` is the name that will be used to create a default ARC for the given MRA. For example: `jtbubl`
- `<default mra name>` is the beginning of the MRA file name that will be used as a reference to uniquely identify and create default ARCs and ROMs. For example: `Bubble Bobble` to use a file named `Bubble Bobble (Japan, Ver 0.1).mra` (if there is no other file starting with the same words).

Adding or removing items to the cores JSON file will increase or decrease the number of cached files (and possible downloads), as well as the number of ARC and ROM files to be generated.

---

## Castellano

### Características

Esta es una herramienta que crea archivos ARC y ROM. Está principalmente orientada a la [familia ZXTRES](https://github.com/zxtres/) de dispositivos FPGA, pero también puede ser útil para otros como MiST, MiSTica o SiDi.

Sus características principales son:

- Utiliza las bases de datos de [Update All de MiSTer](https://github.com/theypsilon/Update_All_MiSTer) (BD Arcades DB y BD JTCores) para obtener información de descarga
- Descarga archivos ZIP y MRA de las fuentes de los metadatos obtenidos
- Descarga la [herramienta mra](https://github.com/kounch/mra-tools-c/tree/master/release) para el sistema operativo utilizado (Mac, Windows o Linux)
- Construye una estructura de archivos ARC y ROM para usar con los cores de Jotego

### Software necesario

- **Python (versión 3.9 o superior)**. Documentación, descarga, etc. [aquí](https://www.python.org/)

### Instalación y uso

Instalar Python 3 para el sistema operativo correspondiente. En el caso de Windows, es interesante incluir `py launcher` en las opciones de instalación.

Copiar los ficheros `ARC_ROM_Builder.py` y `cores.json` en un directorio con suficiente espacio disponible (al menos, 3,5GB, si se usa el fichero `cores.json` por defecto), y ejecutar el script:

    python3 ARC_ROM_Builder.py

En Windows

    py -3 ARC_ROM_Builder.py

o bien

    ...python.exe ARC_ROM_Builder.py

Esto creará una estructura de ficheros y directorios como la siguiente

    <directorio de ARC_ROM_Builder/
       |
       +--cache/
       |     +--bin/
       |     |    +-mra(.exe)
       |     |
       |     +--mra/
       |     |    +-(..).mra
       |     |    (..)
       |     |
       |     +--roms/
       |     |    +-(..).zip
       |     |    (..)
       |     |
       |     +--arcade_roms_db.json.zip
       |     +--jtbindb.json.zip
       |
       +--JOTEGO/
             +--(...).arc
             +--(...).rom
             (...)

Una vez el proceso haya finalizado, si no se han producido errores, copiar el directorio `JOTEGO` a la raíz de una tarjeta microSD para utilizar con los cores de Arcade.

Si se produjera alguna situación que interrumpa la descarga de ficheros, se recomienda volver a lanzar el script, que continuará a partir de ese último fallo.

### Uso avanzado

El script tiene los siguientes parámetros:

    -v, --version         Mostrar el número de versión del programa y salir
    -C CACHE_DIR, --cache_dir CACHE_DIR
                          Cambiar la ubicación del directorio de la Caché
    -c CORES_DB, --cores_db CORES_DB
                          Cambiar el nombre y la ubicación del archivo JSON de la BD de Cores
    -O OUTPUT_DIR, --output_dir OUTPUT_DIR
                          Cambiar el nombre y la ubicación del directorio de salida
    -a, --force_arcade_db
                          Fuerza la descarga de nuevo de la base de datos de Arcade almacenada en caché
    -m, --force_mra_db    Fuerza la descarga de nuevo de la base de datos MRA almacenada en caché
    -i INCLUDE, --include INCLUDE
                          Lista de nombres de cores a incluir, separados por comas
    -e EXCLUDE, --exclude EXCLUDE
                          Lista de nombres de cores a excluir, separados por comas
    -n, --no_arc_rom      No crear archivos ARC y ROM
    -f, --force           Fuerza la descarga de nuevo de los archivos ZIP y MRA almacenados en caché

#### Base de datos de cores

El fichero `cores.json` define el criterio por el que se buscarán los ficheros zip y mra que se van a descargar, así como, para los casos en que un core soporte varios, indicar uno para utilizar por defecto. Su estructura es la siguiente:

    {
        "<nombre de core 1>": {
            "default_arc": "<nombre de arc por defecto>",
            "default_mra": "<nombre de mra por defecto>"
        },
        "<nombre de core 2>": {
            "default_arc": "<nombre de arc por defecto>",
            "default_mra": "<nombre de mra por defecto>"
        },

        (...)
    }

Donde:

- `<nombre de core n>` indica el nombre a buscar en las BD de ROM y MRA para identificar los ficheros ZIP y MRA que se utilizarán. Ejemplos: `jt1942`, `jtcps2`
- `<nombre de arc por defecto>` es el nombre que se usará para crear un ARC por defecto para el MRA indicado. Por ejemplo: `jtbubl`
- `<nombre de mra por defecto>` es el comienzo del nombre del fichero MRA que se usará como referencia para identificar de manera única y crear ARC y ROM por defecto. Por ejemplo: `Bubble Bobble` para usar un fichero llamado `Bubble Bobble (Japan, Ver 0.1).mra` (si no hubiera ningún otro que comenzase por esas mismas palabras)

Añadir o quitar elementos al fichero JSON de cores implicará aumentar o reducir el número de ficheros (y posibles descargas) en caché, así como el número de ficheros ARC y ROM a generar.

---

## License

BSD 2-Clause License

Copyright (c) 2023, kounch
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

[Update All](https://github.com/theypsilon/Update_All_MiSTer) for [MiSTer](https://github.com/MiSTer-devel/Main_MiSTer/wiki)

Copyright © 2020-2022, [José Manuel Barroso Galindo](https://twitter.com/josembarroso).
Released under the [GPL v3 License](LICENSE).
