// Screen-space line proximity: filled interiors are resolved in shared geometry.
export function nearSegment(p,a,b,radius=5){
 const dx=b.x-a.x,dy=b.y-a.y,length=dx*dx+dy*dy;
 const t=length?Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/length)):0;
 return Math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy)<=radius;
}
export function contourIndices(features,point,project){
 return features.flatMap((feature,index)=>{
  if(!['contour','region'].includes(feature.properties.kind)||feature.properties.visible===false)return [];
  if(feature.geometry.type==='Point')return nearSegment(point,project(feature.geometry.coordinates),project(feature.geometry.coordinates))?[index]:[];
  if(feature.geometry.type==='LineString'){const line=feature.geometry.coordinates;return line.some((p,i)=>i>0&&nearSegment(point,project(line[i-1]),project(p)))?[index]:[];}
  const rings=feature.geometry.type==='MultiPolygon'?feature.geometry.coordinates.flat():feature.geometry.coordinates;
  return rings.some(ring=>ring.some((v,i)=>i>0&&nearSegment(point,project(ring[i-1]),project(v))))?[index]:[];
 });
}
