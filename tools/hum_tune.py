"""자연 흥얼(Seed Audio)의 흠 구간마다 재생속도로 음만 계이름에 맞춤 (안 꺾임은 그대로 · 겹침 X). usage: python3 tools/hum_tune.py in.wav out.wav [마지막음 C4 | same = 원래 높이에서 전부 같은 음]"""
import sys, wave; sys.path.insert(0,'tools'); import numpy as np
from hum_melody import load, f0, SR, hz
src,out=sys.argv[1],sys.argv[2]; LAST=sys.argv[3] if len(sys.argv)>3 else 'C4'   # 마지막 음 (니온 앤 비온드만이면 C4)
x=load(src)[:-int(0.08*SR)]; h=441
db=np.array([20*np.log10(np.sqrt((x[i:i+h]**2).mean())+1e-6) for i in range(0,len(x)-h,h)])
on=db>db.max()-35; segs=[]; i=0
while i<len(on):
    if on[i]:
        j=i
        while j<len(on) and on[j]: j+=1
        if j-i>=4: segs.append((i*h,j*h))
        i=j
    else: i+=1
print('segments',len(segs))
def seg_f0(s): return np.median([f0(s[k:k+2048],190,450) for k in range(0,max(1,len(s)-2048),512)]) if len(s)>2100 else f0(s,190,450)
ALL_MED = np.median([seg_f0(x[a:b]) for a,b in segs])   # 'same': 원래 목소리 높이 그대로, 모든 음을 같은 음으로만 (늘어짐 최소)
y=np.zeros(int(len(x)*2)+SR,np.float32); pos=0; prev_end=0
for n,(a,b) in enumerate(segs):
    gap=a-prev_end; pos+=gap; s=x[a:b]
    vals=[f0(s[k:k+2048],190,450) for k in range(0,max(1,len(s)-2048),512)] if len(s)>2100 else [f0(s,190,450)]
    tg=ALL_MED if LAST=='same' else (hz(LAST) if n==len(segs)-1 else hz('C4')); r=tg/np.median(vals)
    s2=np.interp(np.arange(0,len(s)-1,r),np.arange(len(s)),s).astype(np.float32)   # 구간 통째로 재생속도만 → 안의 자연스러운 꺾임은 그대로
    f=min(len(s2)//4,int(0.01*SR)); s2[:f]*=np.linspace(0,1,f); s2[-f:]*=np.linspace(1,0,f)
    y[pos:pos+len(s2)]+=s2; pos+=len(s2); prev_end=b
y=y[:pos]; y=y/np.abs(y).max()*0.8
with wave.open(out,'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y*32767).astype(np.int16).tobytes())
print(out, round(len(y)/SR,2))
