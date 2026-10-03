import {climateHoursLabel,selectedClimateHours,type ClimateQuery,type ClimateWindRose,type ClimateDescriptor} from '../../climateDomain';
import type {WindViewModel} from './viewModel';
import {esc,fmt,text,line,svg,geographyFrame,boundaryMarkup} from './plots';

export const roseColors=['#b8dedc','#69bfc2','#3195b1','#366caa','#6b4c96','#ac4266'];
type AvailableRose=Extract<ClimateWindRose,{available:true}>;

export function checkedRose(vm:WindViewModel):AvailableRose|null {
 const r=vm.windRose;if(!r?.available)return null;
 const periods=new Map(vm.annualPeriods.map(p=>[p.id,p]));
 const hours=selectedClimateHours(vm.metadata.query as ClimateQuery);
 if(!Array.isArray(r.native_hours_utc)||r.native_hours_utc.length!==hours.length||new Set(r.native_hours_utc).size!==hours.length||r.native_hours_utc.some(h=>!hours.includes(h)))throw Error('風配のUTC時刻と固定集計条件が一致しません。');
 if(r.level_id!==vm.levels[vm.levelIndex].id||r.sectors.length!==16||r.speed_classes.length!==6||
   ![r.point.lat,r.point.lon].every(Number.isFinite)||r.rows.length!==periods.size*96)throw Error('風配の地点・面・区間の対応を読めません。');
 const requested=(vm.metadata.query as ClimateQuery).rose_cell_id,source=vm.metadata.source as ClimateDescriptor;
 if(requested!==undefined&&requested!==r.point.cell_id)throw Error('要求した風配の元格子点と結果が一致しません。');
 const native=source.native_grid.find(c=>c.cell_id===r.point.cell_id);
 if(!native||native.lat!==r.point.lat||native.lon!==r.point.lon)throw Error('風配の地点が資料の元格子と一致しません。');
 const sectors=new Set(r.sectors.map(s=>s.sector)),speeds=new Set(r.speed_classes.map(s=>s.speed_class)),keys=new Set<string>(),totals=new Map<number,number>(),calm=new Map<number,number>();
 if(r.calm_counts!==undefined){if(!Array.isArray(r.calm_counts)||r.calm_counts.length!==periods.size)throw Error('静穏件数の区間が一致しません。');for(const row of r.calm_counts){const p=periods.get(row.timebin_id);if(!p||calm.has(p.id)||!Number.isInteger(row.count)||row.count<0||row.count>p.timeCount||row.time_count!==p.timeCount||row.time_count<=0||!Number.isFinite(row.frequency)||Math.abs(row.frequency-row.count/row.time_count)>1e-10)throw Error('静穏件数・分母・区間に不整合があります。');calm.set(p.id,row.count);}}
 for(const row of r.rows){const p=periods.get(row.timebin_id),key=[row.timebin_id,row.sector,row.speed_class].join(':');
  if(!p||keys.has(key)||!sectors.has(row.sector)||!speeds.has(row.speed_class)||!Number.isInteger(row.count)||row.count<0||row.time_count!==p.timeCount||row.time_count<=0||!Number.isFinite(row.frequency)||Math.abs(row.frequency-row.count/row.time_count)>1e-10)throw Error('風配の件数・分母・区間に欠落または不整合があります。');
  keys.add(key);totals.set(p.id,(totals.get(p.id)??0)+row.count);
 }
 for(const p of periods.values())if((totals.get(p.id)??0)+(calm.get(p.id)??0)!==p.timeCount)throw Error('風配の頻度合計が対象時刻数と一致しません。');
 return r;
}

export function roseUnavailable(vm:WindViewModel):string {
 if(vm.windRose?.available)return '';
 return vm.windRose?.reason==='hour_subset_not_available'?'時刻を絞った風配は元資料にありません。平均プロファイルは選択時刻で表示できます。':!vm.windRose?'この保存結果には風配がありません。新しい集計で対応する図を追加できます。':'この資料には代表地点の風配がありません。';
}

export function rosePopulationLabel(r:AvailableRose):string {return climateHoursLabel({source_id:'',level_id:r.level_id,bounds:null,grain:'half',hours_utc:r.native_hours_utc})+'・代表地点の経験頻度';}
export function roseMethod(r:ClimateWindRose|undefined):string {return r?.available?rosePopulationLabel(r)+'。'+(r.calm_counts?'静穏（風速0）は方向を持たず、方向別頻度の分母には含めます。':'0–5 m/sは通常の速度階級で、静穏の独立区分ではありません。'): '風配は資料が持つ固定代表元格子の経験頻度です。';}
export function rosePointLabel(r:AvailableRose):string {return `代表元格子 ${r.point.cell_id}：${r.point.lat.toFixed(4)}°N / ${r.point.lon.toFixed(4)}°E · ${r.point_in_selected_region?'選択地域内':'選択地域外'}（地域全体の分布ではありません）`;}
export function roseScale(vm:WindViewModel):number {
 const r=checkedRose(vm);if(!r)return 10;
 const sums=new Map<string,number>();for(const row of r.rows){const key=row.timebin_id+':'+row.sector;sums.set(key,(sums.get(key)??0)+row.frequency);}
 return Math.max(10,Math.ceil(Math.max(...sums.values())*100/10)*10);
}
export function roseLegend(r:AvailableRose):string {return svg(740,32,r.speed_classes.map((c,i)=>`<rect x="${i*120}" y="3" width="14" height="10" fill="${roseColors[i]}"/>`+text(i*120+19,13,`${c.label} m/s`,11)).join('')+text(0,30,r.calm_counts?'来向16方位 · 静穏（0 m/s）は方向なし・分母には含む':'来向16方位 · 0–5 m/sも通常階級に含む（静穏の独立区分なし）',10),'実資料の風速階級');}

export function climateRosePlot(vm:WindViewModel,index:number,upper=roseScale(vm)):string {
 const r=checkedRose(vm);if(!r)throw Error(roseUnavailable(vm));const p=vm.annualPeriods[index],cx=95,cy=94,radius=56;
 let b=text(cx,12,p.label,12,'text-anchor="middle" font-weight="650" data-period-label="true"');for(const step of [.25,.5,.75,1])b+=`<circle cx="${cx}" cy="${cy}" r="${radius*step}" fill="none" stroke="#b6cacc" stroke-width=".7"/>`+text(cx+2,cy-radius*step+10,`${fmt(upper*step,(upper*step)%1?1:0)}%`,10);
 b+=line(cx-radius,cy,cx+radius,cy)+line(cx,cy-radius,cx,cy+radius);
 const byKey=new Map(r.rows.filter(row=>row.timebin_id===p.id).map(row=>[row.sector+':'+row.speed_class,row]));
 for(const sector of r.sectors){let total=0;for(let j=0;j<r.speed_classes.length;j++){const c=r.speed_classes[j],row=byKey.get(sector.sector+':'+c.speed_class)!;if(!row.count)continue;const ri=radius*total*100/upper,ro=radius*(total+row.frequency)*100/upper,a=(sector.centre_deg-10)*Math.PI/180,z=(sector.centre_deg+10)*Math.PI/180,P=(rad:number,angle:number)=>`${cx+Math.sin(angle)*rad},${cy-Math.cos(angle)*rad}`,path=ri?`M${P(ri,a)} L${P(ro,a)} A${ro},${ro} 0 0 1 ${P(ro,z)} L${P(ri,z)} A${ri},${ri} 0 0 0 ${P(ri,a)} Z`:`M${cx},${cy} L${P(ro,a)} A${ro},${ro} 0 0 1 ${P(ro,z)} Z`;
   b+=`<path data-rose-bin="${sector.sector}" data-speed-class="${c.speed_class}" data-count="${row.count}" d="${path}" fill="${roseColors[j]}" stroke="white" stroke-width=".4"><title>${esc(`${p.label} / 来向 ${sector.compass_16} (${sector.centre_deg}°) / ${c.label} m/s：${row.count}/${row.time_count}時刻 (${fmt(row.frequency*100)}%)`)}</title></path>`;total+=row.frequency;
  }}
 const calm=r.calm_counts?.find(row=>row.timebin_id===p.id);
 b+=text(cx,27,'北 0°',11,'text-anchor="middle"')+text(162,97,'東',11)+text(cx,166,'南',11,'text-anchor="middle"')+text(16,97,'西',11)+text(cx,calm?.count?181:190,`N=${p.timeCount}気象時刻`,11,'text-anchor="middle"')+(calm?.count?text(cx,194,`静穏${calm.count}/${p.timeCount}（方向なし）`,10,'text-anchor="middle"'):'');
 return svg(190,196,b,`${p.label}の実風配`,`data-rose="true" data-period="${p.id}" data-radius-max="${upper}" data-sample-count="${p.timeCount}"`);
}

export function meanProfilePlot(vm:WindViewModel,index:number):string {
 const p=vm.annualPeriods[index],W=190,H=196,x0=32,y0=32,pw=146,ph=128,max=vm.annualSpeedMax,zMax=Math.max(...vm.levels.map(l=>l.height)),X=(s:number)=>x0+s/max*pw,Y=(h:number)=>y0+ph*(1-h/zMax);let b=text(W/2,12,p.label,12,'text-anchor="middle" font-weight="650" data-period-label="true"');
 for(let k=0;k<=3;k++){const x=max*k/3;b+=line(X(x),y0,X(x),y0+ph)+text(X(x),y0+ph+14,fmt(x,0),10,'text-anchor="middle"');}
 for(let z=0;z<=zMax;z+=5)b+=line(x0,Y(z),x0+pw,Y(z))+text(x0-5,Y(z)+3,z,10,'text-anchor="end"');
 b+=`<polyline data-mean-profile="true" points="${vm.annual[index].map((q,j)=>`${X(q!.s)},${Y(vm.levels[j].height)}`).join(' ')}" fill="none" stroke="#087f83" stroke-width="2"/>`;
 vm.annual[index].forEach((q,j)=>{const l=vm.levels[j];b+=`<circle cx="${X(q!.s)}" cy="${Y(l.height)}" r="2" fill="#087f83"><title>${esc(`${p.label} / ${l.pressure} hPa / 平均風速 ${fmt(q!.s)} m/s / 各格子${q!.timeCount}気象時刻`)}</title></circle>`;});
 b+=text(1,27,'ISA km',10)+text(110,192,'平均風速 [m/s]',11,'text-anchor="middle"');return svg(W,H,b,p.label+'の平均風速プロファイル',`data-profile="mean" data-period="${p.id}" data-axis-max="${max}"`);
}

export function roseLocationMap(vm:WindViewModel):string {
 const r=checkedRose(vm);if(!r)return '';const bounds={west:Math.min(vm.nativeBounds.west,r.point.lon),east:Math.max(vm.nativeBounds.east,r.point.lon),south:Math.min(vm.nativeBounds.south,r.point.lat),north:Math.max(vm.nativeBounds.north,r.point.lat)},g=geographyFrame(200,100,bounds,false),[x,y]=g.project(r.point.lat,r.point.lon);
 return svg(200,100,g.b+boundaryMarkup(g.project,vm.selectionBounds)+`<circle cx="${x}" cy="${y}" r="5" fill="#c86b32" stroke="white" stroke-width="2"/>`+text(4,96,'破線：選択地域 / 点：表示中の風配地点',9),'元格子範囲と実風配の代表地点');
}

/** Selection uses the displayed native grid, never an interpolated arbitrary location. */
export function nativeRosePointMap(vm:WindViewModel,selected:number,background:boolean):string {
 const source=vm.metadata.source as ClimateDescriptor,g=geographyFrame(440,300,vm.nativeBounds,background),applied=checkedRose(vm)?.point.cell_id;
 let b=g.b+boundaryMarkup(g.project,vm.selectionBounds);
 for(const c of source.native_grid){const [x,y]=g.project(c.lat,c.lon);b+=`<circle data-native-rose-cell="${c.cell_id}" cx="${x}" cy="${y}" r="${c.cell_id===applied?4:1.6}" fill="${c.cell_id===applied?'#c86b32':'#3c7081'}"><title>${esc(`元格子 ${c.cell_id}：${c.lat.toFixed(4)}°N / ${c.lon.toFixed(4)}°E`)}</title></circle>`;if(c.cell_id===selected)b+=`<circle cx="${x}" cy="${y}" r="7" fill="none" stroke="#b23c39" stroke-width="2" data-selected-native-cell="${c.cell_id}"/>`;}
 return svg(440,300,b,'風配の元格子点選択。クリックに最も近い元格子を選択します。');
}
export function nearestRosePoint(vm:WindViewModel,x:number,y:number):number|null {
 if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>440||y<0||y>300)return null;
 const source=vm.metadata.source as ClimateDescriptor,g=geographyFrame(440,300,vm.nativeBounds,false);
 let best:number|null=null,distance=Infinity;for(const c of source.native_grid){const [cx,cy]=g.project(c.lat,c.lon),d=(cx-x)**2+(cy-y)**2;if(d<distance){best=c.cell_id;distance=d;}}return best;
}
