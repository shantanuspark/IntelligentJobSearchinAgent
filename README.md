# Intelligent Job Searching Agent
An intelligent agent built using python to scrape data from the job websites and finding closest matched job for the search key using tf-idf vectorization and KNN algorithm. Furthermore, using Llyod's algorithm to cluster the jobs.

Steps to run the program:
Run the python file ‘shantanu_deshmukh_career_job.py’, it will open an intuitive command line user interface as below:
<img scr="https://github.com/shantanuspark/IntelligentJobSearchinAgent/blob/master/input.png" />

Enter appropriate values for each option.
First option asks for the search key word.
Second option is the value of k or the no. of results to be displayed on the results page.
Third option asks for the advanced options, if user says no here only kNN algorithm will be applied and top k results will be displayed. 
Fourth and fifth options are for the clustering mode, it sets the no. of clusters. Note that no. of clusters should be less then the value of k. The program will alert the user if wrong value is entered.
Sixth option is about scraping, how deep or till what page in the result should the agent go so as to pull in the data. Having higher value will fetch more data but slow down the agent.
Last option is to clear up the lookup table(cache).

Output of the program looks is as below:
<img src="https://github.com/shantanuspark/IntelligentJobSearchinAgent/blob/master/output.png" />

Features implemented in the program:<ul><li>
•	String documents represented as tf-idf vectors</li><li>
•	Llyod’s algorithm used to group similar jobs</li><li>
•	Distance calculations done using cosine distance</li><li>
•	Command-line user interface</li><li>
•	Lookup/cache table used so as to avoid scraping the data on each search</li><li>
•	Only External library used is BeautifulSoup</li><li>
•	kNN algorithm used to find nearest matches</li><li>
•	Persisting the table on every run, so that the table is prebuilt in next iterations</li><li>
•	Timestamp protection to avoid stale data in the prebuilt table</li><li>
•	Output of the program is in HTML</li>
</ul>
