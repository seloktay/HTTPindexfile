# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 21:59:05 2022

@author: Lenovo
"""

#to run program on console, write:
#run CloudDownloader.py dijkstra.cs.bilkent.edu.tr/~cs421/descriptor1.txt cs421:bilkent
import sys
import socket
import base64
import re
import numpy

def noheader(reply):
    end = reply.find('\r\n\r\n')
    if end >= 0:
        return reply[end+4:]
    return reply

args = list(sys.argv)
url = sys.argv[1]
tempurl = url
url_elm = url.split("/",1) 
host = url_elm[0]
path = url_elm[1]
userpass = str(sys.argv[2])
token = base64.b64encode(userpass.encode()).decode()
sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.connect((host, 80))
cmd = "GET /{} HTTP/1.0\r\nHost: {}\r\nAuthorization: Basic {}\r\n\r\n".format(path, host, token)
sock1.send(cmd.encode())

content = b""
while True:
    data = sock1.recv(512)
    content = content + data
    if len(data) < 1:
        break
content = content.decode()
resp = re.search("200 OK", content) #check if the content is retrieved correctly
if resp is None:
    print("\n\nERROR: Cannot reach requested page\nProgram terminated")
    sys.exit()
else:
    print("\n Webpage has been reached")

sock1.close()


#URL LIST
urls = re.findall(".+edu.+|com.+|org.+",content) #only used 3 popular TLDs
print("The URLS for partial download:")
for elm in urls:
    print(elm)
print("\n")
    
for elm in urls:
    elm = elm.split("/",1) 
    host = elm[0]
    path = elm[1]

#USERNAME:PASSWORD LIST
contentlist = content.split("\n")
temp = []
for line in contentlist:
    newelm = re.findall(".+:.+", line)
    temp.append(newelm)

matchlist = [item for sublist in temp for item in sublist]
ups = [] #user:password list
for line in matchlist:
    if " " not in line:
        ups.append(line)

print("username:password combinations")
for elm in ups:
    print(elm)
print("\n")

#LENGTH OF FILES
byteslist = []
contentlength = []
available_bytes = []

for elm in contentlist:
    newelm2 = re.findall("^[0-9]+-[0-9]+", elm)
    byteslist.append(newelm2)

for elm in byteslist:
    if len(elm) != 0:
        available_bytes.append(elm)

tempnew = [] #to store first and last bytes as a list of list
#will be useful for detecting overlaps
for x in range(len(available_bytes)):
    temp = str(available_bytes[x][0]).split("-")
    tempnew.append(temp)
#find overlaps by checking last byte of xth file to first byte of (x+1)th file 
tempnew2 = numpy.copy(tempnew)
tempnew2 = tempnew2.tolist()
for i in range(len(tempnew2)):
    if i == len(tempnew2) - 1:
        break
    else:
        dif = int(tempnew2[i][1]) - int(tempnew2[i+1][0])
        if dif > 0:
            tempnew2[i+1][0] = int(tempnew2[i][1])
#tempnew[i] = range of bytes to download from URL[i] 
for url in range(len(urls)):
    urls[url] = urls[url].rstrip()
    
temp22 = numpy.copy(tempnew2)
temp22 = temp22.tolist()

length_to_get = []
for i in range(len(tempnew)):
    length_to_get.append(int(tempnew2[i][1]) - int(tempnew2[i][0]))

temp22[0][0] = int(temp22[0][0]) - 1
temp22[0][1] = int(temp22[0][0]) - 1
for x in range(1,len(tempnew)):
     temp22[x][0] = int(tempnew2[x-1][1]) - int(tempnew[x][0])
     temp22[x][1] = int(temp22[x][0]) + int(length_to_get[x])

fulltext = b""
realfull = ""
length2 = []
servers = []
for x in range(len(urls)):
#for x in range(0,len(urls)-2):
    urlelms = urls[x].split("/",1) 
    host2 = urlelms[0]
    path2 = urlelms[1]
    uptemp = str(ups[x])
    token2 = base64.b64encode(uptemp.encode()).decode()
    cmd2 = "GET /{} HTTP/1.0\r\nHost: {}\r\nAuthorization: Basic {}\r\nRange: bytes={}-{}\r\n\r\n".format(path2, host2, token2, int(temp22[x][0]), int(temp22[x][1]))
    
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect((host2, 80))
    sock1.send(cmd2.encode())
    content2 = b""
    while True:
        data2 = sock1.recv(4096)
        content2 = content2 + data2
        if len(data) < 1:
            break
    filelen = re.findall("Content-Length: (.*)\r\n", data2.decode())
    length2.append(filelen[0])
    
    servername = re.findall("Server: (.*) OpenSSL", data2.decode())
    servers.append(servername[0])
    
    mytext = noheader(content2.decode())
    fulltext = fulltext + mytext.encode()
    
    len22 = int(tempnew[x][1]) - int(tempnew[x][0]) + 1
    
    print("""URL of index file: {}
File size of index file:{}
Index file is partially downloaded
Downloaded bytes {}-{}
Size of download:{}\n\n""".format(urls[x],filelen,tempnew[x][0],tempnew[x][1],len22))
  

print("Download of the file is complete")

fulltext = fulltext.decode()

fname = tempurl.replace("/", " ")

with open(fname, 'w') as f:
    f.write(fulltext)