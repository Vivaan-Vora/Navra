"""Policy comparator."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from environment import generate_environment
from pathfinder import astar
from q_agent import QLearningAgent, ACTIONS
from sensors import get_sensor_vector
from scorer import compute_vns

def _rollout(agent: QLearningAgent, env, max_steps: int) -> dict:
    """Roll out one greedy episode."""
    pos=env.start; path=[pos]; reward=0.0; collisions=0
    for _ in range(max_steps):
        s=get_sensor_vector(env,pos)
        a=int(max(range(4), key=lambda i: agent._get_q(agent._state_key(s))[i]))
        dr,dc=ACTIONS[a]; n=(pos[0]+dr,pos[1]+dc)
        if not env.in_bounds(n) or env.is_obstacle(n):
            collisions+=1; reward-=10; n=pos
        elif n==env.goal:
            reward+=100; path.append(n); return {'path':path,'reward':reward,'collisions':collisions,'success':True}
        else:
            reward-=1
        pos=n; path.append(pos)
    return {'path':path,'reward':reward,'collisions':collisions,'success':False}

def compare_agents(config: dict, q_agent: QLearningAgent, environments: int=10, seed: int=42) -> None:
    """Create side-by-side frames and summary plot."""
    out=Path('logs/plots')/f"comparator_frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}"; out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i in range(environments):
        env=generate_environment(config['environment']['grid_size'],config['environment']['difficulty'],config['environment']['moving_obstacles'],seed+i)
        _,opt,_=astar(env); opt=max(1,opt)
        result=_rollout(q_agent,env,config['training']['max_steps'])
        vns=compute_vns(len(result['path']),opt,result['path'],env.grid,config['vns'])['vns']
        fig,ax=plt.subplots(1,2,figsize=(10,4))
        for j in range(2):
            ax[j].imshow(env.grid,cmap='gray_r'); ax[j].plot([p[1] for p in result['path']],[p[0] for p in result['path']],c='b' if j==0 else 'purple'); ax[j].set_title(f'Agent {j+1}')
        fig.suptitle(f'Episode {i+1} Reward {result["reward"]:.1f} Steps {len(result["path"])} Collisions {result["collisions"]} VNS {vns:.1f}')
        plt.tight_layout(); plt.savefig(out/f'frame_{i:03d}.png',dpi=140); plt.close()
        rows.append({'reward':result['reward'],'success':1 if result['success'] else 0,'vns':vns,'steps':len(result['path'])})
    if rows:
        vals=[sum(r[k] for r in rows)/len(rows) for k in ['reward','success','vns','steps']]
        plt.figure(figsize=(8,4)); plt.bar(['Avg Reward','Success Rate','Avg VNS','Avg Steps'],[vals[0],vals[1]*100,vals[2],vals[3]]); plt.title('Comparator Summary'); plt.tight_layout(); plt.savefig(out/'summary.png',dpi=140); plt.close()
