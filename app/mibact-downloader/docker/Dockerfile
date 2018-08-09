FROM python:3.6

LABEL version="0.0.1"

COPY app/mibact-downloader/docker/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src /opt/mibact-downloader/src

WORKDIR /opt/mibact-downloader

RUN mkdir data
RUN mkdir logs

# da decommentare per l'esecuzione in locale
#COPY vaulted_data/ssh_keys/pac_mibact_daf_key /opt/mibact-downloader/config/keys/pac_mibact_daf_key
#ENV sftp_host daf.teamdigitale.it
#ENV sftp_user pac_mibact_daf
#ENV sftp_key_file ./config/keys/pac_mibact_daf_key
#ENV sftp_folder EDUC/luoghi/mibact_luoghi_della_cultura/

CMD python ./src/mibact/mibact.py --dataset ${dataset}