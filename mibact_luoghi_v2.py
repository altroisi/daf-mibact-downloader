# script per python versione 2

import urllib
import urllib2
import time
import os
import json
import sys

print(sys.argv)
workfolder = sys.argv[1]
outfilepath = workfolder + '/mibact_luoghi_cultura_' + str(int(time.time())) + '.csv'
print('Querying MIBACT endpoint for "Luoghi della cultura" dataset')

sparql_endpoint = 'http://dati.beniculturali.it/sparql?default-graph-uri=&'

# parametri per la paginazione
limit = 10000
offset = 0

# select per le query
select = 'select+*+'
select_count = 'select+count(*)+as+%3Fc+'

# corpo della query
where = 'where+{+select+distinct+%3Fs+as+%3Fsubject+%3FNome_Istituzionale+%3FDescrizione+%3FDescription+%3FISILIdentifier+%3FLatitudine+%3FLongitudine+%3FDisciplina+%3FTipo_luogo+%3FIndirizzo+%3FCodice_postale+%3FComune+%3FProvincia+%3FPrenotazioni+%3FOrari_di_apertura+%3FTelefono+%3FFax+%3FEmail+%3FWebSite+str%28%3FBiglietti%29+as+%3FBiglietti+%3FServizi+where+%7B+graph+%3Chttp%3A%2F%2Fdati.beniculturali.it%2Fmibact%2Fluoghi%3E+%7B+%3Fs+rdf%3Atype+cis%3ACulturalInstituteOrSite+%3B+cis%3AinstitutionalName+%3FNome_Istituzionale+.+optional+%7B+%3Fs+cis%3Adescription+%3FDescrizione+.+filter%28lang%28%3FDescrizione%29+%3D+%22it%22+%7C%7C+lang%28%3FDescrizione%29+%3D+%22%22%29+%7D+optional+%7B+%3Fs+cis%3Adescription+%3FDescription+.+filter%28lang%28%3FDescription%29+%3D+%22en%22%29+%7D+optional+%7B+%3Fs+cis%3AISILIdentifier+%3FISILIdentifier+%7D+optional+%7B+%3Fs+geo%3Alat+%3FLatitudine+%7D+optional+%7B+%3Fs+geo%3Along+%3FLongitudine+%7D+optional+%7B+%3Fs+dc%3Atype+%3FTipo_luogo+%7D+optional+%7B+%3Fs+cis%3AhasDiscipline+%5Bcis%3Aname+%3FDisciplina%5D+%7D+optional+%7B+%3Fs+cis%3AhasSite+%5Bcis%3AhasAddress+%3Faddress+%5D+.+optional+%7B+%3Faddress+cis%3AfullAddress+%3FIndirizzo+%7D+optional+%7B+%3Faddress+cis%3ApostCode+%3FCodice_postale+%7D+optional+%7B+%3Faddress+cis%3ApostName+%3FComune+%7D+optional+%7B+%3Faddress+cis%3AadminUnitL2+%3FProvincia+%7D+%7D+optional+%7B%3Fs+cis%3AhasAccessCondition+%5Brdf%3Atype+cis%3ABooking+%3B+cis%3Aname+%3FPrenotazioni%5D+%7D+optional+%7B%3Fs+cis%3AhasAccessCondition+%5Brdf%3Atype+cis%3AOpeningHoursSpecification+%3B+cis%3Adescription+%3FOrari_di_apertura+%5D+%7D+optional+%7B+%3Fs+cis%3AhasContactPoint+%3FcontactPoint+.+optional+%7B+%3FcontactPoint+cis%3AhasTelephone+%3FTelefono+%7D+optional+%7B+%3FcontactPoint+cis%3AhasFax+%3FFax+%7D+optional+%7B+%3FcontactPoint+cis%3AhasEmail+%3FEmail+%7D+optional+%7B+%3FcontactPoint+cis%3AhasWebSite+%3FWebSite+%7D+%7D+optional+%7B+%3Fs+cis%3AhasTicket+%3Fticket+.+%3Foffer+cis%3Aincludes+%3Fticket+%3B+cis%3AhasPriceSpecification+%5Bcis%3AhasCurrencyValue+%3FBiglietti%5D+%7D+optional+%7B+%3Fs+cis%3AprovidesService+%5Bcis%3Aname+%3FServizi%5D+%7D+%7D+%7D+order+by+%3Fs+}'

# formati della risposta
format_json ='&format=application%2Fjson&timeout=0'
format_csv ='&format=text%2Fcsv&timeout=0'

# interrogazione per recuperare il numero di elementi
query = 'query=' + select_count + where + format_json
response = urllib2.urlopen(sparql_endpoint + query)
res = response.read()
res_json = json.loads(res.decode("utf-8"))
record_count = res_json.get('results').get('bindings')[0].get('c').get('value')
print('Total number of records: ' + record_count)

# scarico le singole pagine
tempfilenames = []
while offset < int(record_count):
    query = 'query=' + select + where + 'limit+' + str(limit) + '+offset+' + str(offset) + format_csv
    filename = outfilepath + '.' + str(offset)
    tempfilenames.append(filename)
    print('Fetching {} record with offset {} in {}'.format(str(limit), str(offset), filename))
    #TODO: gestire eccezioni
    local_filename, headers = urllib.urlretrieve(sparql_endpoint + query, filename)
    offset += limit

# recupero la riga di intestazione dal primo file per poterla aggiungere al file finale di output
header = ''
with open(tempfilenames[0], 'r') as f:
    header = f.readline()

# unisco i file in un unico csv, saltando la riga di intestazione
with open(outfilepath, 'a') as outfile:
    outfile.write(header)
    for filename in tempfilenames:
        with open(filename, 'r') as infile:
            next(infile)
            for line in infile:
                outfile.write(line)
print('Results collected in ' + outfilepath)

# cancello i file temporanei
print('Deleting temp files')
for filename in tempfilenames:
    os.remove(filename)
