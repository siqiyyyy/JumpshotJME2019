# import ROOT in batch mode
import sys
import time
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')

#default options
options.inputFiles="files.txt"
options.outputFile="mets.root"
options.maxEvents=-1

#overwrite if given any command line arguments
options.parseArguments()
#in case of txt input file, read the information from txt
li_f=[]
for iF,F in enumerate(options.inputFiles):
    print F
    if F.split('.')[-1] == "txt":
        options.inputFiles.pop(iF)
        with open(F) as f:
            li_f+=f.read().splitlines()
#add a prefix:
for ifilename,filename in enumerate(li_f):
    if filename[:6]=='/store':
        li_f[ifilename]='root://cmsxrootd.fnal.gov/'+filename
options.inputFiles+=li_f
print "analyzing files:"
for F in options.inputFiles: print F

# define deltaR
from math import hypot, pi, sqrt, fabs, cos, sin
import numpy as n

from jetmet_tree import *
from functions import *

# create an oput tree.

fout = ROOT.TFile (options.outputFile,"recreate")
t   = newEventTree()

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

#to print out the progress
def print_same_line(s):
    sys.stdout.write(s)                  # just print
    sys.stdout.flush()                    # needed for flush when using \x08
    sys.stdout.write((b'\x08' * len(s)).decode())# back n chars

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

vertex  , vertexLabel = Handle("std::vector<reco::Vertex>") , "offlineSlimmedPrimaryVertices" #for npv
rhoall_ , rhoallLabel = Handle("double")                    , "fixedGridRhoFastjetAll"          #for rhoall
muons   , muonLabel   = Handle("std::vector<pat::Muon>")    , "slimmedMuons"                   #muon collection
mets    , metLabel    = Handle("std::vector<pat::MET>")     , "slimmedMETs"                   #pf+chs met collection
pmets   , pmetLabel   = Handle("std::vector<pat::MET>")     , "slimmedMETsPuppi"              #pf+puppi met collection


events = Events(options)
nevents = int(events.size())
print "total events: ", events.size()

for ievent,event in enumerate(events):

        if options.maxEvents is not -1:
                if ievent > options.maxEvents: continue

        event.getByLabel(muonLabel, muons)
        event.getByLabel(metLabel, mets)
        event.getByLabel(pmetLabel, pmets)
        event.getByLabel(vertexLabel, vertex)
        event.getByLabel(rhoallLabel,rhoall_)

        npv[0]  = vertex.product().size()
        rhoall[0]        = rhoall_.product()[0]

        print_same_line(str(round(100.*ievent/nevents,2))+'%')

        #met information
        metprod   = mets.product().front()
        met[0]  = metprod.pt()
        genmet[0] = metprod.genMET().pt()
        rawmet[0] = metprod.uncorPt()

        #puppi met information
        pmetprod   = pmets.product().front()
        pmet[0] = pmetprod.pt()
        genpmet[0] = pmetprod.genMET().pt()
        rawpmet[0] = pmetprod.uncorPt()
        ###Reconstruct Z boson:
        nmuons = len(muons.product())
        Zvector = None
        if nmuons <2: continue
        muonCollection=[]
        for imu,mu in enumerate(muons.product()):
                if len(muonCollection)>1: continue
                if len(muonCollection)==0 and mu.pt() < 20: continue
                if len(muonCollection)==1 and mu.pt() < 10: continue
                if not mu.isLooseMuon(): continue
                if abs(mu.eta())>2.4: continue
                if mu.trackIso()/mu.pt()>0.10: continue #Loose working point ;
                muonCollection.append(mu.p4())
        if len(muonCollection)<2: continue
        mu1_pt[0]=muonCollection[0].pt()
        mu1_eta[0]=muonCollection[0].eta()
        mu1_phi[0]=muonCollection[0].phi()
        mu2_pt[0]=muonCollection[1].pt()
        mu2_eta[0]=muonCollection[1].eta()
        mu2_phi[0]=muonCollection[1].phi()
        Zvector=muonCollection[0]+muonCollection[1] #Sum of two muon Lerentz vectors
        h_Zmass.Fill(Zvector.M())
        if Zvector.M()<75 or Zvector.M()>105: continue
        Zmass[0]=Zvector.M()
        pfmetvector = mets.product().front().corP4()
        puppimetvector = pmets.product().front().corP4()
        pfrecoil = pfmetvector + Zvector
        puppirecoil = puppimetvector + Zvector
        qt[0] = Zvector.pt()
        q_eta[0] = Zvector.eta()
        u_pll_pf[0] = - pfrecoil.pt() * cos(Zvector.phi()-pfrecoil.phi())
        u_pll_puppi[0] = - puppirecoil.pt() * cos(Zvector.phi()-puppirecoil.phi())
        u_prp_pf[0] = pfmetvector.pt() * sin(Zvector.phi()-pfmetvector.phi())
        u_prp_puppi[0] = puppimetvector.pt() * sin(Zvector.phi()-puppimetvector.phi())
        t.Fill()
fout.Write()
fout.Close()
