''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', action='store', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], default='INFO', help="Log level for logging")
argParser.add_argument('--mode', default='dilepton', action='store', choices=['doubleMu', 'doubleEle', 'muEle', 'dilepton', 'sameFlavour'])
argParser.add_argument('--charges', default='OS', action='store', choices=['OS', 'SS'])
argParser.add_argument('--zMode', default='offZ', action='store', choices=['onZ', 'offZ', 'allZ'])
argParser.add_argument('--noData', action='store_true', help='Skip data', )
argParser.add_argument('--small', action='store_true', help='Small?', )
argParser.add_argument('--PR', action='store_true',  help='PR?', )
argParser.add_argument('--dPhi', action='store', default = 'def', choices=['def', 'inv', 'none', 'lead'], help='dPhi?', )
argParser.add_argument('--loop', action='store_true', help='Loop all cuts?', )
argParser.add_argument('--trigger', action='store_true', help='Apply trigger?', )
argParser.add_argument('--dPhiLepMET', action='store_true', help='Apply lepton/MET d-phi cut?', )
argParser.add_argument('--lowMT2ll', action='store', type=int, default = 0, help='low mt2ll?', )
argParser.add_argument('--highMT2ll', action='store', type=int, default = 1000, help='high mt2ll?', )
argParser.add_argument('--lowMET', action='store', type=int, default = 0, help='low met?', )
argParser.add_argument('--highMET', action='store', type=int, default = 1000, help='high met?', )
argParser.add_argument('--splitDiBoson', action='store_true', help='splitDiBoson?', )
argParser.add_argument('--noScaling', action='store_true', help='no scaling?', )
argParser.add_argument('--reversed', action='store_true', help='Reversed?', )
argParser.add_argument('--njet', default='2p', type=str, action='store', choices=['0', '0p', '1', '1p', '2', '2p', '01'])
#argParser.add_argument('--mIsoWP', default=5, type=int, action='store', choices=[0, 1, 2, 3, 4, 5])
argParser.add_argument('--relIso03', default=0.12, type=float, action='store')
argParser.add_argument('--nbtag', default='1p', action='store', choices=['0', '0p', '1', '1p', ])
argParser.add_argument('--met', default='def', action='store', choices=['def', 'none', 'low'], help='met cut', )
argParser.add_argument('--pu', default="reweightPU27fb", action='store', choices=["None", "reweightPU27fb", "reweightPU27fbUp", "reweightPU27fbDown"], help='PU weight', )
argParser.add_argument('--ttjets', default='pow', action='store', choices=['mg', 'pow'], help='ttjets sample', )
argParser.add_argument('--signals', action='store', nargs='*', type=str, default=[], help="Signals?")
argParser.add_argument('--overwrite', default = False, action='store_true', help='overwrite?', )
argParser.add_argument('--plot_directory', default='80X_v21_correlation', action='store', )

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

# Extra requirements on data
mcFilterCut   = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadronSummer2016&&Flag_badMuonSummer2016"
dataFilterCut = mcFilterCut+"&&weight>0"

# MC
data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *

data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v21/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *

sample_DoubleMuon  = DoubleMuon_Run2016_backup
sample_DoubleEG    = DoubleEG_Run2016_backup
sample_MuonEG      = MuonEG_Run2016_backup

if args.mode=="doubleMu":
    lepton_selection_string_data = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    lepton_selection_string_mc   = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    data_samples = [sample_DoubleMuon]
    sample_DoubleMuon.setSelectionString([dataFilterCut, lepton_selection_string_data])
    if args.trigger: sample_DoubleMuon.addSelectionString( "(HLT_mumuIso||HLT_mumuNoiso)" )
    data_sample_texName = "Data (2 #mu)"
    #qcd_sample = QCD_Mu5 #FIXME
elif args.mode=="doubleEle":
    lepton_selection_string_data = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    data_samples = [sample_DoubleEG]
    sample_DoubleEG.setSelectionString([dataFilterCut, lepton_selection_string_data])
    if args.trigger: sample_DoubleEG.addSelectionString( "HLT_ee_DZ" )
    data_sample_texName = "Data (2 e)"
    #qcd_sample = QCD_EMbcToE
elif args.mode=="muEle":
    lepton_selection_string_data = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    data_samples = [sample_MuonEG]
    sample_MuonEG.setSelectionString([dataFilterCut, lepton_selection_string_data])
    if args.trigger: sample_MuonEG.addSelectionString( "HLT_mue" )
    data_sample_texName = "Data (1 #mu, 1 e)"
    #qcd_sample = QCD_Mu5EMbcToE
elif args.mode=="dilepton":
    doubleMu_selectionString    = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&abs(dl_mass-91.2)>15"
    doubleEle_selectionString   = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&abs(dl_mass-91.2)>15"
    muEle_selectionString       = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1"
    lepton_selection_string_mc = "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1|| ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 ) && abs(dl_mass-91.2)>15)"
    data_samples = [sample_DoubleMuon, sample_DoubleEG, sample_MuonEG]
    sample_DoubleMuon.setSelectionString([dataFilterCut, doubleMu_selectionString])
    sample_DoubleEG.setSelectionString([dataFilterCut, doubleEle_selectionString])
    sample_MuonEG.setSelectionString([dataFilterCut, muEle_selectionString])
    if args.trigger: 
        sample_DoubleMuon.addSelectionString( "(HLT_mumuIso||HLT_mumuNoiso)" )
        sample_DoubleEG.addSelectionString( "HLT_ee_DZ" )
        sample_MuonEG.addSelectionString( "HLT_mue" )

    data_sample_texName = "Data"
    #qcd_sample = QCD_Mu5EMbcToE

elif args.mode=="sameFlavour":
    doubleMu_selectionString =  "&&".join([ "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    doubleEle_selectionString = "&&".join([ "isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join([ "(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2)", getZCut(args.zMode)])

    data_samples = [sample_DoubleMuon, sample_DoubleEG]
    sample_DoubleMuon.setSelectionString([dataFilterCut, doubleMu_selectionString])
    sample_DoubleEG.setSelectionString([dataFilterCut, doubleEle_selectionString])
    if args.trigger: 
        sample_DoubleMuon.addSelectionString( "(HLT_mumuIso||HLT_mumuNoiso)" )
        sample_DoubleEG.addSelectionString( "HLT_ee_DZ" )

    data_sample_texName = "Data (SF)"
    #qcd_sample = QCD_Mu5EMbcToE

else:
    raise ValueError( "Mode %s not known"%args.mode )


if args.splitDiBoson:
    diBoson_samples = [VVTo2L2Nu, WWNo2L2Nu, WZ, ZZNo2L2Nu]
else:
    diBoson_samples = [diBoson] 

if args.ttjets=='mg':
    TTJets_sample = Top
elif args.ttjets=='pow':
    TTJets_sample = Top_pow 

mc_samples = [ TTJets_sample] + diBoson_samples + [DY_HT_LO, TTZ_LO, TTXNoZ, triBoson, TWZ]

signal_samples = []
if len(args.signals)>0:
#    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_2l_postProcessed import *
    signal_colors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen]
    postProcessing_directory = "postProcessed_80X_v12/dilepTiny/"
    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *

    for i_s, s in enumerate( args.signals ):
        if "*" in s:
            split = s.split("*")
            sig, fac = split[0], int(split[1])
        else:
            sig, fac = s, 1

        try:
            sample = eval(sig)

            if fac!=1:
                sample.name+=" x"+str(fac)              
                raise NotImplementedError( "Need to scale signal sample" )
            sample.style = styles.lineStyle( signal_colors[i_s], width = 2)
            signal_samples.append( sample )
            logger.info( "Adding sample %s with factor %3.2f", sig, fac)
        except NameError:
            logger.warning( "Could not add signal %s", s)

if args.small:
    for sample in mc_samples + data_samples + signal_samples:
        sample.reduceFiles(to = 1)

for d in data_samples:
    d.style = styles.errorStyle( ROOT.kBlack )

stack = Stack(mc_samples) 
stack.extend( [ [s] for s in signal_samples ] )
if not args.noData:
    stack.append( data_samples ) 

#Averaging lumi
lumi_scale = sum(d.lumi for d in data_samples)/float(len(data_samples))/1000

logger.info( "Lumi scale for mode %s is %3.2f", args.mode, lumi_scale )

mc_weight_string = "weight*reweightDilepTriggerBackup*reweightLeptonSF"#*reweightLeptonHIPSF*reweightBTag_SF"
if args.pu != "None":
    mc_weight_string+="*"+args.pu

data_weight_string = "weight"

for sample in mc_samples :
    sample.style = styles.fillStyle( sample.color)

for sample in mc_samples + signal_samples:
    sample.setSelectionString([ mcFilterCut, lepton_selection_string_mc])
    if args.pu != "None":
        sample.read_variables = [args.pu+'/F', 'reweightDilepTriggerBackup/F', 'reweightBTag_SF/F', 'reweightLeptonSF/F', 'reweightLeptonHIPSF/F']
        sample.weight = lambda event, sample: getattr( event, args.pu )*event.reweightDilepTriggerBackup*event.reweightLeptonSF#*event.reweightBTag_SF*event.reweightLeptonHIPSF
    else:
        sample.read_variables = ['reweightDilepTriggerBackup/F', 'reweightBTag_SF/F', 'reweightLeptonSF/F', 'reweightLeptonHIPSF/F']
        sample.weight = lambda event, sample: event.reweightDilepTriggerBackup*event.reweightLeptonSF#*event.reweightBTag_SF*event.reweightLeptonHIPSF

weight = lambda event, sample: event.weight

if args.dPhi == 'inv':
    dPhi = [ ("dPhiJetMETInv", "(!(Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0))") ]
if args.dPhi == 'lead':
    dPhi = [ ("dPhiJetMETLead", "Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0") ]
elif args.dPhi=='def':
    dPhi = [ ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0") ]
else:
    dPhi = []

#wpStr = { 5: "VT", 4: "T", 3: "M" , 2: "L" , 1: "VL", 0:"None"}
basic_cuts=[
    ("mll20", "dl_mass>20"),
    ("l1pt25", "l1_pt>25"),
    #("mIso%s"%wpStr[args.mIsoWP], "l1_mIsoWP>=%i&&l2_mIsoWP>=%i"%( args.mIsoWP, args.mIsoWP)),
    ("relIso03-%3.2f"%args.relIso03, "l1_relIso03<%3.2f&&l2_relIso03<%3.2f"%( args.relIso03, args.relIso03 ) ),
    ] + dPhi + [
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
]

def mCutStr( arg ):
    if not arg in ['0', '0p', '1', '1p', '2', '2p', '01']: raise ValueError( "Don't know what to do with cut %s" % arg )

    if arg=='0':
        return '==0'
    elif arg=='0p':
        return '>=0'
    elif arg=='1':
        return '==1'
    elif arg=='1p':
        return '>=1'
    elif arg=='2':
        return '==2'
    elif arg=='2p':
        return '>=2'
    elif arg=='01':
        return '<=1'

def selection( ):
    res = [ \
        ("njet%s"%args.njet, "nJetGood%s"%mCutStr( args.njet )),
        ("nbtag%s"%args.nbtag, "nBTag%s"%mCutStr( args.nbtag ))]
    if args.met=='def': res.extend([\
        ("met80", "met_pt>80"),
        ("metSig5", "(met_pt/sqrt(ht)>5||nJetGood==0)"),
        ])
    elif args.met=='low':
        res.extend([  ("metSm80", "met_pt<80")] )
    elif args.met=='none':
        pass
    return res

cuts = selection()

if args.dPhiLepMET:
    cuts.extend( [ 
        ("dPhiLepMET", "cos(l1_phi-met_phi)>-0.9"),
        ] )

def drawObjects( scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    if scale is not None: 
        lines.append( (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*10)/10., scale ) ) )
    else:
        lines.append( (0.50, 0.95, '13 TeV' ) )
    return [tex.DrawLatex(*l) for l in lines] 

sequence = []
read_variables = ["weight/F"]

from StopsDilepton.tools.helpers import deltaR
from StopsDilepton.tools.objectSelection import getJets

def mth_func( event, sample):
    mth =  sqrt(2.*event.dl_pt*event.met_pt*( 1 - cos(event.dl_phi - event.met_phi)))
    #print mth
    return mth

def makeMinDeltaRLepJets( event, sample ):
    event.jets = filter(lambda j: j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(event, jetColl="JetGood"))
    if len(event.jets)>0:
        dr =  [deltaR(j, {'eta':event.l1_eta, 'phi':event.l1_phi}) for j in event.jets] 
        dr += [deltaR(j, {'eta':event.l2_eta, 'phi':event.l2_phi}) for j in event.jets] 
        setattr( event, "minDeltaRLepJets", min(dr) )
    else:
        setattr( event, "minDeltaRLepJets", float('nan') )

    event.bjets = filter(lambda j: j['btagCSV']>0.8, event.jets)
    loose_bjets = filter(lambda j: j['btagCSV']>0.605, event.jets)
    if len(loose_bjets)>0:
        dr =  [deltaR(j, {'eta':event.l1_eta, 'phi':event.l1_phi}) for j in loose_bjets] 
        dr += [deltaR(j, {'eta':event.l2_eta, 'phi':event.l2_phi}) for j in loose_bjets] 
        setattr( event, "minDeltaRLepBJets", min(dr) )
    else:
        setattr( event, "minDeltaRLepBJets", float('nan') )
read_variables += [ "JetGood[pt/F,eta/F,phi/F,btagCSV/F,id/I]", "nJetGood/I", "isOS/I", 'nGoodMuons/I', 'nGoodElectrons/I', 'met_phi/F']

sequence.append( makeMinDeltaRLepJets )

def makeMT2BJetDisc( event, sample ):
    event.sortedJetsForMT2 = event.bjets + [j for j in event.jets if j not in event.bjets]
    event.mt2BJetDisc = event.sortedJetsForMT2[1]['btagCSV'] if len( event.sortedJetsForMT2 )>=2 else float('nan')        

sequence.append( makeMT2BJetDisc )

#from StopsDilepton.tools.m2Calculator import m2Calculator
#m2Calc = m2Calculator()
#def makeM2CC( event, sample ):
#    m2Calc.reset()
#    if len(event.sortedJetsForMT2)>=2:
#        bj0, bj1 = event.sortedJetsForMT2[:2]
#        m2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
#        m2Calc.setLepton1(event.l1_pt, event.l1_eta, event.l1_phi)
#        m2Calc.setLepton2(event.l2_pt, event.l2_eta, event.l2_phi)
#        m2Calc.setMet(event.met_pt, event.met_phi)
#        event.m2CC = m2Calc.m2CC()
#    else:
#        event.m2CC = float('nan') 
#
#sequence.append( makeM2CC )


if args.loop:
    rev = reversed if args.reversed else lambda x:x
    l_combs = rev( range( len(cuts)+1 ) )
else:
    l_combs = [ len(cuts) ]

ppfixes = [args.mode]
if args.mode.lower() != "dilepton": ppfixes.append( args.zMode )
#ppfixes.append( "DBS%i"%(100*args.diBosonScaleFactor) )
if args.splitDiBoson: ppfixes.append( "splitDiBoson" )
if args.noScaling: ppfixes.append( "noScaling" )
if args.ttjets=='mg': ppfixes.append( "TTMG" )
if args.noData : ppfixes.append( "noData" )
ppfixes.append( 'PR' if args.PR else 'RR' )
if args.small: ppfixes = ['small'] + ppfixes

plot_subdirectory = "-".join( ppfixes )

for l_comb in l_combs:
    for comb in itertools.combinations( cuts, l_comb ):

        for s in mc_samples + data_samples + signal_samples:
            s.clear()

        if args.charges=="OS":
            presel = [("isOS","isOS")]
        elif args.charges=="SS":
            presel = [("isSS","l1_pdgId*l2_pdgId>0")]
        else:
            raise ValueError

        presel.extend( basic_cuts )
        presel.extend( comb )

        prefix =  '-'.join([p[0] for p in presel ] )

        selectionString = "&&".join( [p[1] for p in presel] )

        if  prefix.count('nbtag')>1: continue
        if  prefix.count('njet')>1: continue

        logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

        for s in data_samples:
            s.scale = 1
        for s in mc_samples + signal_samples:
            s.scale = lumi_scale
#        for s in diBoson_samples:
#            s.scale*=args.diBosonScaleFactor

        if not args.noData:
            logger.info( "Calculating normalization constants" )
            yield_mc    = {s.name: s.scale*s.getYieldFromDraw( selectionString = selectionString+"&&dl_mt2ll<100", weightString = mc_weight_string)['val'] for s in mc_samples}
            yield_data  = sum(s.getYieldFromDraw( selectionString = selectionString+"&&dl_mt2ll<100", weightString = data_weight_string)['val'] for s in data_samples)
            
            non_top = sum(yield_mc[s.name] for s in mc_samples if s.name != TTJets_sample.name)
            if (not args.noScaling) and yield_data - non_top>0 and yield_mc[TTJets_sample.name]>0:
                top_sf  = (yield_data - non_top)/yield_mc[TTJets_sample.name]
            else:
                top_sf = 1.
            logger.info( "Data: %i MC TT %3.2f MC other %3.2f SF %3.2f", yield_data, yield_mc[TTJets_sample.name], non_top, top_sf )

        else:
            top_sf = 1 

        TTJets_sample.scale *= top_sf

        prefix+='-mt2ll-%i-%i'%(args.lowMT2ll, args.highMT2ll)
        selectionString+='&&dl_mt2ll>=%i&&dl_mt2ll<%i'%(args.lowMT2ll, args.highMT2ll)
        prefix+='-met-%i-%i'%(args.lowMET, args.highMET)
        selectionString+='&&met_pt>=%i&&met_pt<%i'%(args.lowMET, args.highMET)

        plot_path = os.path.join(plot_directory, args.plot_directory, plot_subdirectory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            logger.info( "Path %s not empty. Skipping."%plot_path )
            continue

        plots = []

        dl_mass  = Plot(
            texX = 'm(ll) (GeV)', texY = 'Number of Events / 3 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_mass/F" ),
            binning=[150/3,0,150],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mass )

        dl_pt  = Plot(
            texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_pt/F" ),
            binning=[40,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_pt )

        dl_eta  = Plot(
            texX = '#eta(ll) ', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_eta/F" ),
            binning=[30,-3,3],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_eta )

        dl_phi  = Plot(
            texX = '#phi(ll) (GeV)', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_phi/F" ),
            binning=[30,-pi,pi],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_phi )

        cosMetJet0phi = Plot(\
            name = "cosMetJet0phi",
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
            stack = stack, 
            attribute =  lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ),  
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet0phi )

        cosMetJet1phi = Plot(\
            name = "cosMetJet1phi",
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ), 
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet1phi )

        minDeltaRLepBJets  = Plot(
            name = "minDeltaRLepBJets",
            texX = 'min #Delta R(loose b-jets, leptons) ', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event, sample:abs(event.minDeltaRLepBJets),
            binning=[30,0,4],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( minDeltaRLepBJets )

        MTH = Plot(\
            name = "MTH",
            texX = 'M_{T}(Z, #slash{E}_{T})', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute =  mth_func,   
            binning = [40,0,800], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( MTH )

        dl_mt2ll  = Plot(
            texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
            binning=[300/20,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2ll )

        dl_mt2ll_coarse  = Plot(
            name = "dl_mt2ll_coarse",
            texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
            binning=Binning.fromThresholds([0,20,40,60,80,100,140,240,340]),
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2ll_coarse )

        dl_mt2bb  = Plot(
            texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
            binning=[300/15,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2bb )

        dl_mt2blbl  = Plot(
            texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
            binning=[300/15,0,300],
            selectionString = selectionString,
            weight = weight,
            ) 
        plots.append( dl_mt2blbl )

#        dl_m2cc  = Plot(
#            name = "M2CC",
#            texX = 'M_{2CC}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
#            stack = stack, 
#            attribute = lambda event,sample:abs(event.m2CC),
#            binning=[800/20,0,800],
#            selectionString = selectionString,
#            weight = weight,
#            )
#        plots.append( dl_m2cc )
 
        l1_pt  = Plot(
            texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "l1_pt/F" ),
            binning=[60,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_pt )

        l1_eta  = Plot(
            texX = '#eta(l_{1})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l1_eta/F" ),
            binning=[36,-3.3,3.3],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_eta )

        l1_phi  = Plot(
            texX = '#phi(l_{1})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l1_phi/F" ),
            binning=[30,-pi,pi],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_phi )

        l1_miniRelIso  = Plot(
            texX = 'I_{rel.mini}', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "l1_miniRelIso/F" ),
            binning=[40,0,2],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_miniRelIso )

        l1_dxy  = Plot(
            name = "l1_dxy",
            texX = '|d_{xy}|', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event,sample:abs(event.l1_dxy),
            read_variables = ["l1_dxy/F"], 
            binning=[40,0,1],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_dxy )

        l1_dz  = Plot(
            name = "l1_dz",
            texX = '|d_{z}|', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event,sample:abs(event.l1_dz), 
            read_variables = ["l1_dz/F"], 
            binning=[40,0,0.15],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_dz )

        l1_pdgId  = Plot(
            texX = 'pdgId(l_{1})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l1_pdgId/I" ),
            binning=[32,-16,16],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_pdgId )

        l2_pt  = Plot(
            texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "l2_pt/F" ),
            binning=[60,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_pt )

        l2_eta  = Plot(
            texX = '#eta(l_{2})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l2_eta/F" ),
            binning=[30,-3,3],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_eta )

        l2_phi  = Plot(
            texX = '#phi(l_{2})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l2_phi/F" ),
            binning=[30,-pi,pi],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_phi )

        l2_miniRelIso  = Plot(
            texX = 'I_{rel.mini}', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "l2_miniRelIso/F" ),
            binning=[40,0,2],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_miniRelIso )

        l2_dxy  = Plot(
            name = "l2_dxy",
            texX = '|d_{xy}|', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event,sample:abs(event.l2_dxy),
            read_variables = ["l2_dxy/F"],
            binning=[40,0,1],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_dxy )

        l2_dz  = Plot(
            name = "l2_dz",
            texX = '|d_{z}|', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event,sample:abs(event.l2_dz),
            read_variables = ["l2_dz/F"],
            binning=[40,0,0.15],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_dz )

        l2_pdgId  = Plot(
            texX = 'pdgId(l_{2})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l2_pdgId/I" ),
            binning=[32,-16,16],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_pdgId )

        metZoomed  = Plot(
            name = "met_pt_zoomed",
            texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 10 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "met_pt/F" ),
            binning=[22,0,220],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( metZoomed )

        met  = Plot(
            texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "met_pt/F" ),
            binning=[1050/50,0,1050],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( met )

        JZB  = Plot(
            name = "JZB",
            texX = 'JZB (GeV)', texY = 'Number of Events / 32 GeV',
            stack = stack, 
            attribute = lambda event, sample: sqrt( (event.met_pt*cos(event.met_phi)+event.dl_pt*cos(event.dl_phi))**2 + (event.met_pt*sin(event.met_phi)+event.dl_pt*sin(event.dl_phi))**2) - event.dl_pt, 
            read_variables = ["met_pt/F","met_phi/F","dl_pt/F","dl_phi/F"],
            binning=[25,-200,600],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( JZB )

        metSig  = Plot(
            name = "metSig",
            texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan'), 
            binning=[30,0,30],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( metSig )

        ht  = Plot(
            texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "ht/F" ),
            binning=[2600/100,0,2600],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( ht )

        ht_zoomed  = Plot(
            name = "ht_zoomed",
            texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "ht/F" ),
            binning=[390/15,0,390],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( ht_zoomed )

        cosMetJet0phi = Plot(\
            name = "cosMetJet0phi",
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ),
            binning = [40,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet0phi )

        cosMetJet1phi = Plot(\
            name = "cosMetJet1phi",
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ),
            binning = [40,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet1phi )

        jet0pt  = Plot(
            name = "jet0pt", 
            texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.JetGood_pt[0],
            binning=[980/20,0,980],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet0pt )

        jet1pt  = Plot(
            name = "jet1pt", 
            texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.JetGood_pt[1],
            binning=[980/20,0,980],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet1pt )

        jet2pt  = Plot(
            name = "jet2pt", 
            texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.JetGood_pt[2],
            binning=[400/20,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet2pt )

        jet3pt  = Plot(
            name = "jet3pt", 
            texX = 'p_{T}(4^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.JetGood_pt[3],
            binning=[400/20,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet3pt )

        jet4pt  = Plot(
            name = "jet4pt", 
            texX = 'p_{T}(5^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.JetGood_pt[4], 
            binning=[400/20,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet4pt )

        nbtags  = Plot(
            texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString('nBTag/I'),
            binning=[8,0,8],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( nbtags )

        CSVv2SubLeadingJet  = Plot(
            name = "CSVv2SubLeadingJet",
            texX = 'CSVv2 of sub-leading jet', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event,sample:event.mt2BJetDisc,
            binning=[10,0,1],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( CSVv2SubLeadingJet )

        njets  = Plot(
            texX = 'number of jets', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString('nJetGood/I'),
            binning=[14,0,14],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( njets )

        nVert  = Plot(
            texX = 'vertex multiplicity', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "nVert/I" ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( nVert )

        plotting.fill(plots, read_variables = read_variables, sequence = sequence)
        if not os.path.exists( plot_path ): os.makedirs( plot_path )

        if args.noData:
            ratio = None
        else:
            ratio = {'yRange':(0.1,1.9), 'num': -1} 

        for plot in plots:
            if args.mode in ['dilepton', 'sameFlavour'] and not args.noData:
                data_histo =  plot.histos_added[-1][0]
                data_histo.style = styles.errorStyle( ROOT.kBlack )
                plot.histos = plot.histos[:-1]+[[data_histo]]
                plot.stack = plot.stack[:-1] + [[plot.stack[-1][0] ]]
                plot.stack[-1][0].texName = data_sample_texName
            #scale_corr = plot.histos_added[1][0].Integral()/plot.histos_added[0][0].Integral() if not args.noScaling else 1
            plotting.draw(plot, 
                plot_directory = plot_path, ratio = ratio, 
                logX = False, logY = True, sorting = True, 
                #scaling = {0:1} if not args.noScaling else {},
                yRange = (0.03, "auto"), 
                drawObjects = drawObjects( yield_data/sum(yield_mc.values()) if args.noScaling else top_sf )
            )
        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )

