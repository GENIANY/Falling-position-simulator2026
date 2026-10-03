import type {ClimateWindRose,ClimateMonthlyProfiles} from '../../climateDomain';
export type WindValue={u:number;v:number;s:number;R:number|null;dir:number|null;timeCount:number;spatialRange?:number};
export type PeriodView={id:number;month:number;label:string;description:string;timeCount:number};
export type LevelView={id:number;pressure:number;height:number;heightDescription:string};
export type DisplayCell={id:number;lat:number;lon:number;label:string;west:number;east:number;south:number;north:number};
export type GeoBounds={west:number;east:number;south:number;north:number};
export type WindViewModel={kind:'fixture'|'climate';identity:Record<string,unknown>;populationLabel:string;countDefinition:string;heightDefinition:string;annualDefinition:string;spatialDefinition:string;levels:LevelView[];levelIndex:number;annualPeriods:PeriodView[];spatialPeriods:PeriodView[];annual:(WindValue|null)[][];spatial:(WindValue|null)[][];cells:DisplayCell[];mapBounds:GeoBounds;selectionBounds:GeoBounds;nativeBounds:GeoBounds;annualSpeedMax:number;annualRangeMax:number;spatialAllMax:number;spatialLevelMax:number;metadata:Record<string,unknown>;windRose?:ClimateWindRose;monthlyProfiles?:ClimateMonthlyProfiles};
export const niceSpeedMax=(n:number)=>Math.max(5,Math.ceil(Math.max(0,n)/5)*5);
export function levelEdges(levels:LevelView[]){return levels.map((l,i)=>({lo:i?(levels[i-1].height+l.height)/2:l.height,hi:i<levels.length-1?(l.height+levels[i+1].height)/2:l.height}));}
