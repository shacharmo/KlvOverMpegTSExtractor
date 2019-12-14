# KLV Over MPEG-TS Extractor
Extract MISB 601 KLV data from MPEG-TS stream (STANAG 4609).

## Credit
KLV Data is adapted from https://github.com/paretech/klvdata.  

The code changes include the following:
* Ignore errors (write -1000 or -2000 as value).
* Output readable value when printing structure.
* Adding CRC validation to packet.  

## Implementation
MPEG-TS extraction is partly implemented, many unneeded fields are not extracted.    
Packet ID extraction doesn't seem to be correct when comparing to FFMPEG.  

The code is exposed a CLI but can be used as a package to extract KLV data.

## Getting Started
Clone the repository.  
Use an IDE such as PyCharm.  
Create a virtual environment fro the project using python 3.6+.  
No additional dependencies are required.

## Extracting KLV
The code can run on entire MPEG-TS file or extracted KLV binary file.  
The extract KLV binary use the following:  
* Using tool such as ffprobe get the mapping of KLV stream, e.g. 0:3
* Using tool such as ffmpeg copy the KLV stream to file, e.g.:
  ```bash
  ffmpeg -i [video-name].ts -map 0:3 -c copy -f data [video-name].klv
  ```  

## Usage
run.py is a CLI for parsing klv/mpeg-ts files.  
As output can be large, depending on input file, it is advised to pipe to log file.
### KLV binary file
```bash
python run.py -f [file.klv] -k
```

### MPEG-TS video file
```bash
python run.py -f [file.ts]
```
