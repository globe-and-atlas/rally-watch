from pathlib import Path
import subprocess
import importlib.util
ROOT=Path(__file__).resolve().parents[1]

def test_policy():
 folder=ROOT/'.tmp';folder.mkdir(exist_ok=True);source=folder/'policy.c';binary=folder/'policy'
 source.write_text('''#include <assert.h>
#include "policy.h"
int main(void){
for(int h=0;h<24;h++){
assert(display_hour(h,2,false)==h);assert(display_hour(h,1,true)==(h%12?h%12:12));
assert(display_hour(h,0,true)==h);assert(display_hour(h,0,false)==(h%12?h%12:12));}
for(int n=0;n<60;n++)for(int p=8;p<=104;p+=96){
int x=pair_left(n,p),l=x+DIGIT_LEFT[n/10],r=x+38+DIGIT_RIGHT[n%10];
assert(l>p+3 && r<p+84);assert(l+r>=2*p+86 && l+r<=2*p+88);
}
assert(battery_bars(0)==0);assert(battery_bars(100)==4);
for(int w=20;w<=60;w++){int x=battery_group_left(w);assert(x>=0 && x+60+w<=200);}
return 0;}
''')
 subprocess.run(['cc','-Wall','-Werror','-I',str(ROOT/'watchface/src/c'),str(source),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)

def test_numeral_masks():
 spec=importlib.util.spec_from_file_location('digits',ROOT/'execution/generate_digits.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 for n in range(10):
  im=m.glyph_mask(n);assert im.size==(34,76);box=im.getbbox();assert box and box[1]<=2 and box[3]>=74
  assert box[0]>=0 and box[2]<=34
