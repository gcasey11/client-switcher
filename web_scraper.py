import math
from bs4 import BeautifulSoup
from urllib.request import urlopen

url = "https://clientdiversity.org/"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

def get_consensus_dist():
    consensus_dist = {}
    consensus = soup.find("div", class_="text-start flex-grow-1 blockprint consensus-data")

    consensus_labels = consensus.find_all("label", class_="form-label")

    for label in consensus_labels:
        name = label.text.split(" ")[0]
        dist_string = label.text.split(" ")[2].replace("%", "")
        distribution = round(float(dist_string), 0)/100
        consensus_dist[name] = distribution
    
    return consensus_dist

def get_execution_dist():
    execution_dist = {}
    execution = soup.find("div", class_="text-start flex-grow-1 supermajority execution-data")

    execution_labels = execution.find_all("label", class_="form-label")

    for label in execution_labels:
        name = label.text.split(" ")[0]
        dist_string = label.text.split(" ")[2].replace("%", "")
        distribution = round(float(dist_string), 0)/100
        execution_dist[name] = distribution
    
    return execution_dist