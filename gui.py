import numpy as np
import queue
from dearpygui.core import *
from dearpygui.simple import *
# add_additional_font("ui/NotoSansSC-Regular.otf", 20, glyph_ranges="chinese_full")
from serv_pdaga.msg import paramsServ
from serv_pdaga.opt import opt_toobox
from multiprocessing import Process,Value
import time,multiprocessing,threading,sys
import time, datetime

class pServGui:

    def __init__(self,mainWinW=1024,mainWinH=760,lPad=2):
        self.logID="xSMFRETda conosle"
        self.lPad=lPad
        self.statesNum=2        
        self.mainWinH=mainWinH
        self.mainWinW=mainWinW
        set_main_window_size(self.mainWinW,self.mainWinH )
        qO  = multiprocessing.Queue()
        qN = multiprocessing.Queue()
        self.qD = multiprocessing.Queue()
        self.q=(qO,qN,self.qD)
        self.stopFlag = Value('b', 0)
        self.joined=False
        self.render_counter=0
        self.histNum=0
        self.fitGoodTime=600
        self.tzoffset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        self.bestf=[]
        self.timelist=[]        

    def get_ke_zero(self):
        ke_zero=[]
        for i in range(self.statesNum):
            for j in range(self.statesNum):
                if i!=j:     
                    idlable="?##rm_"+str(i)+"_"+str(j)
                    if get_value(idlable):
                        ke_zero.append(i*self.statesNum+j+1)
        return ke_zero    

    def stop_callback(self,sender, callback):
        configure_item("Stop", enabled=False)
        set_item_label("Stop","Stopping, wait 4 min")
        self.stopFlag.value=1
        self.joinThr.join(60)
        if self.joinThr.is_alive():
            self.paramsServ_p.terminate()
            self.optBox_p.terminate()
            self.joinThr.join(6)

        self.enableInput(True)
        set_item_label("Stop","Stop")
        
    def enableInput(self,enable):
        configure_item("Start", enabled=enable)
        configure_item("##port", enabled=enable)
        configure_item("##indNum", enabled=enable)
        configure_item("##maxGen", enabled=enable)
        configure_item("##state", enabled=enable)
        for i in range(self.statesNum):
            for j in range(self.statesNum):
                if not i==j:     
                    idlable="?##rm_"+str(i)+"_"+str(j)
                    configure_item(idlable,enabled=enable)      

    def start_callback(self,sender, callback):
        # show_logger()
        log_info("=============",logger=self.logID)
        log_info(str(get_value("##maxGen")),logger=self.logID)    
        log_info("Listening "+str(get_value("##port")),logger=self.logID)
        log_info("StatesNum "+str(self.statesNum),logger=self.logID)
        self.stopFlag.value=0
        self.pServ = paramsServ(str(get_value("##port")),self.statesNum)
        self.paramsServ_p = Process(target=self.pServ.run, args=(self.stopFlag,self.q))
        self.ke_zero=self.get_ke_zero()
        self.optBox=opt_toobox(self.statesNum, self.ke_zero)
        self.optBox_p=Process(target=self.optBox.run, args=(self.stopFlag,self.q,get_value("##indNum"),get_value("##maxGen")))
        self.paramsServ_p.daemon = True
        self.optBox_p.daemon = True
        self.optBox_p.start()
        self.paramsServ_p.start()
        self.joined=False
        configure_item("Stop", enabled=True)   
        # configure_item("Start", enabled=False)
        self.enableInput(False)
        self.joinThr=threading.Thread(target=self.joinProcesses)#, args=(1,)
        self.joinThr.start()
        
    def joinProcesses(self):
        pJoined=False
        oJoined=False
        while not self.joined:
            # log_debug("joinning",logger=self.logID)            
            while not (oJoined or pJoined):
                self.paramsServ_p.join(5)
                if self.paramsServ_p.exitcode!=None:
                    pJoined=True
                self.optBox_p.join(5)
                if self.optBox_p.exitcode!=None:
                    oJoined=True
            if not oJoined:
                if sys.platform == 'win32':
                    self.optBox_p.terminate()
                    print("optBox_p terminate")
                    self.joined=True
                else:
                    self.optBox_p.join(6)
                    if self.optBox_p.exitcode==None:
                        self.optBox_p.terminate()
                        print("optBox_p terminate")
                        self.joined=True
            if not pJoined:
                if sys.platform == 'win32':
                    self.paramsServ_p.terminate()
                    print("paramsServ_p terminate")
                    self.joined=True
                else:
                    self.paramsServ_p.join(6)
                    if self.paramsServ_p.exitcode==None:
                        self.paramsServ_p.terminate()
                        print("paramsServ_p terminate")
        self.enableInput(True)
        configure_item("Stop", enabled=False)
        set_item_label("Stop","Stop")        
    '''
    def query(self,sender, data):
        show_item("Plot Window")
        set_plot_xlimits("Plot2", data[0], data[1])
        set_plot_ylimits("Plot2", data[2], data[3])
    def table_printer(self,sender, data):
        log_debug(f"Table Called: {sender}",logger=self.logID)
        coord_list = get_table_selections("k_ij_table",logger=self.logID)
        log_debug(f"Selected Cells (coordinates): {coord_list}",logger=self.logID)
        names = []
        for coordinates in coord_list:
            names.append(get_table_item("k_ij_table", coordinates[0], coordinates[1]))
        log_debug(names,logger=self.logID)
        ht=get_item_configuration("k_ij_table")
        print(ht)
        configure_item("k_ij_table", hide_headers=not ht['hide_headers'])
    '''

    def rateMat_callback(self,sender, data):
        if get_value(sender):
            # ol=get_item_label(sender)
            # nl=ol.replace("?","0",1)
            set_item_label(sender,"0")
        else:
            # ol=get_item_label(sender)
            # nl=ol.replace("0","?",1)
            set_item_label(sender,"?")
        log_debug(f"{sender} ran a callback its value is {get_value(sender)}",logger=self.logID)

    def add_matrix_inp(self,size):
        with managed_columns("k_ij_table##cs", size,parent="input_Panel",before="##sep_after_matrix"):
            for i in range(size):
                for j in range(size):
                    if i==j:     
                        add_text("?")
                    else:
                        idlable="?##rm_"+str(i)+"_"+str(j)
                        add_selectable(idlable,span_columns=False,callback=self.rateMat_callback)

    def state_num_callback(self,sender, data):
        log_debug(f"{sender} ran a callback its value is {get_value(sender)}",logger=self.logID)
        n=get_value("##state")
        log_info("Number of state "+str(n),logger=self.logID)
        delete_item("k_ij_table##cs")
        self.add_matrix_inp(n)        
        if n>self.statesNum:
            self.moveLoggerWindow(False)
        else:
            self.moveLoggerWindow(False,False)
        self.statesNum=n

    def moveLoggerWindow(self,force=False,bigger=True):
        p0=get_window_pos("log_window")
        if force or abs(p0[0])<=10:
            h=get_item_height("input_Panel")
            if force:
                H=h+112
            elif bigger:
                H=h+20
            else:
                H=h-7
            set_window_pos("log_window",0,H)
            set_item_height("log_window",self.mainWinH-H-50)

    def drawHist(self):
        '''
        qD=(ii,histList)
        ii = 0 no data
        ii = 1 histList has mcHist
        ii > 1 histList has oHist , ii = histNum
        '''
        ii=0
        bestcs=3.2E32
        try:
            ii , bestcs, histList = self.qD.get(False)
            # print(bestcs)
        except queue.Empty:
            return
        clear_plot("Fittness")
        if ii>0:
            if self.histNum!=ii:
                self.histNum=ii-self.lPad
                self.bin_edges=np.linspace(0,1.0,ii)[self.lPad:]
            self.oHist=histList[self.lPad:]
            add_shade_series("Fittness","FRET data",self.bin_edges.tolist(),self.oHist)  
            self.bestf.clear()
            self.timelist.clear()
            dtime = datetime.datetime.now()
            localts=time.mktime(dtime.timetuple())-self.tzoffset            
            set_plot_xlimits("Fit_Goodness",localts,localts+60*2)
        elif ii==-1:
            clear_plot("Fit_Goodness")
            dtime = datetime.datetime.now()                      
            localts=time.mktime(dtime.timetuple())-self.tzoffset
            self.timelist.append( localts)
            add_shade_series("Fittness","FRET data",self.bin_edges.tolist(),self.oHist)
            add_line_series("Fittness","Simulation data",self.bin_edges.tolist(),histList[self.lPad:],
                        color=(1, 1, 1, -1),weight=2) 
            self.bestf.append(bestcs)
            print(len(self.timelist))
            print(self.bestf)            
            set_plot_xlimits("Fit_Goodness",self.timelist[0],self.timelist[-1]+60)
            set_plot_ylimits("Fit_Goodness",min(self.bestf),max(self.bestf))
            add_line_series("Fit_Goodness","Fit Goodness",self.timelist,self.bestf,
                        color=(255, 255, 0),weight=3)             
    def render_timer(self,sender,data):
        self.render_counter=self.render_counter+1
        if self.render_counter %30==0:
            self.drawHist()

    def showGUI(self):
        with window("fit_Window",width=777,height=450,x_pos=232,y_pos=0):
            add_plot("Fittness", height=-1)
        with window("fitGoodness_Window",width=777,height=255,x_pos=232,y_pos=453):
            add_plot("Fit_Goodness", height=-1,xaxis_time=True)

        with window("log_window",width=230):
            add_logger(self.logID,autosize_x=True,autosize_y=True)

        with window("input_Panel", width=230,autosize=True,x_pos=0,y_pos=0): 
            add_text("Setup parameters first.", bullet=True)
            add_text("Press the 'Start' to run.", wrap=220, bullet=True)
            add_text("Listening port")
            add_input_int("##port",default_value=7777,min_value=1,max_value=65535)
            add_text("Number of state")
            add_slider_int("##state", default_value=self.statesNum, min_value=1, max_value=8, callback=self.state_num_callback) #TODO set it to 0, means auto det
            add_text("Max generations")
            add_input_int("##maxGen",default_value=1000,min_value=3,max_value=9999)
            add_text("Individual # in one generation")
            add_input_int("##indNum",default_value=0,min_value=0,max_value=3600,
                            tip="Use 0 to auto calculate individual size")
            add_text("Which K_{i,j} element are zero")
            #add_input_text("##kZero", multiline=True)
            # add_table("k_ij_table",["1","2"],callback=table_printer)
            # add_row("k_ij_table", ["?", "?"])
            # add_row("k_ij_table", ["?", "?"])
            # try:
            #     configure_item("k_ij_table", hide_headers=True)
            # except:
            #     pass             
            add_separator()
            add_separator(name="##sep_after_matrix")
            self.add_matrix_inp(self.statesNum)    
            add_button("Start", callback=self.start_callback)
            add_same_line()
            add_button("Stop", callback=self.stop_callback,enabled=False)

        set_main_window_title("pySMFRETda")
        # set_logger_window_title("xSMFRETda conosle")
        # show_logger()
        enable_docking(shift_only=True,dock_space=True)
        # start_dearpygui(primary_window="Main Window")
        self.moveLoggerWindow(True)
        set_render_callback(self.render_timer)
        start_dearpygui()