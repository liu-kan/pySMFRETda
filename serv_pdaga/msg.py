import time,os
import queue 
import random
from nanomsg import Socket, REP
from .protobuf import args_pb2
import signal,sys

class gpuClient:
    runTime=99999.9
    timeStamp=-1
    def __init__(self):
        self.timeStamp=time.perf_counter()
    def updateRunTime(self):
        self.runTime=time.perf_counter()-self.timeStamp
        self.timeStamp=time.perf_counter()
    def updateTimeStamp(self):
        self.timeStamp=time.perf_counter()

class paramsServ():
    def __init__(self, port: str ,s_n: int ,pid: int =None):
        self.port=port
        self.s_n=s_n
        self.ppid=pid
        self.bestcs=3.2E32
        print("paramsServ init with s_n",s_n,"port ",port)
        self.counter=0
    def run(self,stopflag,q):
        # signal.signal(signal.SIGINT, signal.SIG_IGN)
        qO,qN,qD=q
        print('tcp://*:'+self.port)
        s1 = Socket(REP)
        # s1.recv_buffer_size=1024*1024
        # s1.reconnect_interval_max=1000
        s1.bind('tcp://*:'+self.port)    
        pb_n=args_pb2.p_n()
        s_n=self.s_n
        ps_n=s_n*(s_n+1)
        pb_n.s_n=s_n
        # print("nanoMesg up")
        time.sleep(0.5)
        running=True
        pb_sid=args_pb2.p_sid()
        pb_sid.sid=0
        clients=dict()        
        sys_platform=sys.platform
        while(running):
            # print("loop start")
            if stopflag.value>len(clients.keys()):
                running=False
                break
            if sys_platform == 'win32':
                try:
                    recvstr=s1.recv()
                except KeyboardInterrupt:
                    if len(clients.keys())<=0:
                        running=False                        
                    elif stopflag.value>=0:
                        print("stopflag.value: ",stopflag.value)
                        with stopflag.get_lock():
                            stopflag.value+=1
                        continue             
                        # os.kill(self.ppid, signal.CTRL_C_EVENT)                    
            else:
                recvstr=s1.recv()
            # recvstr=s1.recv()
            # print(ord('c'),ord('p'),ord('r'),ord('k'),"recvstr[0]: ",recvstr[0])
            if recvstr[0]==ord('c'):
                pb_cap=args_pb2.p_cap()
                pb_cap.ParseFromString(recvstr[1:])
                # print("pb_cap.idx",pb_cap.idx)
                s1.send(pb_n.SerializeToString())
            elif recvstr[0]==ord('p'):
                pb_gpuid=args_pb2.p_str()
                pb_gpuid.ParseFromString(recvstr[1:])
                # TODO 解析  p_str get ohist
                if pb_gpuid.histNum>0:
                    # print(list(pb_gpuid.ohist))
                    qD.put((pb_gpuid.histNum,self.bestcs,list(pb_gpuid.ohist)))                    
                pb_ga=args_pb2.p_ga()
                pb_ga.start=0
                pb_ga.stop=-1
                ii=-1
                ind_=[]
                try:
                    ii , ind_ , self.bestcs= qO.get(False) #TODO change proto to allow ord('p') fail and retry later.                    
                except queue.Empty:
                    if stopflag.value >=1:
                        print("stopflag.value: ",stopflag.value)
                        pb_ga.idx=-2
                        stopflag.value+=1
                    else:
                        pb_ga.idx=-1
                    s1.send(pb_ga.SerializeToString())
                    continue
                # ind_=[random.random()]*(s_n*(s_n+1))
                pb_ga.idx=ii
                pb_ga.bestfv=self.bestcs
                for i in range(s_n):
                    pb_ga.params.append(ind_[i])
                for i in range(s_n*s_n-s_n):
                    pb_ga.params.append(ind_[i+s_n])
                for i in range(s_n):
                    pb_ga.params.append(ind_[i+s_n*s_n])
                s1.send(pb_ga.SerializeToString())
                # clients_lastTimeS[pb_ga.idx]=time.perf_counter()
                # print("p: ",clients_lastTimeS[pb_ga.idx])
                if pb_gpuid.str not in clients:
                    clients[pb_gpuid.str]=gpuClient()
                    print(pb_gpuid.str," connected.")
                else:
                    clients[pb_gpuid.str].updateTimeStamp()
            elif recvstr[0]==ord('r'):
                res=args_pb2.res()
                res.ParseFromString(recvstr[1:])
                # print("res chi2 recv",res.e, " ridx: ",res.ridx)
                if stopflag.value >=1:
                    pb_sid.sid=-1                    
                    print("time spend: ",clients.pop(res.idx).runTime)
                    if len(clients.keys())<=0:
                        running=False
                    # print("stopflag: ",stopflag.value)
                    # s1.close() 
                s1.send(pb_sid.SerializeToString())
                # print("pb_sid send",pb_sid.sid, " ridx: ",res.ridx)
                if res.idx in clients:
                    clients[res.idx].updateRunTime()
                #TODO 解析res get shist           
                qN.put((res.ridx,res.e))
                if res.hist:
                    # self.counter=self.counter+1
                    # print(self.counter,self.bestcs)
                    if self.bestcs<3.2E31:
                        qD.put((-1,self.bestcs,list(res.shist)))
                    
            elif recvstr[0]==ord('k'):
                pidx=args_pb2.p_sid()
                pidx.ParseFromString(recvstr[1:])
                # print("keepalive: ",pidx.sid)
                s1.send('l')
            else:
                print("Err recv: ",recvstr[0])
        s1.close()
        qN.close()
        qD.close()
        qN.join_thread()
        qD.join_thread()
        print("paramsServ done!")