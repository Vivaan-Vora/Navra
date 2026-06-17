"""Benchmark runner."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from environment import generate_environment
from pathfinder import astar, bfs, dijkstra
from analyzer import compute_edi
from scorer import compute_vns, print_vns_leaderboard

def run_benchmark(config: dict, runs: int = 20, seed: int = 42) -> dict:
    """Run benchmark across pathfinding methods."""
    methods={'A*':astar,'BFS':bfs,'Dijkstra':dijkstra}
    stats={m:{'success':0,'steps':0.0,'reward':0.0} for m in methods}
    vns_by_method=defaultdict(list)
    vns_vs_edi=defaultdict(list)
    for i in range(runs):
        env=generate_environment(config['environment']['grid_size'],config['environment']['difficulty'],config['environment']['moving_obstacles'],seed+i)
        edi=compute_edi(env)['edi']
        for name,fn in methods.items():
            path,length,_=fn(env)
            ok=1 if path else 0
            reward=100-max(0,length-1) if ok else -100
            stats[name]['success']+=ok
            stats[name]['steps']+=length if ok else config['training']['max_steps']
            stats[name]['reward']+=reward
            if path:
                v=compute_vns(length,max(1,length),path,env.grid,config['vns'])['vns']
                vns_by_method[name].append(v)
                vns_vs_edi[name].append((edi,v))
    print('Method     | Success Rate | Avg Steps | Avg Reward')
    print('-----------+--------------+-----------+-----------')
    for name in methods:
        print(f"{name:<10} | {stats[name]['success']/runs:<12.2%} | {stats[name]['steps']/runs:<9.2f} | {stats[name]['reward']/runs:<9.2f}")
    print_vns_leaderboard(vns_by_method)
    _plot_bar(stats,runs,Path(config['paths']['plot_dir']))
    _plot_scatter(vns_vs_edi,Path(config['paths']['plot_dir']))
    return stats

def _plot_bar(stats: dict, runs: int, plot_dir: Path) -> None:
    """Plot benchmark reward bar chart."""
    plot_dir.mkdir(parents=True, exist_ok=True)
    labels=list(stats.keys()); vals=[stats[x]['reward']/runs for x in labels]
    plt.figure(figsize=(7,4)); plt.bar(labels, vals); plt.title('Benchmark Average Reward'); plt.tight_layout(); plt.savefig(plot_dir/f"benchmark_bar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",dpi=140); plt.close()

def _plot_scatter(points: dict, plot_dir: Path) -> None:
    """Plot VNS vs EDI scatter."""
    plt.figure(figsize=(7,5))
    for name, arr in points.items():
        if arr:
            plt.scatter([x for x,_ in arr],[y for _,y in arr],label=name,alpha=0.7)
    plt.xlabel('EDI'); plt.ylabel('VNS'); plt.title('VNS vs EDI'); plt.legend(); plt.tight_layout(); plt.savefig(plot_dir/f"vns_vs_edi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",dpi=140); plt.close()
