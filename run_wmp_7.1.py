import os
import sys
import glob
import time
from multiprocessing import Pool
from contextlib import redirect_stdout
#
#import openmc
from multipole_deplete import *

neutron_dir = '/home/jiankai/codes/jingang-work/nucdata/endf-b-vii.1/neutrons'
#endf_files = [i for i in glob.glob(os.path.join(neutron_dir, "*.endf")) if os.path.isfile(i)]
endf_files = [i for i in glob.glob(os.path.join(neutron_dir, "*.endf")) if os.path.isfile(i)]
out_dir = "WMP_Lib"

print("Start processing {} nuclides - {}".format(len(endf_files), time.ctime()))

def process(endf_file):

    nuc_name = (IncidentNeutron.from_endf(endf_file)).name
    path_out = os.path.join(out_dir, nuc_name)
    if not os.path.exists(path_out):
        os.makedirs(path_out)

    # print message
    print("Processing {} - {} {} ".format(endf_file, nuc_name, time.ctime()))

    # run wmp
    time_start = time.time()
    wmp_file = os.path.join(out_dir, nuc_name+".h5")
    if os.path.exists(wmp_file):
        print("Existed file for {}, processing will be skipped.".format(wmp_file))
        return 
    try:
        if not os.path.isfile(wmp_file):
            mp_file = os.path.join(path_out, nuc_name+"_mp.pickle")
            if os.path.isfile(mp_file):
                with open(os.path.join(path_out, nuc_name+"_windowing.log"),'w') as f:
                    with redirect_stdout(f):
                        try:
                            nuc = WindowedMultipole.from_multipole(mp_file, search=True, log=True)
                        except:
                            try:
                                nuc = WindowedMultipole.from_multipole(mp_file, search=True, log=True, rtol=5e-3)
                            except:
                                nuc = WindowedMultipole.from_multipole(mp_file, search=True, log=2, rtol=1e-2)
            else:
                with open(os.path.join(path_out, nuc_name+".log"),'w') as f:
                    with redirect_stdout(f):
                        try:
                            nuc = WindowedMultipole.from_endf(endf_file,
                                   vf_options={"log":True, "path_out":path_out}, 
                                   wmp_options={"search":True, "log":True})
                        except:
                            nuc = WindowedMultipole.from_endf(endf_file,
                                   vf_options={"log":True, "rtol":5e-3, "path_out":path_out}, 
                                   wmp_options={"search":True, "rtol":5e-3, "log":True})
            nuc.export_to_hdf5(wmp_file)
        print('Done. {} {:.1f} s'.format(nuc_name, time.time()-time_start))
    except:
        print('Failed. {} {:.1f} s'.format(nuc_name, time.time()-time_start))

    sys.stdout.flush()

todo_files = []
for endf_file in endf_files:
    nuc_name = (IncidentNeutron.from_endf(endf_file)).name
    wmp_file = os.path.join(out_dir, nuc_name+".h5")
    if os.path.isfile(wmp_file):
        # print message
        time_start = time.time()
        print("Processing {} - {} {} ".format(endf_file, nuc_name, time.ctime()))
        print('Done. {} {:.1f} s'.format(nuc_name, time.time()-time_start))
    else:
        todo_files.append(endf_file)

print("{} nuclides to be processed - {}".format(len(todo_files), time.ctime()))

with Pool(44) as p:
   p.map(process, todo_files)

print("Finish processing all nuclides - {}".format(time.ctime()))

