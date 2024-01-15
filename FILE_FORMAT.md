# Heartbeat Capture File Definition

## Filename
`<START_DATETIME>-<END_DATETIME>_<NODE_ID>-<CAPTURE_ID>.csv`
`YYYYMMDD_HHMMSS-YYYYMMDD_HHMMSS_ET0000-0000.csv`

## Header section

The file header contains crucial details regarding the capture, including date/time and location information. This metadata is essential for efficient cataloging and subsequent analysis.

Each line of metadata consists of a metadata key, followed by one or more tab characters `\t`, and then the corresponding value.

### Header format
```
## BEGIN HEADER
# FILE				<FILENAME>
# CREATED			Month DD, YYYY HH:mm:ss UTC
# NODE				<NODE_ID>
# LOCATION			<CITY>, <STATE/REGION>
# GPS_LOCATION		<LATITUDE decimal>, <LONGITUDE decimal>, <ELEVATION in meters>
# OPERATOR			<OPERATOR_IDENTIFIER>
# CAPTURE_ID		<CAPTURE_ID>
# SOFTWARE_VERSION	<SOFTWARE_VERSION>
# DATETIME_START    <START_DATETIME>
# DATETIME_END      <END_DATETIME>
## END HEADER
```

### Metadata parameters

- `FILE`: The anticipated filename.
- `CREATED`: The date and time when the file was created.
- `NODE`: The unique identifier of the data collection device, such as ET0001.
- `LOCATION`: The geographical location of the data capture device represented as City, State/Region.
- `GPS_LOCATION`: The latitude and longitude ([WGS84](https://nsgreg.nga.mil/doc/view?i=4085)), along with the elevation measured in meters.
- `OPERATOR`: An identifier for the node operator. Could be a station callsign or a personal callsign.
- `CAPTURE_ID`: The identification code for a group of files that together form a single capture.
- `SOFTWARE_VERSION`: The version of the software used for the capture.
- `DATETIME_START`: The start time of the capture in seconds since the Unix Epoch (midnight, January 1, 1970).
- `DATETIME_END`: The end time of the capture in seconds since the Unix Epoch (midnight, January 1, 1970).

## Data section

Immediately following the header are lines of data, separated by a line feed `\n` (ASCII `0xA`).

### Data format
Each line will follow this format:
```
<GPS_TIME>,<GPS_LAT>,<GPS_LONG>,<GPS_ELEV>,<FLAGS>,<CHECKSUM>,[DATA...]\n
```

Certainly, here's a revised version:
- `GPS_TIME`: The number of seconds that have passed since the Unix Epoch (midnight, January 1, 1970) as a decimal value.
- `GPS_LAT`: The latitude expressed in decimal degrees.
- `GPS_LONG`: The longitude expressed in decimal degrees.
- `GPS_ELEV`: The elevation measured in meters.
- `FLAGS`: *To be determined (TODO)*
- `CHECKSUM`: The outcome of performing a bitwise XOR operation on each data point, resulting in a 16-bit number.


## Example file

*TODO*
