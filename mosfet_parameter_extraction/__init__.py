"""
=========
MOSFET PARAMETER EXTRACTION
=========

My Entity model template The System Development Kit
Used as a template for all TheSyDeKick Entities.

Current docstring documentation style is Numpy
https://numpydoc.readthedocs.io/en/latest/format.html

This text here is to remind you that documentation is important.
However, youu may find it out the even the documentation of this 
entity may be outdated and incomplete. Regardless of that, every day 
and in every way we are getting better and better :).

Initially written by Marko Kosunen, marko.kosunen@aalto.fi, 2017.

"""

import os
import sys
if not (os.path.abspath('../../thesdk') in sys.path):
    sys.path.append(os.path.abspath('../../thesdk'))

from thesdk import *
from rtl import *
from spice import *
import random

import numpy as np

class mosfet_parameter_extraction(rtl,spice,thesdk):

    def __init__(self,*arg): 
        self.print_log(type='I', msg='Inititalizing %s' %(__name__)) 
        self.proplist = [ 'Rs' ];    # Properties that can be propagated from parent
        self.Rs =  100e6;            # Sampling frequency
        self.IOS=Bundle()            # Pointer for input data
        self.IOS.Members['DRAIN'] = IO()
        self.IOS.Members['GATE'] = IO()
        self.IOS.Members['SOURCE'] = IO()
        self.IOS.Members['BULK'] = IO()
        self.IOS.Members['control_write'] = IO()
        self.vdd = 1.0
        self.model='py';             # Can be set externally, but is not propagated
        self.par= False              # By default, no parallel processing
        self.queue= []               # By default, no parallel processing
        self.kp=2.33082E-05
        self.lamda=0.013333
        self.vt0=0.69486
        self.gamma=0.60309
        self.phi=1
        self.tox=1.9800000E-08
        self.nsub=4.9999999E+16
        self.nss=0.0000000E+00
        self.cj=4.091E-4
        self.mj=0.307
        self.pb=1.0
        self.cjsw=3.078E-10
        self.mjsw=3.078e-10
        self.cgso=3.93e-10
        self.cgdo=3.93e-10
        self.vg=5
        self.vb=0
        self.vd=5


        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;

        self.init()

    def init(self):
        pass #Currently nohing to add

    def main(self):
        '''Guideline. Isolate python processing to main method.
        
        To isolate the interna processing from IO connection assigments, 
        The procedure to follow is
        1) Assign input data from input to local variable
        2) Do the processing
        3) Assign local variable to output

        '''
        inval=self.IOS.Members['DRAIN'].Data
        out=inval
        if self.par:
            self.queue.put(out)
        self.IOS.Members['SOURCE'].Data=out

    def run(self,*arg):
        '''Guideline: Define model depencies of executions in `run` method.

        '''
        if len(arg)>0:
            self.par=True      #flag for parallel processing
            self.queue=arg[0]  #multiprocessing.queue as the first argument
        if self.model=='py':
            self.main()
        else:
            if self.model in ['eldo','spectre','ngspice']:

                self.nproc = 2
                self.spiceoptions = {
                            'eps': '1e-6'
                        }
                self.spiceparameters = {
                            'sweep_vgs': self.vg,
                            'sweep_vds': self.vd,
                            'sweep_vss': 0,
                            'sweep_vbs': self.vb,
                            'param_KP':self.kp,
                            'param_lambda':self.lamda,
                            'param_vt0':self.vt0,
                            'param_gamma':self.gamma,
                            'param_phi':self.phi,
                            'param_tox':self.tox,
                            'param_nsub':self.nsub,
                            'param_nss':self.nss,
                            'param_cj':self.cj,
                            'param_mj':self.mj,
                            'param_pb':self.pb,
                            'param_cjsw':self.cjsw,
                            'param_mjsw':self.mjsw,
                            'param_cgso':self.cgso,
                            'param_cgdo':self.cgdo,


                        }

                # Defining library options
                # Path to model libraries needs to be defined in TheSDK.config as
                # either ELDOLIBFILE or SPECTRELIBFILE. In this case, no model libraries
                # will be included (assuming these variables are not defined). The
                # temperature will be set regardless.
                self.spicecorner = {
                            'corner': 'top_tt',
                            'temp': 27,
                        }

                # Example of defining supplies (not used here because the example inverter has no supplies)
                _=spice_dcsource(self,name='GSN',value='sweep_vgs',pos='G',neg='0',extract=True)
                _=spice_dcsource(self,name='DSN',value='sweep_vds',pos='D',neg='0',extract=True)
                _=spice_dcsource(self,name='SSN',value='sweep_vss',pos='S',neg='0',extract=True)
                _=spice_dcsource(self,name='BSN',value='sweep_vbs',pos='B',neg='0',extract=True)

                # Adding a resistor between VDD and VSS to demonstrate power consumption extraction
                # This also demonstrates how to inject manual commands in to the testbench
                if self.model=='spectre':
                    self.spicemisc.append('simulator lang=spice')
                #self.spicemisc.append('Rtest VDD VSS 2000')
                #self.spicemisc.append('VGSN G 0 sweep_vgs') 
                #self.spicemisc.append('VDSN D 0 sweep_vds') 
                #self.spicemisc.append('VSSN S 0 sweep_vss') 
                #self.spicemisc.append('VBSN B 0 sweep_vbs')

                ##raw file is only generated if not with the .control block
                #self.spicemisc.append('.dc vgsn 0 1.5 0.05 vbsn 0 -2.5 -0.5')
                #self.spicemisc.append('.dc vdsn 0 5 0.05 vgsn 0 5 0.05')
                #self.spicemisc.append('.op') ## will only spit out the values if in termianl if no -r
                #self.spicemisc.append('show all')

                #self.spicemisc.append('.control')
                #self.spicemisc.append('dc vgsn 0 1.5 0.05 vbsn 0 -2.5 -0.5')
                #self.spicemisc.append('dc vgsn 0 1.5 0.05 vbsn 0 -2.5 -0.5')
                #self.spicemisc.append("print vssn#branch") ##print alnd plot will only work if dc is within the control block
               
                #self.spicemisc.append("save vssn#branchl")
                #self.spicemisc.append("save all")
                #self.spicemisc.append("run")
                
                #self.spicemisc.append("save @m.Xmosfet_parameter_extraction.M1[vdsat]")
                
                if self.model=='spectre':
                    self.spicemisc.append('simulator lang=spectre')
                
                # Plotting nodes for interactive waveform viewing.
                # Spectre also supported, but without 'v()' specifiers.
                # i.e. plotlist = ['A','Z']
                if self.model == 'eldo':
                    plotlist = ['v(A)','v(Z)']
                elif self.model == 'spectre':
                    plotlist = ['A','Z']
                else:
                    plotlist = []

                # Simulation command
                #_=spice_simcmd(self,sim='tran',plotlist=plotlist)
                self.preserve_spicefiles=True
                self.preserve_iofiles=True
                self.interactive_spice=False
                if self.interactive_spice:
                    self.spicemisc.append("plot vssn#branch ylabel 'Id vs. Vgs, Vbs 0 ... -2.5'")
                #capture=['gm','gds','vgs','vth','vds','ids','cds','cdb','cgs','cgd','region','vsat']
                capture=['gm']
                base='Xmosfet_parameter_extraction'
                dev=['.M1']
                plotlist=[base+'%s[%s]' % (d,c) for d in dev for c in capture]
                plotlist=['m.Xmosfet_parameter_extraction.m1[gm]','m.Xmosfet_parameter_extraction.m1[vgs]','m.Xmosfet_parameter_extraction.m1[von]','m.Xmosfet_parameter_extraction.m1[vds]','m.Xmosfet_parameter_extraction.m1[id]']
                #mc=False
                #self.fmin=10
                #self.fmax=10e9
                #self.strobeperiod=100e6
                #self.noise=False
                #self.mc_seed=random.randint(100000,999999)

                _=spice_simcmd(self,sim='dc',plotlist=plotlist)
                

                #_=spice_simcmd(self,sim='dc',plotlist=plotlist,fmin=self.fmin,fmax=self.fmax,fscale='log',fstepsize=100,strobeperiod=self.strobeperiod,mc=mc,mc_seed=self.mc_seed,noise=self.noise)
                #_=spice_simcmd(sim='dc',sweep='',subcktname='mosfet_parameter_extraction',swpstart=0.1,swpstop=1.5,step=0.05)
                self.run_spice()
                self.gm=self.extracts.Members['oppts']['xmosfet_parameter_extraction']['gm']
                self.vgs=self.extracts.Members['oppts']['xmosfet_parameter_extraction']['vgs']
                self.vth=self.extracts.Members['oppts']['xmosfet_parameter_extraction']['von']
                self.vds=self.extracts.Members['oppts']['xmosfet_parameter_extraction']['vds']
                self.ids=self.extracts.Members['oppts']['xmosfet_parameter_extraction']['id']
                print('gm=',self.gm)
                print('vgs=',self.vgs)
                print('vth=',self.vth)
                print('vds=',self.vds)
                print('ids=',self.ids)
                                

            if self.par:
                self.queue.put(self.IOS.Members)

if __name__=="__main__":
    import argparse
    import matplotlib.pyplot as plt
    from  mosfet_parameter_extraction.signal_source import signal_source
    from  mosfet_parameter_extraction import *
    from  mosfet_parameter_extraction.controller import controller as mosfet_parameter_extraction_controller
    import pdb
    import math
    # Implement argument parser
    parser = argparse.ArgumentParser(description='Parse selectors')
    parser.add_argument('--show', dest='show', type=bool, nargs='?', const = True, 
            default=False,help='Show figures on screen')
    args=parser.parse_args()

    length=1024
    rs=100e6
    indata=np.cos(2*math.pi/length*np.arange(length)).reshape(-1,1)

    models=[ 'ngspice']
    #mosfet_supply=[0.01,0.1,1.8,3.3,5.0]
    mosfet_supply=[5.0]
    duts=[]
    plotters=[]
    gm_array=[]
    von_array=[]
    id_array=[]
    plt.figure()

    #######plotting transfer curve###########################
    for model in models:
        for vd in mosfet_supply:
            vg_voltage=np.linspace(0,10,50)
            for vg in vg_voltage: 
                d=mosfet_parameter_extraction()
                d.init()
                duts.append(d) 
                d.model=model
                d.Rs=rs 
                d.vg=vg
                d.vd=vd
                #pdb.set_trace()         
                d.run()
                gm_array.append(d.gm)
                von_array.append(d.vth)
                id_array.append(d.ids)
            plt.plot(vg_voltage.tolist(),np.asarray(id_array)/1e-3,label=str(vd))

    plt.legend(title='Vds')
    plt.xlabel('Vgs (V)')
    plt.ylabel('Ids (mA) ')
    plt.show()


