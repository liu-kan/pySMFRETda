import signal, os
from multiprocessing import Process, Value
import sys, argparse,multiprocessing
from msg import paramsServ
from opt import opt_toobox
ctrlc=0

def cmdargs():
    parser = argparse.ArgumentParser(description='A optimizing skeleton to provide parameters for gSMFRETda',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=
'''
Pls cite the 
work.
 
''')
    parser.add_argument('-p','--port',default='7777',help='listening port (default 7777)')
    parser.add_argument('-s','--s_n',default=3, type=int, help="states' number (default 3)")
    parser.add_argument('-g','--gen_num',default=1000, type=int, help="NGEN (default 1000)")
    parser.add_argument('-i','--ind_num',default=0, type=int, help="individual number of one gen")
    parser.add_argument('-k','--ke_zero', nargs="*", type=int, help="which K_{i,j} element are zero")    
    return parser.parse_args()
    
if __name__ == '__main__':
    stopFlag = Value('b', 0)
    args = cmdargs()
    # https://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
    # https://www.cloudcity.io/blog/2019/02/27/things-i-wish-they-told-me-about-multiprocessing-in-python/
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    qO  = multiprocessing.Queue()
    qN = multiprocessing.Queue()
    pServ = paramsServ(args.port,args.s_n,os.getpid())
    q=(qO,qN)
    paramsServ_p = Process(target=pServ.run, args=(stopFlag,q))
    optBox=opt_toobox(args.s_n, args.ke_zero)
    optBox_p=Process(target=optBox.run, args=(stopFlag,q,args.ind_num,args.gen_num))
    def exit_handler(signal_received, frame):
        global ctrlc
        ctrlc=ctrlc+1
        print("Ctrl+c press, program try to end gracefully! Press Ctrl+c twice to quit immediately.")
        stopFlag.value=1
        if ctrlc>1:
            stopFlag.value=2
            paramsServ_p.terminate()
            optBox_p.terminate()
            # time.sleep(1)
            sys.exit()
        # time.sleep(1)
    paramsServ_p.daemon = True
    optBox_p.daemon = True
    optBox_p.start()
    paramsServ_p.start()
    signal.signal(signal.SIGINT, original_sigint_handler)
    signal.signal(signal.SIGINT, exit_handler)
    paramsServ_p.join()
    print("paramsServ_p joined")
    if sys.platform == 'win32':
        optBox_p.terminate()
        print("optBox_p terminate")
    else:
        optBox_p.join()
        print("optBox_p joined")