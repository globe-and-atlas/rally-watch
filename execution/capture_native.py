"""Capture fixture cases from the root-owned, already-running Emery emulator."""
from pathlib import Path
import argparse
import importlib.util
import json
import socket
import subprocess
import time
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
UUID=json.loads((ROOT/'watchface/package.json').read_text())['pebble']['uuid']
PALETTES=[((0,0,85),(255,255,170),(255,85,0)),((0,0,0),(255,255,255),(170,0,0)),
          ((0,85,0),(255,255,255),(0,85,170)),((85,0,85),(255,255,255),(170,0,85)),
          ((0,0,0),(170,255,255),(0,85,170)),((255,255,255),(0,0,0),(170,170,170))]
CUSTOM=((0,0,85),(255,255,255),(170,0,85))
spec=importlib.util.spec_from_file_location('desk_digits',ROOT/'execution/generate_digits.py')
digits=importlib.util.module_from_spec(spec);spec.loader.exec_module(digits)


def command(args: list[str]) -> None:
    result=subprocess.run(['pebble']+args,cwd=ROOT/'watchface',capture_output=True,text=True,timeout=45)
    if result.returncode:raise RuntimeError(result.stderr[-1500:])


def screenshot(port: int, expected_peak: int) -> Image.Image:
    path=ROOT/'.tmp/native-frame.ppm';path.unlink(missing_ok=True)
    with socket.create_connection(('localhost',port),timeout=5) as connection:
        connection.recv(65536)
        connection.sendall(f'screendump "{path.resolve()}"\n'.encode())
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            connection.recv(65536)
            try:
                result=Image.open(path).convert('RGB');break
            except (FileNotFoundError,OSError):continue
        else:raise TimeoutError('QEMU screendump incomplete')
    pixels=result.get_flattened_data() if hasattr(result,'get_flattened_data') else result.get_flattened_data()
    peak=max(max(pixel) for pixel in pixels)
    result=result.point(lambda channel:round(channel/max(peak,1)*expected_peak/85)*85)
    path.unlink(missing_ok=True)
    assert result.size==(200,228)
    return result


def pair_left(value,panel_x):
    left=digits.glyph_mask(value//10).getbbox()[0];right=digits.glyph_mask(value%10).getbbox()[2]-1
    return panel_x+int((87-left-38-right)/2)


def check(image,hour,minute,format_,date,battery,colors):
    bg,fg,accent=colors
    assert image.getpixel((2,2))==bg,'Background differs'
    assert image.getpixel((50,35))==fg,'Hour panel differs'
    assert image.getpixel((150,35))==accent,'Minute panel differs'
    display=hour if format_==2 else (hour%12 or 12)
    for value,panel_x,panel_color,ink in [(display,8,fg,bg),(minute,104,accent,fg)]:
        left=pair_left(value,panel_x)
        for digit,x in [(value//10,left),(value%10,left+38)]:
            expected=Image.new('RGB',(34,76),panel_color);expected.paste(ink,(0,0,34,76),digits.glyph_mask(digit))
            assert image.crop((x,43,x+34,119)).tobytes()==expected.tobytes(),'Athletic numeral pixels differ'
        points=[x for y in range(43,119) for x in range(panel_x+2,panel_x+86) if image.getpixel((x,y))==ink]
        assert abs((min(points)+max(points))/2-(panel_x+43.5))<=.5,'Panel pair not centered'
    assert any(p==fg for p in image.crop((60,8,140,26)).get_flattened_data())==(format_==1),'AMPM differs'
    assert any(p==fg for p in image.crop((10,157,190,187)).get_flattened_data())==(date!=0),'Date differs'
    left=next(x for x in range(25,100) if image.getpixel((x,207))==fg)
    bars=(battery+24)//25
    for index in range(4):
        assert image.getpixel((left+7+10*index,207))==(fg if index<bars else bg),'Battery bars differ'


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--monitor',required=True,type=int)
    options=parser.parse_args()
    keys=json.loads((ROOT/'watchface/build/js/message_keys.json').read_text())
    media=ROOT/'media';media.mkdir(exist_ok=True);(ROOT/'.tmp').mkdir(exist_ok=True)
    # Explicit12/24 cases avoid dependency on the emulator's clock-style preference.
    cases=[('default',10,8,2,1,0,82)]
    cases += [(f'palette-{p}',10,8,2,1,p,82) for p in range(1,6)]
    cases += [('custom',10,8,2,1,6,82)]
    cases += [(f'date-{d}',10,8,2,d,0,82) for d in range(5)]
    cases += [(f'{name}-{fmt}h',h,m,fmt,1,0,82) for name,h,m in [('midnight',0,0),('noon',12,0),('late',23,59),('eleven',11,11)] for fmt in [1,2]]
    cases += [('battery-empty',10,8,2,1,0,0),('battery-full',10,8,2,1,0,100)]
    evidence=[]
    for name,hour,minute,format_,date,palette,battery in cases:
        colors=CUSTOM if palette==6 else PALETTES[palette]
        values={keys['Palette']:palette,keys['TimeFormat']:format_,keys['DateFormat']:date,11000:hour,11001:minute,11004:battery}
        if palette==6:
            for key,rgb in zip(['Background','Foreground','Accent'],CUSTOM):values[keys[key]]=(rgb[0]<<16)|(rgb[1]<<8)|rgb[2]
        command(['send-app-message','--emulator','emery','--app-uuid',UUID,'--int']+[f'{key}={value}' for key,value in values.items()])
        error=None
        for attempt in range(30):
            image=screenshot(options.monitor,max(max(rgb) for rgb in colors))
            try:
                check(image,hour,minute,format_,date,battery,colors);break
            except AssertionError as caught:error=caught;time.sleep(.1)
        else:raise AssertionError(f'{name}: {error}')
        image.save(media/f'rally-{name}.png')
        evidence.append({'case':name,'exact_digit_pixels':True,'palette':palette,'date':date,'time_format':format_,'battery':battery})
        print(f'PASS: {name}',flush=True)
    (ROOT/'.tmp/native-checks.json').write_text(json.dumps(evidence,indent=2))
    contact=Image.new('RGB',(4*220,((len(cases)+3)//4)*258),(32,32,32));draw=ImageDraw.Draw(contact)
    for index,(name,*_) in enumerate(cases):
        x=index%4*220+10;y=index//4*258
        contact.paste(Image.open(media/f'rally-{name}.png'),(x,y));draw.text((x,y+232),name,fill='white')
    contact.save(ROOT/'.tmp/native-contact.png')
    # Restore visual default at end for the root comparison board.
    command(['send-app-message','--emulator','emery','--app-uuid',UUID,'--int']+[f'{key}={value}' for key,value in {keys['Palette']:0,keys['TimeFormat']:2,keys['DateFormat']:1,11000:10,11001:8,11004:82}.items()])
if __name__=='__main__':main()
