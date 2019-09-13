import ROOT
import numpy as np

        #for assessing pileup
npv             = np.zeros(1,dtype=int)
rhoall   = np.zeros(1,dtype=float)

        #met information
met     = np.zeros(1,dtype=float)
genmet = np.zeros(1,dtype=float)
rawmet = np.zeros(1,dtype=float)
        #puppi met information
pmet    = np.zeros(1,dtype=float)
genpmet = np.zeros(1,dtype=float)
rawpmet = np.zeros(1,dtype=float)
        #for ZMM sample; met resolution:
qt              = np.zeros(1,dtype=float) # i.e. Z pt
q_eta   = np.zeros(1,dtype=float)
u_pll_pf = np.zeros(1,dtype=float) #u parallel
u_prp_pf = np.zeros(1,dtype=float) #u perpendicular
u_pll_puppi = np.zeros(1,dtype=float) #similar but for puppi mets
u_prp_puppi = np.zeros(1,dtype=float)

def newEventTree():
        t = ROOT.TTree("events","events")
        t.Branch("npv", npv, 'npv/I')
        t.Branch("rhoall", rhoall, 'rhoall/D')
        t.Branch("met", met, 'met/D')
        t.Branch("genmet", genmet, 'genmet/D')
        t.Branch("rawmet", rawmet, 'rawmet/D')
        t.Branch("pmet", pmet, 'pmet/D')
        t.Branch("genpmet", genpmet, 'genpmet/D')
        t.Branch("rawpmet", rawpmet, 'rawpmet/D')
        t.Branch("qt"             , qt            , 'qt/D')
        t.Branch("q_eta"           , q_eta         , 'q_eta/D')
        t.Branch("u_pll_pf"     , u_pll_pf      , 'u_pll_pf/D')
        t.Branch("u_prp_pf"     , u_prp_pf      , 'u_prp_pf/D')
        t.Branch("u_pll_puppi" , u_pll_puppi , 'u_pll_puppi/D')
        t.Branch("u_prp_puppi" , u_prp_puppi , 'u_prp_puppi/D')
        return t

def setBranchAddresses(t):
        t.SetBranchAddress("npv"                    , npv                    )
        t.SetBranchAddress("rhoall"                 , rhoall                 )
        t.SetBranchAddress("met"                    , met                    )
        t.SetBranchAddress("genmet"                 , genmet                 )
        t.SetBranchAddress("rawmet"                 , rawmet                 )
        t.SetBranchAddress("pmet"                   , pmet                   )
        t.SetBranchAddress("genpmet"                , genpmet                )
        t.SetBranchAddress("rawpmet"                , rawpmet                )
        t.SetBranchAddress("qt"                     , qt                     )
        t.SetBranchAddress("q_eta"                  , q_eta                  )
        t.SetBranchAddress("u_pll_pf"               , u_pll_pf               )
        t.SetBranchAddress("u_prp_pf"               , u_prp_pf               )
        t.SetBranchAddress("u_pll_puppi"            , u_pll_puppi            )
        t.SetBranchAddress("u_prp_puppi"            , u_prp_puppi            )
