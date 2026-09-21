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
                # Creating a clock signal, which is used for testing the sample output features
                #_=spice_iofile(self, name='GATE', dir='in', iotype='sample', ionames='G', rs=2*self.Rs, \
                #               vhi=self.vdd, trise=1/(self.Rs*8), tfall=1/(self.Rs*8))

                # Sample type input
                #_=spice_iofile(self, name='SOURCE', dir='out', iotype='sample', ionames='A', rs=self.Rs, \
                #               vhi=self.vdd, trise=1/(self.Rs*4), tfall=1/(self.Rs*4))

                # These are helper IOS for analog simulation
                #_=spice_iofile(self, name='SOURCE', dir='out', iotype='event', sourcetype='V', ionames='S')
                
                # Sample type output
                # Clock is used to sample the waveform in analog simulation
                #_=spice_iofile(self, name='Z', dir='out', iotype='sample', ionames='Z', trigger='CLK', \
                #               vth=self.vdd/2,edgetype='rising',ioformat='dec')
                

                # Saving the analog waveform of the input as well
                #_=spice_iofile(self, name='A_OUT', dir='out', iotype='event', sourcetype='V', ionames='A')

                # For Extracting rising edges from the output waveform
                #_=spice_iofile(self, name='Z_RISE', dir='out', iotype='time', sourcetype='V', ionames='Z', \
                #               edgetype='rising',vth=self.vdd/2)


                ## Extracting values of A and Z at falling edges of CLK in decimal format (integer, in this case 0 or 1)
                ## The clock signal can be any node voltage in the simulation
                #_=spice_iofile(self, name='A_DIG', dir='out', iotype='sample', ionames='A', trigger='CLK', \
                #               vth=self.vdd/2,edgetype='rising',ioformat='dec')

                # Multithreading, options and parameters
                self.nproc = 2
                self.spiceoptions = {
                            'eps': '1e-6'
                        }
                self.spiceparameters = {
                            'sweep_vgs': self.vdd,
                            'sweep_vds': self.vdd,
                            'sweep_vss': 0,
                            'sweep_vbs': 0,
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
                #_=spice_dcsource(self,name='gsn',value='sweep_vgs',pos='G',neg='0',extract=True)
                #_=spice_dcsource(self,name='dsn',value='sweep_vds',pos='D',neg='0')
                #_=spice_dcsource(self,name='ssn',value='sweep_vss',pos='S',neg='0',extract=True)
                #_=spice_dcsource(self,name='bsn',value='sweep_vbs',pos='B',neg='0',extract=True)

                # Adding a resistor between VDD and VSS to demonstrate power consumption extraction
                # This also demonstrates how to inject manual commands in to the testbench
                if self.model=='spectre':
                    self.spicemisc.append('simulator lang=spice')
                #self.spicemisc.append('Rtest VDD VSS 2000')
                self.spicemisc.append('VGSN G 0 sweep_vgs') 
                self.spicemisc.append('VDSN D 0 sweep_vds') 
                self.spicemisc.append('VSSN S 0 sweep_vss') 
                self.spicemisc.append('VBSN B 0 sweep_vbs')
                self.spicemisc.append('.control')
                self.spicemisc.append('dc vgsn 0 1.5 0.05 vbsn 0 -2.5 -0.5')
                self.spicemisc.append("plot vssn#branch ylabel 'Id vs. Vgs, Vbs 0 ... -2.5'")
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
                #_=spice_simcmd(self,sim='dc',plotlist=['*:vgs','*:id'],sweep='sweep_vgs',swpstart=0.1,swpstop=1.5,step=0.05)
                #_=spice_simcmd(sim='dc',sweep='',subcktname='mosfet_parameter_extraction',swpstart=0.1,swpstop=1.5,step=0.05)
                self.run_spice()

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
    duts=[]
    plotters=[]
    for model in models:
        d=mosfet_parameter_extraction()
        duts.append(d) 
        d.model=model
        d.Rs=rs
        #d.IOS.Members['GATE'].Data=indata
        d.init()
        d.run()

    pdb.set_trace()
    for k in range(len(duts)):
        hfont = {'fontname':'Sans'}
        figure,axes=plt.subplots(2,1,sharex=True)
        x = np.arange(length).reshape(-1,1)
        axes[0].plot(x,indata)
        axes[0].set_ylim(-1.1, 1.1);
        axes[0].set_xlim((np.amin(x), np.amax(x)));
        axes[0].set_ylabel('Input', **hfont,fontsize=18);
        axes[0].grid(True)
        axes[1].plot(x, duts[k].IOS.Members['Z'].Data)
        axes[1].set_ylim(-1.1, 1.1);
        axes[1].set_xlim((np.amin(x), np.amax(x)));
        axes[1].set_ylabel('Output', **hfont,fontsize=18);
        axes[1].set_xlabel('Sample (n)', **hfont,fontsize=18);
        axes[1].grid(True)
        titlestr = "mosfet model %s" %(duts[k].model) 
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        printstr="./inv_%s.eps" %(duts[k].model)
        plt.show(block=False);
        figure.savefig(printstr, format='eps', dpi=300);
    #This is here to keep the images visible
    #For batch execution, you should comment the following line 
    if args.show:
       input()
    #This is to have exit status for succesfuulexecution
    sys.exit(0)

