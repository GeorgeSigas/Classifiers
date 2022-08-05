import math
import os
import collections
import string


R1=1

R2=5

R3=11


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
    counterH=0
    counterS=0
    CounterList=[[0,0]]
    pointer=0
    stop=string.punctuation
    Vdict=collections.OrderedDict()
    path='part'
    for i in range(R1, R2):
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
    ham_list=[]
    spam_list=[]
    spamCounter=0
    hamCounter=0
    path='part'
    for i in range(R1, R2):
        for filename in os.listdir(path+str(i)):
            with open(path+str(i)+'/'+filename,'r')as file:
                f=file.read()
                if 'spmsga' in filename:               
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
                file.close()
    return ham_list, spam_list ,hamCounter ,spamCounter


Vdict,CounterList,TrainHcounter,TrainScounter=createDict()#create vocabluary
Vdict=IG(Vdict,CounterList,TrainHcounter,TrainScounter)
Vdict=collections.OrderedDict(sorted(Vdict.items(),key=lambda t: t[1]))
cut(Vdict) #pick the best words
ham_list, spam_list,hamCounter, spamCounter=createLists(Vdict)#create lists with 1 if a word exists in an example(email) and 0 if it doesn't
DataSum=hamCounter+spamCounter







                    #############################   ADABOOST TRAIN   #############################



N = len(spam_list) + len(ham_list) #Number of examples (emails)
M = len(Vdict) #Number of words to check

#Initializing examples = [example_1, example_2,.... example_N]
#Where example[i] = [1,0,1,....,1] (1/0 meaning if each word exists and last 1/0 shows the category(spam/ham)
examples = [ [0]*M ] * N

#Creating examples
for i in range(len(spam_list)):
    examples[i] = spam_list[i] + [1]

for i in range(len(ham_list)):
    examples[i+len(spam_list)] = ham_list[i] + [0]

#Decision Tree with depth 1
def DT(examples, x):
    
    S_spam = 0
    S_ham = 0
    
    for i in range( len(examples) ):

        #looking only at examples that contain the x-th word
        if( examples[i][x] == 1 ):
            if( examples [i][M] == 1 ):
                S_spam += 1
            else:
                S_ham += 1


    #print('spam: ', S_spam)
    #print('ham: ', S_ham)
                
    if( S_spam > S_ham ):
        return 1
    else:
        return 0

    
def normalize(x):
    s = 0
    r = [0]*len(x)
    for i in range(len(x)):
        s += x[i]
    for i in range( len(r) ):
        r[i] = x[i] / s
    return r


#Returns majority of h's responses, according to their weights
def weighted_majority(h,z):
    
    S1=0
    
    S0=0
    
    for i in range(len(h)):
        if( h[i] == 1 ):
            S1 += z[i]
        else:
            S0 += z[i]

    if(S1 > S0):
        return 1
    else:
        return 0
    

#N = Number of examples (emails)
#M = Words

def AdaBoost(examples, DT, M):

    w = []
    #Initializing Weights
    for i in range(N): w.append(1/N)

    h = [0]*M #Predictions
    z = [0]*M #Weights of h

    #For each word we are checking all examples
    for m in range(M):
        h[m] = DT(examples, m) #Prediction based only on existance of m'th word
        #print(h[m])
        L = 0

        #Comparing DT's prediction with actual results in every example that m'th word exists
        for k in range(N):
            #examples[k][m] = word m exists in example k | examples[k][M] = example[k] category (spam/ham)
            if (examples[k][m] == 1) and ( examples[k][M] == h[m] ): L = L + w[k]

        for j in range(N):
            if (examples[j][m] == 1) and( examples[j][M] != h[m] ): w[j] = w[j] * L / (1-L)

        #print(L)

        w = normalize(w)
        
        z[m] = math.log2( (1-L) / L )
    #print(z)

    return z



zeta = AdaBoost(examples, DT, M) 








                    ############################## ADABOOST TEST ##############################

def AdaTest(filename):

    test = []
    
    with open(filename,'r')as testfile:

        f=testfile.read()
        testfile.close()
        
        for word in Vdict.keys():
            if word in f:
                test.append(1)
            else:
                test.append(0)

    Vote_S = 0
    Vote_H = 0

    for i in range( M ):
        if( test[i] == 1 ):
            Vote_S += zeta[i]
        else:
            Vote_H += zeta[i]
                
    if( Vote_S > Vote_H ):
        return 1
    else:
        return 0



Correct = 0
Total = 0
tp = 0 #True Positives (cases where answer = spam and correct =spam)
fp = 0 #False Positives (cases where answer = spam and correct = ham)
fn = 0 #False Negatives (cases where answer = ham and correct = spam)
path='part'
for i in range(R2, R3):
    for filename in os.listdir(path+str(i)):
        
        f = (path+str(i)+'/'+filename)
        
        answer = AdaTest(f)
        Total += 1
        
        if('spmsg' in filename):
            if( answer == 1):
                tp += 1
                Correct += 1
            else:
                fn += 1
        else:
            if( answer == 0 ):
                Correct += 1
            else:
                fp += 1
            
result = (Correct*100) / Total
precision = tp / (tp + fp)
recall = tp / (tp + fn)
F1 = 2*( (precision*recall) / (precision+recall) )

print(result, '% Correct!')
print(precision, ' Precision')
print(recall, ' Recall')
print(F1, ' F1 score')

 

            











