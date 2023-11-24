#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
"""
Copyright (c) 2023, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause
"""

from __future__ import print_function
from typing import Any
import logging
import sys
import platform
import argparse
import pathlib
import os
import json
import hashlib
import ssl
import subprocess
from zipfile import ZipFile, is_zipfile
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, quote, unquote, urljoin
import socket
import time

__MY_VERSION__ = '0.0.2'

MY_BASEPATH: str = os.path.dirname(sys.argv[0])
MY_DIRPATH: str = os.path.abspath(MY_BASEPATH)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOG_FORMAT = logging.Formatter(
    '%(asctime)s [%(levelname)-5.5s] - %(name)s: %(message)s')
LOG_STREAM = logging.StreamHandler(sys.stdout)
LOG_STREAM.setFormatter(LOG_FORMAT)
LOGGER.addHandler(LOG_STREAM)

if sys.version_info < (3, 9, 0):
    LOGGER.error('This software requires Python version 3.9 or greater')
    sys.exit(1)

ssl._create_default_https_context = ssl._create_unverified_context  # pylint: disable=protected-access
socket.setdefaulttimeout(900)


def main():
    """Main routine"""

    arg_data: dict[str, Any] = parse_args()
    LOGGER.debug('Starting up...')

    s_cache_path: str = arg_data['cache_dir']
    s_roms_path: str = os.path.join(s_cache_path, 'roms')
    s_mras_path: str = os.path.join(s_cache_path, 'mra')
    s_out_path: str = arg_data['output_dir']

    d_arcade_db: dict[str, Any] = load_arcade_bd(s_cache_path,
                                                 arg_data['force_bda'],
                                                 arg_data['arcadebd_commit'])
    if not d_arcade_db:
        LOGGER.error("There's no Arcade JSON data")
        sys.exit(2)

    d_mra_db: dict[str, Any] = load_mra_bd(s_cache_path, arg_data['force_bdm'],
                                           arg_data['mrabd_commit'])
    if not d_mra_db:
        LOGGER.error("There's no MRA JSON data")
        sys.exit(2)

    d_tmp: dict[str, Any] = load_cores_bd(arg_data['cores_db'])
    if not d_tmp:
        LOGGER.error("There's no Cores DB JSON file")
        sys.exit(2)

    d_cores_db = filter_cores(d_tmp, arg_data['include'], arg_data['exclude'])

    print('Checking ROM ZIP files cache...')
    chk_zip_cache(d_arcade_db, d_cores_db, s_roms_path, arg_data['force'])

    print('Checking MRA files cache...')
    d_mras: dict[str, Any] = chk_mra_cache(d_mra_db, d_cores_db, s_mras_path,
                                           arg_data['force'],
                                           arg_data['mras_commit'])

    if arg_data['build_arc_rom']:
        print('Building ARC files...')
        build_arc_files(d_mras, d_cores_db, s_out_path, s_mras_path,
                        s_roms_path, s_cache_path)


def parse_args() -> dict[str, Any]:
    """
    Parses command line
    :return: Dictionary with different options
    """
    global LOGGER  # pylint: disable=global-variable-not-assigned

    values: dict[str, Any] = {}
    values['cache_dir'] = os.path.join(MY_DIRPATH, 'cache')
    values['cores_db'] = os.path.join(MY_DIRPATH, 'cores.json')
    values['output_dir'] = os.path.join(MY_DIRPATH, 'JOTEGO')
    values['force_bda'] = False
    values['force_bdm'] = False
    values['include'] = []
    values['exclude'] = []
    values['build_arc_rom'] = True
    values['force'] = False
    values['arcadebd_commit'] = 'db'
    values['mrabd_commit'] = 'main'
    values['mras_commit'] = '71dae38d45b3646f35345848a87cc4a709b6b6af'

    parser = argparse.ArgumentParser(
        description='ARC and ROM Builder',
        epilog='Build ARC and ROM files for FPGA Arcade Cores')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=f'%(prog)s {__MY_VERSION__}')

    parser.add_argument('-C',
                        '--cache_dir',
                        required=False,
                        action='store',
                        dest='cache_dir',
                        help='Cache directory name and location')
    parser.add_argument('-c',
                        '--cores_db',
                        required=False,
                        action='store',
                        dest='cores_db',
                        help='Cores DB JSON file name and location')
    parser.add_argument('-O',
                        '--output_dir',
                        required=False,
                        action='store',
                        dest='output_dir',
                        help='Output dir name and location')
    parser.add_argument('-a',
                        '--force_arcade_db',
                        required=False,
                        action='store_true',
                        dest='force_bda',
                        help='Force to download again cached Arcade DB file')
    parser.add_argument('-m',
                        '--force_mra_db',
                        required=False,
                        action='store_true',
                        dest='force_bdm',
                        help='Force to download again cached MRA DB file')
    parser.add_argument('-i',
                        '--include',
                        required=False,
                        action='append',
                        dest='include',
                        help='Names of cores to include, separated by commas')
    parser.add_argument('-e',
                        '--exclude',
                        required=False,
                        action='append',
                        dest='exclude',
                        help='Names of cores to exclude, separated by commas')
    parser.add_argument('-n',
                        '--no_arc_rom',
                        required=False,
                        action='store_true',
                        dest='no_build_arc_rom',
                        help='Do not build ARC and ROM files')
    parser.add_argument('--arcadebd_commit',
                        required=False,
                        action='store',
                        dest='arcadebd_commit',
                        help='Arcade BD Commit ID')
    parser.add_argument('--mrabd_commit',
                        required=False,
                        action='store',
                        dest='mrabd_commit',
                        help='MRA BD Commit ID')
    parser.add_argument('--mras_commit',
                        required=False,
                        action='store',
                        dest='mras_commit',
                        help='MRA files Commit ID')
    parser.add_argument(
        '-f',
        '--force',
        required=False,
        action='store_true',
        dest='force',
        help='Force to download again cached ZIP and MRA files')

    parser.add_argument('--debug',
                        required=False,
                        action='store_true',
                        dest='debug')

    arguments = parser.parse_args()

    if arguments.debug:
        LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug(sys.argv)

    if arguments.cache_dir:
        values['cache_dir'] = os.path.abspath(arguments.cache_dir)

    if arguments.cores_db:
        values['cores_db'] = os.path.abspath(arguments.cores_db)

    if arguments.output_dir:
        values['output_dir'] = os.path.abspath(arguments.output_dir)

    if arguments.force_bda:
        values['force_bda'] = arguments.force_bda

    if arguments.force_bdm:
        values['force_bdm'] = arguments.force_bdm

    if arguments.include:
        for s_include in arguments.include:
            values['include'] += s_include.split(',')

    if arguments.exclude:
        for s_exclude in arguments.exclude:
            values['exclude'] += s_exclude.split(',')

    if arguments.no_build_arc_rom:
        values['build_arc_rom'] = False

    if arguments.arcadebd_commit:
        values['arcadebd_commit'] = arguments.arcadebd_commit

    if arguments.mrabd_commit:
        values['mrabd_commit'] = arguments.mrabd_commit

    if arguments.mras_commit:
        values['mras_commit'] = arguments.mras_commit

    if arguments.force:
        values['force'] = arguments.force

    LOGGER.debug(values)
    return values


def load_cores_bd(s_name: str) -> dict[str, Any]:
    """
    Loads Cores Database from JSON file
    :param s_name: Where the JSON file should be
    :return: Dictionary with data
    """

    d_cores: dict[str, Any] = {}
    if not os.path.isfile(s_name):
        LOGGER.error('Cores database not found: %s', s_name)

    with open(s_name, 'r', encoding='utf-8') as json_handle:
        LOGGER.debug('Loading Cores database...')
        d_cores = json.load(json_handle)
        LOGGER.debug('%s loaded OK', s_name)

    return d_cores


def load_arcade_bd(s_dirpath: str,
                   b_force: bool,
                   s_commit: str = '') -> dict[str, Any]:
    """
    Loads Arcade Database from JSON inside ZIP file
    :param s_dirpath: Directory where the ZIP file should be
    :param b_force: If True, delete (if exists) and download again
    :return: Dictionary with data
    """

    if not s_commit:
        s_commit = 'db'

    s_name: str = 'arcade_roms_db.json'
    s_urlbase: str = 'https://raw.githubusercontent.com/theypsilon/'
    s_urlbase += f'ArcadeROMsDB_MiSTer/{s_commit}/'
    d_arcade: dict[str, Any] = load_zip_bd(s_dirpath, s_name, s_urlbase,
                                           b_force)

    return d_arcade


def load_mra_bd(s_dirpath: str,
                b_force: bool,
                s_commit: str = '') -> dict[str, Any]:
    """
    Loads MRA Database from JSON inside ZIP file
    :param s_dirpath: Directory where the ZIP file should be
    :param b_force: If True, delete (if exists) and download again
    :return: Dictionary with data
    """

    if not s_commit:
        s_commit = 'main'

    s_name: str = 'jtbindb.json'
    s_urlbase: str = f'https://raw.githubusercontent.com/jotego/jtcores_mister/{s_commit}/'
    d_mra: dict[str, Any] = load_zip_bd(s_dirpath, s_name, s_urlbase, b_force)

    return d_mra


def filter_cores(d_cores_db: dict[str, Any], l_include: list[str],
                 l_exclude: list[str]) -> dict[str, Any]:
    """
    Filters the cores DB, and gives a reduced copy
    :param d_cores_db: Dict with cores DB
    :param l_include: List of names of cores to include
    :param l_exclude: List of names of cores to exclude
    :return: Filtered dictionary with data
    """

    d_result: dict[str, Any] = {}
    for s_key, o_values in d_cores_db.items():
        b_include: bool = True
        if l_include:
            b_include = False
            if s_key in l_include:
                b_include = True
        if l_exclude:
            if s_key in l_exclude:
                b_include = False

        if b_include:
            d_result[s_key] = o_values

    return d_result


def chk_zip_cache(d_arcade_db: dict[str, Any], d_cores_db: dict[str, Any],
                  s_roms_path: str, b_force: bool):
    """
    Populates ROM ZIP files disk cache
    :param d_arcade_db: Dict with arcade DB
    :param d_cores_db: Dict with cores DB
    :param s_roms_path: Path for the ROM files cache
    :param b_force: If True, delete (if exists) and download again
    :return: Nothing
    """

    d_files: dict[str, Any] = d_arcade_db['files']
    d_tags: dict[str, Any] = d_arcade_db['tag_dictionary']

    for s_file in d_files:
        s_name: str = s_file.split('/')[-1]
        for i_item in d_files[s_file]['tags']:
            for j_item in d_tags:
                if d_tags[j_item] == i_item and j_item in d_cores_db:
                    b_ok = chk_or_download(s_roms_path, s_name,
                                           d_files[s_file]['hash'],
                                           d_files[s_file]['size'],
                                           d_files[s_file]['url'], b_force)
                    if not b_ok:
                        print(f'{s_name} Bad file!')


def chk_mra_cache(d_mra_db: dict[str, Any],
                  d_cores_db: dict[str, Any],
                  s_mras_path: str,
                  b_force: bool,
                  s_commit: str = '') -> dict[str, Any]:
    """
    Populates MRA text files disk cache
    :param d_mra_db: Dict with MRA DB
    :param d_cores_db: Dict with cores DB
    :param s_mras_path: Path for the MRA files cache
    :param b_force: If True, delete existing files and download again
    :param s_commit: If not empyt, commit id to use to download the MRA files
    :return: Dict with MRA groups info
    """

    d_mras: dict[str, Any] = {}

    if not s_commit:
        s_commit = 'master'

    d_files: dict[str, Any] = d_mra_db['files']
    d_tags: dict[str, Any] = d_mra_db['tag_dictionary']
    s_baseurl: str = f'https://raw.githubusercontent.com/jotego/jtbin/{s_commit}/mra/'
    for s_file in d_files:
        s_name: str = s_file.split('/')[-1]
        if s_name.endswith('.mra') and not '_alternatives' in s_file:
            for s_item in d_files[s_file]['tags']:
                for s_tagitem in d_tags:
                    if d_tags[s_tagitem] == s_item and ''.join(
                            s_tagitem.split('arcade')) in d_cores_db:
                        if not s_tagitem in d_mras:
                            d_mras[s_tagitem] = []
                        d_mras[s_tagitem].append(s_name)
                        b_ok = chk_or_download(s_mras_path, s_name,
                                               d_files[s_file]['hash'],
                                               d_files[s_file]['size'],
                                               s_baseurl + s_name, b_force)
                        if not b_ok:
                            print(f'{s_name} Bad file!')

    return d_mras


def build_arc_files(d_mras: dict[str, Any], d_cores_db: dict[str, Any],
                    s_out_path: str, s_mras_path: str, s_roms_path,
                    s_cache_path: str):
    """
    Builds ARC and ROM files from MRA and ROM ZIP files
    :param d_mras: Dict with MRA groups info
    :param s_out_path: Base path where the ARC and ROM files are created
    :param s_mras_path: Path for the MRA files cache
    :param s_roms_path: Path for the ROM ZIP files cache
    :param s_cache_path: Path to the main cache (to find the bin)
    :return: Nothing
    """

    if not os.path.isdir(s_out_path):
        pathlib.Path(s_out_path).mkdir(parents=True, exist_ok=True)

    s_mra_bindirpath: str = os.path.join(s_cache_path, 'bin')
    s_mra_binpath: str = chk_or_download_mrabin(s_mra_bindirpath)
    if s_mra_binpath != '':
        for s_mra, l_mra in d_mras.items():
            s_basename_arc: str = ''.join(s_mra.split('arcade'))
            s_subdir_arc: str = ''
            if len(l_mra) > 1:
                s_subdir_arc: str = ''.join(s_basename_arc.split('jt')).upper()

            for s_submra in l_mra:
                s_mra_path: str = os.path.join(s_mras_path, s_submra)
                default_mra = d_cores_db[s_basename_arc]['default_mra']
                l_mra_params: list[str] = []

                s_arc_path: str = s_out_path
                if s_subdir_arc == '' or (default_mra != '' and
                                          s_submra.startswith(default_mra)):
                    s_arc_name: str = ''.join(s_mra.split('arcade')) + '.arc'
                    if d_cores_db[s_basename_arc]['default_arc'] != '':
                        s_arc_name = d_cores_db[s_basename_arc][
                            'default_arc'] + '.arc'

                    l_mra_params = [
                        s_mra_binpath, '-A', '-z', s_roms_path, '-O',
                        s_arc_path, '-a',
                        s_arc_name.upper(), s_mra_path
                    ]
                    LOGGER.debug(' '.join(l_mra_params))
                    run_process(l_mra_params, s_submra)

                if s_subdir_arc != '':
                    s_arc_path = os.path.join(s_arc_path, s_subdir_arc)
                    if not os.path.isdir(s_arc_path):
                        pathlib.Path(s_arc_path).mkdir(parents=True,
                                                       exist_ok=True)

                l_mra_params = [
                    s_mra_binpath, '-A', '-z', s_roms_path, '-O', s_arc_path,
                    s_mra_path
                ]
                LOGGER.debug(' '.join(l_mra_params))
                run_process(l_mra_params, s_submra)


def load_zip_bd(s_dirpath: str, s_name: str, s_urlbase: str,
                b_force: bool) -> dict[str, Any]:
    """
    Loads Database from JSON inside ZIP file
    :param s_dirpath: Directory where the ZIP file should be
    :param s_name: JSON file name
    :param s_urlbase: Base URL to compose the path to download
    :param b_force: If True, delete an existing file and download again
    :return: Dictionary with data
    """

    s_zipname: str = s_name + '.zip'
    s_jsonzip: str = os.path.join(s_dirpath, s_zipname)
    s_urlpath: str = urljoin(s_urlbase, s_zipname)

    if b_force:
        os.remove(s_jsonzip)

    if not os.path.isfile(s_jsonzip):
        b_ok: bool = chk_or_download(s_dirpath, s_zipname, s_url=s_urlpath)
        if not b_ok:
            print(f'{s_name} Bad file!')

    d_result: dict[str, Any] = {}
    if is_zipfile(s_jsonzip):
        with ZipFile(s_jsonzip, "r") as z_handle:
            for s_filename in z_handle.namelist():
                if s_filename == s_name:
                    LOGGER.debug('Loading Arcade DB...')
                    with z_handle.open(s_filename) as json_handle:
                        json_data: bytes = json_handle.read()
                        d_result = json.loads(json_data.decode("utf-8"))
                    LOGGER.debug('%s loaded OK', s_jsonzip)
                    break
    else:
        print(f'{s_name} Not a ZIP file!')

    return d_result


def chk_or_download_mrabin(s_mrabin_dirpath: str,
                           b_force: bool = False) -> str:
    """
    Download mra binary file if does not exist
    :param s_mra_dirpath: Path to dir where the file should be
    :param b_force: If True, delete an existing file and download again
    :return: String with the full path to the binary file
    """

    b_ok: bool = True

    s_mra_binname: str = 'mra'
    s_mra_binurl: str = 'https://github.com/kounch/mra-tools-c/raw/master/release/'

    if sys.platform == 'darwin':
        s_mra_binurl = urljoin(s_mra_binurl, 'macos/')
    elif sys.platform == 'win32':
        s_mra_binurl = urljoin(s_mra_binurl, 'windows/')
        s_mra_binname = 'mra.exe'
    else:  # Assume Linux
        s_mra_binurl = urljoin(s_mra_binurl, 'linux/')
        if platform.machine() == 'armv7l':
            s_mra_binname = 'mra.armv7l'
        elif platform.machine() == 'aarch64':
            s_mra_binname = 'mra.aarch64'

    s_mra_binpath: str = os.path.join(s_mrabin_dirpath, s_mra_binname)
    s_mra_binurl = urljoin(s_mra_binurl, s_mra_binname)

    if not os.path.isfile(s_mra_binpath):
        b_ok = chk_or_download(s_mrabin_dirpath,
                               s_mra_binname,
                               s_url=s_mra_binurl,
                               b_force=b_force)
        time.sleep(15)  # Give Windows some time to check the file
        if sys.platform != 'win32':
            run_process(['chmod', 'a+x', s_mra_binpath], 'mra tool binary')
        if not b_ok:
            s_mra_binpath = ''

    return s_mra_binpath


def chk_or_download(s_path: str,
                    s_name: str,
                    s_hash: str = '',
                    i_size: int = 0,
                    s_url: str = '',
                    b_force: bool = False) -> bool:
    """
    Download a file if does not exist and, optionally check hash
    :param s_path: Path to dir where the file should be
    :param s_name: File name
    :param s_hash: Optional MD5 hash to check
    :param i_size: Optional size (bytes) to check
    :param s_url : Optional URL to download from
    :param b_force: If True, delete an existing file and download again
    :return: Boolean indicating download, check, etc. where all ok
    """

    b_ok: bool = True

    if not os.path.isdir(s_path):
        pathlib.Path(s_path).mkdir(parents=True, exist_ok=True)

    s_fpath: str = os.path.join(s_path, s_name)

    if b_force:
        if os.path.isfile(s_fpath):
            os.remove(s_fpath)

    if os.path.isfile(s_fpath):
        if s_hash != '':
            i_fsize: int = os.stat(s_fpath).st_size
            LOGGER.debug('%s exists, checking...', s_name)
            s_hashcheck: str = get_file_hash(s_fpath)
            if s_hash == s_hashcheck and i_fsize == i_size:
                LOGGER.debug('%s is OK!', s_name)
            else:
                LOGGER.warning('%s wrong hash!', s_name)
                os.remove(s_fpath)

    if not os.path.isfile(s_fpath):
        if s_url != '':
            print(f'Downloading {s_name}..')
            s_turl = unquote(s_url, encoding='utf-8', errors='replace')
            if len(s_turl) == len(s_url):
                s_turl = urlparse(s_url)
                s_url = s_turl.scheme + "://" + s_turl.netloc + quote(
                    s_turl.path)
                if s_turl.query != '':
                    s_url += "?" + quote(s_turl.query)

            try:
                urllib.request.urlretrieve(s_url, s_fpath)
            except HTTPError as error:
                LOGGER.debug('Cannot fetch %s! %s', s_url, error)
            except URLError as error:
                LOGGER.error('Connection error: %s! %s', s_url, error)
                b_ok = False
        else:
            LOGGER.error('%s not found!', s_name)
            b_ok = False

    if os.path.isfile(s_fpath):
        if s_hash != '' and i_size != 0:
            i_fsize: int = os.stat(s_fpath).st_size
            LOGGER.debug('%s downloaded, checking...', s_name)
            s_hashcheck: str = get_file_hash(s_fpath)
            if s_hash == s_hashcheck and i_fsize == i_size:
                LOGGER.debug('%s is OK!', s_name)
            else:
                LOGGER.error('%s wrong file!', s_name)
                b_ok = False
    else:
        LOGGER.error('Error downloading %s!', s_name)
        b_ok = False

    return b_ok


def get_file_hash(s_file: str) -> str:
    """
    Get file md5 hash
    :param s_file: Path to file
    :return: String with hash data
    """
    md5_hash: object = hashlib.md5()
    with open(s_file, "rb") as f_data:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f_data.read(4096), b""):
            md5_hash.update(byte_block)

    return md5_hash.hexdigest()


def run_process(l_mra_params: list[str], s_item: str):
    """
    Runs a process, printing stdout, and logging an errir if stderr not empty
    :param l_mra_params: list of command line command and parameters
    :param s_item: Text to show as element in error if stderr not empty
    :return: Nothing
    """

    mra_process = subprocess.run(l_mra_params,
                                 capture_output=True,
                                 check=False,
                                 encoding='utf8')
    if mra_process.stdout != '':
        print(mra_process.stdout)
    if mra_process.stderr != '':
        LOGGER.error('Problem processing %s: %s', s_item, mra_process.stderr)


if __name__ == "__main__":
    main()
