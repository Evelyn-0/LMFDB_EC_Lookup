import json
import requests
# List of collections and properties can be found at https://www.lmfdb.org/api/
# LMFDB collection to choose from
api_base = 'https://www.lmfdb.org/api/ec_nfcurves/'
# properties to filter the data by as key=value pairs seperated by &
api_query = '?field_label=2.2.5.1'
# language to output data for
format = 'sage'  # only sage and magma supported
limit = 10000  # API limit for LMFDB
# list of keys to grab with each entry
curve_data = ['short_label', 'ainvs', 'torsion_structure', 'torsion_primes', 'torsion_order', 'semistable', 'signature', 'q_curve',
              'potential_good_reduction', 'bad_primes', 'base_change', 'cm', 'class_deg', 'conductor_norm', 'galois_images', 'isodeg', 'jinv']

api_url = api_base + api_query + '&_format=json&_offset='


def magmaize(line):
    '''This is a helper function to make a regular nested list into a magma list'''
    new_list = ''
    for n in line:
        if n == '[':
            new_list = new_list + n + '*'
        elif n == ']':
            new_list = new_list + '*' + n
        else:
            new_list = new_list + n
    return new_list


def write_data(properties, format, file):
    '''Grabs the data requested and writes it to the file in the given format'''
    for n in range(limit):
        # API returns max 100 items at a time, so need to grab new data every 100 entries
        if (n % 100 == 0):
            next_request = api_url + str(n)
            response = requests.get(next_request)
            data = json.loads(json.dumps(response.json()))
            print(n, '/', limit)
        # this if statement avoids crashes due to end of entries
        if n % 100 < len(data['data']):
            curve = data['data'][n % 100]
            if format == 'sage':
                to_write = {}
                for d in properties:
                    # special case for ainvs, reformats as list of 2 element lists,
                    # you need to remove this conditional if you plan to query over any collection other than ec_nfcurves
                    if d == 'ainvs':
                        h = [i.split(',') for i in curve[d].split(';')]
                        to_write['ainvs'] = [[int(j) for j in i] for i in h]
                    else:
                        to_write[d] = curve[d]
                file.write(str(to_write) + ',\n')
            elif format == 'magma':
                to_write = []
                for d in curve_data:
                    # special case for ainvs, reformats as list of 2 element lists,
                    # you need to remove this conditional if you plan to query over any collection other than ec_nfcurves
                    if d == 'ainvs':
                        h = [i.split(',') for i in curve[d].split(';')]
                        to_write.append([[int(j) for j in i] for i in h])
                    else:
                        to_write.append(curve[d])
                file.write(magmaize(str(to_write)) + ',\n')


if format == 'sage':
    f = open('elliptic_curves.sage', 'w')
    f.write('R.<x> = QQ[];\n')
    f.write('data = [\n')

elif format == 'magma':
    f = open('elliptic_curves.m', 'w')
    f.write('P<x> := PolynomialRing(Rationals());\n')
    f.write('data := [*\n')

write_data(curve_data, format, f)

f.write('*' if format == 'magma' else '')
f.write(']')
f.close()
