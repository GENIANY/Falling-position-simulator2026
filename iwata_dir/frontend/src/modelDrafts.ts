import {candidateFamily} from './domain';
import type { Config, Project } from './domain';

type Values = Record<string, string | number>;
export type ModelDrafts = Partial<Record<'ascent' | 'burst' | 'descent' | 'density', Record<string, Values>>>;
const defaults: Record<string, Record<string, Values>> = {
  ascent: { constant_speed: {mode:'constant_speed',speed_m_s:5}, isothermal_buoyancy: {mode:'isothermal_buoyancy',gas_mass_kg:.5,envelope_mass_kg:1,payload_mass_kg:1,drag_coefficient:.47} },
  burst: { altitude:{mode:'altitude',altitude_m:30000}, diameter:{mode:'diameter',diameter_m:8} },
  descent: { rated_speed:{mode:'rated_speed',reference_speed_m_s:5,density_model:'weather',reference_density_kg_m3:1.225}, constant_cda:{mode:'constant_cda',mass_kg:2,drag_area_m2:.5} },
  density: { weather:{reference_density_kg_m3:1.225}, exponential:{scale_height_m:8400} },
};

/** Active scientific input stays in config; inactive editor choices never enter a run. */
export function switchModel(config:Config, previous:ModelDrafts = {}, section:keyof ModelDrafts, mode:string) {
  if(!defaults[section]?.[mode]) throw Error('未対応のモデル選択です。');
  const c=structuredClone(config), cache=structuredClone(previous);
  if(section==='density') {
    const old=String(c.descent.density_model??'weather');
    cache.density={...cache.density,[old]: old==='weather'?{reference_density_kg_m3:c.descent.reference_density_kg_m3??1.225}:{scale_height_m:c.descent.scale_height_m??8400}};
    const value=cache.density[mode]??defaults.density[mode];
    c.descent={mode:'rated_speed',reference_speed_m_s:c.descent.reference_speed_m_s,density_model:mode,...structuredClone(value)};
  } else {
    cache[section]={...cache[section],[String(c[section].mode)]:structuredClone(c[section])};
    c[section]=structuredClone(cache[section]![mode]??defaults[section][mode]);
  }
  return {config:c,cache};
}

export function applyCandidateWeather(project:Project, ids:string[], sourceId:string):Project {
  const selected=new Set(candidateFamily(project.candidates,ids).map(c=>c.id));
  return {...project,candidates:project.candidates.map(c=>selected.has(c.id)&&c.weather_source_id!==sourceId?{...c,weather_source_id:sourceId,revision:c.revision+1}:c)};
}
