import codecs
import sys
import gzip
import os
from collections import defaultdict

def convertPlainPairsGZ(filenameIn,filenameOut):
    infile=gzip.open(filenameIn,'rb')
    outfile=codecs.open(filenameOut,'wb','utf-8')
    infile=codecs.getreader('utf-8')(gzip.open(filenameIn), errors='replace')
    line=infile.readline()
    while line:
        #line = line.decode('utf-8')
        line=line.strip().lower().replace(" ","_")
        outfile.write('$ ')
        for i,c in enumerate(line):
            outfile.write(c+" ")
        outfile.write("&\n")
        line=infile.readline()

def splitPairsList(dirnameIn,lang,percForDev, percForTest=0):
    devPerc=int(percForDev)
    testPerc=int(percForTest)
    i=0
    fileIn=codecs.open(dirnameIn+"/train/corpus."+lang,"r",'utf-8')
    devOut=codecs.open(dirnameIn+"/tune/tune."+lang,'w','utf-8')
    if testPerc>0:
        testOut=codecs.open(dirnameIn+"/test/test."+lang,'w','utf-8')
    trainOut=codecs.open(dirnameIn+"/train/train."+lang,'w','utf-8')
    line=fileIn.readline()
    while line:
        if i<devPerc:
            devOut.write(line)
            i+=1
        elif (i<devPerc+testPerc):
            testOut.write(line)
            i+=1
        else:
            trainOut.write(line)
            if i==99:
                i=0
            else:
                i+=1
        line=fileIn.readline()
    trainfile=dirnameIn+'/train/train.'+lang
    devfile=dirnameIn+'/tune/tune.'+lang
    testfile=dirnameIn+'/test/test.'+lang
    os.system("gzip -9n "+trainfile)
    os.system("gzip -9n "+devfile)
    if testPerc>0:
        os.system("gzip -9n "+testfile)

#Write a file of OOV words in the input file (nbest file) to the output file and zip it
def getOOVs(infile,outfile):
    inread=codecs.open(infile,'r','utf-8')
    outwrite=codecs.open(outfile,'w','utf-8')
    line=inread.readline()
    oovs=defaultdict(int)
    while line:
        line=line.split("|||")
        if len(line)>2:
            for word in line[1].split():
                word=word.strip()
                if word.endswith("_OOV"):
                    word=word.replace("_OOV","")
                    oovs[word]+=1
        line=inread.readline()
    for w in oovs:
        outwrite.write(w+"\n")
    os.system("gzip -9n "+outfile)

#transliterations of the srcDict items are in trgDict; creates dictionary of two files
#then uses dictionry to replace OOVs in nbestlist and writes 1best output with transliterations to outputfile
def subOOVTranslits(srcDict,trgDict,nbestlist,outputfile):
    srcFile=codecs.open(srcDict,'r','utf-8')
    trgFile=codecs.open(trgDict,'r','utf-8')
    sline=srcFile.readline()
    tline=trgFile.readline()
    oovDict=defaultdict(list)
    while sline:
        sline=sline.strip().strip("$").strip("&").strip().replace(" ","").replace("_"," ")
        tline=tline.strip().strip("$").strip("&").strip().replace(" ","").replace("_"," ")
        oovDict[sline].append(tline)
        sline=srcFile.readline()
        tline=trgFile.readline()
    nbestFile=codecs.open(nbestlist,'r','utf-8')
    outFile=codecs.open(outputfile,'w','utf-8')
    nline=nbestFile.readline()
    num=-1
    while nline:
        nline=nline.split(" ||| ")
        mynum=int(nline[0])
        if mynum>num:
            num=mynum
            sent=nline[1]
            for w in sent.split():
                if w.endswith("_OOV"):
                    w=w.replace("_OOV","")
                    translit=oovDict[w][0]
                    outFile.write(translit)
                else:
                    outFile.write(w)
                outFile.write(" ")
            outFile.write("\n")
        nline=nbestFile.readline()

if __name__=="__main__":
    #convert files to have spaces between characters and $ at beginning and & at end of lines
    if int(sys.argv[1])==1:
        convertPlainPairsGZ(sys.argv[1],sys.argv[2])
    #split input file into train and dev
    elif int(sys.argv[1])==2:
        if len(sys.argv)==6:
            splitPairsList(sys.argv[2],sys.argv[3], sys.argv[4], sys.argv[5])
        elif len(sys.argv)==5:
            splitPairsList(sys.argv[2],sys.argv[3], sys.argv[4])            
        else:
            print "unknown number of arguments for splitPairsList function"
            exit()
    elif int(sys.argv[1])==3:
        getOOVs(sys.argv[2],sys.argv[3])
    elif int(sys.argv[1])==4:
        subOOVTranslits(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
