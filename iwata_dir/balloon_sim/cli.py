"""User operations: assemble acquisition, offline flight and artifact export.

Existing rendering/export names remain imported for compatibility. Their actual
implementations live in results; internal dependencies do not route through CLI.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .environment.storage import read_json
from .results.export import export_result, make_geojson, sha256
from .results.report import render_report


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main(argv=None):
    parser=argparse.ArgumentParser(description="Balloon-JP 気象取得と軌道計算")
    sub=parser.add_subparsers(dest="command",required=True)
    fetch=sub.add_parser("fetch",help="明示run・領域・期間でGFSを取得する")
    fetch.add_argument("request",type=Path);fetch.add_argument("--output",required=True,type=Path)
    simulate=sub.add_parser("simulate",help="保存された気象場から軌道を計算する")
    simulate.add_argument("config",type=Path);simulate.add_argument("--weather",required=True,type=Path)
    simulate.add_argument("--output",required=True,type=Path)
    inspect=sub.add_parser("inspect",help="保存気象場の来歴を確認する")
    inspect.add_argument("weather",type=Path)
    replay=sub.add_parser("replay",help="保存GRIBの指紋を確認し気象場を通信なしで再生成する")
    replay.add_argument("acquisition",type=Path);replay.add_argument("--output",required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        if hasattr(args,"output") and args.output.exists():
            raise FileExistsError("既存出力は上書きしません: "+str(args.output))
        from .environment.storage import load_weather
        if args.command=="replay":
            from .environment.gfs import replay_gfs
            path=replay_gfs(args.acquisition,args.output)
            print(_json({"status":"weather_replayed","bundle":str(path)}),end="")
            return 0
        if args.command=="fetch":
            from .environment.gfs import acquire_gfs
            path=acquire_gfs(read_json(args.request),args.output)
            print(_json({"status":"weather_saved","bundle":str(path)}),end="")
            return 0
        weather=load_weather(args.weather)
        if args.command=="inspect":
            print(_json(weather.metadata),end="")
            return 0
        from .flight.trajectory import simulate as run_simulation
        result=run_simulation(read_json(args.config),weather)
        out=export_result(result,args.config,args.weather,args.output,weather.metadata)
        print(_json({"status":result["status"],"complete":result["complete"],
                     "stop_reason":result.get("stop_reason"),"output":str(out),
                     "summary":result.get("summary",{})}),end="")
        return 0 if result["complete"] else 2
    except (ValueError,OSError,ImportError,RuntimeError) as exc:
        print(_json({"status":"error","code":getattr(exc,"code",type(exc).__name__),
                     "message":str(exc)}),end="",file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
