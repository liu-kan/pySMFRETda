import random,array,signal
from timeit import default_timer as timer
from deap import base, creator, tools

from opt_helper import *
from opt_const import *
class opt_toobox():        
    def __init__(self,s_n,k_zero_list):
        self.k_zero=k_zero_list
        self.zero_len=0
        if (k_zero_list!=None):
            self.zero_len=len(k_zero_list)
            if not checkList0(s_n,self.k_zero):
                print("Input of s_n or ke_zero has errors")
                return
        else:
            self.k_zero=[]
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        # creator.create("Individual", array.array, typecode="d", fitness=creator.FitnessMin)
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        self.toolbox = base.Toolbox()
        # self.toolbox.register("map", futures.map)
        FLT_MIN_E, FLT_MAX_E = MIN_E, MAX_E
        FLT_MIN_K, FLT_MAX_K = MIN_K, MAX_K
        FLT_MIN_V, FLT_MAX_V = MIN_V, MAX_V
        self.s_n = s_n
        self.toolbox.register("attr_flt", random.random)
        self.toolbox.register("attr_flt_k", random.uniform, FLT_MIN_K, FLT_MAX_K)
        self.toolbox.register("attr_flt_v", random.uniform, FLT_MIN_V, FLT_MAX_V)
        ind_type=[]
        for _ in range(s_n):
            ind_type.append(self.toolbox.attr_flt)
        for _ in range(s_n*(s_n-1)-self.zero_len):
            ind_type.append(self.toolbox.attr_flt_k)
        for _ in range(s_n):
            ind_type.append(self.toolbox.attr_flt_v)
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                        tuple(ind_type), n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        # self.toolbox.decorate("mate", checkBounds(ind_range_min, ind_range_max))
        # self.toolbox.decorate("mutate", checkBounds(ind_range_min, ind_range_max))        
    def run(self,stopflag,q,ind_num=0,NGEN=n_gen,CXPB=cxpb,MUTPB=mutpb,topNum=top_num):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.ind_num=ind_num
        qO,qN=q
        s_n=self.s_n
        if ind_num==0:
            self.ind_num=20*s_n*(s_n+1)
        running=True
        pop=self.toolbox.population(n=self.ind_num)
        bestcs=3.2E32
        FLT_MIN_E, FLT_MAX_E = MIN_E, MAX_E
        FLT_MIN_K, FLT_MAX_K = MIN_K, MAX_K
        FLT_MIN_V, FLT_MAX_V = MIN_V, MAX_V
        ind_range_max=[]
        ind_range_min=[]
        for _ in range(s_n):
            ind_range_max.append(FLT_MAX_E)
            ind_range_min.append(FLT_MIN_E)
        for _ in range(s_n*(s_n-1)-self.zero_len):
            ind_range_max.append(FLT_MAX_K)
            ind_range_min.append(FLT_MIN_K)
        for _ in range(s_n):
            ind_range_max.append(FLT_MAX_V) 
            ind_range_min.append(FLT_MIN_V)        
        for gen in range(NGEN):
            # Select the next generation individuals
            tops=tools.selBest(pop, topNum)
            selNum=len(pop)-int(len(pop)/3)-topNum
            selected= self.toolbox.select(pop, selNum)
            newRandPop=self.toolbox.population(n=len(pop)-selNum-topNum)
            selected.extend(newRandPop)
            # Clone the selected individuals
            offspring = [self.toolbox.clone(ind) for ind in selected]
            # Apply crossover on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    self.toolbox.mate(child1, child2)
                    fixBounds(child1,ind_range_min, ind_range_max)
                    fixBounds(child2,ind_range_min, ind_range_max)
                    del child1.fitness.values
                    del child2.fitness.values
            # Apply mutation on the offspring
            for mutant in offspring:
                if random.random() < MUTPB:
                    self.toolbox.mutate(mutant)
                    fixBounds(mutant,ind_range_min, ind_range_max)                    
                    del mutant.fitness.values
            for tInd in tops:
                offspring.append(self.toolbox.clone(tInd))
            # # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            count=len(invalid_ind)
            print("sent count: ",count)
            for i in range(count):
                if stopflag.value>=1:
                    running=False
                    break
                realInd=genRealInd(self.s_n,invalid_ind[i],self.k_zero)
                
                ## qO.put() put compute parameter sets to the parameters sending queue.
                ## you should keep it in you own algorithm                 
                qO.put((i,realInd,bestcs))

            # The population is entirely replaced by the offspring
            count_r=0
            for _ in range(count):
                if stopflag.value>=1:
                    running=False
                    break
                ## qN.get() get compute result of each parameter set
                ## you should keep it in you own algorithm
                ii , ind_fit = qN.get()
                count_r=count_r+1
                # print("recv idx: ",ii, " tot_recv: ",count_r," ind_fit: ",ind_fit) 
                invalid_ind[ii].fitness.values=(ind_fit,)
            
            if not running or stopflag.value>=1:
                break
            pop[:] = offspring            
            for oi in offspring:
                # print(gen, " oi.fitness.values",oi.fitness.values)
                if (oi.fitness.valid):
                    if (oi.fitness.values[0])<bestcs:
                        bestcs=(oi.fitness.values[0])
            print("Gen ",gen," , best chisq: ", bestcs)
        # connOpt.close()
        print("Top 3 result:")
        top3=tools.selBest(pop, topNum)
        for t in top3:            
            print(genRealInd(self.s_n,t,self.k_zero))

if __name__ == '__main__':
    pass
