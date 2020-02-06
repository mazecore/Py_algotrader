calculateMoneyFlowIndex=function(stx, sd){
    var quotes=sd.chart.scrubbed;
    if(quotes.length<sd.days+1){
        sd.error=true;
        return;
    }
    var cumPosMF=0, cumNegMF=0;
    var startQuote=quotes[sd.startFrom-1];
    var rawMFLbl="_rawMF " + sd.name;
    var cumMFLbl="_cumMF " + sd.name;
    var resultLbl="Result " + sd.name;
    if(startQuote && startQuote[cumMFLbl]){
        cumPosMF=startQuote[cumMFLbl][0];
        cumNegMF=startQuote[cumMFLbl][1];
    }
    for(var i=sd.startFrom;i<quotes.length;i++){
        var typPrice=quotes[i]["hlc/3"];
        if(i>0){
            var lastTypPrice=quotes[i-1]["hlc/3"];
            var rawMoneyFlow=typPrice*quotes[i].Volume;
            if(typPrice>lastTypPrice){
                cumPosMF+=rawMoneyFlow;
            }else if(typPrice<lastTypPrice){
                rawMoneyFlow*=-1;
                cumNegMF-=rawMoneyFlow;
            }else{
                rawMoneyFlow=0;
            }
            if(i>sd.days){
                var old=quotes[i-sd.days][rawMFLbl];
                if(old>0) cumPosMF-=old;
                else cumNegMF+=old;
                if(cumNegMF===0) quotes[i][resultLbl]=100;
                else quotes[i][resultLbl]=100 - 100/(1 + (cumPosMF/cumNegMF));
            }
            quotes[i][rawMFLbl]=rawMoneyFlow;
            quotes[i][cumMFLbl]=[cumPosMF, cumNegMF];
        }

        if ( i === quotes.length ) {
            console.log(quotes);
        }
    }
};

module.export(calculateMoneyFlowIndex);