import requests
import pandas as pd
import pysftp
import time
import os
import argparse

from utils import _query_sparql_endpoint, _sftp_upload

# gestione argomenti a riga di comando
parser = argparse.ArgumentParser(description='Process MIBACT dataset')
parser.add_argument('--dest_folder',
                    help='destination folder for downloaded data',
                    default='./data',
                    required=False)
parser.add_argument('--dataset',
                    help='dataset to download',
                    choices=['luoghi','eventi'],
                    required=True)
args = parser.parse_args()

outfilepath = '{}/mibact_{}_cultura_{}.csv'.format(args.dest_folder, args.dataset, str(int(time.time())))

# corpo della query
if args.dataset == 'luoghi':
    query_where_body = 'where+{+select+distinct+%3Fs+as+%3Fsubject+%3FNome_Istituzionale+%3FDescrizione+%3FDescription+%3FISILIdentifier+%3FLatitudine+%3FLongitudine+%3FDisciplina+%3FTipo_luogo+%3FIndirizzo+%3FCodice_postale+%3FComune+%3FProvincia+%3FPrenotazioni+%3FOrari_di_apertura+%3FTelefono+%3FFax+%3FEmail+%3FWebSite+str%28%3FBiglietti%29+as+%3FBiglietti+%3FServizi+where+%7B+graph+%3Chttp%3A%2F%2Fdati.beniculturali.it%2Fmibact%2Fluoghi%3E+%7B+%3Fs+rdf%3Atype+cis%3ACulturalInstituteOrSite+%3B+cis%3AinstitutionalName+%3FNome_Istituzionale+.+optional+%7B+%3Fs+cis%3Adescription+%3FDescrizione+.+filter%28lang%28%3FDescrizione%29+%3D+%22it%22+%7C%7C+lang%28%3FDescrizione%29+%3D+%22%22%29+%7D+optional+%7B+%3Fs+cis%3Adescription+%3FDescription+.+filter%28lang%28%3FDescription%29+%3D+%22en%22%29+%7D+optional+%7B+%3Fs+cis%3AISILIdentifier+%3FISILIdentifier+%7D+optional+%7B+%3Fs+geo%3Alat+%3FLatitudine+%7D+optional+%7B+%3Fs+geo%3Along+%3FLongitudine+%7D+optional+%7B+%3Fs+dc%3Atype+%3FTipo_luogo+%7D+optional+%7B+%3Fs+cis%3AhasDiscipline+%5Bcis%3Aname+%3FDisciplina%5D+%7D+optional+%7B+%3Fs+cis%3AhasSite+%5Bcis%3AhasAddress+%3Faddress+%5D+.+optional+%7B+%3Faddress+cis%3AfullAddress+%3FIndirizzo+%7D+optional+%7B+%3Faddress+cis%3ApostCode+%3FCodice_postale+%7D+optional+%7B+%3Faddress+cis%3ApostName+%3FComune+%7D+optional+%7B+%3Faddress+cis%3AadminUnitL2+%3FProvincia+%7D+%7D+optional+%7B%3Fs+cis%3AhasAccessCondition+%5Brdf%3Atype+cis%3ABooking+%3B+cis%3Aname+%3FPrenotazioni%5D+%7D+optional+%7B%3Fs+cis%3AhasAccessCondition+%5Brdf%3Atype+cis%3AOpeningHoursSpecification+%3B+cis%3Adescription+%3FOrari_di_apertura+%5D+%7D+optional+%7B+%3Fs+cis%3AhasContactPoint+%3FcontactPoint+.+optional+%7B+%3FcontactPoint+cis%3AhasTelephone+%3FTelefono+%7D+optional+%7B+%3FcontactPoint+cis%3AhasFax+%3FFax+%7D+optional+%7B+%3FcontactPoint+cis%3AhasEmail+%3FEmail+%7D+optional+%7B+%3FcontactPoint+cis%3AhasWebSite+%3FWebSite+%7D+%7D+optional+%7B+%3Fs+cis%3AhasTicket+%3Fticket+.+%3Foffer+cis%3Aincludes+%3Fticket+%3B+cis%3AhasPriceSpecification+%5Bcis%3AhasCurrencyValue+%3FBiglietti%5D+%7D+optional+%7B+%3Fs+cis%3AprovidesService+%5Bcis%3Aname+%3FServizi%5D+%7D+%7D+%7D+order+by+%3Fs+}'
else:
    query_where_body = 'where+{+select+distinct++%3Fs+AS+%3Fevento_uri+%3Fevento_id+%3Fnome+%3Fdescrizione+%3Flatitudine+%3Flongitudine+%3Ftipo_evento+%3Fprenotazione+%3Fcopertina_url+%3Flocandina_url+%3Fcomunicato_stampa_url+%3Fcontact_point_tipo+%3Fcontact_point_telefono+%3Fcontact_point_fax+%3Fcontact_point_email+%3Fcontact_point_website+%3Fcontact_point_orari+%3Fsede_indirizzo+%3Fsede_cap+%3Fsede_comune++%3Fsede_provincia+%3Fdata_inizio+%3Fdata_fine+%3Fraffigurazione_url+%3Ftipo_biglietto+%3Fimporto_biglietto+FROM+<http%3A%2F%2Fdati.beniculturali.it%2Fmibact%2Feventi>+FROM+<http%3A%2F%2Fdati.beniculturali.it%2Fmibact%2Fluoghi>+WHERE+{+%3Fs+rdf%3Atype+cis%3AEvent+.+OPTIONAL+{+%3Fs+cis%3Aidentifier+%3Fevento_id+}+OPTIONAL+{+%3Fs+cis%3Aname+%3Fnome}+OPTIONAL+{+%3Fs+rdfs%3Acomment+%3Fdescrizione}+OPTIONAL+{+%3Fs+geo%3Alat+%3Flatitudine+}+OPTIONAL+{+%3Fs+geo%3Along+%3Flongitudine+}+OPTIONAL+{+%3Fs+dc%3Atype+%3Ftipo_evento}+OPTIONAL+{+%3Fs+cis%3AhasAccessCondition+[+rdf%3Atype+cis%3ABooking+%3B++rdfs%3Alabel+%3Fprenotazione+]++}+OPTIONAL+{+%3Fs+cis%3AisSubjectOf+%3FcreativeWork+.++OPTIONAL+{+%3FcreativeWork+rdfs%3Alabel+%3FCreativeWorkLabel+}++OPTIONAL+{+%3FcreativeWork+cis%3Aurl+%3Fcopertina_url+}++FILTER(REGEX(%3FCreativeWorkLabel%2C\'Copertina\'%2C\'i\'))+}+OPTIONAL+{+%3Fs+cis%3AisSubjectOf+%3FcreativeWork2+.++OPTIONAL+{+%3FcreativeWork2+rdfs%3Alabel+%3FCreativeWorkLabel2+}++OPTIONAL+{+%3FcreativeWork2+cis%3Aurl+%3Flocandina_url+}++FILTER(REGEX(%3FCreativeWorkLabel2%2C\'Locandina\'%2C\'i\'))+}+OPTIONAL+{+%3Fs+cis%3AisSubjectOf+%3FcreativeWork3+.++OPTIONAL+{+%3FcreativeWork3+rdfs%3Alabel+%3FCreativeWorkLabel3+}++OPTIONAL+{+%3FcreativeWork3+cis%3Aurl+%3Fcomunicato_stampa_url+}++FILTER(REGEX(%3FCreativeWorkLabel3%2C\'Comunicato+stampa\'%2C\'i\'))+}+OPTIONAL+{+%3Fs+cis%3AhasContactPoint+%3FcontactPoint+.+OPTIONAL+{+%3FcontactPoint+rdfs%3Alabel+%3Fcontact_point_tipo+}+OPTIONAL+{+%3FcontactPoint+cis%3AhasTelephone+%3Fcontact_point_telefono+}+OPTIONAL+{+%3FcontactPoint+cis%3AhasFax+%3Fcontact_point_fax+}+OPTIONAL+{+%3FcontactPoint+cis%3AhasEmail+%3Fcontact_point_email+}+OPTIONAL+{+%3FcontactPoint+cis%3AhasWebSite+%3Fcontact_point_website+}+OPTIONAL+{++%3FcontactPoint+cis%3Aavailable+%3Favailable+.+OPTIONAL+{+%3Favailable+cis%3Adescription+%3Fcontact_point_orari+}+}+}+OPTIONAL+{+%3Fs+cis%3AisHostedBy+%3Fhost+.+OPTIONAL+{+%3Fhost+cis%3AhasAddress+%3Faddress+.+%3Faddress+rdfs%3Alabel+%3Faddress_label+.+OPTIONAL+{+%3Faddress+cis%3AfullAddress+%3Fsede_indirizzo+}+OPTIONAL+{+%3Faddress+cis%3ApostCode+%3Fsede_cap+}++OPTIONAL+{+%3Faddress+cis%3ApostName+%3Fsede_comune+}++OPTIONAL+{+%3Faddress+cis%3AadminUnitL2+%3Fsede_provincia+}+}+}+OPTIONAL+{+%3Fs+cis%3AtakesPlaceDuring+%3FtakesPlaceDuring+.+OPTIONAL+{+%3FtakesPlaceDuring+cis%3AstartDate+%3Fdata_inizio+}+OPTIONAL+{+%3FtakesPlaceDuring+cis%3AendDate+%3Fdata_fine}+}+OPTIONAL+{+%3Fs+foaf%3Adepiction+%3Fraffigurazione_url}+OPTIONAL+{++%3Fs+cis%3AhasTicket+%3Fticket+.++%3Foffer+cis%3Aincludes+%3Fticket+.+%3Foffer+rdfs%3Alabel+%3Ftipo_biglietto+.+%3Foffer+cis%3AhasPriceSpecification+%3FpriceSpec+.+%3FpriceSpec+cis%3AhasCurrencyValue+%3Fimporto_biglietto+}}+ORDER+BY+%3Fs}'

print('Querying MIBACT endpoint for dataset {}'.format(args.dataset))
_query_sparql_endpoint(outfilepath, query_where_body)

# carico su SFTP
sftp_host = os.environ['sftp_host']
sftp_user = os.environ['sftp_user']
sftp_key_file = os.environ['sftp_key_file']
sftp_folder = os.environ['sftp_folder']
_sftp_upload(sftp_host, sftp_user, sftp_key_file, outfilepath, sftp_folder)

# cancello il file locale
os.remove(outfilepath)
