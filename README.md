# Babel project

## Description

## Installation

## File book

✔: Supported by Babel project

〰️: Partially supported (may require command lines)

❌: No supported by Babel project

➖: No concerned

Extension | Description of file | Supported |
:---: | :----: | :---:
adx | proprietary audio file system | ➖ |
afs | Archive File System | ✔ |
cpk | Criware archive format | 〰 |
dat (gpda) | archive file used by guyzware | 〰️ |
iso | ISO file | ✔ |
ks | script file used by kirikiri | ✔ |
obj (gpda) | script object used by guyzware | ❌ |
pmf | PSP movie file | ➖ |
xp3 | archive file used by kirikiri | ✔ |
xtx | image format | 〰 |

## TODO

### FC

- Delete the old folder (after the HTML translation)

#### format

##### CPK

- Adding the repackCPK

- Rewrite extractCPK, seem to bug a little

##### otherformat

- Adding the repack for GDPA dat

- Find how to read GPDA obj file (see translate)

#### translate

- Adding the HTML translate (see old)

- Write a better translateks, can possibly has some problem in some case

- Adding the CPK translate

- Adding the GPDA obj translate (see otherformat)

### UI

- Refont the GUI

## References

### afs

Scripts based on the work of:

- Nickworokin, https://github.com/nickworonekin/puyotools

### cpk

Scripts based on the work of:

- esperknight, https://github.com/esperknight/CriPakTools/

### GPDA dat:

Scripts based on the work of:

- Giacomo Stelluti Scala, http://rsk.twilight.free.fr/ps2/index.php5 (tenoritool)

### ks

Scripts based on the work of:

- https://kirikirikag.sourceforge.net/contents/

### xp3

Scripts based on the work of:

- Edward Keyes, http://www.insani.org/tools/

- SmilingWolf, https://bitbucket.org/SmilingWolf/xp3tools-updated

### GPDA obj

See

- https://github.com/xyzz/taiga-aisaka

- https://sourceforge.net/p/oreimo/code/HEAD/tree/

### Libraries use

pycdlib, https://pypi.org/project/pycdlib/

request, https://pypi.org/project/requests/

chardet, https://pypi.org/project/chardet/
