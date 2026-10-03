import {describe, it, expect, vi} from 'vitest';
const {owner, ground} = vi.hoisted(() => ({owner: {current: null as any}, ground: vi.fn()}));
vi.mock('react', () => ({useRef: (x: any) => owner.current.ref(x), useState: (x: any) => owner.current.state(x), useEffect: (f: any, d: any[]) => owner.current.effect(f, d)}));
vi.mock('./api', () => ({api: {ground}}));
import {GroundPreparation, groundBinding, groundMatches} from './GroundPreparation';
import type {Candidate, WeatherSource} from './domain';

function harness(render: () => any) {
  let cursor = 0; const slots: any[] = [], effects: any[] = [], cleanups: any[] = [];
  const hooks = {
    ref: (x: any) => { const i = cursor++; return slots[i] ?? (slots[i] = {current: x}); },
    state: (x: any) => { const i = cursor++; if (!(i in slots)) slots[i] = x; return [slots[i], (v: any) => { slots[i] = v; }]; },
    effect: (f: any, deps: any[]) => { const i = cursor++; if (!slots[i] || deps.some((d, j) => !Object.is(d, slots[i][j]))) { slots[i] = deps; effects.push(() => { cleanups[i]?.(); cleanups[i] = f(); }); } },
  };
  return {render() { cursor = 0; owner.current = hooks; const tree = render(); effects.splice(0).forEach(f => f()); return tree; }, close() { cleanups.forEach(f => f?.()); }};
}
function nodes(tree: any): any[] { return !tree || typeof tree !== 'object' ? [] : Array.isArray(tree) ? tree.flatMap(nodes) : [tree, ...nodes(tree.props?.children)]; }
const nextTurn = () => new Promise(resolve => setImmediate(resolve));
const source = {id: 'gfs', sha256: 'a'.repeat(64), default_config: null} as WeatherSource;
const candidate = {id: 'A', weather_source_id: 'gfs', config: {launch: {time_utc: '2026-09-30T03:17:13Z', latitude_deg: 43.5, longitude_deg: 143, altitude_m: 70}}} as Candidate;
const query = {time_utc: candidate.config.launch.time_utc, latitude_deg: 43.5, longitude_deg: 143, launch_altitude_m: 70};
const observation = {schema: 'balloon.weather-ground/1', weather_source_id: 'gfs', weather_sha256: source.sha256!, query: {...query, time_utc: '2026-09-30T03:17:13+00:00'}, ground_altitude_m: 1109.2, clearance_m: -1039.2, below_model_ground: true, ground_model: 'coarse_gfs_orography', height_reference: 'geometric_asl_m', is_fine_dem: false, scope: 'point_ground_only_not_full_flight_validation'} as const;

describe('model-ground observation belongs to the selected field and position', () => {
  it('accepts equivalent UTC formatting and rejects field replacement or another query', () => {
    expect(groundMatches(observation, source, query)).toBe(true);
    expect(groundMatches({...observation, weather_sha256: 'b'.repeat(64)}, source, query)).toBe(false);
    expect(groundMatches({...observation, query: {...query, longitude_deg: 144}}, source, query)).toBe(false);
    expect(groundBinding(candidate, source)).not.toBe(groundBinding({...candidate, config: {...candidate.config, launch: {...candidate.config.launch, time_utc: '2026-09-30T03:17:14Z'}}}, source));
    expect(groundBinding(candidate, {...source, sha256: undefined})).toBeNull();
  });
  it('does not apply a late observation after a location edit, and needs explicit altitude application', async () => {
    let complete!: (value: typeof observation) => void;
    ground.mockImplementationOnce(() => new Promise(resolve => { complete = resolve; }));
    const apply = vi.fn(); let current = candidate;
    const h = harness(() => GroundPreparation({candidate: current, source, onApply: apply}));
    nodes(h.render()).find(n => n.type === 'button').props.onClick();
    current = {...candidate, config: {...candidate.config, launch: {...candidate.config.launch, longitude_deg: 144}}};
    h.render(); complete(observation); await nextTurn();
    expect(nodes(h.render()).some(n => n.props?.role === 'status')).toBe(false);
    expect(apply).not.toHaveBeenCalled();
    current = candidate; ground.mockResolvedValueOnce(observation);
    nodes(h.render()).find(n => n.type === 'button').props.onClick(); await nextTurn();
    const buttons = nodes(h.render()).filter(n => n.type === 'button');
    expect(apply).not.toHaveBeenCalled(); buttons[1].props.onClick();
    expect(apply).toHaveBeenCalledExactlyOnceWith(1114.2); h.close();
  });
});
