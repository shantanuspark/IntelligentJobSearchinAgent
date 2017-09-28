'''
Created on Sep 21, 2017

@author: Shantanu Deshmukh

'''

# For safe imports
libnames = ['urllib2', 'bs4', 'time', 'threading', 're', 'math', 'operator', 'os', 'webbrowser', 'string', 'pickle', 'random']
terminate = False
for libname in libnames:
    try:
        lib = __import__(libname)
    except:
        print 'Module '+libname+' not found. Please install it and re-run the program.\n'
        terminate = True
    else:
        globals()[libname] = lib

if terminate:
    exit()
    
BeautifulSoup = bs4.BeautifulSoup
randint = random.randint


'''
Threaded web scrapper class to fetch jobs from IEEE, acm and indeed, parallelly
'''
class fetchJobs (threading.Thread):
    def __init__(self, name, url, searchKey, grabDataTillResultPage):
        threading.Thread.__init__(self)
        self.urlsConstant = url
        self.name = name
        self.searchKey = searchKey
        self.grabDataTillResultPage = grabDataTillResultPage
    def run(self):
        
        if self.name == "ieee":
            '''
            Fetching dataRows from ieee
            '''
            ieeeurl = self.urlsConstant["ieee"].replace("<searchKey>",self.searchKey)
            print "\nFetching jobs from IEEE..."
            ieeepage = urllib2.urlopen(ieeeurl)
            ieeesoup = BeautifulSoup(ieeepage, 'html.parser')
            totalPage = ieeesoup.find("span",{"class":"aiPageTotalTop"})
            pagination = False
            if(totalPage):
                totalPage = int(totalPage.get_text())
                pagination = True
            for job in ieeesoup.find_all("div",{"id":"aiDevHighlightBoldFontSection"}):
                row = {}
                row["title"]=cleanText(job.a.get_text())
                row["url"]="http://jobs.ieee.org"+job.a['href']
                row["desc"] = cleanText(job.find("div",{"class":"aiResultsMainDiv"}).find_all("div")[-1].get_text())
                dataRows.append(row)
            '''
            If more then one page found in results, get records till grapDataTillResultPage 
            '''
            if pagination:
                maxIteration = 1
                if totalPage > self.grabDataTillResultPage:
                    maxIteration = self.grabDataTillResultPage
                else:
                    maxIteration = totalPage
                for i in range(2,maxIteration+1):
                    ieeeInnerPage = self.urlsConstant["ieeePagination"].replace("<searchKey>",self.searchKey).replace("<pagenumber>",repr(i))
                    ifpj = fetchPaginationJobs(None,ieeeInnerPage,None)
                    ifpj.start()
                    childThreads.append(ifpj)
                    
        if self.name == "acm":
            '''
            Fetching dataRows from ACM
            '''
            acmurl = self.urlsConstant["acm"].replace("<searchKey>",self.searchKey);
            print "\nFetching jobs from ACM..."
            page = urllib2.urlopen(acmurl)
            soup = BeautifulSoup(page, 'html.parser')
            totalPage = soup.find("span",{"class":"aiPageTotalTop"})
            pagination = False
            if(totalPage):
                totalPage = int(totalPage.get_text())
                pagination = True
            for job in soup.find_all("div",{"id":"aiDevHighlightBoldFontSection"}):
                row = {}
                row["title"]=cleanText(job.a.get_text())
                row["url"] = "http://jobs.acm.org"+job.a['href']
                row["desc"] = cleanText(job.find("div",{"class":"aiResultsMainDiv"}).find_all("div")[-1].get_text())
                threadLock.acquire()
                dataRows.append(row)
                threadLock.release()
            '''
            If more then one page in result, grab records from the next grapDataTillResultPage
            '''
                
            if(pagination):
                maxIteration = 1
                if int(totalPage) > self.grabDataTillResultPage:
                    maxIteration = self.grabDataTillResultPage
                else:
                    maxIteration = totalPage
                for i in range(2,maxIteration+1):
                    acmInnerPage = self.urlsConstant["acmPagination"].replace("<searchKey>",self.searchKey).replace("<pagenumber>",repr(i))
                    afpj = fetchPaginationJobs(None,None,acmInnerPage)
                    afpj.start()
                    childThreads.append(afpj)
                    
        if self.name == "indeed":
            indeedPageUrl = self.urlsConstant["indeed"].replace("<searchKey>",self.searchKey)
            print "\nFetching jobs from Indeed..."
            indeedpage = urllib2.urlopen(indeedPageUrl)
            indeedsoup = BeautifulSoup(indeedpage, 'html.parser')
            [s.extract() for s in indeedsoup('script')]
            #Find total result pages in indeed
            indeedtotalPage = indeedsoup.find("div",{"id":"searchCount"})
            multipleResultPages = False
            #If the search count is present i.e. there are multiple pages in result
            if indeedtotalPage:
                indeedtotalPage = indeedtotalPage.get_text()
                multipleResultPages = True
            #Fetch all the results on the first page
            for indeedjob in indeedsoup.find_all("div",{"class":"result"}):
                row = {}
                #Discard sponsored jobs
                if indeedjob.find("span",{"class":"sponsoredGray"}) is not None:
                    continue
                row["title"]= cleanText(indeedjob.a.get_text())
                row["url"]="https://www.indeed.com"+indeedjob.a['href']
                desiredExp = indeedjob.find("span",{"class":"experienceList"})
                if desiredExp is not None:
                    row["desc"]=cleanText(indeedjob.find("span",{"class":"summary"}).get_text()+" "+desiredExp.get_text())
                else:
                    row["desc"]=cleanText(indeedjob.find("span",{"class":"summary"}).get_text())
                threadLock.acquire()
                dataRows.append(row)
                threadLock.release()
            #If more then one page in result, grab records from the next grabDataTillResultPage
            
            if multipleResultPages:
                #Get exact no. of result pages
                totalresults=0
                try:
                    totalresults = indeedtotalPage[indeedtotalPage.index('of')+3:len(indeedtotalPage)].replace(",","")
                    totalresults = int(totalresults)
                except:
                    return
                totalPage=totalresults/50
                #Set maximum no. of iterations
                maxIteration = 1
                if totalPage > self.grabDataTillResultPage:
                    maxIteration = self.grabDataTillResultPage
                else:
                    maxIteration = totalPage
                for i in range(1,maxIteration):
                    indeedIneerPageUrl = self.urlsConstant["indeedPagination"].replace("<searchKey>",self.searchKey).replace("<pagenumber>",repr(50*i))
                    #Create threads for each new page
                    fpj = fetchPaginationJobs(indeedIneerPageUrl,None,None)
                    fpj.start()
                    childThreads.append(fpj)
                    
'''
Threaded scrapper class to fetch jobs from paginated pages of each sites
'''        
class fetchPaginationJobs (threading.Thread):
    def __init__(self, indeedIneerPageUrl, ieeePageUrl, acmPageUrl):
        threading.Thread.__init__(self)
        self.indeedIneerPageUrl = indeedIneerPageUrl
        self.ieeePageUrl = ieeePageUrl
        self.acmPageUrl = acmPageUrl
    def run(self):
        if self.indeedIneerPageUrl:
            page = urllib2.urlopen(self.indeedIneerPageUrl)
            indeedsoup = BeautifulSoup(page, 'html.parser')
            for job in indeedsoup.find_all("div",{"class":"result"}):
                if job.find("span",{"class":"sponsoredGray"}) is not None:
                    continue
                row = {}
                row["title"]= cleanText(job.a.get_text())
                row["url"]="https://www.indeed.com"+job.a['href']
                desiredExp = job.find("span",{"class":"experienceList"})
                if desiredExp is not None:
                    row["desc"]=cleanText(job.find("span",{"class":"summary"}).get_text()+" "+desiredExp.get_text())
                else:
                    row["desc"]=cleanText(job.find("span",{"class":"summary"}).get_text())
                threadLock.acquire()
                dataRows.append(row)
                threadLock.release()
        if self.ieeePageUrl:
            page = urllib2.urlopen(self.ieeePageUrl)
            ieeesoup = BeautifulSoup(page, 'html.parser')
            for job in ieeesoup.find_all("div",{"id":"aiDevHighlightBoldFontSection"}):
                row = {}
                row["title"]=cleanText(job.a.get_text())
                row["url"]="http://jobs.ieee.org"+job.a['href']
                row["desc"] = cleanText(job.find("div",{"class":"aiResultsMainDiv"}).find_all("div")[-1].get_text())
                threadLock.acquire()
                dataRows.append(row)
                threadLock.release()
        if self.acmPageUrl:
            page = urllib2.urlopen(self.acmPageUrl)
            acmsoup = BeautifulSoup(page, 'html.parser')
            for job in acmsoup.find_all("div",{"id":"aiDevHighlightBoldFontSection"}):
                row = {}
                row["title"]=cleanText(job.a.get_text())
                row["url"]="http://jobs.acm.org"+job.a['href']
                row["desc"] = cleanText(job.find("div",{"class":"aiResultsMainDiv"}).find_all("div")[-1].get_text())
                threadLock.acquire()
                dataRows.append(row)
                threadLock.release()


class Table(object):
    '''
    Table built using dictionary
    '''
    def __init__(self):
        self.key2rowsMap = {}

    def addRow(self, row):
        self.key2rowsMap[row['searchKey']] = row

    def getRow(self, searchKey):
        return self.key2rowsMap[searchKey]
    
    def getSize(self):
        return len(self.key2rowsMap)

def cosineDistance(rowVector, searchRowVector):
    '''
    Using cosine similarity on tf idf vector
    '''
    # rowVector.searchRowVector
    numerator = 0
    #||searchRowVector||
    denominatorS = 0
    #||rowVector||
    denominatorR = 0
    
    for word in searchRowVector.keys():
        if rowVector.has_key(word):
            numerator+=(searchRowVector[word]*rowVector[word])
        denominatorS+=(searchRowVector[word]*searchRowVector[word])
    
    for word in rowVector.keys():
        denominatorR+=(rowVector[word]*rowVector[word])
    
    return 1 - round(numerator / (math.sqrt(denominatorS) * math.sqrt(denominatorR )), 5)

def vectorAddition(vector1, vector2):
    '''
    Adds vector 1 and vector 2
    '''
    resultVector = vector1
    for word in vector2.keys():
        if resultVector.has_key(word):
            resultVector[word]+=vector2[word]
        else:
            resultVector[word]=vector2[word]
    
    return resultVector

def divideVector(vector,divider):
    for word in vector.keys():
        vector[word]/=divider
    return vector

#threadLock, scrappedData list and inDepthSearch threads list defined
threadLock = threading.Lock()
dataRows = []
childThreads = []
lookupTable = Table()

def reset():
    del dataRows[:]
    del childThreads[:]

def cleanText(text):
    '''
    Function to sanitize text before using it for computing scores
    '''
    paras = (line.strip() for line in text.splitlines())
    chunks = (words.strip() for line in paras for words in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return re.sub("[,.;@#?:/\-+!&()$]+\ *"," ",text.encode('ascii','ignore')).lower()

def calculateTermination(centroids, n, itr):
    '''
    Find the terminating condition by comparing distance of existing centroid with its previous iteration counterpart
    ''' 
    distance = 0
    for clusterID in range(n):
        #get the id of last centroid
        backId = len(centroids) - clusterID - 1
        #calculate sum of distances of each centroid with their older counterparts in the previous iteration
        distance += cosineDistance(centroids[backId + n*itr], centroids[backId-n + n*itr])
    
    #getting the mean distance of movement of each centroid
    distance /= n
    if distance < 0.01:
        return True
    else:
        return False

def htmlOutputer(resultJobs, keyword, time, isClustered, clusters):
    '''
    Outputs the job results in the html format
    '''
    outputFile = open("testfile.html","w") 
     
    htmlhead="""<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
        <title>Intelligent Search Agent</title>
        
        <!-- Bootstrap -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    
      </head>
      <body>
        <div class="container">
            <div class="page-header">
              <h1>Job and Career Search <small>Intelligent Agent</small></h1>
            </div>"""
    
    if time < 0.2:
        if not isClustered:        
            successAlert = """<div class="alert alert-success" role="alert"> """+repr(len(resultJobs))+" top matching '"+keyword+"""' jobs fetched from the lookup table in """+repr(round(time,2))+""" seconds </div>"""
        else:
            successAlert = """<div class="alert alert-success" role="alert"> """+repr(len(resultJobs))+" top matching '"+keyword+"""' jobs fetched from the lookup table in """+repr(round(time,2))+""" seconds </div> <div class="alert alert-info" role="alert">Similar jobs are grouped together</div>"""
        
    else:
        if not isClustered:        
            successAlert = """<div class="alert alert-success" role="alert"> """+repr(len(resultJobs))+" top matching '"+keyword+"""' jobs scrapped over the internet in """+repr(round(time,2))+""" seconds </div>"""
        else:
            successAlert = """<div class="alert alert-success" role="alert"> """+repr(len(resultJobs))+" top matching '"+keyword+"""' jobs scrapped over the internet in """+repr(round(time,2))+""" seconds </div> <div class="alert alert-info" role="alert">Similar jobs are grouped together</div>"""
        
    
    jobSearch = {}
    if not isClustered:
        i = 0
        for job in resultJobs:
                    jobSearch[i] = """
                    <div class="panel panel-default">
                      <div class="panel-heading">
                        <a href='"""+job["url"]+"""'  target="_blank"><h3 class="panel-title">"""+string.capwords(job["title"])+"""</h3></a>
                      </div>
                      <div class="panel-body">
                        """+job["desc"]+"""<a href='"""+job["url"]+"""'  target="_blank">...more info</a>
                      </div>
                    </div> """
                    i+=1
    else:
        oldClusterid = 0
        i=0
        jobSearch[i] = "<div class='well well-lg'> <h4>Cluster "+repr(i + 1)+"</h4>"
        for job in resultJobs:
            # Using mod to get exact cluster ids(i.e. getting rid of the multiple iteration value 'k' used while creating cluster)
            if job["centroid"]%clusters != oldClusterid:
                jobSearch[i] = "</div><div class='well well-lg'><h4>Cluster "+repr(job["centroid"]%clusters + 1)+"</h4>"
                oldClusterid = job["centroid"]%clusters
            try:
                jobSearch[i] = jobSearch[i]+"""
                        <div class="panel panel-warning">
                          <div class="panel-heading">
                            <a href='"""+job["url"]+"""'  target="_blank"><h3 class="panel-title">"""+string.capwords(job["title"])+"""</h3></a>
                          </div>
                          <div class="panel-body">
                            """+job["""desc"""]+"""<a href='"""+job["""url"""]+"""'  target="_blank">...more info</a>
                          </div>
                        </div> """
            except KeyError:
                jobSearch[i] = """
                        <div class="panel panel-warning">
                          <div class="panel-heading">
                            <a href='"""+job["url"]+"""'  target="_blank"><h3 class="panel-title">"""+string.capwords(job["title"])+"""</h3></a>
                          </div>
                          <div class="panel-body">
                            """+job["""desc"""]+"""<a href='"""+job["""url"""]+"""'  target="_blank">...more info</a>
                          </div>
                        </div> """
            i+=1
                
                
    htmlfooter="""</div><div class="alert alert-warning" role="alert"> Go back to the python console to continue job search..</div>
            
        </div>
      </body>
    </html>"""
    
    outputFile.write(htmlhead+successAlert)
    for job in jobSearch.keys():
        outputFile.write(jobSearch[job])
    
    outputFile.write(htmlfooter)    
     
    webbrowser.open_new_tab('file://' + os.path.realpath("testfile.html"))
     
    outputFile.close()    

class Agent(object):
    '''
    Agent class senses input, perform computations on input(function()) and takes action(actuator())
    '''
    def __init__(self, k, searchKey, urlsConstant, grabDataTillResultPage, startTime):
        '''
        Sets value of k, searchKey, urlsConstant and the depth of scraping as set by the user
        initializes accuracy and attributeInfo lists
        '''
        self.urlsConstant = urlsConstant
        self.grabDataTillResultPage = grabDataTillResultPage
        self.k = k 
        self.searchKey = searchKey
        self.start = startTime
        self.minScore = 99999999
        self.minScoreRow = {}
        
    def sensor(self):
        '''
        Scrapes the data through 3 sites parallelly 
        '''
        global lookupTable
        #Check if lookup table already has the result computed
        try:
            lookupTableResult = lookupTable.getRow(self.searchKey)
            if lookupTableResult["k"] >= self.k and lookupTableResult["timeStamp"] - time.time() < 86400:
                return lookupTableResult["resultJobs"][0:self.k]
        except KeyError:
            print "\nScratching data over the internet.."
        
        #create threads for each site
        indeedFetch = fetchJobs("indeed",self.urlsConstant,self.searchKey,self.grabDataTillResultPage)
        acmFetch = fetchJobs("acm",self.urlsConstant,self.searchKey,self.grabDataTillResultPage)
        ieeeFetch = fetchJobs("ieee",self.urlsConstant,self.searchKey,self.grabDataTillResultPage)
        
        #start scraping
        indeedFetch.start()
        acmFetch.start()
        ieeeFetch.start()
        
        #wait for scraping to end
        indeedFetch.join()
        acmFetch.join()
        ieeeFetch.join()
        
        #wait for in depth scraping to end
        for t in childThreads:
            t.join()
            
        done = time.time()
        elapsed = done - self.start
        
        print repr(len(dataRows)) + " jobs fetched in "+repr(round(elapsed,2))+" seconds, finding the best match for you..\n";
        
        if len(dataRows) == 0:
            return dataRows
        
        #Create dummy row in scrappedData with title & desc as the search key. So as to simplify the vectorization process in the agent's function method
        searchRow = {}
        searchRow["title"] = self.searchKey.replace("+", " ")
        searchRow["desc"] = searchRow["title"]
        dataRows.append(searchRow)
        
        #call the agent function and pass on the scraped dataRows
        return self.function(dataRows)
    
    def function(self, dataRows):
        '''
        Computes score of each scraped job
        '''
        totalDocuments = len(dataRows)
        docFrequency = {}
        
        #Caluclate doc frequency of a word
        for row in dataRows:
            #set of words from title and desc of each row
            markedWords = set([])
            for word in row["desc"].split(" "):
                markedWords.add(word)
            for word in row["title"].split(" "):
                markedWords.add(word)
            #increase the document frequency of that word
            for word in markedWords:
                if docFrequency.has_key(word):
                    docFrequency[word]+=1
                else:
                    docFrequency[word]=1
        

        #Calculates score of each job
        for row in dataRows:
            textFrequency = {}
            #Compute text frequency of a word in desc and title for each row
            for word in row["desc"].split(" "):          
                if textFrequency.has_key(word):
                    textFrequency[word]+=1
                else:
                    textFrequency[word]=1
            for word in row["title"].split(" "):          
                if textFrequency.has_key(word):
                    textFrequency[word]+=3
                else:
                    textFrequency[word]=3
            #Calculate tfidfVector of each word in the row
            tfidfVector = {}
            for wf in textFrequency.keys():
                if docFrequency[wf] == 0:
                    print "no doc frequency found for ",wf
                    continue
                #first term penilazes for long length of text(title, description), second term minimizes the magnification effect of unique words
                tfidfVector[wf]= textFrequency[wf]/float(len(textFrequency)) * math.log10(totalDocuments/float(docFrequency[wf]))
            row["tfidfVector"] = tfidfVector
        
        
        #Calculate the cosine distance matrix for each job
        for row in dataRows:
            row["distance"] = cosineDistance(row["tfidfVector"], dataRows[len(dataRows) - 1]["tfidfVector"])
            
        #Pass on the results to actuator    
        return self.actuator(dataRows)
                    
    def actuator(self, dataRows): 
        '''
        Builds the resultJobs list with top k scored jobs
        '''
        resultJobs = []
        if len(dataRows) > self.k:
            resultJobs = sorted(dataRows, key=operator.itemgetter("distance"))[1:self.k+1]
        else:
            resultJobs = sorted(dataRows, key=operator.itemgetter("distance"))[1:len(dataRows)-1]
        
        #Build the lookup table        
        if len(resultJobs) > 0:
            lookupTableRow = {}
            lookupTableRow["searchKey"] = self.searchKey
            lookupTableRow["resultJobs"] = resultJobs
            lookupTableRow["timeStamp"] = time.time()
            lookupTableRow["k"] = self.k
            lookupTable.addRow(lookupTableRow)
        
        return resultJobs
        
class Environment(object):
    '''
    Environment of the agent. It gets input from the user and passes on to the agent. Also get the processed response form the agent and displays on screen for the user 
    '''
    def __init__(self):
        self.urlsConstant = {
                       "acm":"http://jobs.acm.org/jobs/results/keyword/<searchKey>?rows=50&radius=0&page=",
                       "acmPagination":"http://jobs.acm.org/jobs/results/keyword/<searchKey>?rows=50&radius=0&page=<pagenumber>",
                       "ieee":"http://jobs.ieee.org/jobs/results/keyword/<searchKey>?locationType=text&sort=score+desc%2C+JobTitle+asc&rows=50",
                       "ieeePagination":"http://jobs.ieee.org/jobs/results/keyword/<searchKey>?sort=score+desc%2C+JobTitle+asc&rows=50&locationType=text&page=<pagenumber>",
                       "indeed":"https://www.indeed.com/jobs?q=<searchKey>&limit=50&filter=0&start=0",
                       "indeedPagination":"https://www.indeed.com/jobs?q=<searchKey>&limit=50&filter=0&start=<pagenumber>"
                       }
        self.grabDataTillResultPage = 5    
    
    def bigBang(self): 
        global lookupTable 
        try:
            with open('lookupTable.pickle', 'rb') as handle:
                lookupTable = pickle.load(handle)  
        except:
            print "" #if lookuptable not available do not anything
        while 1:
            '''
            Display Menu
            '''
            # Infinite loop to handle user input errors
            while 1:
                try:
                    searchKey = raw_input("Enter your search string \n")
                    self.searchKey = searchKey.replace(' ', '+').lower()
                    k = int(raw_input("\nEnter no. of results you want to display (value of k) \n"))
                    clusteringMode = 0
                    advancedOptions = 1
                    clusters = 0
                    while True:
                        advancedOptions = int(raw_input("\nEdit advanced options (clustering and data scrapping depth)?\n1. No\n2. Yes\n"))
                        if advancedOptions == 2:
                            while True:
                                clusteringMode = int(raw_input("\nDo you want similar jobs to be grouped together(Enable clustering)?\n1.Yes\n2.No\n"))
                                if clusteringMode == 1:
                                    while True:
                                        clusters = int(raw_input("\nEnter the no. of clusters\n"))
                                        if clusters >= k:
                                            print "\nNo. of clusters should be less then the value of k, kindly enter correct value\n"
                                        else:
                                            break
                                    break
                                elif clusteringMode == 2:
                                    break
                                else:
                                    print "Wrong input encountered, kindly enter correct value.."
                            self.grabDataTillResultPage = int(raw_input("\nEnter no. of (paginated)results pages in result to be scraped (more pages results in more time)\n"))
                            while True:
                                clearLookupTable = int(raw_input("\nClear lookup table? 1.Yes 2.No\n"))
                                if clearLookupTable == 1:
                                    lookupTable = Table()
                                    break
                                elif clearLookupTable == 2:
                                    break
                                else:
                                    print "Wrong input encountered, kindly enter correct value.." 
                            break
                        elif advancedOptions == 1:
                            break
                        else:
                            print "Wrong input encountered, kindly enter correct values.."
                    break
                except:
                    print "Wrong input encountered, kindly enter correct values.."   
                
            start = time.time()
            
            #Create agent using k, the search string and other parameters
            jobAgent = Agent(k,self.searchKey,self.urlsConstant,self.grabDataTillResultPage,start)
            
            #call the sensor, which internally calls function which in turn calls actuator. Actuator returns the k nearest jobs, which are returned in resultJobs
            resultJobs = jobAgent.sensor()
            
            done = time.time()
            elapsed = done - start
            
            if elapsed > 0.2:
                print repr(len(resultJobs)) + " jobs fetched from the lookup table in "+repr(round(elapsed,2))+" seconds !!"
            else:
                print repr(len(resultJobs)) + " jobs fetched in "+repr(round(elapsed,2))+" seconds !!"
            
            if clusteringMode != 1:
                if len(resultJobs) > 0:
                #Print output in browser
                    htmlOutputer(resultJobs, searchKey, elapsed, False, clusters)
                    print "\nKindly open url -> "+'file://' + os.path.realpath("testfile.html") + " in browser to view results\n"
                    
                else:
                    print "\nSorry, no jobs found with entered string\n"
                
            else:
                centroids = {}
                tempIndexes = []
                
                #randomly select initial centroids
                for key in range(clusters):
                    while True:
                        jobIndex = randint(1, len(resultJobs)-1)
                        if not tempIndexes.__contains__(jobIndex):
                            break
                    tempIndexes.append(jobIndex)
                    centroids[key] = resultJobs[jobIndex]["tfidfVector"]
                
                itr = 0;
                while True:
                    
                    #Find distance of each job from the centroid
                    for centroid in centroids.keys():
                        for job in resultJobs:
                            job[centroid] = cosineDistance(centroids[centroid], job["tfidfVector"])
                    
                    #Assign the closest centroid as the centroid for each job
                    for job in resultJobs:
                        minVal = 9
                        for key in centroids.keys():
                            if job[key] <= minVal:
                                minVal = job[key]
                                job["centroid"] = key       
                    
                    resultJobs = sorted(resultJobs, key=operator.itemgetter("centroid"))
                    
                    #Find mean vector for each centroid group and add new centroid
                    centroidCount = {}
                    for row in resultJobs:
                        try:
                            #compute vector addition and count of rows in each vector
                            centroids[clusters+row["centroid"]] = vectorAddition(row["tfidfVector"], centroids[clusters+row["centroid"]])
                            centroidCount[clusters+row["centroid"]] += 1
                        except KeyError:
                            centroids[clusters+row["centroid"]] = vectorAddition(row["tfidfVector"], centroids[row["centroid"]])  
                            centroidCount[clusters+row["centroid"]] = 1  
                    #get mean by dividing vector addition of all jobs of a centroid by count of all jobs of that centroid
                    for centroidId in centroidCount:
                        centroids[centroidId] = divideVector(centroids[centroidId],centroidCount[centroidId])
                    
                    #evaluate the termination condition
                    if calculateTermination(centroids, clusters, itr):
                        break
                    
                    #remove old centroids
                    for i in range(clusters):
                        centroids.pop(i + (itr*clusters))
                    #maximize distance of old centroids in each job
                    for row in resultJobs:
                        for i in range(clusters):
                            row[i+(itr*clusters)] = 9
                        
                    itr+=1
                    
                if len(resultJobs) > 0:
                #Print output in browser
                    htmlOutputer(resultJobs, searchKey, elapsed, True, clusters)
                    print "\nKindly open url -> "+'file://' + os.path.realpath("testfile.html") + " in browser to view results\n"
                    
                else:
                    print "\nSorry, no jobs found with entered string\n"
                            
            exitInput = raw_input("\nEnter e to exit.. Enter any other key to rerun..\n")
            
            if exitInput == 'e':
                print "THANK YOU !!"
                #Persist the lookup table
                with open('lookupTable.pickle', 'wb') as handle:
                    pickle.dump(lookupTable, handle, protocol=pickle.HIGHEST_PROTOCOL)
                exit()
                
            reset()
            
#Create Environment
Environment().bigBang()
