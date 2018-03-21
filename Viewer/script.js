//**** SIGNAL OPTIONS ****
// this creates "SBoxes", basically writing the HTML structure of the signal form divs
// setting up all the relevant ids, labels, options, etc.
function makeSBox(sboxname, values, realHeadingHTML)
{
	// make sbox div
	let sbox = document.createElement("div");
	sbox.id = sboxname+"_div";
	sbox.className = "sbox";

	// make sbox title, an h3
	let heading = document.createElement("h3");
	heading.className = "sbox";
	heading.innerHTML = realHeadingHTML;
	sbox.appendChild(heading);

	// make form
	let form = document.createElement("form");
	form.id = sboxname+"_form";
	for (i = 0; i < values.length; i++)
	{
		// make options with id, radio type, values as given
		// check the first box
		let opt = document.createElement("input");
		opt.id = sboxname+"_opt_"+i.toString();
		opt.type = "radio";
		opt.name = sboxname;
		opt.value = values[i];
		opt.addEventListener("click", update);
		if (i == 0) { opt.checked = true; }
		form.appendChild(opt);

		// make labels with id, labeltext, and for = option id
		let label = document.createElement("label");
		label.id = sboxname+"_lab_"+i.toString();
		label.className = "sbox";
		label.for = sboxname+"_opt_"+i.toString();
		label.textContent = values[i].toString();
		form.appendChild(label);
	}
	sbox.appendChild(form);
	return sbox;
}

//**** PLOT TYPE OPTIONS ****
// make all the plot type options in one go
// it uses the TYPES constant below
function makePlotTypeOptions()
{
	let form = document.getElementById("plottype_form");
	let divs = [
		document.getElementById("plottype_0"),
		document.getElementById("plottype_1"),
		document.getElementById("plottype_2"),
		document.getElementById("plottype_3")
	];
	//let disabled = [false, false, false, false, false, false];

	for (i=0; i<TYPES.length; i++)
	{
		let opt = document.createElement("input");
		opt.id = "plottype_opt_"+i.toString();
		opt.name = "plottype";
		opt.type = "radio";
		opt.value = TYPES[i][0];
		opt.addEventListener("click", update);

		let lab = document.createElement("label");
		lab.id = "plottype_lab_"+i.toString();
		lab.for = "plottype_opt_"+i.toString();
		lab.className = "sbox";
		lab.innerHTML = TYPES[i][1];

		divs[TYPES[i][2]].appendChild(opt);
		divs[TYPES[i][2]].appendChild(lab);
		divs[TYPES[i][2]].appendChild(document.createElement("br"));

	}
	form.elements[0].checked = true;
}

// **** UPDATE AND SET PLOT FUNCTIONS ****
// update is the function that gets called on any option button click
// it sets all the labels with logic and calls setPlotBySignal, which changes the plot image src
// it uses the SIGNALS and TYPES constants below
function update()
{
	// gets the current form indices for mH, mX, cTau, and plottype
	let i_mH   = getFormValueIndex(0);
	let i_mX   = getFormValueIndex(1);
	let i_cTau = getFormValueIndex(2);
	let i_type = getFormValueIndex(3);

	// sets the mX labels based on value of mH
	for (j=0; j<4;                           j++)   { setDisplay("mX", j, "none");  }
	for (j=0; j<SIGNALS[i_mH].children.length; j++) { setDisplay("mX", j, "inline");
		setOption("mX", j, SIGNALS[i_mH].children[j].value);
	}

	// sets the currently checked mX to the highest possible if the previously checked mX
	// is "higher up" than what is now possible
	while (true)
	{
		let opt = getOpt("mX", i_mX);
		if (opt.style.display == 'none') { i_mX--; } else { opt.checked = true; break; }
	}

	// sets the cTau labels based on value of mH and mX
	for (j=0; j<SIGNALS[i_mH].children[i_mX].children.length; j++)
	{
		setOption("cTau", j, SIGNALS[i_mH].children[i_mX].children[j].value);
	}

	setPlot(SIGNALS[i_mH].value, SIGNALS[i_mH].children[i_mX].value, SIGNALS[i_mH].children[i_mX].children[i_cTau].value, TYPES[i_type][0], TYPES[i_type][3]);
}

// sets the plot src
function setPlot(mH, mX, cTau, type, stype)
{
	let sstring = mH.toString() + "_" + mX.toString() + "_" + cTau.toString();
	let filename = '';
	if (stype == 'per')
	{
		filename = "img/png/"+type+"_"+sstring+".png";
	}
	else if (stype == 'glo')
	{
		filename = "img/png/"+type+".png";
	}
	document.getElementById("plot").src=filename;
	window.location.hash = 'plottype='+type+'&mH='+mH+'&mX='+mX+'&cTau='+cTau;
}

// **** USEFUL GETTERS AND SETTERS ****
// these are useful getters and setters to make above code prettier
// should be pretty obvious what they do
function getFormValueIndex(i)
{
	let opts = document.forms[i].elements;
	for (j=0; j<opts.length; j++) { if (opts[j].checked) { return j; } }
}

function getOpt(sboxname, index) { return document.getElementById(sboxname+"_opt_"+index.toString()); }
function getLab(sboxname, index) { return document.getElementById(sboxname+"_lab_"+index.toString()); }

function setDisplay(sboxname, index, val)
{
	getOpt(sboxname, index).style.display = val;
	getLab(sboxname, index).style.display = val;
}

function setOption(sboxname, index, val)
{
	getOpt(sboxname, index).value     = val;
	getLab(sboxname, index).innerHTML = val;
}

// pair object constructor for making a tree of signal points
function pair(value, children)
{
	this.value = value;
	this.children = children;
}

// on page load, pre-populate the form using the # anchor string
function prePopulate()
{
	url = window.location;
	if (!url.href.includes('#'))
	{
		update();
		return;
	}
	qs = url.hash.substring(1);
	pairs = qs.split('&');
	for (i=0;i<pairs.length;i++)
	{
		keyval = pairs[i].split('=');
		if (['plottype', 'mH', 'mX', 'cTau'].includes(keyval[0]))
		{
			els = document.getElementById(keyval[0]+"_form").elements;
			for (j=0;j<els.length;j++)
			{
				if (els[j].value == keyval[1])
				{
					els[j].checked = true;
					update();
					break;
				}
			}
		}
	}
	update();
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
	])
];

// plot types.
// the first is the file prefix and used in option/label id
// the second is the actual label HTML
// the third is which div it should go in, 0-3
// make sure all the div 0 come first, then the div 1, then div 2
// or else the indexing isn't going to work
// the fourth is if this is a per signal plot or a global plot
var TYPES = [
	['massH'     , 'm' + 'H'.sub()               , 0, 'per'],
	['massX'     , 'm' + 'X'.sub()               , 0, 'per'],
	['cTau'      , 'c&tau;'                      , 0, 'per'],
	['Lxy'       , 'L' + 'xy'.sub()              , 0, 'per'],
	['d00'       , '&Delta;d' + '0'.sub()        , 0, 'per'],

	['pTH'       , 'p' + 'T'.sub() +' H'         , 1, 'per'],
	['pTX'       , 'p' + 'T'.sub() +' X'         , 1, 'per'],
	['beta'      , '&beta; X'                    , 1, 'per'],
	['d0'        , 'd' + '0'.sub()               , 1, 'per'],
	['pTmu'      , 'p' + 'T'.sub() + ' &mu;'     , 1, 'per'],

	['DSA_pTRes' , 'DSA p' + 'T'.sub() + ' Res'  , 2, 'per'],
	['DSA_d0Dif' , 'DSA d' + '0'.sub() + ' Diff' , 2, 'per'],
	['DSA_nMuon' , 'DSA N' + '&mu;'.sub()        , 2, 'per'],
	['DSA_pTEff' , 'DSA p' + 'T'.sub() + ' Eff'  , 2, 'glo'],
	['DSA_LxyEff', 'DSA L' + 'xy'.sub() + ' Eff' , 2, 'glo'],

	['RSA_pTRes' , 'RSA p' + 'T'.sub() + ' Res'  , 3, 'per'],
	['RSA_d0Dif' , 'RSA d' + '0'.sub() + ' Diff' , 3, 'per'],
	['RSA_nMuon' , 'RSA N' + '&mu;'.sub()        , 3, 'per'],
	['RSA_pTEff' , 'RSA p' + 'T'.sub() + ' Eff'  , 3, 'glo'],
	['RSA_LxyEff', 'RSA L' + 'xy'.sub() + ' Eff' , 3, 'glo']
];

//**** MAIN CODE ****
// "main" code. it runs once when the page is loaded.
// so it actually calls the makeSBox functions
// then update() is run once so that everything gets set up correctly
var signaldiv = document.getElementById("signals");
signaldiv.appendChild(makeSBox("mH",   [125, 200, 400, 1000], "m" + "H".sub()));
signaldiv.appendChild(makeSBox("mX",   [20, 50, 150, 350]   , "m" + "X".sub()));
signaldiv.appendChild(makeSBox("cTau", [13, 130, 1300]      , "c&tau;"       ));
makePlotTypeOptions();
prePopulate();
