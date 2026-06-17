"""Tabular Q-learning agent."""
from __future__ import annotations
import json, random
from pathlib import Path
import numpy as np
from environment import generate_environment
from sensors import get_sensor_vector
from logger import append_episode_log
from diagnostics import HealthState, update_health
from scorer import compute_vns
from pathfinder import astar, manhattan
from failure_logger import classify_failure
ACTIONS=[(-1,0),(1,0),(0,-1),(0,1)]

class QLearningAgent:
    """Q-table agent keyed by rounded sensor vectors."""
    def __init__(self, action_count:int, alpha:float, gamma:float, epsilon:float) -> None:
        """Initialize agent."""
        self.action_count=action_count; self.alpha=alpha; self.gamma=gamma; self.epsilon=epsilon; self.q_table={}
    def _state_key(self, obs: np.ndarray) -> str:
        """Build rounded state key."""
        return str(tuple(np.round(obs,1).tolist()))
    def _get_q(self, key: str) -> list[float]:
        """Get Q row."""
        if key not in self.q_table: self.q_table[key]=[0.0]*self.action_count
        return self.q_table[key]
    def choose_action(self, obs: np.ndarray, rng: random.Random) -> int:
        """Epsilon-greedy action."""
        if rng.random() < self.epsilon: return rng.randrange(self.action_count)
        return int(np.argmax(self._get_q(self._state_key(obs))))
    def update(self, s: np.ndarray, a:int, r:float, sn: np.ndarray, done: bool) -> None:
        """Bellman update."""
        q=self._get_q(self._state_key(s)); nq=self._get_q(self._state_key(sn)); target=r if done else r+self.gamma*max(nq); q[a]+=self.alpha*(target-q[a])
    def save(self, path: Path) -> None:
        """Save Q table JSON."""
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(self.q_table),encoding='utf-8')
    def load(self, path: Path) -> None:
        """Load Q table JSON."""
        if path.exists(): self.q_table=json.loads(path.read_text(encoding='utf-8'))

def _step(env,pos,a):
    """Take one environment step."""
    dr,dc=ACTIONS[a]; n=(pos[0]+dr,pos[1]+dc)
    if not env.in_bounds(n) or env.is_obstacle(n): return pos,-10.0,False,True
    if n==env.goal: return n,100.0,True,False
    return n,-1.0,False,False

def train_q_agent(config: dict, seed:int=42, episodes_override:int|None=None) -> QLearningAgent:
    """Train Q-learning and append logs per episode."""
    rng=random.Random(seed); np_rng=np.random.default_rng(seed)
    ep=episodes_override or int(config['training']['episodes']); ms=int(config['training']['max_steps'])
    q=config['q_learning']; d=config['diagnostics']; f=config['failure_logger']; w=config['vns']
    agent=QLearningAgent(4,q['learning_rate'],q['discount_factor'],q['epsilon_start'])
    log=Path(config['paths']['log_csv'])
    for e in range(1,ep+1):
        env=generate_environment(config['environment']['grid_size'],config['environment']['difficulty'],config['environment']['moving_obstacles'],seed+e)
        _,opt,_=astar(env); opt=max(1,opt)
        health=HealthState(); pos=env.start; path=[pos]; reward=0.0; done=False
        revisits={}; max_rev=0; same=0; max_same=0; cwin=[]; cburst=0
        for _ in range(ms):
            env.update_moving_obstacles(rng)
            s=get_sensor_vector(env,pos,rng=np_rng); a=agent.choose_action(s,rng)
            n,r,done,col=_step(env,pos,a)
            sn=get_sensor_vector(env,n,rng=np_rng); agent.update(s,a,r,sn,done)
            same = same+1 if n==pos else 0; max_same=max(max_same,same)
            revisits[n]=revisits.get(n,0)+1; max_rev=max(max_rev,revisits[n])
            cwin.append(1 if col else 0); cwin=cwin[-f['collision_storm_window']:]
            if sum(cwin)>f['collision_storm_hits']: cburst+=1
            health=update_health(health,1 if col else 0,1 if same>5 else 0,1 if len(path)>3*opt else 0,d['degradation_per_collision'],d['degradation_per_stuck_event'],d['degraded_threshold'],d['critical_threshold'],d['maintenance_cycle_steps'])
            pos=n; path.append(pos); reward+=r
            if done: break
        v=compute_vns(len(path),opt,path,env.grid,w)
        far=manhattan(pos,env.goal)>config['environment']['grid_size']//2
        ft=classify_failure(done,len(path),ms,max_rev,max_same,cburst,far,f['timeout_threshold_steps'],f['loop_threshold_revisits'])
        append_episode_log(log,{'episode':e,'reward':reward,'steps':len(path),'success':bool(done),'epsilon':agent.epsilon,'final_health':health.health,'degraded_events':health.degraded_events,'critical_events':health.critical_events,'vns':v['vns'],'path_efficiency_ratio':v['path_efficiency_ratio'],'smoothness_ratio':v['smoothness_ratio'],'obstacle_avoidance_ratio':v['obstacle_avoidance_ratio'],'failure_type':ft,'final_row':pos[0],'final_col':pos[1]})
        agent.epsilon=max(q['epsilon_end'],agent.epsilon*q['epsilon_decay'])
        if e%int(config['training']['progress_interval'])==0: print(f"[Q] Episode {e}/{ep} reward={reward:.2f} success={done} epsilon={agent.epsilon:.3f}")
    agent.save(Path(config['paths']['q_table']))
    return agent
