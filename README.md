# MIBACT Downloader 

## Abstract
Questo componente esegue lo scarico dei dati relativi ai **luoghi e agli eventi della cultura** interrogando lo SPARQL endpoint messo a disposizione dal MIBACT al link http://dati.beniculturali.it/sparql

Sono fornite di seguito le indicazioni per la costruzione dell'immagine Docker e l'avvio del container, e per il deploy su Kubernetes. Per la logica di scarico vedere [mibact.py](src/mibact/mibact.py)


## Docker

Per l'esecuzione sono necessarie le seguenti variabili d'ambiente, impostabili nel Dockerfile o passabili al lancio del container:
- `dataset` dataset da scaricare tra `luoghi` e `eventi`
- `sftp_host` host sftp del DAF sul quale caricare i dati
- `sftp_user` utente sftp che effettua il caricamento (deve essere stato abilitato dal DAF)
- `sftp_key_file` chiave privata per l'accesso a sftp (la chiave pubblica deve essere stata comunicata al DAF)
- `sftp_folder` cartella di destinazione del file su sftp

Dopo aver eventualmente modificato il [Dockerfile](app/mibact-downloader/docker/Dockerfile), costruire l'immagine docker posizionandosi nella root del progetto con il comando 

    sudo docker build -t mibact-downloader:0.0.1 -f app/mibact-downloader/docker/Dockerfile .


Il processo di build aggiunge le librerie python necessarie al funzionamento dell'applicazione ed elencate nel file [requirements.txt](app/mibact-downloader/docker/requirements.txt) oltre al codice python.

All'avvio del container fornire i mapping per i seguenti volumi:
- cartella dove è salvata la chiave privata per l'accesso sftp, referenziata dalla variabile d'ambiente `sftp_key_file` 
- `data` (opzionale) contenente i file temporanei prodotti per la raccolta dei dati fino al richiamo di tutte le pagine
- `logs` (opzionale) contenente i log prodotti (da implementare)


Se le variabili d'ambiente sono state impostate nel Dockerfile, lanciare il container docker con i soli mapping dei volumi (se desiderati)

    sudo docker run \
        -v /path/to/data:/opt/mibact-downloader/data \
        -v /path/to/logs:/opt/mibact-downloader/logs \
        mibact-downloader:0.0.1

Altrimenti, aggiungere nel comando le variabili necessarie:

    sudo docker run \
        -v /path/to/key:/opt/mibact-downloader/config/keys \
        -e "dataset=luoghi" \
        -e "sftp_host=daf.teamdigitale.it" \
        -e "sftp_user=pac_mibact_daf" \
        -e "sftp_key_file=./config/keys/pac_mibact_daf_key" \
        -e "sftp_folder=EDUC/luoghi/mibact_luoghi_della_cultura/" \
        mibact-downloader:0.0.1

## Kubernetes

La configurazione per il deploy dell'applicazione come CronJob è contenuta nei file 
- [mibact-luoghi.yaml](app/mibact-downloader/kubernetes/mibact-luoghi.yaml) per i luoghi
- [mibact-eventi.yaml](app/mibact-downloader/kubernetes/mibact-eventi.yaml)per gli eventi.

Controllare le configurazioni e lanciare i comandi:

    kubectl create -f ./app/mibact_downloader/kubernetes/mibact-luoghi.yaml
    kubectl create -f ./app/mibact_downloader/kubernetes/mibact-eventi.yaml