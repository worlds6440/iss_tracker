
import ephem
from ephem import degree
import urllib2
import math


class ISS:

    # default constructor
    def __init__(self):
        """ Default TLE (Two Line Entry) for ISS """
        self.name = "ISS (ZARYA)"
        self.line1 = "1 25544U 98067A   19339.68821539  .00001078  00000-0  26837-4 0  9993"
        self.line2 = "2 25544  51.6433 231.0438 0006897   3.7494  54.5315 15.50092821201865"
        self.degrees_per_radian = 180.0 / math.pi
        self.iss = None
        self.observer = None
        self.last_checked_date = None
        self.next_pass_date = None
        self.next_pass_info = None
        self.last_tle_update = None

        # Get latest TLE info on construction
        self.update_iss_tle()

    def update_iss_tle(self):
        """ Download uptodate TLE TXT file """
        try:
            date_now = datetime.now()
            if self.last_tle_update is None or self.last_tle_update.day() != date_now.day:
                # Only update once a day
                self.last_tle_update = date_now

                response = urllib2.urlopen(
                    'http://www.celestrak.com/NORAD/elements/stations.txt')
                tle_txt = response.read()  # Read online file into string variable
                tle_list = tle_txt.split('\n')  # split the file into list of lines

                # Find list index which has ZARYA in the name
                indices = [i for i, s in enumerate(tle_list) if 'ZARYA' in s]

                # If we found it, update the initial default ISS TLE strings
                if len(indices) and len(tle_list) > (indices[0]+2):
                    self.name = tle_list[indices[0]]
                    self.line1 = tle_list[indices[0]+1]
                    self.line2 = tle_list[indices[0]+2]
        except:
            pass

    def get_observer(self, date):
        """ Return the current observer,
            or create one if needs be """
        if self.observer is None:
            self.observer = ephem.Observer()

            # Set observers lat/lon/elevation location
            self.observer.lon = '-0.195639'
            self.observer.lat = '52.084596'
            self.observer.elevation = 52

        # Set/update the observers current datetime.
        self.observer.date = date

        return self.observer

    def get_iss(self):
        if self.iss is None:
            self.iss = ephem.readtle(self.name, self.line1, self.line2)

        return self.iss

    def compute_iss_position(self, date):
        """ Compute current location of ISS NOW """

        # Ensure we have the latest TLE information
        # Note: will only check online once a day
        self.update_iss_tle()

        # Compute location based on updated varaibles
        self.get_iss().compute(self.get_observer(date))

        # Convert to decimal Lat/Lon
        lat = self.get_iss().sublat / degree
        lon = self.get_iss().sublong / degree
        alt = self.get_iss().alt * self.degrees_per_radian

        # Update the date when we last checked
        self.last_checked_date = date

        return lat, lon, alt

    def compute_iss_next_pass(self, date):
        """ Compute current location of ISS NOW
            Only calculate IF we actually need too. """
        if self.next_pass_date is None or date > self.next_pass_date:

            # Ensure we have the latest TLE information
            # Note: will only check online once a day
            self.update_iss_tle()

            # Calculate next pass the ISS will make over Observer location
            self.next_pass_info = self.get_observer(date).next_pass(self.get_iss())

        # 0  Rise time
        # 1  Rise azimuth
        # 2  Maximum altitude time
        # 3  Maximum altitude
        # 4  Set time
        # 5  Set azimuth
        return self.next_pass_info

