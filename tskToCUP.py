
import xmltodict as xd
from pathlib import Path
from bs4 import BeautifulSoup
import math

def main():

    directory = r'C:\input\tskfiles'
    files = Path(directory).rglob('*.tsk')

    dir_out = r'C:\output\tsk_to_cup\cup'
    suffix = ".cup"

    if not Path(dir_out).is_dir():
        print("Out directory does not exist")
        exit()

    if not Path(directory).is_dir():
        print("Input files does not exist")
        exit()


    for file in files:
        filename = file.name

        # read input file
        with open(file, "r", encoding="latin-1") as f:
            data = f.read()
            Bs_data = BeautifulSoup(data, "xml")
            b_points = Bs_data.find_all('Point', {'type': 'Turn'})
            b_start = Bs_data.find('Point', {'type': 'Start'})
            b_finish = Bs_data.find('Point', {'type': 'Finish'})

            points = []
            point_text = []

            doc = xd.parse(b_start.prettify())
            point_text.append(doc['Point']['Waypoint']['@name'])
            lat = float(doc['Point']['Waypoint']['Location']['@latitude'])
            point_text.append(deg_to_dm(lat,"lat"))
            lon = float(doc['Point']['Waypoint']['Location']['@longitude'])
            point_text.append(deg_to_dm(lon,"lon"))
            point_text.append(doc['Point']['Waypoint']['@altitude'])
            point_text.append(doc['Point']['@type'])
            points.append(point_text)

            for idx, point in enumerate(b_points):
                point_text = []
                doc = xd.parse(b_points[idx].prettify())
                point_text.append(doc['Point']['Waypoint']['@name'])
                lat = float(doc['Point']['Waypoint']['Location']['@latitude'])
                point_text.append(deg_to_dm(lat, "lat"))
                lon = float(doc['Point']['Waypoint']['Location']['@longitude'])
                point_text.append(deg_to_dm(lon, "lon"))
                point_text.append(doc['Point']['Waypoint']['@altitude'])
                point_text.append(doc['Point']['@type'])
                points.append(point_text)

            point_text = []

            doc = xd.parse(b_finish.prettify())
            point_text.append(doc['Point']['Waypoint']['@name'])
            lat = float(doc['Point']['Waypoint']['Location']['@latitude'])
            point_text.append(deg_to_dm(lat,"lat"))
            lon = float(doc['Point']['Waypoint']['Location']['@longitude'])
            point_text.append(deg_to_dm(lon,"lon"))
            point_text.append(doc['Point']['Waypoint']['@altitude'])
            point_text.append(doc['Point']['@type'])
            points.append(point_text)
            f.close()

        out_text = "name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\n"
        for point in points:
            value = "\"{}\",,,{},{},{}m,1,,,,\n".format(point[0],point[1],point[2],point[3])
            out_text = out_text + value

        out_text = out_text + "-----Related Tasks-----\n"
        line_text = []
        line_text.append(filename.rstrip('.tsk'))
        line_text.append(points[0][0])
        for point in points:
            line_text.append(point[0])
        line_text.append(points[len(points)-1][0])
        value = ""
        for text in line_text:
            value = value + "\"{}\",".format(text)
        out_text = out_text + value.rstrip(',') + "\n"
        # value = "Options,TaskTime=09:00:00,WpDis=True,MinDis=True,RandomOrder=False,MaxPts=13\n"
        value = "Options,WpDis=True\n"
        out_text = out_text + value

        for idx, point in enumerate(points):
            if point[4] == "Start":
                value = "ObsZone={},Style=2,R1=3000m,A1=180,Line=1\n".format(idx)
            if point[4] == "Turn":
                value = "ObsZone={},Style=1,R1=500m,A1=180\n".format(idx)
            if point[4] == "Finish":
                value = "ObsZone={},Style=3,R1=500m,Line=1\n".format(idx)
            out_text = out_text + value

        # write to file
        base_filename = file.name.rstrip(".tsk")
        out_file = (Path(dir_out, base_filename).with_suffix(suffix))
        with open(out_file, "w") as f_out:
            f_out.write(out_text)
            f_out.close()

def deg_to_dm(deg, type):
    decimals, number = math.modf(deg)
    d = int(number)
    # m = int(decimals * 60)
    m = round(decimals * 60,3)
    # s = (deg - d - m / 60) * 3600.00
    compass = {
        'lat': ('N','S'),
        'lon': ('E','W')
    }
    compass_str = compass[type][0 if d >= 0 else 1]
    if type == "lat":
        text= "{}{}{}".format(abs(d), f'{m:06.3f}', compass_str)
        # print("{}{}{} -- {}".format(abs(d), f'{m:06.3f}', compass_str, text))
    if type == "lon":
        text= "0{}{}{}".format(abs(d), f'{m:06.3f}', compass_str)
        # print("0{}{}{} -- {}".format(abs(d), f'{m:06.3f}', compass_str, text))
        # print("0{} + {} -> {} -- {}".format(d, m, f'{m:06.3f}', text))
    return text


if __name__ == '__main__':
    main()
