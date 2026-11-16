var Clay = require('@rebble/clay');
var defaults = {Palette: 0, Background: 0x000055, Foreground: 0xFFFFAA, Accent: 0xFF5500, TimeFormat: 0, DateFormat: 1};

function integer(value, fallback, maximum) {
  if (value === undefined || value === null || value === '' || typeof value === 'boolean') return fallback;
  var number = Number(value);
  return isFinite(number) && Math.floor(number) === number && number >= 0 && number <= maximum ? number : fallback;
}
function normalize(raw) {
  raw = raw || {};
  return {
    Palette: integer(raw.Palette, defaults.Palette, 6),
    Background: integer(raw.Background, defaults.Background, 0xFFFFFF),
    Foreground: integer(raw.Foreground, defaults.Foreground, 0xFFFFFF),
    Accent: integer(raw.Accent, defaults.Accent, 0xFFFFFF),
    TimeFormat: integer(raw.TimeFormat, defaults.TimeFormat, 2),
    DateFormat: integer(raw.DateFormat, defaults.DateFormat, 4)
  };
}
var clay = new Clay([
  {type: 'heading', defaultValue: 'Rally'},
  {type: 'text', defaultValue: 'A bold scoreboard: hours on the left and minutes on the right.'},
  {type: 'select', messageKey: 'TimeFormat', label: 'Time format', defaultValue: '0', options: [
    {label: 'Watch default', value: '0'}, {label: '12-hour', value: '1'}, {label: '24-hour', value: '2'}
  ]},
  {type: 'select', messageKey: 'DateFormat', label: 'Date', defaultValue: '1', options: [
    {label: 'Off', value: '0'}, {label: 'THU NOV 05', value: '1'},
    {label: 'YYYY-MM-DD', value: '2'}, {label: 'MM/DD/YYYY', value: '3'}, {label: 'DD/MM/YYYY', value: '4'}
  ]},
  {type: 'heading', defaultValue: 'Colors'},
  {type: 'select', messageKey: 'Palette', label: 'Palette', defaultValue: '0', options: [
    {label: 'Navy & orange', value: '0'}, {label: 'Red', value: '1'},
    {label: 'Field green', value: '2'}, {label: 'Plum', value: '3'}, {label: 'Ice', value: '4'},
    {label: 'Monochrome', value: '5'}, {label: 'Custom colors', value: '6'}
  ]},
  {type: 'text', defaultValue: 'Select Custom colors to use the choices below. Background colors the face and left digits. Foreground colors the left panel, right digits and footer. Accent colors the right panel. Choose contrasting colors.'},
  {type: 'color', messageKey: 'Background', label: 'Face & left digits', defaultValue: '000055', sunlight: false, allowGray: true},
  {type: 'color', messageKey: 'Foreground', label: 'Left panel & right digits', defaultValue: 'FFFFAA', sunlight: false, allowGray: true},
  {type: 'color', messageKey: 'Accent', label: 'Right panel', defaultValue: 'FF5500', sunlight: false, allowGray: true},
  {type: 'submit', defaultValue: 'Save to watch'}
], null, {autoHandleEvents: false});

function sendSaved() {
  var raw = localStorage.getItem('clay-settings');
  if (!raw) return;
  try { Pebble.sendAppMessage(normalize(JSON.parse(raw))); } catch (error) { console.log('Rally settings could not be loaded'); }
}
Pebble.addEventListener('ready', sendSaved);
Pebble.addEventListener('showConfiguration', function() { Pebble.openURL(clay.generateUrl()); });
Pebble.addEventListener('webviewclosed', function(event) {
  if (!event || !event.response || event.response === 'CANCELLED') return;
  try {
    clay.getSettings(event.response, false);
    sendSaved();
  } catch (error) { console.log('Rally settings were not saved'); }
});

module.exports = {normalize: normalize, defaults: defaults};
