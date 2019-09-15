# import ROOT in batch mode
import os,sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT
from math import sqrt
from array import array
import numpy as np
ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

f_in = ROOT.TFile("mets.root","READ")
t_in = f_in.Get("events")

_pt = [0,10,20,25,30,40,50,60,80,100]
_npv = [0,20,40,80]
folder = "result"
os.system("mkdir -p "+folder)
os.system("mkdir -p "+folder+"/fit")
ROOT.gStyle.SetOptStat(0) 


# A simple function to plot multiple histograms into one plot
def plot_hists(hist_list, title="", legend_title_list=None, x_title="", y_title="", text_description=None, plot_name=None, limits=None):
	colors=[ROOT.kCyan+1,ROOT.kBlue+1,ROOT.kMagenta+1,ROOT.kRed+1,ROOT.kOrange,ROOT.kYellow+1,ROOT.kGreen+1,ROOT.kGray]
	canv = ROOT.TCanvas("canv","canv")
	mg=ROOT.TMultiGraph() #Use a multiGraph to auto adjust the frame size:
	mg.SetTitle(title+"; "+x_title+"; "+y_title+";") 
	if len(hist_list)>0:
		for ihist,hist in enumerate(hist_list):
			hist.SetLineWidth(2)
			hist.SetMarkerStyle(1)
			hist.SetMarkerSize(0.8)
			hist.SetLineColor(colors[ihist])
			mg.Add(ROOT.TGraphErrors(hist))
	if limits != None:
		mg.SetMinimum(limits[0])
		mg.SetMaximum(limits[1])
	mg.Draw("AP")
	if(text_description):
		latex = ROOT.TLatex()
		latex.SetNDC()
		latex.SetTextSize(0.4*canv.GetTopMargin())
		latex.SetTextFont(42)
		latex.SetTextAlign(31) # align right
		latex.DrawLatex(0.90, 0.93,text_description)
		latex.Draw("same")
	if legend_title_list==None:
		legend_title_list = [i.GetTitle() for i in hist_list]
	legend=ROOT.TLegend(0.60,0.80,0.95,.91)
	for ihist,hist in enumerate(hist_list):
		legend.AddEntry(hist,legend_title_list[ihist],"lp")
	legend.Draw("same")
	if plot_name==None:
		plot_name=base_hist.GetTitle().replace("_pf","").replace("_puppi","")
	canv.Print(folder+"/"+plot_name+".png")




def get_met_params(rg): #given a phase spacific range, return response, resolution, and their errors
	params={} # we will fill this dict and return it

	print "getting params in range: " + rg
	print "number of events in range: " + str(t_in.GetEntries(rg))
	if t_in.GetEntries(rg) < 5:
		print "Warning: number of entries too smale in this region, abort"
		return None
	
	# Histograms to be filled
	_pt_shape=np.arange(-200,200,5)
	_ratio_shape=np.arange(-3.,5.,0.02)
	shape_pf_response = ROOT.TH1F("shape_pf_response","shape_pf_response",len(_ratio_shape)-1,array('d',_ratio_shape))
	shape_puppi_response = ROOT.TH1F("shape_puppi_response","shape_puppi_response",len(_ratio_shape)-1,array('d',_ratio_shape))
	shape_pf_pll = ROOT.TH1F("shape_pf_pll","shape_pf_pll",len(_pt_shape)-1,array('d',_pt_shape)) 
	shape_puppi_pll = ROOT.TH1F("shape_puppi_pll","shape_puppi_pll",len(_pt_shape)-1,array('d',_pt_shape))
	shape_pf_prp = ROOT.TH1F("shape_pf_prp","shape_pf_prp",len(_pt_shape)-1,array('d',_pt_shape)) 
	shape_puppi_prp = ROOT.TH1F("shape_puppi_prp","shape_puppi_prp",len(_pt_shape)-1,array('d',_pt_shape))

	# Fill histograms
	t_in.Draw("-u_pll_pf/qt>>shape_pf_response",rg)
	t_in.Draw("-u_pll_puppi/qt>>shape_puppi_response",rg)
	t_in.Draw("u_pll_pf+qt>>shape_pf_pll",rg)
	t_in.Draw("u_pll_puppi+qt>>shape_puppi_pll",rg)
	t_in.Draw("u_prp_pf+qt>>shape_pf_prp",rg)
	t_in.Draw("u_prp_puppi+qt>>shape_puppi_prp",rg)


	#Obtain the parameters
	#For simplicity we are taking directly the mean and RMS of histograms here
	#But to do it more accurately you would want to do a fit
	params["response_pf"] = shape_pf_response.GetMean()
	params["response_pf_error"] = shape_pf_response.GetMeanError()
	params["response_puppi"] = shape_puppi_response.GetMean()
	params["response_puppi_error"] = shape_puppi_response.GetMeanError()
	params["resolution_pll_pf"] = shape_pf_pll.GetRMS() / params["response_pf"]
	params["resolution_pll_pf_error"] = sqrt( pow(shape_pf_pll.GetRMSError(),2) + pow( params["resolution_pll_pf"]*params["response_pf_error"]/params["response_pf"],2))
	params["resolution_pll_puppi"] = shape_puppi_pll.GetRMS() / params["response_puppi"]
	params["resolution_pll_puppi_error"] = sqrt( pow(shape_puppi_pll.GetRMSError(),2) + pow( params["resolution_pll_puppi"]*params["response_puppi_error"]/params["response_puppi"],2))
	params["resolution_prp_pf"] = shape_pf_prp.GetRMS() / params["response_pf"]
	params["resolution_prp_pf_error"] = sqrt( pow(shape_pf_prp.GetRMSError(),2) + pow( params["resolution_prp_pf"]*params["response_pf_error"]/params["response_pf"],2))
	params["resolution_prp_puppi"] = shape_puppi_prp.GetRMS() / params["response_puppi"]
	params["resolution_prp_puppi_error"] = sqrt( pow(shape_puppi_prp.GetRMSError(),2) + pow( params["resolution_prp_puppi"]*params["response_puppi_error"]/params["response_puppi"],2))

	plot_hists([shape_pf_response,shape_puppi_response], legend_title_list=["PF met","PUPPI MET"], x_title="-u_{||}/q_{T}", y_title="Events", plot_name="fit/response_"+rg,text_description=rg)
	plot_hists([shape_pf_pll,shape_puppi_pll], legend_title_list=["PF met","PUPPI MET"], x_title="u_{||}+q_{T}", y_title="Events", plot_name="fit/pll_"+rg,text_description=rg)
	plot_hists([shape_pf_prp,shape_puppi_prp], legend_title_list=["PF met","PUPPI MET"], x_title="u_{#perp}", y_title="Events", plot_name="fit/prp_"+rg,text_description=rg)
	return params

# Create histograms to store the parameters
h_response_pf = ROOT.TH1F("h_response_pf","pf met scale",len(_pt)-1,array('d',_pt))
h_response_puppi = ROOT.TH1F("h_response_puppi","puppi met scale",len(_pt)-1,array('d',_pt))
h_resolution_pll_pf = ROOT.TH1F("h_resolution_pll_pf","pf met resolution parallel",len(_pt)-1,array('d',_pt))
h_resolution_pll_puppi = ROOT.TH1F("h_resolution_pll_puppi","puppi met resolution parallel",len(_pt)-1,array('d',_pt))
#loop through Z pt bins
for ipt in range(len(_pt)-1):
	ptlow, pthigh = _pt[ipt], _pt[ipt+1]
	sel_qt="qt>"+str(_pt[ipt])+"&&qt<"+str(_pt[ipt+1])
	params=get_met_params(sel_qt)
	if params:
		#print(sel_qt)
		#print(params)
		h_response_pf.SetBinContent(ipt+1,params["response_pf"])
		h_response_pf.SetBinError(ipt+1,params["response_pf_error"])
		h_response_puppi.SetBinContent(ipt+1,params["response_puppi"])
		h_response_puppi.SetBinError(ipt+1,params["response_puppi_error"])
		h_resolution_pll_pf.SetBinContent(ipt+1,params["resolution_pll_pf"])
		h_resolution_pll_pf.SetBinError(ipt+1,params["resolution_pll_pf_error"])
		h_resolution_pll_puppi.SetBinContent(ipt+1,params["resolution_pll_puppi"])
		h_resolution_pll_puppi.SetBinError(ipt+1,params["resolution_pll_puppi_error"])
	else:
		#in case return value is none, possibly no stat in this region
		#you can do something about it like setting big error bars
		continue


ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)

# Make plot for the MET response
c1 = ROOT.TCanvas("c1","c1",800,800)
h_response_pf.SetLineColor(ROOT.kRed)
h_response_pf.SetAxisRange(0,1.5,"Y")
h_response_pf.GetXaxis().SetTitle("q_{T}/GeV")
h_response_pf.GetYaxis().SetTitle("u_{||}/q_{T}")
h_response_pf.Draw()
h_response_puppi.SetLineColor(ROOT.kBlue)
h_response_puppi.Draw("same")
leg1=ROOT.TLegend(0.55,0.1,0.9,0.3)
leg1.AddEntry(h_response_pf,"PF+CHS MET")
leg1.AddEntry(h_response_puppi,"PUPPI MET")
leg1.Draw("same")
c1.Print("result/met_response.png")
# Make plot for the MET resolution
c2 = ROOT.TCanvas("c2","c2",800,800)
h_resolution_pll_pf.SetLineColor(ROOT.kRed)
h_resolution_pll_pf.SetAxisRange(0,50,"Y")
h_resolution_pll_pf.GetXaxis().SetTitle("q_{T}/GeV")
h_resolution_pll_pf.GetYaxis().SetTitle("RMS(u_{||}+q_{T})")
h_resolution_pll_pf.Draw()
h_resolution_pll_puppi.SetLineColor(ROOT.kBlue)
h_resolution_pll_puppi.Draw("same")
leg2=ROOT.TLegend(0.55,0.1,0.9,0.3)
leg2.AddEntry(h_resolution_pll_pf,"PF+CHS MET")
leg2.AddEntry(h_resolution_pll_puppi,"PUPPI MET")
leg2.Draw("same")
c2.Print("result/met_resolution_pll.png")
