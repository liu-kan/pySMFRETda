import sys
eps=sys.float_info.epsilon
import random,numbers
from typing import List,Any

def checkBounds(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for child in offspring:
                for i in range(len(child)):
                    if child[i] > max[i]:
                        if random.random()<0.8:
                            child[i] = max[i]- ((child[i] - max[i]) % (max[i]-min[i]))
                        else:
                            child[i] = max[i]-eps*random.randint(1,1e10) # eps ~ 1e-16 * e10 -> \us
                    elif child[i] < min[i]:
                        if random.random()<0.8:
                            child[i] = min[i]+ (( min[i]-child[i]) % (max[i]-min[i]))
                        else:
                            child[i] = min[i]+eps*random.randint(1,1e10) # eps ~ 1e-16 * e10 -> \us                            
            return offspring
        return wrapper
    return decorator

def fixBounds(child, min, max):
    for i in range(len(child)):
        if child[i] > max[i]:
            if random.random()<0.8:
                child[i] = max[i]- ((child[i] - max[i]) % (max[i]-min[i]))
            else:
                child[i] = max[i]-eps*random.randint(1,1e10) # eps ~ 1e-16 * e10 -> \us
        elif child[i] < min[i]:
            if random.random()<0.8:
                child[i] = min[i]+ (( min[i]-child[i]) % (max[i]-min[i]))
            else:
                child[i] = min[i]+eps*random.randint(1,1e10) # eps ~ 1e-16 * e10 -> \us                            


def checkList0(n,list0):
    if n <=0 or type(n)!=int:
        return False
    if len(list0)==0:
        return True
    list0.sort()
    if list0[0]<=1:
        return False
    if list0[-1]>=n*n:
        return False
    return True

def betavariate_k(mink,maxk):
    return random.betavariate( 2, 5)*(maxk-mink)+mink

def genRealInd(n: int,gaInd: List[numbers.Real],list0: List[int]) -> List[numbers.Real]:
    '''Genrate real ind from GA to the real model

    @type n: int
    @param n: n is number of states

    @type gaInd: List[numbers.Real]
    @param gaInd: gaInd ind in GA

    @type list0: List[int]
    @param list0: which elements are 0 in rate matrix

    @rtype: List[numbers.Real]
    @return: Returns parameters really used in the model
    '''
    if len(list0)==0:
        return gaInd
    idxRow=0
    realInd=[]
    realInd.extend(gaInd)
    for item0 in list0:
        while item0>(idxRow+1)*n:
            idxRow=idxRow+1
        if item0<idxRow*n+1+idxRow:
            realInd.insert(item0-idxRow-1+n,0)
        elif  item0>idxRow*n+1+idxRow:
            realInd.insert(item0-idxRow-2+n,0)
    return realInd

if __name__ == '__main__':
    gaInd=[0.25,0.22,0.33,0.45,2,3,5,7,9,12,14,15,100,100,100,100]
    print(gaInd)
    list0=[8,4,13,10]
    checkList0(4,list0)
    print(list0)
    realInd=genRealInd(4,gaInd,list0)
    print(realInd)