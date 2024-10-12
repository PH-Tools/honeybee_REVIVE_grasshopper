// Copyright  1999-2015 Russell K. Marcks, P.E.  All rights reserved
// No part of this script and associated web page may be produced, transmitted, transcribed,
// stored in a retrieval system, or translated into any language in any form without the
// express written consent of the author.

//establish parameters & constants
var barcalc = 2;
var watercalc = 2;

//constants for vapor pressure over water/ice per
//ASHRAE HOF 1993 and ANSI/ASHRAE 41.6-1994
var c1 = -5674.5359;
var c2 = -0.51523058;
var c3 = -0.0096778430;
var c4 = 0.00000062215701;
var c5 = 0.0000000020747825;
var c6 = -0.00000000000094840240;
var c7 = 4.1635019;
var c8 = -5800.2206;
var c9 = -5.5162560;
var c10 = -0.048640239;
var c11 = 0.000041764768;
var c12 = -0.000000014452093;
var c13 = 6.5459673;

//constants to determine dew point
var c14 = 6.54;
var c15 = 14.526;
var c16 = 0.7389;
var c17 = 0.09486;
var c18 = 0.4569;

//define variables
var hg;
var elev;
var kpa;

//This variable may no longer be needed
var dbtemp;
var wb;

//Dewpoint
var dew_point;

var rh;
var pws;
var dp;
var wstar;
var wsstar;
var pwsstar;

//dummy variable
var x;

//Barometric pressure based on elevation
function bara(form) {
    barcalc = 1;
    form.elev.value = "306";   //306 meters amsl is elevation for Dayton
    elev = 306;
}

//Barometric pressure in kPa
function barb(form) {
    barcalc = 2;
    form.elev.value = "101.3";
    kpa = 101.325;
}

//Barometric pressure in mm hg
function barc(form) {
    barcalc = 3;
    form.elev.value = "760";
    hg = 760;
}

//set value of parameter used to find barometric pressure
function setelev(elv) {
    if (barcalc == 1) { elev = elv.value; }
    else if (barcalc == 3) { hg = elv.value; }
    else if (barcalc == 2) { kpa = elv.value; }
}

//Humidity parameter is rh
function watera(form) {
    watercalc = 1;
    form.watervalue.value = "50";
    rh = 0.50;
    form.dbtemp.value = "";
    clearparta(form);
}        //Clear table

//Humidity parameter is wb
function waterb(form) {
    watercalc = 2;
    form.watervalue.value = "";
    form.dbtemp.value = "";
    clearparta(form);
}        //Clear table

function waterc(form)        //Humidity parameter is dp
{
    watercalc = 3;
    form.watervalue.value = "";
    form.dbtemp.value = "";
    clearparta(form);
}        //Clear table

function setwater(hto)       //set value of humidity parameter
{
    if (watercalc == 1) { rh = hto.value / 100; }
    if (watercalc == 2) { wb = hto.value; }
    if (watercalc == 3) { dp = hto.value; }
}

function setdb(form)         //set dry bulb as a temporary variable
{
    dbtemp = document.worksheet.dbtemp.value;
    if ((dbtemp * 1.8 + 32) > 50) {
        document.worksheet.wind1.checked = false; //disable wind chill calculation above 10 deg C
        document.worksheet.wind1.disabled = true;
        document.worksheet.wind.value = "";
        document.worksheet.wind.disabled = true;
    }
    else {
        document.worksheet.wind1.disabled = false;
        document.worksheet.wind.disabled = false;
    }
}

function ppw(t)              //calc saturation pressure over water equal or above 0 deg
{
    x = (273.15 + t * 1);
    pws = Math.exp(c8 / x + c9 + c10 * x + c11 * Math.pow(x, 2) + c12 * Math.pow(x, 3) + c13 * Math.log(x));
    return pws;
}

function ppww(t)             //calc saturation pressure over ice below 0 deg
{
    x = (273.15 + t * 1);
    pws = Math.exp(c1 / x + c2 + c3 * x + c4 * Math.pow(x, 2) + c5 * Math.pow(x, 3) + c6 * Math.pow(x, 4) + c7 * Math.log(x));
    return pws;
}

function wws(p, pw)           //calc humidity ratio based on barometric pressure and partial pressure of water
{
    var ws = 0.62198 * pw / (p - pw);
    return ws;
}

db, wb, wss
function wwb(db, wb, wss)    //calc humidity ratio based on wb db and ws
{
    var w = ((2501 - 2.381 * wb) * wss - (db - wb)) / (2501 + 1.805 * db - 4.186 * wb);
    return w;
}

function wetbulb(guess, db, p) //Calculate wet bulb iteration parameters
{
    pwsstar = ppw(guess);
    wsstar = wws(p, pwsstar);
    wstar = wwb(db, guess, wsstar);
    return wstar;
}

function prh(saturation, partialPressureWaterDryBulb, barometricPressure)      //calc percent rh
{
    var rh = saturation / (1 - (1 - saturation) * (partialPressureWaterDryBulb / barometricPressure));
    return rh;
}

function h(db, w)             //calc enthalpy
{
    var enthalpy = 1.006 * db + w * (2501 + 1.805 * db);
    return enthalpy;
}

//calc dew point
function dew(pw, relative_humidity, dry_bulb, wet_bulb) {
    var a = Math.log(pw);
    dew_point = c14 + c15 * a + c16 * Math.pow(a, 2) + c17 * Math.pow(a, 3) + c18 * Math.pow(pw, 0.1984);

    if (dew_point < 0) { dew_point = 6.09 + 12.608 * a + 0.4959 * Math.pow(a, 2); }

    if (relative_humidity == 100) { var dew_point = dry_bulb; }

    if (dry_bulb == wet_bulb) { var dew_point = dry_bulb; }

    if (relative_humidity == 0) { var dew_point = -273.15; }

    return dew_point;
}

function cpa(db)             //specific heat of dry air (Shapiro 2ed)
{
    var t = db * 1 + 273.15;
    var a = 3.653;
    var b = -1.337e-3;
    var c = 3.294e-6;
    var d = -1.913e-9;
    var e = 0.2763e-12;
    var cpair = (a * 1 + b * t + c * Math.pow(t, 2) + d * Math.pow(t, 3) + e * Math.pow(t, 4)) * 0.287055;
    return cpair;
}

function cpw(db)             //specific heat of water vapor (Shapiro 2ed)
{
    var t = db * 1 + 273.15;
    var a = 4.070;
    var b = -1.108e-3;
    var c = 4.152e-6;
    var d = -2.964e-9;
    var e = 0.807e-12;
    var cpvapor = (a * 1 + b * t + c * Math.pow(t, 2) + d * Math.pow(t, 3) + e * Math.pow(t, 4)) * 0.461520;
    return cpvapor;
}

function psych(form)         //calc psychrometric parameters
{
    var pws;                    //Declare variables
    var wss;
    var w;
    var saturationPressure;
    var ws;
    var saturation;
    var vol;
    var density;
    var enthalpy;
    var u;                      //internal energy
    var pw;
    var db = document.worksheet.dbtemp.value;   //Redefine dry bulb
    //var c = clearparta(form); //Clear table  (why does this exist?  see if can eliminate)
    var sph;
    var barometricPressure;
    var cp;
    var cv;
    var k;
    var speed;                  //speed of sound in air sample
    var chill;                  //windchill
    var mw;                     //molecular weight
    var molefractionwater;
    var gasconstant;
    var entropyair;
    var entropyvapor;
    var entropy;
    var tv;                     //Virtual Temperature

    if (document.worksheet.wind1.checked == true) //Wind Chill
    {
        var dbimp = db * 1.8 + 32;
        var wind0 = document.worksheet.wind.value / 0.44704; //convert m/s to mph
        chill = ((35.74 + 0.6215 * dbimp - 35.75 * Math.pow(wind0, 0.16) + 0.4275 * dbimp * Math.pow(wind0, 0.16)) - 32) / 1.8;
    }

    if (barcalc == 1)            //Calculate barometric pressure from elevation and express in kPa
    { barometricPressure = (29.921 * Math.pow((1 - 6.87535e-06 * elev / 0.3048), 5.256) * 3.38650); }
    else if (barcalc == 3)       //Convert in hg to mm hg
    { barometricPressure = hg * 0.13331; }
    else if (barcalc == 2)       //accept kPa input
    { barometricPressure = kpa; }

    if (db < 0)                //Partial pressure of water vapor at dry bulb
    { saturationPressure = ppww(db); }
    else { saturationPressure = ppw(db); }

    if (watercalc == 3)          //Partial pressure of water vapor at dew point
    {
        {
            if (dp < 0) { pw = ppww(dp); }
            else { pw = ppw(dp); }
        }
        { w = wws(barometricPressure, pw); }
    }     //Humidity ratio of actual air sample

    if (watercalc == 2) {
        {
            if (wb < 0) { pws = ppww(wb); }
            else { pws = ppw(wb); }
        } //Partial pressure of water vapor at wet bulb
        {
            wss = wws(barometricPressure, pws);      //Humidity ratio at saturation if db equals wb
            w = wwb(db, wb, wss);
        }
    } //Humidity ratio of actual air sample

    if (watercalc == 1) {
        pw = saturationPressure * rh;            //Partial pressure of water vapor in air sample
        w = wws(barometricPressure, pw);
    }      //Humidity ratio of actual air sample

    sph = w / (1 + w);               //Specific humidity

    molefractionwater = w / (w + 0.62198);  //Mole fraction of water in air sample

    mw = molefractionwater * 18.01528 + (1 - molefractionwater) * 28.96443; //Molecular weight of moist air sample

    gasconstant = 8.314472 / mw;   //Gas constant for actual air sample

    cp = cpa(db) * (1 - molefractionwater) + cpw(db) * molefractionwater;   //Isobaric specific heat

    cv = cp - gasconstant;                                                //Isometric specific heat

    k = cp / cv;                                                            //Specific heat ratio

    entropyair = cpa(db) * Math.log((db * 1 + 273.15) / 273.15);              //Entropy of dry air

    entropyvapor = 9.75441 - cpw(db) * Math.log((db * 1 + 273.15) / 273.15);  //Entropy of water vapor

    entropy = entropyair + entropyvapor * w;                              //Entropy moist air sample

    speed = Math.sqrt(k * gasconstant * (db * 1 + 273.15) * 9.80665);               //Speed of sound

    ws = wws(barometricPressure, saturationPressure);                                                     //Humidity ratio of saturated air sample

    saturation = w / ws;                                                    //Degree of saturation

    if (watercalc > 1)                                                    //Relative humidity
    { rh = prh(saturation, saturationPressure, barometricPressure); }

    vol = 0.287055 * (db * 1 + 273.15) * (1 + 1.60776874 * w) / barometricPressure;                     //Psych specific volume

    density = (1 / vol) * (1 + w);                                              //Density

    enthalpy = h(db, w);                                                   //Enthalpy

    u = enthalpy - gasconstant * (db * 1 + 273.15);                             //Internal energy

    enthalpys = db * cpa(db);                                             //Sensible enthalpy

    enthalpyl = enthalpy - enthalpys;                                     //Latent enthalpy

    //z = (bp*144*mw)/((db*1 + 459.67)*1545.3488*density);                //Compressibility factor
    //Compressibility is no longer displayed or used in calculations.  Keep for now

    tv = (1 + 0.608 * w) * (db * 1 + 273.15) - 273.15;                            //Virtual Temperature

    if (watercalc == 2)                                                    //Partial pressure of water vapor in actual sample
    { pw = (barometricPressure * w) / (0.62198 + w * 1); }

    if (watercalc != 3)                                                   //Dew point
    { dp = dew(pw, rh, db, wb); }

    if (watercalc != 2)                                                   //Wet bulb
    {
        var step = 10;
        var guess = db - step;
        wstar = wetbulb(guess, db, barometricPressure);
        while (Math.abs(wstar - w) > 0.000001) {
            if ((wstar - w) < 0) {
                guess = guess + step * 1;
                step = step / 10;
                guess = guess - step;
                wstar = wetbulb(guess, db, barometricPressure);
            }
            else {
                guess = guess - step;
                wstar = wetbulb(guess, db, barometricPressure);
            }
        }

        if (db == dp) { wb = db; }
        else { wb = guess; }
    }                                                  //End wet bulb

    if (db == "" || document.worksheet.elev.value == "")                //Error messages
    { document.worksheet.comment.value = "Check your data entry"; }
    else if ((w * 1 < 0 || rh * 1 < 0) && watercalc == 2) { document.worksheet.comment.value = "Wet bulb is to low for stated dry bulb"; }
    else if (db * 1 < wb * 1 && watercalc == 2) { document.worksheet.comment.value = "Wet bulb cannot exceed dry bulb"; }
    else if (dp * 1 > db * 1 && watercalc == 3) { document.worksheet.comment.value = "Dew point cannot exceed dry bulb"; }
    else if ((rh * 1 < 0 || rh * 1 > 1) && watercalc == 1) { document.worksheet.comment.value = "Relative humidity must be between 0% and 100% inclusive"; }
    else                                                                 //Truncate excess decimals and display
    {
        document.worksheet.dbfinal.value = Math.round(document.worksheet.dbtemp.value * 10) / 10;
        document.worksheet.wbfinal.value = Math.round(wb * 10) / 10;
        document.worksheet.rhfinal.value = Math.round(rh * 1000) / 10;
        document.worksheet.dpfinal.value = Math.round(dp * 10) / 10;
        document.worksheet.satfinal.value = Math.round(saturation * 1000) / 10;
        document.worksheet.wfinal.value = Math.round(w * 100000) / 100000;
        document.worksheet.hfinal.value = Math.round(enthalpy * 100) / 100;
        document.worksheet.hsfinal.value = Math.round(enthalpys * 100) / 100;
        document.worksheet.hlfinal.value = Math.round(enthalpyl * 100) / 100;
        document.worksheet.inteng.value = Math.round(u * 100) / 100;
        document.worksheet.psvfinal.value = Math.round(vol * 1000) / 1000;
        document.worksheet.svfinal.value = Math.round((1 / density) * 100) / 100;
        document.worksheet.densityfinal.value = Math.round(density * 100) / 100;
        document.worksheet.abhfinal.value = Math.round((density - 1 / vol) * 10000) / 10000;
        document.worksheet.barfinal.value = Math.round(barometricPressure * 10) / 10;
        document.worksheet.sphfinal.value = Math.round(sph * 100000) / 100000;
        document.worksheet.cpfinal.value = Math.round(cp * 1000) / 1000;
        document.worksheet.k_final.value = Math.round(k * 100) / 100;
        document.worksheet.cvfinal.value = Math.round(cv * 1000) / 1000;
        document.worksheet.speedofsoundfinal.value = Math.round(speed * 10) / 10;
        document.worksheet.entropyfinal.value = Math.round(entropy * 1000) / 1000;
        document.worksheet.gasconstant.value = Math.round(gasconstant * 1000) / 1000;
        document.worksheet.molefraction.value = Math.round((1 - molefractionwater) * 10000) / 100;
        document.worksheet.molwgt.value = Math.round(mw * 100) / 100;
        if (document.worksheet.wind1.checked == true) { document.worksheet.windchill.value = Math.round(chill * 10) / 10; }
        else { document.worksheet.windchill.value = "------"; }
        document.worksheet.tv.value = Math.round(tv * 10) / 10;

        if (dp < -45 || dp > 93 || db < -100 || wb < -100 || db > 200 || wb > 200) { document.worksheet.comment.value = "Results are outside the scope of ANSI/ASHRAE 41.6-1994"; }
        else { document.worksheet.comment.value = "Results are within the scope of ANSI/ASHRAE 41.6-1994"; }
    }
}

function clearall(form)      //clear all user inputs
{
    clearparta(form);
    clearpartb(form);
    clearpress(form);
    document.location = '#start';
}

function clearparta(form)    //clear result table
{
    document.worksheet.dbfinal.value = "";
    document.worksheet.wbfinal.value = "";
    document.worksheet.rhfinal.value = "";
    document.worksheet.dpfinal.value = "";
    document.worksheet.satfinal.value = "";
    document.worksheet.wfinal.value = "";
    document.worksheet.hfinal.value = "";
    document.worksheet.psvfinal.value = "";
    document.worksheet.svfinal.value = "";
    document.worksheet.densityfinal.value = "";
    document.worksheet.barfinal.value = "";
    document.worksheet.sphfinal.value = "";
    document.worksheet.cpfinal.value = "";
    document.worksheet.cvfinal.value = "";
    document.worksheet.k_final.value = "";
    document.worksheet.entropyfinal.value = "";
    document.worksheet.speedofsoundfinal.value = "";
    document.worksheet.comment.value = "";
    document.worksheet.gasconstant.value = "";
    document.worksheet.molefraction.value = "";
    document.worksheet.hsfinal.value = "";
    document.worksheet.hlfinal.value = "";
    document.worksheet.inteng.value = "";
    document.worksheet.windchill.value = "";
    document.worksheet.molwgt.value = "";
    document.worksheet.abhfinal.value = "";
    document.worksheet.tv.value = "";
}

function clearpartb(form)    //clear temperature/humidity inputs
{
    document.worksheet.watervalue.value = "";
    document.worksheet.dbtemp.value = "";
    document.worksheet.water[0].checked = false;
    document.worksheet.water[1].checked = false;
    document.worksheet.water[2].checked = false;
    document.worksheet.wind1.disabled = false;
    document.worksheet.wind1.checked = false;
    document.worksheet.wind.disabled = false;
    document.worksheet.wind.value = "";
}

function clearpress(form)    //clear barometric pressure form
{
    document.worksheet.elev.value = "";
    document.worksheet.bar[0].checked = false;
    document.worksheet.bar[1].checked = false;
    document.worksheet.bar[2].checked = false;
}

function more(form) {
    if (parent.location.search) {
        dbtemp = parseFloat(parent.location.search.substr(1, 5));
        document.worksheet.dbtemp.value = Math.round(dbtemp * 1000) / 1000;
        barcalc = parseInt(parent.location.search.substr(18, 1));
        elev = parseFloat(parent.location.search.substr(11, 7));         //barcalc = 1
        hg = parseFloat(parent.location.search.substr(11, 7));           //barcalc = 3
        kpa = parseFloat(parent.location.search.substr(11, 7));          //barcalc = 2
        document.worksheet.elev.value = Math.round((elev * (barcalc == 1) + kpa * (barcalc == 2) + hg * (barcalc == 3)) * 1000) / 1000;
        document.worksheet.bar[barcalc - 1].checked = true;
        watercalc = parseInt(parent.location.search.substr(19, 1));
        rh = parseFloat(parent.location.search.substr(6, 5));            //watercalc = 1
        wb = parseFloat(parent.location.search.substr(6, 5));            //watercalc = 2
        dp = parseFloat(parent.location.search.substr(6, 5));            //watercalc = 3
        document.worksheet.watervalue.value = Math.round((rh * (watercalc == 1) * 100 + wb * (watercalc == 2) + dp * (watercalc == 3)) * 100) / 100;
        document.worksheet.water[watercalc - 1].checked = true;
        setdb();
        document.worksheet.wind1.checked = parseFloat(parent.location.search.substr(20, 1)) * 1;
        document.worksheet.wind.value = Math.round(parseFloat(parent.location.search.substr(21, 4)) * 100) / 100;
        psych();
    }
}
