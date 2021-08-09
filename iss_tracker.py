import iss
from PIL import Image
from inky import InkyWHAT
from datetime import datetime, timedelta
import time

from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use("Pdf")
import matplotlib.pyplot as plt  # has to be BELOW use PDF line


# Filename for temporary map image
filename = "/home/pi/Downloads/globe.png"
retry_mins = 5  # update every x minutes

iss_sat = iss.ISS()
try:
    running = True
    while running:

        print("Get Date/Time")

        # Get current date/time
        date_now = datetime.now()
        date_utc_now = datetime.utcnow()

        # Calculate current ISS position
        lat, lon, alt = iss_sat.compute_iss_position(date_utc_now)

        # Calculate when the ISS will next be overhead
        next_pass_info = iss_sat.compute_iss_next_pass(date_utc_now)
        next_rise_time = next_pass_info[0]
        next_rize_azi = next_pass_info[1]
        next_peak_time = next_pass_info[2]
        next_peak_alt = next_pass_info[3]
        next_set_time = next_pass_info[4]
        next_set_azi = next_pass_info[5]


        print("Create map image")

        # Draw a globe centered about current ISS location
        map = Basemap(projection='ortho', lat_0=lat, lon_0=lon)
        map.drawmapboundary(fill_color='white')
        map.fillcontinents(color='grey', lake_color='white')
        map.drawcoastlines()

        # Plot lat/lon of ISS
        lons, lats = map([lon], [lat])
        map.scatter(lons, lats, marker='o', color='red', zorder=5)

        print("Compute previous ISS position points")

        # Compute previous and next locations (path) of ISS
        path_lats = []
        path_lons = []
        for x in range(-20, 25, 5):
            # Calculate ISS position at point on orbit
            path_date = datetime.utcnow() + timedelta(minutes=x)
            r_lat, r_lon, r_alt = iss_sat.compute_iss_position(path_date)
            # append location to path_list
            path_lats.append(r_lat)
            path_lons.append(r_lon)
        # Plot the path line
        lons, lats = map(path_lons, path_lats)
        map.plot(lons, lats, marker=None, color='magenta')

        # Annotate drawing
        ax = plt.gca()  # Get plot axis
        plt.text(
            -0.35,
            1.1,
            'ISS Location',
            horizontalalignment='left',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=24
        )

        plt.text(
            -0.35,
            1.0,
            'Alt: %4.1fdeg' % (alt),
            horizontalalignment='left',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=18)

        plt.text(
            1.35,
            1.1,
            date_now.strftime("%d/%m/%Y, %H:%M:%S"),
            horizontalalignment='right',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=18
        )

        plt.text(
            0.5,
            -0.1,
            "Next Pas: {}".format(next_rise_time.datetime().strftime("%d/%m/%Y, %H:%M:%S")),
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=18,
            color='red'
        )

        print("Export globe and ISS to temp image")

        # Export globe and ISS image to temp file
        plt.savefig(filename)
        plt.clf()

        print("Load temp image and display on e-ink display")
        print(filename)

        # Instantiate InkywHAT display and
        # load temp image from file and scale to 400x300
        inkywhat = InkyWHAT('red')
        img = Image.open(filename)
        w, h = img.size
        h_new = 300
        w_new = int((float(w) / h) * h_new)
        w_cropped = 400
        img = img.resize((w_new, h_new), resample=Image.LANCZOS)
        x0 = (w_new - w_cropped) / 2
        x1 = x0 + w_cropped
        y0 = 0
        y1 = h_new
        img = img.crop((x0, y0, x1, y1))

        print("Converting Image to 3 colour palette")

        # Convert image to 3 colour palette (W, B, R)
        pal_img = Image.new("P", (1, 1))
        pal_img.putpalette(
            (255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252
        )
        img = img.convert("RGB").quantize(palette=pal_img)

        print("Displaying image on Inky Display")

        # Display image on InkywHAT
        inkywhat.set_image(img)
        inkywhat.show()

        # Wait 5 minutes before looping again
        time.sleep(retry_mins * 60)

except Exception as e:
    print(e)
