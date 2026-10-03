// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
/* The annual direction map and its saved SVG share one FROM-direction key.
   Radius/area carry no frequency or speed. No wind or calendar calculation here. */
(function(root){
 'use strict';
 const color=degrees=>`hsl(${((degrees%360)+360)%360},65%,45%)`;
 const definition={version:'from-direction-key-v1',convention:'北0°、東90°、南180°、西270°。吹いてくる方位（FROM）',undefined:'全無風または平均u=v=0はdir=null。新しい静穏の風速閾値は設けない',lowConstancy:'R<0.3は平均来向の代表性が弱いため灰。時刻間と地点間の相殺を含む。静穏や欠測ではない'};
 function appearance(summary){
  if(!summary)return {kind:'missing',fill:'#ffffff',label:'標本なし'};
  if(!Number.isFinite(summary.dir))return {kind:'undefined',fill:'#e9eeee',label:summary.s===0?'平均来向なし（全標本が無風）':'平均来向なし（平均ベクトルが0）'};
  const low=Number.isFinite(summary.R)&&summary.R<.3;
  return {kind:low?'low':'direction',fill:low?'#aeb9ba':color(summary.dir),label:`${summary.dir.toFixed(1)}°（来向${low?'・代表性が弱い':''}）`};
 }
 function legend(){
  const cx=108,cy=276,outer=32,inner=22,point=(r,d)=>[cx+r*Math.sin(d*Math.PI/180),cy-r*Math.cos(d*Math.PI/180)].map(v=>v.toFixed(3)).join(','),txt=(x,y,value,size=11,anchor='start')=>`<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${value}</text>`;
  let body='<g data-direction-key="from-circular" role="img" aria-label="平均来向の円環凡例。北0度が上、東90度が右、時計回り。色は風の強さではありません。">';
  for(let d=0;d<360;d+=3)body+=`<path data-from-degrees="${d}" d="M${point(outer,d)} A${outer},${outer} 0 0 1 ${point(outer,d+3.05)} L${point(inner,d+3.05)} A${inner},${inner} 0 0 0 ${point(inner,d)} Z" fill="${color(d)}"/>`;
  body+=txt(cx,238,'北 0°',11,'middle')+txt(149,280,'東 90°')+txt(cx,324,'南 180°',11,'middle')+txt(66,280,'西 270°',11,'end')+txt(cx,280,'来向',10,'middle');
  body+='<rect x="210" y="247" width="11" height="11" fill="#aeb9ba"/>'+txt(229,257,'灰：平均の向きが代表しにくい（R &lt; 0.3）');
  body+='<rect x="210" y="269" width="11" height="11" fill="#e9eeee"/><path d="M212 274.5h7" stroke="#61777c"/>'+txt(229,279,'—：平均来向なし（無風・平均ベクトル0）');
  body+='<rect x="210" y="291" width="11" height="11" fill="white" stroke="#c5d5d9"/>'+txt(229,301,'白：標本なし')+txt(385,301,'色は風の強さを表しません。');
  return body+'</g>';
 }
 root.WindDirection={color,appearance,legend,definition};
 
})(typeof window==='undefined'?globalThis:window);

}
