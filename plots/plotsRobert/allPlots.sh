nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=allZ --mode=doubleMu" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=allZ --mode=doubleEle" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=onZ --mode=doubleMu" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=onZ --mode=doubleEle" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=offZ --mode=doubleEle" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=offZ --mode=doubleMu" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=allZ --mode=muEle" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=onZ --mode=muEle" &
nohup krenew -t -K 10 -- bash -c "python simple1DPlots.py $1 --zMode=offZ --mode=muEle" &
