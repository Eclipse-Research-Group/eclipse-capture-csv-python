import re
from datetime import datetime
from pytz import timezone
import uuid

class EclipseCapture:

    def __init__(self):
        pass

    def hello_world(self):
        return "Hello World!"
    
class EclipseCaptureLine:
    def __init__(self, time, data):
        self.time = time
        self.data = data

    def generate_line(self) -> str:
        return "%f," % self.time + ",".join([str(x) for x in self.data])
    
class EclipseCaptureFileInfo:
    
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

    def validate(text: str):
        pass

    def filename(self) -> str:
        return "%s-%s_%s_%s.csv" % (self.start.strftime("%Y%m%d_%H%M%S"),
                                           self.end.strftime("%Y%m%d_%H%M%S"),
                                           self.node_id,
                                           self.capture_id.hex[:8])
    
    def parse_header(self, text: str):
        pass

    def generate_header(self):
        header = "## BEGIN HEADER ##\n"

        # Print mandatory fields
        header += "# FILE\t\t\t\t%s\n" % self.filename()
        header += "# CAPTURE_ID\t\t%s\n" % self.capture_id
        header += "# NODE_ID\t\t\t%s\n" % self.node_id
        header += "# SAMPLE_RATE\t\t%d\n" % self.sample_rate
        header += "# UTC_START\t\t\t%d\n" % self.start.timestamp()
        header += "# UTC_END\t\t\t%d\n" % self.end.timestamp()
        header += "## END HEADER ##\n"

        return header

class EclipseCaptureFile:

    PATTERN_HEADER_START = r"## BEGIN HEADER ##"
    PATTERN_HEADER_END = r"## END HEADER ##"
    PATTERN_METADATA = r"# ([A-Z_]+)\s+(.+)"

    def __init__(self, file_path: str):
        self.file_path = file_path

        print("Loading file %s" % self.file_path)

        found_header = False
        found_header_end = False

        with open(self.file_path, 'r') as f:
            while True:
                line = f.readline()

                match = re.match(EclipseCaptureFile.PATTERN_HEADER_START, line)

                if match:
                    # We found the header
                    found_header = True
                    break

                if not line:
                    break

            pass
            
            if not found_header:
                raise Exception("No header found")
            
            # Parse header here

            found_metadata = {}

            while True:
                line = f.readline()

                match = re.match(EclipseCaptureFile.PATTERN_HEADER_END, line)

                if match:
                    # We found the end of the header
                    found_header_end = True
                    break

                match = re.match(EclipseCaptureFile.PATTERN_METADATA, line)

                if not match:
                    raise Exception("Invalid header")

                key, value = match.groups()

                found_metadata[key] = value

            if found_metadata["FILE"] is None:
                raise Exception("Invalid header: Missing mandatory field FILE")

            if found_metadata["UTC_START"] is None:
                raise Exception("Invalid header: Missing mandatory field UTC_START")

            if found_metadata["UTC_END'"] is None:
                raise Exception("Invalid header: Missing mandatory field UTC_END'")


            self.ideal_filename = found_metadata["FILE"]
            self.capture_id = found_metadata["CAPTURE_ID"]
            self.location = found_metadata["LOCATION"]
            self.gps_location = found_metadata["GPS_LOCATION"].split(",")
            self.start_time = datetime.fromtimestamp(float(found_metadata["UTC_START"]), tz=timezone("UTC"))
            self.end_time = datetime.fromtimestamp(float(found_metadata["UTC_END'"]), tz=timezone("UTC"))


        pass

def capture_file(file_path):
    return EclipseCaptureFile(file_path)