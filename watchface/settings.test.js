var assert=require('assert'),Module=require('module'),path=require('path');
var original=Module._load;
var keys={Palette:10000,Background:10001,Foreground:10002,Accent:10003,TimeFormat:10004,DateFormat:10005};
var bundle=path.join(__dirname,'node_modules/@rebble/clay/src/js/index.js');
var config;
Module._load=function(name) {
 if(name==='message_keys') return keys;
 if(name==='@rebble/clay') {
  var ActualClay=original.call(this,bundle);
  return function(items,custom,options) {config=items;return new ActualClay(items,custom,options);};
 }
 return original.apply(this,arguments);
};
var events={},storage={},sent=[];
global.localStorage={getItem:function(k) {return storage[k]||null;},setItem:function(k,v) {storage[k]=v;}};
global.Pebble={
 addEventListener:function(k,fn) {(events[k]||(events[k]=[])).push(fn);},
 getAccountToken:function() {return 'test';},getWatchToken:function() {return 'test';},
 getActiveWatchInfo:function() {return {platform:'emery',model:'emery',language:'en_US',firmware:{major:4,minor:33,patch:1}};},
 sendAppMessage:function(value) {sent.push(value);},openURL:function(url) {assert(url.indexOf('data:text/html')===0);}
};
var settings=require('./src/pkjs/index');
function fire(name,event) {(events[name]||[]).forEach(function(fn) {fn(event);});}
assert.deepStrictEqual(settings.normalize({}),settings.defaults);
for(var p=0;p<=6;p++) assert.strictEqual(settings.normalize({Palette:String(p)}).Palette,p);
for(var t=0;t<=2;t++) assert.strictEqual(settings.normalize({TimeFormat:String(t)}).TimeFormat,t);
for(var d=0;d<=4;d++) assert.strictEqual(settings.normalize({DateFormat:String(d)}).DateFormat,d);
assert.deepStrictEqual(settings.normalize({Palette:7,TimeFormat:-1,DateFormat:5,Background:null,Foreground:true,Accent:'invalid'}),settings.defaults);
assert.strictEqual(settings.normalize({Background:0}).Background,0);
fire('ready');assert.strictEqual(sent.length,0);fire('showConfiguration');
fire('webviewclosed',{response:''});fire('webviewclosed',{response:'CANCELLED'});fire('webviewclosed',{response:'invalid'});
assert.strictEqual(sent.length,0);
var raw={Palette:{value:'6'},Background:{value:0},Foreground:{value:0xAAFFAA},Accent:{value:0xAAFFFF},TimeFormat:{value:'2'},DateFormat:{value:'4'}};
fire('webviewclosed',{response:encodeURIComponent(JSON.stringify(raw))});
assert.deepStrictEqual(sent[0],{Palette:6,Background:0,Foreground:0xAAFFAA,Accent:0xAAFFFF,TimeFormat:2,DateFormat:4});
fire('ready');assert.deepStrictEqual(sent[0],sent[1]);
Object.keys(keys).forEach(function(key) {assert(config.some(function(item) {return item.messageKey===key;}));});
console.log('PASS: Rally palettes, custom colors, time/date, real Clay Save/Cancel/reload');
