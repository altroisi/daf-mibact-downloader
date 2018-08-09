import requests
import pandas as pd
import pysftp

def _to_csv(df, path, extraction_time, mode='a', header=True):
    """
    df: dataframe to write
    path: destination path
    mode: for csv can be 'a' -> append or 'w' -> write
    header: whether to write the column names
    """
    df['extraction_time'] = extraction_time
    # inserisco manualmente l'escape per il carattere '\' visto che nella costruzione del dataframe viene perso
    df = df.replace('\\\\', '\\\\\\\\', regex=True)
    df.to_csv(path, header=header, index=False, mode=mode, escapechar='\\', quotechar='"')

def _sftp_upload(sftp_host, sftp_user, sftp_key_file, localpath, remotepath):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True
    with pysftp.Connection( host=self._sftp_host, 
                            username=self._sftp_user, 
                            private_key=self._sftp_key_file, 
                            cnopts=cnopts) as sftp:
        folder, filename = os.path.split(localpath)
        rpath = remotepath.strip() + filename
        sftp.put(localpath=localpath, remotepath=rpath, preserve_mtime=False, confirm=True)
        logger.info('File uploaded to SFTP in {}'.format(rpath))

def _query_sparql_endpoint(outfilepath, where_body):
    sparql_endpoint = 'http://dati.beniculturali.it/sparql?default-graph-uri=&'

    # parametri per la paginazione
    limit = 10000
    offset = 0

    # select per le query
    select = 'select+*+'
    select_count = 'select+count(*)+as+%3Fc+'

    # formati della risposta
    format_json ='&format=application%2Fjson&timeout=0'
    format_csv ='&format=text%2Fcsv&timeout=0'

    # interrogazione per recuperare il numero di elementi
    query = 'query=' + select_count + where_body + format_json
    r = requests.get(sparql_endpoint + query)
    res_json = r.json()
    record_count = res_json.get('results').get('bindings')[0].get('c').get('value')
    print('Total number of records: ' + record_count)

    # scarico le singole pagine
    now = int(pd.Timestamp.timestamp(pd.Timestamp.now()))
    while offset < int(record_count):
        query = 'query=' + select + where_body + 'limit+' + str(limit) + '+offset+' + str(offset) + format_csv
        print('Fetching {} record with offset {}'.format(str(limit), str(offset)))
        df = pd.read_csv(sparql_endpoint + query, header=0)
        _to_csv(df, outfilepath, now, mode='a', header=(offset == 0))
        offset += limit