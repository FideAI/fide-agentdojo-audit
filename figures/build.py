"""Render review manuscripts and research figures from verified companion counters.
No model calls, archive execution, network or changes to the sealed companion.
"""
from pathlib import Path
import hashlib, html, json, os, subprocess, sys
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import markdown

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
result=subprocess.run([sys.executable,'-B',str(PROJECT/'archive/verify.py')],capture_output=True,text=True,check=True)
c=json.loads(result.stdout)
assert c['passed']
a=c['arms']; rows=[]
for key,label in [('baseline','Baseline'),('repeat_user_prompt','Repeat prompt'),('spotlighting_with_delimiting','Spotlighting'),('tool_filter','Tool filter'),('transformers_pi_detector','Detector')]:
    rows.append(dict(configuration=label,**a[key]))
sourcefiles=['data/comparison-count-inputs.json','data/observability-count-inputs.json']
data=dict(scope='Selected task 0 / important_instructions / five GPT-4o-2024-05-13 configurations; exploratory, post hoc. No new model runs.',source_commit=c['upstream_commit'],rows=rows,sources=[dict(path='../archive/'+n,sha256=sha(PROJECT/'archive'/n)) for n in sourcefiles],uncertainty='Logical event-evidence bounds, not confidence intervals. Fixed-state scores and saved labels remain distinct.')
(ROOT/'figure-data.json').write_text(json.dumps(data,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.edgecolor':'#9a9a91','axes.labelcolor':'#272b27','text.color':'#272b27','xtick.color':'#555b55','ytick.color':'#272b27','figure.facecolor':'#faf9f4','axes.facecolor':'#faf9f4','svg.fonttype':'none','pdf.fonttype':42})
ink='#244c46'; neutral='#919991'; accent='#ad643c'
def header(fig,title,sub):
    fig.text(.08,.955,'FIDE AI  /  AGENTDOJO AUDIT',fontsize=10,weight='bold',color=ink)
    fig.text(.08,.892,title,fontsize=21,weight='bold')
    fig.text(.08,.84,sub,fontsize=11,color='#555b55')
def save(fig,name):
    for ext in ['png','pdf','svg']:
        fig.savefig(ROOT/f'{name}.{ext}',dpi=180,facecolor=fig.get_facecolor(),metadata={'Creator':'Fide AI — figures/build.py'} if ext!='png' else None)
    plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,7),gridspec_kw={'wspace':.27})
fig.subplots_adjust(left=.12,right=.95,top=.69,bottom=.30)
header(fig,'The filter changed which defense looked better','Saved attack-success labels held fixed. Lower rates favor a defense on this metric only.')
for ax,shared,title in [(axs[0],False,'All 40 selected tasks'),(axs[1],True,'Common 29 retained tasks')]:
    field='shared_publisher' if shared else 'full_publisher'; denom=29 if shared else 40
    vals=[a['transformers_pi_detector'][field],a['tool_filter'][field]]
    ax.barh([1,0],[100*v/denom for v in vals],height=.43,color=[ink,neutral])
    for y,v in zip([1,0],vals):
        if v==0: ax.plot(0,y,'o',color=ink,markersize=5,clip_on=False)
        ax.text(100*v/denom+.7,y,f'{v}/{denom}',va='center',fontsize=14,weight='bold')
    ax.set_xlim(0,25);ax.set_ylim(-.65,1.65);ax.set_yticks([1,0],['Detector','Tool filter'])
    ax.set_xticks([0,5,10,15,20,25],[f'{v}%' for v in [0,5,10,15,20,25]])
    ax.set_title(title,loc='left',fontsize=14,pad=15,weight='bold')
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0,pad=9)
    ax.set_axisbelow(True);ax.grid(axis='x',alpha=.18);ax.set_xlabel('Saved attack-success rate',labelpad=12)
fig.text(.08,.145,'Removed from the detector: all 8 labeled successes + 3 labeled failures.',fontsize=12,weight='bold')
fig.text(.08,.09,'Fide applied the same 11-task exclusion to both configurations. This is our audit filter,\nnot an upstream leaderboard change. One objective / attack family; exploratory sample.',fontsize=10,linespacing=1.5)
fig.text(.08,.025,'Source: pinned AgentDojo records; Fide selection audit. Figure data and code accompany the paper.',fontsize=9,color='#555b55')
save(fig,'selection-comparison')
fig,ax=plt.subplots(figsize=(11,7));fig.subplots_adjust(left=.24,right=.94,top=.72,bottom=.30)
header(fig,'Same reconstructed states. Different scores.','Direct task-0 predicate substitution on the same 29 tasks in each configuration.')
for y,r in zip(range(4,-1,-1),rows):
    x0=r['shared_original'];x1=r['shared_corrected']
    ax.plot([x0,x1],[y,y],color='#b7bdb7',lw=3,zorder=1)
    ax.scatter([x0],[y],s=90,facecolors='#faf9f4',edgecolors=neutral,lw=2,zorder=3)
    ax.scatter([x1],[y],s=44,color=ink,zorder=4)
    ax.text(max(x0,x1)+.6,y,f'{x0} → {x1}' if x0!=x1 else f'{x1} → {x1}',va='center',fontsize=12)
ax.set_ylim(-.6,4.6);ax.set_xlim(-.5,29);ax.set_xticks([0,5,10,15,20,25,29]);ax.set_yticks(range(4,-1,-1),[r['configuration'] for r in rows]);ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0,pad=12);ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True);ax.set_xlabel('Reconstructed attack successes / 29 tasks',labelpad=12)
fig.text(.24,.78,'○ Original predicate     ● Shipped task-0 predicate',fontsize=11,color=ink)
fig.text(.08,.145,'The ordering stays the same. These are reconstructed scores, not fresh trials.',fontsize=12,weight='bold')
fig.text(.08,.09,'Later event-evidence analysis leaves repeat prompt at 5–6/29; point five retains the original\nstate-reconstruction assumptions. Event bounds are a different measure, not confidence intervals.',fontsize=10,linespacing=1.5)
fig.text(.08,.025,'Source: pinned AgentDojo records; Fide predicate comparison. All values are counts out of 29.',fontsize=9,color='#555b55')
save(fig,'predicate-comparison')
