# import ROOT in batch mode
import os,sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT
from math import sqrt
from array import array
import numpy as np
setTDRStyle()
ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

f_in = ROOT.TFile("mets.root","READ")
t_in = f_in.Get("events")

_pt = [0,10,20,25,30,40,50,60,80,100]
_npv = np.arange(20,64,4)
folder = "result"
os.system("mkdir -p "+folder)
os.system("mkdir -p "+folder+"/fit")

def get_met_params(rg): #given a phase space range, return response, sigma u_pll, sigma uprp, and their errors                                                                                             params={} #this dict is to be returned
    #get the responses
    #mean of upll devided by the mean of qt
    #do the same thing for both pf and puppi
    print "getting params in range: " + rg
    print "number of events in range: " + str(t_in.GetEntries(rg))
    _shape=np.arange(-200,200,5)
    shape_qt = ROOT.TH1F("shape_qt","shape_qt",len(_shape)-1,array('d',_shape))
    shape_pf = ROOT.TH1F("shape_pf","shape_pf",len(_shape)-1,array('d',_shape)) #this can be used to fill several different variables
    shape_puppi = ROOT.TH1F("shape_puppi","shape_puppi",len(_shape)-1,array('d',_shape)) #this can be used to fill several different variables
    t_in.Draw("qt>>shape_qt", rg)
    t_in.Draw("u_pll_pf>>shape_pf", rg)
    if shape_qt.GetMean()==0 or shape_pf.GetMean()==0: return None
    params["response_pf"]=abs(shape_pf.GetMean()/shape_qt.GetMean())
    params["response_pf_error"]=sqrt((shape_pf.GetMeanError()/shape_pf.GetMean())**2+(shape_qt.GetMeanError()/shape_qt.GetMean())**2) * params["response_pf"]
    t_in.Draw("u_pll_puppi>>shape_puppi",rg)
    if shape_puppi.GetMean()==0: return None
    params["response_puppi"]=abs(shape_puppi.GetMean()/shape_qt.GetMean())
    params["response_puppi_error"]=sqrt((shape_puppi.GetMeanError()/shape_puppi.GetMean())**2+(shape_qt.GetMeanError()/shape_qt.GetMean())**2) * params["response_puppi"]
    plot_hists([shape_qt,shape_pf,shape_puppi], legend_title_list=["q_{T}", "u_{||}(PF)","u_{||}(PUPPI)"], x_title="p_{T}(GeV)", y_title="Events/5GeV", plot_name="fit/qt_upll"+rg,text_description=rg)    t_in.Draw("u_pll_pf>>shape_pf",rg)
    if shape_pf.GetStdDev()<=0: return None
    params["sigma_pll_pf"]=shape_pf.GetStdDev()
    params["sigma_pll_pf_error"]=shape_pf.GetStdDevError()
    params["resolution_pll_pf"]=params["sigma_pll_pf"]/params["response_pf"]
    params["resolution_pll_pf_error"]=sqrt((params["sigma_pll_pf_error"]/params["sigma_pll_pf"])**2+(params["response_pf_error"]/params["response_pf"])**2)*params["resolution_pll_pf"]
    t_in.Draw("u_pll_puppi>>shape_puppi",rg)
    if shape_puppi.GetStdDev()<=0: return None
    params["sigma_pll_puppi"]=shape_puppi.GetStdDev()
    params["sigma_pll_puppi_error"]=shape_puppi.GetStdDevError()
    params["resolution_pll_puppi"]=params["sigma_pll_puppi"]/params["response_puppi"]                                                                                                                      params["resolution_pll_puppi_error"]=sqrt((params["sigma_pll_puppi_error"]/params["sigma_pll_puppi"])**2+(params["response_puppi_error"]/params["response_puppi"])**2)*params["resolution_pll_puppi"]
    t_in.Draw("u_prp_pf>>shape_pf",rg)
    if shape_pf.GetStdDev()<=0: return None
    params["sigma_prp_pf"]=shape_pf.GetStdDev()
    params["sigma_prp_pf_error"]=shape_pf.GetStdDevError()
    params["resolution_prp_pf"]=params["sigma_prp_pf"]/params["response_pf"]
    params["resolution_prp_pf_error"]=sqrt((params["sigma_prp_pf_error"]/params["sigma_prp_pf"])**2+(params["response_pf_error"]/params["response_pf"])**2)*params["resolution_prp_pf"]
    t_in.Draw("u_prp_puppi>>shape_puppi",rg)
    if shape_puppi.GetStdDev()<=0: return None
    params["sigma_prp_puppi"]=shape_puppi.GetStdDev()
    params["sigma_prp_puppi_error"]=shape_puppi.GetStdDevError()
    params["resolution_prp_puppi"]=params["sigma_prp_puppi"]/params["response_puppi"]                                                                                                                      params["resolution_prp_puppi_error"]=sqrt((params["sigma_prp_puppi_error"]/params["sigma_prp_puppi"])**2+(params["response_puppi_error"]/params["response_puppi"])**2)*params["resolution_prp_puppi"]
    plot_hists([shape_pf,shape_puppi], legend_title_list=["PF met","PUPPI MET"], x_title="u_{#perp}(GeV)", y_title="Events/5GeV", plot_name="fit/uprp"+rg,text_description=rg)
    return params

# Create one TMultigraph for each of the following measurement
mg_metResponse_pf = ROOT.TMultiGraph()
mg_metResolution_pf = ROOT.TMultiGraph()
#Loop through eta bins
for ieta in range(len(_eta)-1):
   sel_eta="qeta>"+str(_eta[ieta])+"&&qeta<"+str(_eta[ieta+1])
   leg_eta=str(_eta[ieta])+" < #eta < " + str(_eta[ieta+1])
   li_metResponse_pf = []
   li_metResponse_pf_error = []
   li_metResolution_pf = []
   li_metResolution_pf_error = []
   li_pt_center = []
   li_pt_halfwidth = []
   #loop through Z pt bins
   for ipt in range(len(_pt)-1):
      ptlow, pthigh = _pt[ipt], _pt[ipt+1]
      sel_qt="qt>"+str(_pt[ipt])+"&&qt<"+str(_pt[ipt+1])
      li_pt_center.append(0.5*ptlow + 0.5*pthigh)
      li_pt_halfwidth.append(0.5*pthigh-0.5*ptlow)
      params=get_params(sel_eta+"&&"+sel_qt)
      li_metResponse_pf.append(params["response_pf"])
      li_metResponse_pf_error.append(params["response_pf_error"])
      li_metResolution_pf.append(params["resolution_pll_pf"])
      li_metResolution_pf_error.append(params["resolution_pll_pf_error"])
   # transfer list into TGraph:
   npoints=len(li_pt_center)
   g_metResponse_pf = ROOT.TGraphErrors(npoints, li_pt_center, li_pt_halfwidth, li_metResponse_pf, li_metResponse_error)
   g_metResolution_pf = ROOT.TGraphErrors(npoints, li_pt_center, li_pt_halfwidth, li_metResponse_pf, li_metResponse_error)
   g_metResponse_pf.SetTitle(leg_eta)
   g_metResolution_pf.SetTitle(leg_eta)
   mg_metResponse_pf.Add(g_metResponse_pf)
   mg_metResolution_pf.Add(g_metResolution_pf)



# Make plot for the MET response
c1 = ROOT.TCanvas("c1","c1",800,800)
mg_Response_pf.Draw("AP")
c1.BuildLegend()
c1.Print("result/met_response.png")
# Make plot for the MET resolution
c2 = ROOT.TCanvas("c2","c2",800,800)
mg_Resolution_pf.Draw("AP")
c2.BuildLegend()
c2.Print("result/met_resolution.png")