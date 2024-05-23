### gcloud

~~~
gcloud init
gcloud compute instances list

gcloud compute ssh gmachine2 --zone=us-central1-a

Alternatively,
ssh -vvv gmachine2
ssh gmachine2
~~~

**To upload files onto the VM:**
>gcloud compute scp [local file path] [username]@[vm-name]:[remote file path]

For example:
> gcloud compute scp "C:\Users\johan\OneDrive\_Msc Data Science\big data\hadoop.pdf" johan@gmachine: --zone=us-central1-a


#### **Aside:** via putty and pscp
(This is not necessary as GCP's OS Login manages the keys)
ssh-keygen -t rsa -b 4096 -C "newkey"
notepad C:\Users\johan\.ssh\idd_rsa.pub


gcloud compute os-login ssh-keys add --key-file=C:\Users\johan/.ssh/id_rsa.pub --project=johannesvc

This was an issue. The solution:
>1. enable OS Login (project-wide):
>gcloud compute project-info add-metadata --metadata enable-oslogin=TRUE
>2. drop the pkk key file

**To upload files onto the VM with pscp:**
`pscp [local file path] [username]@[host]:[remote file path]`

For example:
>`pscp -i "C:\Users\johan\OneDrive\_Msc Data Science\big data\hadoop.pdf" yourhighnessjohannes_gmail_com@35.193.118.221:/`


#### **gcloud compute commands**
Stop ([see](https://cloud.google.com/compute/docs/instances/stop-start-instance))
>gcloud compute instances stop gmachine --zone=us-central1-a

Start
>gcloud compute instances start gmachine --zone=us-central1-a

Reset
>gcloud compute instances reset gmachine2 --zone=us-central1-a

gcloud compute project-info add-metadata --metadata serial-port-enable=TRUE

gcloud compute ssh gmachine2 --troubleshoot --zone=us-central1-a

To print out the necessary ssh flags :
gcloud compute ssh gmachine2 --zone=us-central1-a --dry-run


#### Set up a conda environment

To set up a lightweight [miniconda](https://docs.anaconda.com/free/miniconda/#quick-command-line-install) install check the linux tab.

https://console.cloud.google.com/security/iap/firewallconfigreview/gmachine?project=johannesvc

gcloud compute ssh gmachine2 --project=johannesvc --zone=us-central1-a --troubleshoot --tunnel-through-iap