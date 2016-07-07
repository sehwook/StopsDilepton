#!/usr/bin/env python
from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.estimators import setup, DataDrivenDYEstimate
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.analysis.regions import regions80X

import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

estimateDY = DataDrivenDYEstimate(name='DY-DD', cacheDir=None, controlRegion=Region('dl_mt2ll', (100,-1)))
estimateDY.initCache(setup.defaultCacheDir())

modifiers = [ {},
#             {'reweight':['reweightPUUp']},
#             {'reweight':['reweightPUDown']},
#             {'reweight':['reweightTopPt']},
#             {'selectionModifier':'JERUp'},
#             {'selectionModifier':'JERDown'},
#             {'selectionModifier':'JECVUp'},
#             {'selectionModifier':'JECVDown'},
#             {'reweight':['reweightLeptonFastSimSFUp']},
#             {'reweight':['reweightLeptonFastSimSFDown']},
#             {'reweight':['reweightBTag_SF']},
#             {'reweight':['reweightBTag_SF_b_Down']},
            ]

selections = [ "met80", "met50" ]

texdir = os.path.join(setup.analysis_results, setup.prefix(), 'tables')
try:
  os.makedirs(texdir)
except:
  pass 

columns = ["DY","TTJets","multiBoson","TTX","observed","scale factor"]
texfile = os.path.join(texdir, "DY_scalefactors.tex")
with open(texfile, "w") as table:
  table.write("\\begin{tabular}{l|c" + "c"*len(columns) + "} \n")
  table.write("  selection & " + "&".join(columns) + " \\\\ \n")
  table.write("  \\hline \n")
  for selection in selections:
    if selection == "met50": setup.parameters['metMin'] = 50
    for channel in ['MuMu']:  # is the same for EE
      for r in [Region('dl_mt2ll', (100,-1))]:  # also the same in each applied region because we use a controlRegion
        for modifier in modifiers:
  	  (yields, data, scaleFactor) = estimateDY._estimate(r, channel, setup.sysClone(modifier), returnScaleFactor=True)
          table.write(selection + " & "+ " & ".join([str(yields[s].val) for s in ['DY','TTJets','multiBoson','TTX']]) + " & " + str(data.val) + " & " + str(scaleFactor) + " \\\\ \n")
  table.write("\\end{tabular} \n")