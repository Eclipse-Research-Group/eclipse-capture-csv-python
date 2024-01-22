import re
from datetime import datetime
from pytz import timezone
import numpy as np
import uuid
import os

class HeartbeatCaptureLine:
    def __init__(self, time: datetime, data):
        self.time = time
        self.data = data

    def generate_line(self) -> str:
        # data = (self.data * 512) + 512
        return "%f," % self.time.timestamp() + ",".join([str(x) for x in self.data])
    
    def to_array(self) -> np.ndarray: 
        return np.array(self.data)
    
    def has_gps_fix(self) -> bool:
        return self.flags.gps
    
    def is_clipping(self) -> bool:
        return self.flags.clipping


        
    
class HeartbeatCaptureLineFlags:
    def __init__(self, gps: bool, clipping: bool):
        self.gps = gps
        self.clipping = clipping
        pass

    def __repr__(self):
        return "HeartbeatCaptureLineFlags(%s, %s)" % (self.gps, self.clipping)
    
    def to_string(self):
        flags = ""
        if self.gps:
            flags += "G"
        if self.clipping:
            flags += "O"

        return flags

    def parse(text: str):
        return HeartbeatCaptureLineFlags(gps=(text.find("G") != -1), clipping=(text.find("O") != -1))
    
class HeartbeatCaptureFileInfo:

    METADATA_START = "## BEGIN METADATA ##"
    METADATA_END = "## END METADATA ##"
    PATTERN_METADATA_START = r"## BEGIN METADATA ##"
    PATTERN_METADATA_END = r"## END METADATA ##"
    PATTERN_METADATA = r"# ([A-Z_]+)\s+(.+)"
    PATTERN_FILENAME = r"(\d{8}_\d{6})-(\d{8}_\d{6})_(E[A-Z]\d{4})_([a-fA-F0-9]{8})"
    
    def __init__(self, start: datetime, 
                 end: datetime, 
                 capture_id: uuid.UUID,
                 node_id: str,
                 sample_rate: float):
        self.start = start
        self.end = end
        self.capture_id: uuid.UUID = capture_id
        self.node_id = node_id
        self.sample_rate = sample_rate
        pass

    def __repr__(self):
        return "HeartbeatCaptureFileInfo(%s, %s, %s, %s, %s)" % (self.start, self.end, self.capture_id, self.node_id, self.sample_rate)

    def validate(text: str):
        pass

    def filename(self) -> str:
        return "%s-%s_%s_%s.csv" % (self.start.strftime("%Y%m%d_%H%M%S"),
                                           self.end.strftime("%Y%m%d_%H%M%S"),
                                           self.node_id,
                                           self.capture_id.hex[:8])
    
    def parse_metadata(header_text: str):
        lines = header_text.splitlines()
        if not lines or len(lines) < 3:
            raise Exception("Invalid header")
        

        
        match = re.match(HeartbeatCaptureFileInfo.PATTERN_METADATA_START, lines.pop(0))
        if not match:
            raise Exception("Invalid header", lines[0])
        


        # Read each line
        metadata = {}

        while True:
            line = lines.pop(0)

            match = re.match(HeartbeatCaptureFileInfo.PATTERN_METADATA, line)
            
            if match:
                (key, value) = match.groups()
                metadata[key] = value
                continue

            if re.match(HeartbeatCaptureFileInfo.PATTERN_METADATA_END, line):
                break

            if match is None:
                raise Exception("Invalid header", line)

        if metadata["CAPTURE_ID"] is None:
            raise Exception("Missing CAPTURE_ID")
        
        if metadata["NODE_ID"] is None:
            raise Exception("Missing NODE_ID")

        if metadata["SAMPLE_RATE"] is None:
            raise Exception("Missing SAMPLE_RATE")
        
        if metadata["UTC_START"] is None:
            raise Exception("Missing UTC_START")
        
        if metadata["UTC_END"] is None:
            raise Exception("Missing UTC_END")
        
        start = datetime.fromtimestamp(float(metadata["UTC_START"]), tz=timezone("UTC"))
        end = datetime.fromtimestamp(float(metadata["UTC_END"]), tz=timezone("UTC"))
        capture_id = uuid.UUID(metadata["CAPTURE_ID"])
        node_id = metadata["NODE_ID"]
        sample_rate = float(metadata["SAMPLE_RATE"])

        return HeartbeatCaptureFileInfo(start, end, capture_id, node_id, sample_rate)

    def parse_filename(filename: str):
        match = re.match(HeartbeatCaptureFileInfo.PATTERN_FILENAME, filename)

        if not match:
            raise Exception("Invalid filename", filename)

        (start, end, node_id, capture_id) = match.groups()

        return (start, end, node_id, capture_id)

    def generate_header(self):
        header = HeartbeatCaptureFileInfo.METADATA_START + "\n"

        # Print mandatory fields
        header += "# FILE\t\t\t\t%s\n" % self.filename()
        header += "# CAPTURE_ID\t\t%s\n" % self.capture_id
        header += "# NODE_ID\t\t\t%s\n" % self.node_id
        header += "# SAMPLE_RATE\t\t%f\n" % self.sample_rate
        header += "# UTC_START\t\t\t%f\n" % self.start.timestamp()
        header += "# UTC_END\t\t\t%f\n" % self.end.timestamp()
        header += HeartbeatCaptureFileInfo.METADATA_END + "\n"

        header += "# This file was generated by heartbeat-capture-python\n"
        header += "# https://github.com/Heartbeat-Research-Group/heartbeat-capture-python\n"

        return header

class HeartbeatCaptureFile:

    def __init__(self, file_path: str, info: HeartbeatCaptureFileInfo):
        self.file_path = file_path
        self.info = info
        self.lines = []
        pass

    def load(file_path: str):
        print("Loading file %s" % file_path)

        with open(file_path, 'r') as f:
            header_text = ""

            while True:
                line = f.readline()
                if not line:
                    break

                if line.startswith("#"):
                    header_text += line
                    continue
            
                break

            header = HeartbeatCaptureFileInfo.parse_metadata(header_text)
            file = HeartbeatCaptureFile(file_path, header)

        return file
    
    def load_all_lines(self):
        self.lines = []
        with open(self.file_path, 'r') as f:
            while True:
                line = f.readline()

                if not line:
                    break

                if line.startswith("#"):
                    continue

                self.lines.append(HeartbeatCaptureLine.parse_line(line))




def parse_line(text: str) -> HeartbeatCaptureLine:
        parts = text.split(",")
        parts_time = float(parts[0])
        parts_flags = HeartbeatCaptureLineFlags.parse(parts[1])
        parts_sample_rate = float(parts[2])
        parts_lat = float(parts[3])
        parts_lon = float(parts[4])
        parts_elev = float(parts[5])
        parts_sats = int(parts[6])
        parts_speed = float(parts[7])
        parts_angle = float(parts[8])

        data = [int(x) for x in parts[9:]]

        capture_line = HeartbeatCaptureLine(datetime.utcfromtimestamp(parts_time), data)

        capture_line.flags = parts_flags
        capture_line.sample_rate = parts_sample_rate
        capture_line.lat = parts_lat
        capture_line.lon = parts_lon
        capture_line.elev = parts_elev
        capture_line.satellites = parts_sats
        capture_line.speed = parts_speed
        capture_line.angle = parts_angle

        return capture_line