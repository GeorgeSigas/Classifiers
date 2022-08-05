import os
import collections
import string
import math
import random

PartList=[1,2,3,4,5,6,7,8,9,10]
def cut(dictionary):#takes last 50 (most found)
    copyDict=collections.OrderedDict(dictionary)
    flag=len(dictionary)-50
    i=1
    for key in copyDict.keys():
        if i>flag:
            dictionary[key]=i-flag
        else:
            del dictionary[key]
        i+=1
    return dictionary

def createDict():
    global PartList
    counterH=0
    counterS=0
    CounterList=[[0,0]]
    pointer=0
    stop=string.punctuation
    Vdict=collections.OrderedDict()
    path='part'
    '''
    for k in range(8):#80%
        i=PartList.pop(random.randint(0,len(PartList)-1))
    '''
    for i in range(2,10):
        for filename in os.listdir(path+str(i)):
            checkedList=[]#so we can count 1 time each word for each mail
            with open(path+str(i)+'/'+filename,'r')as file:
                f=file.read()
                file.close()
                words=f.split()
                for word in words:
                    if word not in checkedList:
                        if word not in stop and len(word)>3:
                            if word not in Vdict:
                                    Vdict[word]=pointer
                                    pointer+=1
                                    CounterList.append([0,0])
                                    checkedList.append(word)
                            if 'spmsg' in filename:
                                    CounterList[Vdict[word]][1]+=1#spam=1 ham=0
                                    counterS+=1
                            else:
                                    CounterList[Vdict[word]][0]+=1
                                    counterH+=1
                                    

                                
                             
    return Vdict,CounterList,counterH,counterS

def createLists(Vdict):
    global PartList
    ham_list=[]
    spam_list=[]
    spamCounter=0
    hamCounter=0
    path='part'
    
    '''
    for k in range(1):#10%
        i=PartList.pop(random.randint(0,len(PartList)-1))
    '''
    for i in range(1,2):
        for filename in os.listdir(path+str(i)):
            with open(path+str(i)+'/'+filename,'r')as file:
                f=file.read()
                file.close()
                if 'spmsg' in filename:               
                    spam_list.append([])
                    for word in Vdict.keys():
                       if (word in f):
                           spam_list[spamCounter].append(1)
                       else:
                            spam_list[spamCounter].append(0)
                    spamCounter+=1
                else:
                    ham_list.append([])
                    for word in Vdict.keys():
                       if (word in f):
                            ham_list[hamCounter].append(1)
                       else:
                            ham_list[hamCounter].append(0)
                    hamCounter+=1
                
    return ham_list, spam_list ,hamCounter ,spamCounter

def wordProb(counter,hsList):
    Prob=[]
    for i in range(0,len(hsList[1])):
        Prob.append(0)
        for item in hsList:
            Prob[i]+=item[i]
        Prob[i]=(Prob[i]+1)/(counter+2)#Laplace
    return Prob
    

def PropabilityCalc(CategoryProb,probList,TestList):
    P =CategoryProb
    for i in range(0,len(TestList)):
        P=P*(TestList[i]*probList[i]+(1-TestList[i])*(1-probList[i]))
    return P

def entropy(spams,hams):
    en=-spams*math.log(spams,2)-hams*math.log(hams,2)
    return en

def  Cond_entropy(index,CounterList,CounterS,CounterH,Sum):
    P_c0_x1=((CounterH/Sum)*(CounterList[index][0]+1/CounterH+2))/(CounterList[index][0]+CounterList[index][1])
    P_c1_x1=((CounterS/Sum)*(CounterList[index][1]+1/CounterS+2))/(CounterList[index][0]+CounterList[index][1])
    P_c0_x0=((CounterH/Sum)*((CounterH-CounterList[index][0])+1/CounterH+2))/(Sum-CounterList[index][0]-CounterList[index][1])
    P_c1_x0=((CounterS/Sum)*((CounterS-CounterList[index][1])+1/CounterS+2))/(Sum-CounterList[index][0]-CounterList[index][1])
   
    H_c_x1=(-P_c0_x1*math.log(P_c0_x1,2)-P_c1_x1*math.log(P_c1_x1,2))
    H_c_x0=(-P_c0_x0*math.log(P_c0_x0,2)-P_c1_x0*math.log(P_c1_x0,2))
    
    return H_c_x1,H_c_x0 

def IG(Vdict,CounterList,Hcounter,Scounter):
    H_c=entropy(Scounter,Hcounter)
    Sum=Scounter+Hcounter
    for word in Vdict:
        index=Vdict[word]
        H_c_x1,H_c_x0=Cond_entropy(index,CounterList,Scounter,Hcounter,Sum)
        
        Vdict[word]=H_c-(Sum-CounterList[index][0]-CounterList[index][1])*H_c_x0-(CounterList[index][0]+CounterList[index][1])*H_c_x1
    return Vdict    



def Test(Vdict,ProbHam,ProbSpam,hamCounter,spamCounter):
    TestList=[]
    TestCounter=0
    Found=0
    path='part'
    DataSum=hamCounter+spamCounter
    '''
    for i in range(1):#10%
            i=PartList.pop(random.randint(0,len(PartList)-1))
    '''
    for i in range(10,11):
        fp=0#false positive when guess spam but its ham
        fn=0#false negative when guess ham but its spam
        tp=0#true positive when guess ham and its ham
        for filename in os.listdir(path+str(i)):
                 TestCounter+=1
                 with open(path+str(i)+'/'+filename,'r')as file:
                     f=file.read()
                     file.close()
                     TestList=[]
                     for word in Vdict.keys():
                         if (word in f):
                                TestList.append(1)
                         else:
                                TestList.append(0)
                     PH=PropabilityCalc((hamCounter/DataSum),ProbHam,TestList)
                     PS=PropabilityCalc((spamCounter/DataSum),ProbSpam,TestList)
                     if 'spmsg' in filename:
                         Type=1
                     else:
                         Type=0
                     if PH>PS:
                         Ttype=0
                     else:
                         Ttype=1
                     if Type==Ttype:
                         Found+=1
                         if Type==0:
                             tp+=1
                     else:
                         if Type==1:
                             fn+=1
                         else:
                             fp+=1
    print(str((Found/TestCounter)*100),"%")
    return tp,fn,fp

def Main():
    Vdict,CounterList,TrainHcounter,TrainScounter=createDict()#create vocabluary
    Vdict=IG(Vdict,CounterList,TrainHcounter,TrainScounter)
    Vdict=collections.OrderedDict(sorted(Vdict.items(),key=lambda t: t[1]))
    cut(Vdict) #pick the best words
    ham_list, spam_list,hamCounter, spamCounter=createLists(Vdict)#create lists with 1 if a word exists in an example(email) and 0 if it doesn't
    ProbHam=wordProb(hamCounter,ham_list)
    ProbSpam=wordProb(spamCounter,spam_list)
    tp,fn,fp=Test(Vdict,ProbHam,ProbSpam,hamCounter,spamCounter)
    prec=tp/(tp+fp)
    recall=tp/(tp+fn)
    f1=(2*(prec*recall))/(prec+recall)
    #print(prec, recall,f1)
Main()
                     


