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
Also works for folder:
`scp ./british-fiction-corpus/* lena:./docs`

**Similarly, to copy from lena to local:**
From CMD, run: `scp lena:./outputtopic31/part-00000 ./`

Or:
`scp lena:./dir/file "/C/Users/johan/Documents/GitHub/notebooks/MSc Data Science/big data"`

**To put a dir on the filesystem:**
`rsync [options] [src] [dest]` # can be ssh to ssh, but unclear why it doesn't work from CMD

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

### Topic 4: clustering

See [programming activity](https://learn.london.ac.uk/pluginfile.php/371923/mod_page/content/14/Topic4_ProgrammingActivity-151220.html)

In CMD:
`scp ./british-fiction-corpus/* lena:./docs`

In ssh lena:
```bash
mkdir ./docs
cd ./docs/
hadoop fs -copyFromLocal .
hadoop fs -ls ./docs
```
Create sequence files, then sparse vectors
```bash
mahout seqdirectory -i docs -o docs-seqfiles -c UTF-8 -chunk 5
mahout seq2sparse -nv -i docs-seqfiles -o docs-vectors
```

Initialise centroids:
```
mahout canopy \
  -i docs-vectors/tfidf-vectors \
  -ow -o docs-vectors/docs-canopy-centroids \
  -dm org.apache.mahout.common.distance.CosineDistanceMeasure \
  -t1 0.5 \
  -t2 0.3
```

More info [here](https://people.apache.org/~isabel/content/users/clustering/canopy-clustering.html)

Run the K-Means algorithm with Mahout:
```
mahout kmeans \
  -i docs-vectors/tfidf-vectors \
  -c docs-canopy-centroids \  # set of initial canopy centroids 
  -o hdfs://lena/user/jcauw001/docs-kmeans-clusters \
  -dm org.apache.mahout.common.distance.CosineDistanceMeasure \
  -cl \   # run input vector clustering after computing canopies
  -cd 0.1 \ # convergence threshold
  -ow \
  -x 20 \   # maxIter 
  -k 10     # numClusters
```    

To evaluate:
```
mahout clusterdump \
  -dt sequencefile \
  -d docs-vectors/dictionary.file-* \
  -i docs-kmeans-clusters/clusters-2-final \
  -o clusters.txt \
  -b 100 \      # format length
  -p docs-kmeans-clusters/clusteredPoints \ # points directory (the set of point ids and cluster id pairs)
  -n 20 \       # number of top terms to print
  
  # -dm org.apache.mahout.common.distance.CosineDistanceMeasure # default is euclidean distance!!

  --evaluate
```

`tail ./clusters.txt`

This gives:
CDbw Separation: 1.4637530057057427E7

On separation: Higher values of separation indicate better clustering quality, as it means that clusters are more distinct from each other with low density of points in between them.

More info: mahout clusterdump --help

#### More info on mahout.apache.org
[See here](https://mahout.apache.org/docs/0.13.0/api/docs/mahout-integration/org/apache/mahout/clustering/cdbw/CDbwEvaluator.html) for more on evaluation metrics. For distance metrics [see here](https://mahout.apache.org/docs/0.13.0/api/docs/mahout-mr/org/apache/mahout/common/distance/package-summary.html). Some more info on the commands, see this [cheat sheet](https://gist.github.com/zviri/7766943)


#### More on my metrics:
Inter-Cluster Density (Low is Good): Your value is 0.264, which is low, indicating good **separation**.
Intra-Cluster Density (High is Good): Your value is 0.536, which suggests moderate **cohesion** within clusters.
CDbw Inter-Cluster Density (Low is Good): Your value is 0.0, which is ideal.
CDbw Intra-Cluster Density (High is Good): Your value is 0.573, which indicates good cohesion within clusters.
CDbw Separation (High is Good): Your value is very high, indicating excellent separation between clusters.

Separation: Your clusters are well-separated (high CDbw separation value, low inter-cluster density).
Cohesion: There is moderate to good cohesion within clusters (intra-cluster density values).
CDbw Metrics: CDbw-specific metrics further confirm excellent separation and good internal cohesion.

## For CW, try:
`-dm org.apache.mahout.common.distance.TanimotoDistanceMeasure` (refer to [here](https://learning.oreilly.com/library/view/mahout-in-action/9781935182689/kindle_split_019.html#ch09)) (also for canopy)

**for canopy**: 
```
-dm org.apache.mahout.common.distance.EuclideanDistanceMeasure \
-t1 1500 -t2 2000
```
**for kmeans**: 
```
-dm org.apache.mahout.common.distance.TanimotoDistanceMeasure  \
-c reuters-canopy-centroids/clusters-0 -cd 0.1 -ow -x 20 -cl
```

**kmeans**: 
```
-dm org.apache.mahout.common.distance.SquaredEuclideanDistanceMeasure \
-cd 1.0 -k 20 -x 20 -cl
```
> A large value of convergenceThreshold (1.0), because we’re using the squared value of the Euclidean distance measure

**for k**:
> In the preceding example, where we have about a million news articles, if there are an average of 500 news articles published about every unique story, you should start your clustering with a k value of about 2,000 (1,000,000/500).
From [mahout in action](https://learning.oreilly.com/library/view/mahout-in-action/9781935182689/kindle_split_019.html#ch09) book.
