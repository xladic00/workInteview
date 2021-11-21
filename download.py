#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import zipfile
import os
import requests
from bs4 import BeautifulSoup
import requests
from requests import get
from os import listdir
from os.path import isfile, join
import glob
import csv
import pickle
import gzip

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }
    strIndex = [3, 51, 52, 54, 55, 56, 58, 59, 62]
    floatIndex = [45, 46, 47, 48, 49, 50, 57]

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder

    def download_data(self):
        downloadLinks = self.getLinksToDownload()
        for link in downloadLinks:
            downloadAndSave(self.url + link, self.folder)


    def parse_region_data(self, regions = None):
        if not os.path.exists(self.folder + "/dictionaries"):
            os.makedirs(self.folder + "/dictionaries")  # create folder if it does not exist
        if (regions is None):
            regions = self.regions.values()
        csvFiles = []
        folders = [x[0] for x in os.walk("data/")]
        for folder in folders:
            csvFiles.extend(glob.glob(folder + "/*.csv"))
        for region in regions:
            localList = []
            myDict = {}
            for header in self.headers:     #creating dictionary
                myDict[header] = np.array([header])
            for file in csvFiles:           #making list of csv for this dictionary
                localString = self.replaceYear(file)
                if(region in localString):
                    localList.append(file)                    
            for csvFile in localList:
                csvFiles.remove(csvFile)    #removing used csvFiles from list
                print("Parsing " + csvFile)
                with open(csvFile, 'r', encoding= "cp1250") as csv_file:
                    data = np.transpose(list(csv.reader(csv_file, delimiter=';')))
                    data =  self.parsingData(data)
                    for index in range(1,len(data)):
                        if not(index in (self.strIndex + self.floatIndex)):
                            myDict[self.headers[index]] = np.append(myDict[self.headers[index]],data[index].astype(np.float64))            
                        elif(index in self.strIndex):
                            if(index == 5):
                                #time change 
                                for s in range(0,len(data[index])):
                                    a = data[index][s][0:2]
                                    b = data[index][s][2:4]
                                    if(a == "25"):
                                        a = "Unknown hour" 
                                    if(b == "60"):
                                        b = "Unknown minute"    
                                    data[index][s] = a + ":" + b                           
                            myDict[self.headers[index]] = np.append(myDict[self.headers[index]],data[index])
                        else:
                            for s in range(0,len(data[index])):
                                if(data[index][s] != ""):
                                    data[index][s].replace(",",".")
                                else:
                                    data[index][s] = None
                            myDict[self.headers[index]] = np.append(myDict[self.headers[index]],np.array(list(map(lambda x: x.replace(',', '.'), data[index]))).astype(np.float64))

            with gzip.open(self.folder + "/dictionaries/" + region + '.pkl.gz', 'wb') as handle:  
                print("Saving dictionary to " + self.folder + "/dictionaries/" + region + '.pkl.gz')     
                pickle.dump(myDict, handle, protocol=pickle.HIGHEST_PROTOCOL)   
                    

    def parsingData(self, data):
        data[data == ""] = np.NaN 
        data[34][data[34] == "XX"] = np.NaN 
        data[45][data[45] == "A:"] = np.NaN
        data[46][data[46] == "B:"] = np.NaN
        data[47][data[47] == "D:"] = np.NaN
        data[48][data[48] == "E:"] = np.NaN
        data[49][data[49] == "F:"] = np.NaN
        data[50][data[50] == "G:"] = np.NaN
        data[55][data[55] == "L:"] = np.NaN
        return(data)

    def replaceYear(self, this):
        this = this.replace('2016', 'XXXX')
        this = this.replace('2017', 'XXXX')
        this = this.replace('2018', 'XXXX')
        this = this.replace('2019', 'XXXX')
        this = this.replace('2020', 'XXXX')
        this = this.replace('2021', 'XXXX')
        return(this)

    def get_dict(self, regions=None):
        
        if (regions is None):
            regions = self.regions.values()
        dicts = []
        try:
            for f in os.listdir("data/dictionaries/"):           
	            dicts.append(f)
        except:
            pass
        neededDicts = list(regions)
        if not (not dicts):#if dicts is not empty
            for region in regions:
                if any (region in s for s in dicts):
                    neededDicts.remove(region)   


        if not ( not neededDicts ):#if neededDicts is empty
            self.download_data()
            self.unZip()
            if(len(regions) == len(neededDicts)):
                self.parse_region_data()     
            else:
                self.parse_region_data(neededDicts)
        dicts.clear()
        for f in os.listdir("data/dictionaries/"):           
	        dicts.append(f)
        returnList = []
        for region in regions:
            localDict = pickle.load(gzip.open("data/dictionaries/" + region + ".pkl.gz", "rb"))
            returnList.append(localDict)
        return(returnList)

    def getLinksToDownload(self):
        zipLinks = []
        soup = BeautifulSoup(requests.get(self.url).text, "html.parser")
        for links in soup.find_all('button'):
            thisLink = links.get('onclick')
            if ".zip" in thisLink:
                zipLinks.append(thisLink.split("'")[1].split("'")[0])

        for year in ["2016","2017","2018", "2019","2020", "2021"]:#hardcoded years for now possible to give years as input argument
            thisYearList = []
            for link in zipLinks:
                if (year in link):
                    thisYearList.append(link)
                    
            for item in thisYearList:
                zipLinks.remove(item)
            found = False 
            array = ["01", "02", "03", "04", "05","06", "07", "08", "09", "10","11"]
            while(not found):
                for yearLink in thisYearList:
                    localString = yearLink
                    localString = localString.replace(year,"xxxx")
                    if not any(x in localString for x in array):
                        zipLinks.append(yearLink)
                        found = True
                        break
                array.pop(-1)
                if(not array):
                    print("for year " + year + " was not found zip file")
                    break
        zipFiles = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
        zipFiles = ["data/" + s for s in zipFiles]
        zipLinks = [item for item in zipLinks if item not in zipFiles]  
        return (zipLinks)

    def unZip(self):
        zipFiles = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
        for zipFile in zipFiles:
            try:
                thisZipFile = zipfile.ZipFile(self.folder + "/" + zipFile)
                path = os.path.join((self.folder + "/" + zipFile).replace(".zip", ""))
                print("Unziping " + zipFile)           
                os.mkdir(path)
                thisZipFile.extractall(path)
            except FileExistsError:
                continue
            
def downloadAndSave(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))
            



# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
