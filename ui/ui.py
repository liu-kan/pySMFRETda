from scipy.io import loadmat
import numpy as np

from dearpygui.core import *
from dearpygui.simple import *
# add_additional_font("NotoSansSC-Regular.otf", 20, glyph_ranges="chinese_full")

mainWinH=1000
mainWinW=1920
set_main_window_size(mainWinW,mainWinH )
logID="xSMFRETda conosle"

x = loadmat('xj.mat')
hist, bin_edges = np.histogram(x['x'],100)
hist1=hist+np.random.rand(1,hist.size)*np.mean(hist)*.1
# callback
def retrieve_callback(sender, callback):
    # show_logger()
    log_info("=============",logger=logID)
    log_info(str(get_value("##maxGen")),logger=logID)    
    log_info("Listening "+str(get_value("##port")),logger=logID)

def query(sender, data):
    show_item("Plot Window")
    set_plot_xlimits("Plot2", data[0], data[1])
    set_plot_ylimits("Plot2", data[2], data[3])
def table_printer(sender, data):
    log_debug(f"Table Called: {sender}",logger=logID)
    coord_list = get_table_selections("k_ij_table",logger=logID)
    log_debug(f"Selected Cells (coordinates): {coord_list}",logger=logID)
    names = []
    for coordinates in coord_list:
        names.append(get_table_item("k_ij_table", coordinates[0], coordinates[1]))
    log_debug(names,logger=logID)
    ht=get_item_configuration("k_ij_table")
    print(ht)
    configure_item("k_ij_table", hide_headers=not ht['hide_headers'])
    
def log_callback(sender, data):
    log_debug(f"{sender} ran a callback its value is {get_value(sender)}",logger=logID)

def state_num_callback(sender, data):
    log_debug(f"{sender} ran a callback its value is {get_value(sender)}",logger=logID)
    log_info("Number of state "+str(),logger=logID)
    delete_item("k_ij_table##cs")
    add_matrix_inp(get_value("##state"))

with window("fit_Window",width=800,height=700,x_pos=232,y_pos=0):

    add_same_line()
    add_plot("Fittness", height=-1)
    add_shade_series("Fittness","FRET",bin_edges[1:].tolist(),hist.tolist())
    print(len(bin_edges[1:].tolist()),len(hist1.tolist()))
    add_line_series("Fittness","Fittness",bin_edges[1:].tolist(),hist1.tolist()[0],
                    color=(1, 1, 1, -1),weight=2)

with window("log_window",width=230):
    add_logger(logID,autosize_x=True,autosize_y=True)

def add_matrix_inp(size):
    with managed_columns("k_ij_table##cs", size,parent="input_Panel",before="##sep_after_matrix"):
        for i in range(size):
            for j in range(size):
                if i==j:     
                    add_text("?")
                else:
                    idlable="?##"+str(i)+" "+str(j)
                    add_selectable(idlable,span_columns=False,callback=log_callback)

with window("input_Panel", width=230,autosize=True,x_pos=0,y_pos=0): 
    add_text("Setup parameters first.", bullet=True)
    add_text("Press the 'Start' to run.", wrap=220, bullet=True)
    add_text("Listening port")
    add_input_int("##port",default_value=7777,min_value=1,max_value=65535)
    add_text("Number of state")
    add_slider_int("##state", default_value=2, min_value=1, max_value=8, callback=state_num_callback) #TODO set it to 0, means auto det
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
    add_matrix_inp(2)    
    add_button("Start", callback=retrieve_callback)

set_main_window_title("pySMFRETda")
# set_logger_window_title("xSMFRETda conosle")
# show_logger()
enable_docking(shift_only=True,dock_space=True)
# start_dearpygui(primary_window="Main Window")

h=get_item_height("input_Panel")
set_window_pos("log_window",0,h+112)
set_item_height("log_window",mainWinH-(h+112)-50)

print(h)
start_dearpygui()



