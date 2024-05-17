### UNIX commands:

`ssh lena`

`ssh jcauw001@lena.doc.gold.ac.uk`

`cd`
`ls` show directories and files
`ls -l -a`: show detail (use: `-la`)
`mkdir`
`touch` make a file
`nano` open file (and write, save it)
`rm` *filename*: remove the file
`Ctrl + l` to clear

**To put data on the local filesystem of the masternode from CMD:**
`scp README.md lena:` 

**Similarly, to copy from lena to local:**
From CMD, run: `scp lena:./outputtopic31/part-00000 ./`

Or:
`scp lena:./dir/file "/C/Users/johan/Documents/GitHub/notebooks/MSc Data Science/big data"`

**To put a dir on the filesystem:**
`rsync [options] [src] [dest]` # can be ssh to ssh 

Specify `-e 'ssh'` if the source is an ssh host.

options: `-avz` is common.

For path syntax see [glob](https://en.wikipedia.org/wiki/Glob_%28programming%29): The most common wildcards are 
- `*` any number or any character, 
- `?` any character but just one, and 
- `[…]` eg. [a-z] one alphabetical character.

### Hadoop commands:
**[For list of commands see here](https://hadoop.apache.org/docs/r3.3.0/hadoop-project-dist/hadoop-common/FileSystemShell.html#moveFromLocal)** or just type `hadoop fs` and it will show all the commands.

`hadoop version`

`hdfs version` 

`hadoop fs -ls` lists files and directories
`hadoop fs -ls -R` lists files and directories recursively
`hadoop fs -mkdir Topic2`

**Copy files onto hadoop**
`hadoop fs -copyFromLocal [file to copy from masternode*] [location on hadoop]`
*note that you have to upload it first with scp

Example: `hadoop fs -copyFromLocal books.txt ./Topic2`

To inspect it (don't use -cd to get into a folder): `hadoop fs -ls ./Topic2`

Create a new file: `hadoop fs -touchz ./Topic2/data.txt`

**Copy files back from hadoop**
`hadoop fs -copyToLocal ./Topic2/data.txt /home/jcauw001`

**other**
`hadoop fs -ls *./example/abcd**`		Lists the files in example directory that matches the pattern abcd
`hadoop fs -du ./example`		Displays disk usage of all files in the directory
`hadoop fs -mv src dest`		Moves the file or directory from source to destination within HDFS
`hadoop fs -cp src dest`		Copies the file or directory from source to destination within HDFS
`hadoop fs -rm path`		Removes the file or empty directory
`hadoop fs -rm -r path`		Removes the file or directory (including child entries)
`hadoop fs -put localSrc dest`		Copies the file or directory from the local file system to the destination in HDFS
`hadoop fs -get [-crc] src localDest`		Copies the file or directory in HDFS to the local file system path represented by localDest

Notes:
Setup public key to get rid of passwords:
`type %USERPROFILE%\.ssh\id_rsa.pub | ssh jcauw001@lena.doc.gold.ac.uk "cat >> .ssh/authorized_keys"`
This pipes the public key created by `ssh-keygen` to the authorised_keys file. Note that I had to create the folders, file and permissions first.

### Topic 3
#### Unix commands
`echo a b d c b b` simply repeats it to stdout
`echo a b d c b b | python mapper.py` inputs string to pythons sys.stdin which then reads it
`echo a b d c b b | python mapper.py | sort | python reducer.py`

`cat books.txt | ./mapper.py | sort | ./reducer.py`
Note:
Check `ls -l mapper.py reducer.py` for permission.
Add execute permission: `chmod +x reducer.py` and `chmod +x mapper.py`

#### hadoop streaming
Since hadoop MapReduce is written in Java, we have to run Python in hadoop streaming. We then read and write from and to standard in and out.

We need the streaming jar file. A .jar file is a java script. 
Location: `/opt/hadoop/current/share/hadoop/tools/lib`

The hadoop command is as follows:
`hadoop jar /opt/hadoop/current/share/hadoop/tools/lib/hadoop-streaming-3.3.0.jar -file mapper.py -mapper mapper.py -file reducer.py -reducer reducer.py -input books.txt -output outputtopic3`

Note: 
- `-file mapper.py ` refers to the local filesystem (not on the cluster but on the local machine)
- The big data file, `books.txt` is on HDFS
  
  Or excecute from batch file - see mapreduce_script