// **** USEFUL GETTERS AND SETTERS ****
// give a column as string, get a selected index number
function getFormIndexByColumn(COL)
{
    let opts = document.getElementById("form_"+COL).elements;
    for (j=0; j<opts.length; j++) { if (opts[j].checked) { return j; } }
    return -1;
}

// give the option name as string, get a selected index number
function getFormIndexByTitle(OPTNAME)
{
    let forms = document.forms;
    for (i=0; i<forms.length; i++)
    {
        if (forms[i].length == 0) { continue; }
        if (forms[i].elements[0].name == 'opt_'+OPTNAME) { return getFormIndexByColumn(i); }
    }
    return -1;
}

// give a column as string, get a selected value
function getFormValueByColumn(COL)
{
    let opts = document.getElementById("form_"+COL).elements;
    for (j=0; j<opts.length; j++) { if (opts[j].checked) { return opts[j].value; } }
    return "";
}

// give the option name as string, get a selected value
function getFormValueByTitle(OPTNAME)
{
    let forms = document.forms;
    for (i=0; i<forms.length; i++)
    {
        if (forms[i].length == 0) { continue; }
        if (forms[i].elements[0].name == 'opt_'+OPTNAME) { return getFormValueByColumn(i); }
    }
    return "";
}

// get rid of headings and forms so we can rewrite them
function clearEverythingAfter(COL)
{
    for (i=COL+1; i<NCOLS; i++)
    {
        document.getElementById("title_"+i.toString()).innerHTML = "";
        document.getElementById("form_"+i.toString()).innerHTML = "";
    }
}

// **** COLUMN SETTERS ****
// initialize the columns
function setupColumns()
{
    let div_info = document.getElementById("info");

    // create a div, a heading, and a form for each column
    let width = 100./NCOLS;
    for (i=0; i<NCOLS; i++)
    {
        let div = document.createElement("div");
        div.id          = "info_"+i.toString();
        div.className   = "float";
        div.style.width = width.toString()+"%";

        let h4 = document.createElement("h4");
        h4.id          = "title_"+i.toString();
        h4.className   = "option";
        h4.style.width = "100%";
        h4.innerHTML   = "";
        div.appendChild(h4);

        let form = document.createElement("form");
        form.id = "form_"+i.toString();
        div.appendChild(form);

        div_info.appendChild(div);
    }

    setupSamples();
}

// create a form column
// basic general setter from which the others are derived
function setupColumn(COL, HEADING, OPTNAME, VALUES, LABELS, CHECKOPT)
{
    // set the width
    let div = document.getElementById("info_"+COL);
    if      (OPTNAME == 'sample'       ) { div.style.width = '20%'  ; }
    else if (OPTNAME == 'mH'           ) { div.style.width = '8%'   ; }
    else if (OPTNAME == 'mX'           ) { div.style.width = '8%'   ; }
    else if (OPTNAME == 'cTau'         ) { div.style.width = '8%'   ; }
    else if (OPTNAME == 'plotcat'      ) { div.style.width = '12.5%'; }
    else if (OPTNAME == 'deltaPhiRange') { div.style.width = '12.5%'; }
    else if (OPTNAME == 'plottype'     ) { div.style.width = '12.5%'; }
    else if (OPTNAME == 'plottype2'    ) { div.style.width = '12.5%'; }
    else if (OPTNAME == 'plottype3'    ) { div.style.width = '12.5%'; }

    // set the heading
    document.getElementById("title_"+COL).innerHTML = HEADING;

    // clear and set defaults
    let form = document.getElementById("form_"+COL);
    form.innerHTML = "";
    if (LABELS == undefined) { LABELS = VALUES; }

    if (CHECKOPT == undefined      ) { CHECKOPT = 0;               }
    if (CHECKOPT == -1             ) { CHECKOPT = 0;               }
    if (CHECKOPT >  VALUES.length-1) { CHECKOPT = VALUES.length-1; }

    // set the options and labels
    for (i=0; i<VALUES.length; i++)
    {
        let opt = document.createElement("input");
        opt.id    = "opt_"+COL+"_"+i.toString();
        opt.type  = "radio";
        opt.name  = "opt_"+OPTNAME;
        opt.value = VALUES[i];
        opt.addEventListener("click", update);
        if (i==CHECKOPT) { opt.checked = true; }
        form.append(opt);

        let lab = document.createElement("label");
        lab.id         = "lab_"+COL+"_"+i.toString();
        lab.className  = "option";
        lab.for        = opt.id;
        lab.innerHTML  = LABELS[i];
        form.append(lab);

        form.appendChild(document.createElement("br"));
    }
}

// initialize samples, probably into column 0, and this function only gets called once
function setupSamples()
{
    let state = {
        i_sample    : 0,
        i_mH        : 0,
        i_mX        : 0,
        i_cTau      : 0,
        i_plotcat   : 0,
        i_dphi      : 0,
        i_plottype  : 0,
        i_plottype2 : 0,
        i_plottype3 : 0,
    };

    setupColumn("0", "sample", "sample", SAMPLEVALS, SAMPLELABELS);
    setupMH(state);
}

// initialize mH, probably into column 1
function setupMH(state)
{
    // "copy" mH values
    let values = [125, 200, 400, 1000, 'Global'];
    let labels = values.map(String);
    // make column
    setupColumn("1", "m<sub>H</sub>", "mH", values, labels, state['i_mH']);
    setupMX(state);
}

// initialize mX, probably into column 2
function setupMX(state)
{
    if (state['i_mH'] != 4)
    {
        // make sure i_mH is a valid option
        if (state['i_mH'] < 0) {state['i_mH'] = 0;}
        // copy mX values
        let values = [];
        for (i=0; i<SIGNALS[state['i_mH']].children.length; i++) { values.push(SIGNALS[state['i_mH']].children[i].value); }
        let labels = values.map(String);
        // make column
        setupColumn("2", "m<sub>X</sub>", "mX", values, labels, state['i_mX']);
        // make sure i_mX is correct if the number of options has decreased
        if (state['i_mX'] > values.length-1) {state['i_mX'] = values.length-1;}
        setupCTAU(state);
    }
    else
    {
        setupColumn("2", "m<sub>X</sub>", "mX", [], [], -1);
        setupColumn("3", "c&tau;", "cTau", [], [], -1);
        setupPlotCat("4", SIGNALVALS, SIGNALLABELS, state);
    }
}

// initialize cTau, probably into column 3
function setupCTAU(state)
{
    // make sure i_mX is a valid option
    if (state['i_mX'] < 0) {state['i_mX'] = 0;}
    // copy cTau values
    let values = [];
    for (i=0; i<SIGNALS[state['i_mH']].children[state['i_mX']].children.length; i++) { values.push(SIGNALS[state['i_mH']].children[state['i_mX']].children[i].value); }
    let labels = values.map(String);
    // make column
    setupColumn("3", "c&tau;", "cTau", values, labels, state['i_cTau']);
    setupPlotCat("4", SIGNALVALS, SIGNALLABELS, state);
}

// initialize plot categories
function setupPlotCat(COL, VALUES, LABELS, state)
{
    setupColumn(COL, "plot category", "plotcat", VALUES, LABELS, state['i_plotcat']);
    // make dPhi column only for certain categories, otherwise continue to plottype
    let optValue = getFormValueByColumn(COL);
    if (optValue == 'NM1' || optValue == 'TCUM')
    {
        setupDPHI((Number(COL)+1).toString(), DPHIVALS, DPHILABELS, state);
    }
    else
    {
        setupPlotType((Number(COL)+1).toString(), PLOTTYPEVALS[optValue], PLOTTYPELABELS[optValue], state);
    }
}

// initialize Delta Phi range
function setupDPHI(COL, VALUES, LABELS, state)
{
    setupColumn(COL, "&Delta;&Phi; Range", "deltaPhiRange", VALUES, LABELS, state['i_dphi']);
    let optValue = getFormValueByColumn((Number(COL)-1).toString());
    setupPlotType((Number(COL)+1).toString(), PLOTTYPEVALS[optValue], PLOTTYPELABELS[optValue], state);
}

// initialize plot types
function setupPlotType(COL, VALUES, LABELS, state, TITLE=true)
{
    // simple strings [s, s, s...]
    if (VALUES[0].constructor != Array)
    {
        if (TITLE)
        {
            setupColumn(COL, "plot type", "plottype", VALUES, LABELS, state['i_plottype']);
            plottype2exists = false;
        }
        else
        {
            if (!plottype2exists)
            {
                setupColumn(COL, "...", "plottype2", VALUES, LABELS, state['i_plottype2']);
                plottype2exists = true;
            }
            else
            {
                setupColumn(COL, "...", "plottype3", VALUES, LABELS, state['i_plottype3']);
            }
        }
    }
    // two arrays [(s, s, s), (s, s, s)]: make every combination
    else if (VALUES[0].constructor == Array && VALUES[0][1].constructor != Array)
    {
        setupPlotType(COL          , VALUES[0], LABELS[0], state, TITLE);
        setupPlotType(Number(COL)+1, VALUES[1], LABELS[1], state, false)
    }
    // array of string-array pairs [(s, []), (s, []), ...]: make each combination as given
    else if (VALUES[0].constructor == Array && VALUES[0][1].constructor == Array)
    {
        let thisColumn = [];
        let thisLabels = [];
        let nextColumn = [];
        let nextLabels = [];
        for (i=0; i<VALUES.length; i++)
        {
            thisColumn.push(VALUES[i][0]);
            thisLabels.push(LABELS[i][0]);
            nextColumn.push(VALUES[i][1]);
            nextLabels.push(LABELS[i][1]);
        }
        setupPlotType(COL          , thisColumn, thisLabels, state, TITLE);
        setupPlotType(Number(COL)+1, nextColumn, nextLabels, state, false);
    }
}

// **** UPDATE: gets called on every option button click ****
// universal update function
// depending on which option button was just clicked, set the other columns
// then call setPlot()
function update()
{
    let i_sample    = getFormIndexByTitle("sample");
    let i_mH        = getFormIndexByTitle("mH");
    let i_mX        = getFormIndexByTitle("mX");
    let i_cTau      = getFormIndexByTitle("cTau");
    let i_plotcat   = getFormIndexByTitle("plotcat");
    let i_dphi      = getFormIndexByTitle("deltaPhiRange");
    let i_plottype  = getFormIndexByTitle("plottype");
    let i_plottype2 = getFormIndexByTitle("plottype2");
    let i_plottype3 = getFormIndexByTitle("plottype3");

    let state = {
        i_sample    : i_sample   ,
        i_mH        : i_mH       ,
        i_mX        : i_mX       ,
        i_cTau      : i_cTau     ,
        i_plotcat   : i_plotcat  ,
        i_dphi      : i_dphi     ,
        i_plottype  : i_plottype ,
        i_plottype2 : i_plottype2,
        i_plottype3 : i_plottype3,
    };

    if (this.name == "opt_sample")
    {
        clearEverythingAfter(0);
        if (this.value == "HTo2XTo4Mu" || this.value == "HTo2XTo2Mu2J")
        {
            setupMH(state);
        }
        else if (this.value == "DY100to200")
        {
            setupPlotCat("1", BGVALS, BGLABELS, state);
        }
        else if (this.value == "DoubleMuonRun2016D-07Aug17")
        {
            setupPlotCat("1", DATAVALS, DATALABELS, state);
        }
    }
    else if (this.name == "opt_mH")
    {
        clearEverythingAfter(1);
        setupMX(state);
    }
    else if (this.name == "opt_mX")
    {
        clearEverythingAfter(2);
        setupCTAU(state);
    }
    else if (this.name == "opt_plotcat")
    {
        let optArray = this.id.split("_");
        COL = Number(optArray[1]);
        clearEverythingAfter(COL);
        if (this.value == "NM1" || this.value == "TCUM")
        {
            setupDPHI((COL+1).toString(), DPHIVALS, DPHILABELS, state);
        }
        else
        {
            setupPlotType((COL+1).toString(), PLOTTYPEVALS[this.value], PLOTTYPELABELS[this.value], state);
        }
    }

    setPlot();
}

// set plot function
// having correctly set everything up, just string all the values together
// and add .png
function setPlot()
{
    let plotcat  = getFormValueByTitle("plotcat");
    let plottype = getFormValueByTitle("plottype") + getFormValueByTitle("plottype2") + getFormValueByTitle("plottype3");
    let dphi     = getFormValueByTitle("deltaPhiRange");
    let sample   = getFormValueByTitle("sample");
    let mH       = getFormValueByTitle("mH").toString();
    let mX       = getFormValueByTitle("mX").toString();
    let cTau     = getFormValueByTitle("cTau").toString();

    filename = "img/png/";
                            filename += plotcat;
    if (plottype != "")   { filename += "_"+plottype; }
    if (dphi     != "")   { filename += "_"+dphi;     }
                            filename += "_"+sample;
    if (mH       != "")   { filename += "_"+mH;       }
    if (mX       != "")   { filename += "_"+mX;       }
    if (cTau     != "")   { filename += "_"+cTau;     }
                            filename += '.png';

    let plot = document.getElementById("plot");
    console.log("Attempting to view "+filename);
    plot.src = filename;
}

//**** CONSTANTS ****
// this code and the Main Code afterwards are not functions, but declarations
// they run once when the script is loaded
// here I declare "literals" for use in all the other functions

// actually write out the signal point tree
// SIGNALS is a list of value:children pairs, where children
// is a list of value:children pairs.
// so SIGNALS[2] is a pair (400, children) where children
// is a list of possible mX:cTau pairs

// pair object constructor for making a tree of signal points

function pair(value, children)
{
	this.value = value;
	this.children = children;
}

var SIGNALS = [
	new pair(125, [
		new pair(20, [
			new pair(13,   []),
			new pair(130,  []),
			new	pair(1300, [])
		]),
		new pair(50, [
			new pair(50,   []),
			new pair(500,  []),
			new pair(5000, [])
		])
	]),
	new pair(200, [
		new pair(20, [
			new pair(7,    []),
			new pair(70,   []),
			new	pair(700,  [])
		]),
		new pair(50, [
			new pair(20,   []),
			new pair(200,  []),
			new pair(2000, [])
		])
	]),
	new pair(400, [
		new pair(20, [
			new pair(4,    []),
			new pair(40,   []),
			new	pair(400,  [])
		]),
		new pair(50, [
			new pair(8,    []),
			new pair(80,   []),
			new pair(800,  [])
		]),
		new pair(150, [
			new pair(40,   []),
			new pair(400,  []),
			new pair(4000, [])
		])
	]),
	new pair(1000, [
		new pair(20, [
			new pair(2,    []),
			new pair(20,   []),
			new	pair(200,  [])
		]),
		new pair(50, [
			new pair(4,    []),
			new pair(40,   []),
			new pair(400,  [])
		]),
		new pair(150, [
			new pair(10,   []),
			new pair(100,  []),
			new pair(1000, [])
		]),
		new pair(350, [
			new pair(35,   []),
			new pair(350,  []),
			new pair(3500, [])
		]),
	]),
    new pair('Global', [])
];

// sample names and labels
var SAMPLEVALS   = ['HTo2XTo4Mu'          , 'HTo2XTo2Mu2J'          , 'DY100to200'          , 'DoubleMuonRun2016D-07Aug17'];
var SAMPLELABELS = ['H&rarr;2X&rarr;4&mu;', 'H&rarr;2X&rarr;2&mu;2j', 'Drell-Yan M(100,200)', 'DoubleMuon2016D'           ];

// plot category names and labels
var SIGNALVALS = ['Dim', 'DSA', 'RSA', 'NM1', 'NM1E', 'TCUM', 'CutTable', 'Gen', 'SME', 'SMR', 'SVFE'];
var BGVALS     = ['Dim', 'DSA', 'RSA', 'NM1', 'NM1E', 'TCUM', 'CutTable'];
var DATAVALS   = ['Dim', 'DSA', 'RSA', 'NM1', 'NM1E', 'TCUM', 'CutTable'];

var SIGNALLABELS = ['dimuon', 'DSA', 'RSA', 'N&minus;1', 'N&minus;1 eff.', 'tail cum.', 'cut table', 'gen', 'sig. m. eff.', 'sig. m. res.', 'sig. v. f. eff.'];
var BGLABELS     = ['dimuon', 'DSA', 'RSA', 'N&minus;1', 'N&minus;1 eff.', 'tail cum.', 'cut table'];
var DATALABELS   = ['dimuon', 'DSA', 'RSA', 'N&minus;1', 'N&minus;1 eff.', 'tail cum.', 'cut table'];

// delta phi range names and labels
var DPHIVALS   = ['Less', 'More'];
var DPHILABELS = ['|&Delta;&Phi;| &lt; &pi;/2', '|&Delta;&Phi;| &gt; &pi;/2'];

// plottype names and labels
var PLOTTYPEVALS = {
    Dim      : [['pT', 'eta', 'mass', 'deltaR', 'cosAlpha', 'deltaPhi', 'vtxChi2', 'Lxy', 'LxySig'], ['', '_Matched']],
    DSA      : [['pT', 'pTSig', 'eta', 'd0', 'd0Sig', 'normChi2', 'nMuonHits', 'nStations', 'nMuon'], ['', '_Matched']],
    RSA      : [['pT', 'pTSig', 'eta', 'd0', 'd0Sig', 'normChi2', 'nMuonHits', 'nStations', 'nMuon'], ['', '_Matched']],
    NM1      : ['pT', 'eta', 'nMuonHits', 'nStations', 'normChi2', 'd0Sig', 'mass', 'vtxChi2', 'deltaR', 'LxySig', 'cosAlpha'],
    TCUM     : ['LxySig', 'd0Sig'],
    NM1E     : [['LxySig', 'cosAlpha', 'deltaPhi', 'deltaR', 'mass', 'vtxChi2', 'pT', 'eta', 'nMuonHits', 'nStations', 'normChi2', 'd0Sig'], ['EffVSpT', 'EffVSeta', 'EffVSd0', 'EffVSLxy']],
    CutTable : [['MUO', 'DIM'], ['-IND', '-SEQ', '-NM1']],
    Gen      : ['massH', 'massX', 'cTau', 'pTH', 'pTX', 'pTmu', 'beta', 'etaMu', 'dPhi', 'cosAlpha', 'Lxy', 'd0', 'dR', 'LxyVSLz'],
    SME      : [['pT', 'eta', 'phi', 'Lxy', 'd0'], ['Eff', 'ChargeEff']],
    SMR      : [['', 'DSA_', 'RSA_'], [['pTRes', 'd0Res', 'LxyRes'], ['', '_Lxy-Binned', '_d0-Binned', '_pT-Binned', '_qm-Binned']]],
    SVFE     : [['pT', 'eta', 'phi', 'Lxy'], ['Eff']],
}
var PLOTTYPELABELS = {
    Dim      : [['p<sub>T</sub>', '&eta;', 'mass', '&Delta;R', 'cos(&alpha;)', '&Delta;&Phi;', 'vertex &chi;<sup>2</sup>/dof', 'L<sub>xy</sub>', 'L<sub>xy</sub>/&sigma;<sub>Lxy</sub>'], ['no selection', 'matched']],
    DSA      : [['p<sub>T</sub>', '&sigma;<sub>pT</sub>/p<sub>T</sub>', '&eta;', 'd<sub>0</sub>', '|d<sub>0</sub>|/&sigma;<sub>d0</sub>', '&chi;<sup>2</sup>/dof', 'nMuonHits', 'nStations', 'nMuon'], ['no selection', 'matched']],
    RSA      : [['p<sub>T</sub>', '&sigma;<sub>pT</sub>/p<sub>T</sub>', '&eta;', 'd<sub>0</sub0', '|d<sub>0</sub>|/&sigma;<sub>d0</sub>', '&chi;<sup>2</sup>/dof', 'nMuonHits', 'nStations', 'nMuon'], ['no selection', 'matched']],
    NM1      : ['p<sub>T</sub>', '&eta;', 'nMuonHits', 'nStations', '&chi;<sup>2</sup>/dof', '|d<sub>0</sub>|/&sigma;<sub>d0</sub>', 'M(&mu;&mu;)', 'vertex &chi;<sup>2</sup>/dof', '&Delta;R', 'L<sub>xy</sub>/&sigma;<sub>Lxy</sub>', 'cos(&alpha;)'],
    NM1E     : [['L<sub>xy</sub> sig.', 'cos(&alpha;)', '&Delta;&Phi;', '&Delta;R', 'M(&mu;&mu;)', 'vtx. &chi;<sup>2</sup>/dof', 'p<sub>T</sub>', '&eta;', 'nMuonHits', 'nStations', 'track &chi;<sup>2</sup>/dof', 'd<sub>0</sub> sig.'], ['vs. p<sub>T</sub>', 'vs. &eta;', 'vs. d<sub>0</sub>', 'vs. L<sub>xy</sub>']],
    TCUM     : ['L<sub>xy</sub>/&sigma;<sub>Lxy</sub>', '|d<sub>0</sub>|/&sigma;<sub>d0</sub>'],
    CutTable : [['Muon', 'Dimuon'], ['Ind.', 'Seq.', 'N&minus;1']],
    Gen      : ['m<sub>H</sub>', 'm<sub>X</sub>', 'c&tau;', 'p<sub>T</sub> H', 'p<sub>T</sub> X', 'p<sub>T</sub> &mu;', '&beta;', '&eta; &mu;', '&Delta;&Phi;', 'cos(&alpha;)', 'L<sub>xy</sub>', 'd<sub>0</sub>', '&Delta;R', 'L<sub>xy</sub> VS L<sub>z</sub>'],
    SME      : ['&epsilon; : p<sub>T</sub>', '&epsilon; : &eta;', '&epsilon; : &phi;', '&epsilon; : L<sub>xy</sub>', '&epsilon; : d<sub>0</sub>', 'Charge &epsilon; : p<sub>T</sub>', 'Charge &epsilon; : &eta;', 'Charge &epsilon; : &phi;', 'Charge &epsilon; : L<sub>xy</sub>', 'Charge &epsilon; : d<sub>0</sub>'],
    SME      : [['p<sub>T</sub>', '&eta;', '&phi;', 'L<sub>xy</sub>', 'd<sub>0</sub>'], ['reco. &epsilon;', 'charge &epsilon;']],
    SMR      : [['Both', 'DSA', 'RSA'], [['p<sub>T</sub> Res.', 'd<sub>0</sub> Dif.', 'L<sub>xy</sub> Dif.'], ['Int.', 'L<sub>xy</sub>-Binned', 'd<sub>0</sub>-Binned', 'p<sub>T</sub>-Binned', 'q.m.-Binned']]],
    SVFE     : [['p<sub>T</sub>', '&eta;', '&phi;', 'L<sub>xy</sub>'], ['v. f. &epsilon;']],
}

var NCOLS = 8;
var plottype2exists = false;

//**** MAIN CODE ****
// setupColumns calls setupSamples which calls setupMH() with all zeroes as defaults
// thereby setting up the entire board. all that remains is to call setPlot once.
setupColumns();
setPlot();
