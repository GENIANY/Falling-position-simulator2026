// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
(function(root){
'use strict';
const S=root.BJP_STYLE,esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function modal(title){let d=document.getElementById('appearanceDialog');if(!d){d=document.createElement('dialog');d.id='appearanceDialog';document.body.append(d);}d.innerHTML=`<h2>${esc(title)}</h2><div class="appearance-body"></div><div class="row"><button data-close>閉じる</button></div>`;d.querySelector('[data-close]').onclick=()=>d.close();d.showModal();return d;}
function swatches(current,attribute='data-color'){return S.palette.map(p=>`<button type="button" class="color-swatch" ${attribute}="${p.color}" style="--swatch:${p.color}" aria-label="${p.label}" title="${p.label} ${p.color}" aria-pressed="${p.color===current}"><span>${p.color===current?'✓':''}</span></button>`).join('');}
function family(parent,onChange){const d=modal(parent.id+' 系列のテーマ色'),body=d.querySelector('.appearance-body');body.innerHTML=`<p>親と遅延子に同じ基調色を使います。</p><div class="color-palette">${swatches(parent.color)}</div>`;body.onclick=e=>{const color=e.target.closest('[data-color]')?.dataset.color;if(!color)return;onChange(color);d.close();};}
function levels(current,onApply){const d=modal('領域レベルと色'),body=d.querySelector('.appearance-body');let rows=structuredClone(current).sort((a,b)=>b.priority-a.priority);const save=()=>{body.querySelectorAll('[data-level-name]').forEach(x=>{const r=rows.find(r=>r.id===x.dataset.levelName);r.name=x.value.trim().slice(0,40)||r.name;});};
 const draw=()=>{body.innerHTML='<p class="muted">上ほど優先。重複した着地点は最上位の色を使い、全ての該当領域は保持します。</p>'+rows.map((r,i)=>`<div class="level-editor-row"><label>名称<input data-level-name="${r.id}" value="${esc(r.name)}" maxlength="40"></label><button data-up="${r.id}" ${i===0?'disabled':''} aria-label="${esc(r.name)} を上位へ">↑</button><button data-down="${r.id}" ${i===rows.length-1?'disabled':''} aria-label="${esc(r.name)} を下位へ">↓</button><details><summary style="--swatch:${r.color}"><i class="theme-dot"></i>色</summary><div class="color-palette" data-level-colors="${r.id}">${swatches(r.color)}</div></details></div>`).join('')+'<div class="row"><button data-add>＋ レベル</button><button data-save class="primary">適用</button></div>';};
 body.onclick=e=>{const button=e.target.closest('button');if(!button)return;save();if(button.hasAttribute('data-add')){let n=rows.length+1;while(rows.some(r=>r.id==='level-'+n))n++;rows.unshift({id:'level-'+n,name:'レベル '+n,color:S.palette[n%S.palette.length].color,priority:rows.length});draw();}else if(button.hasAttribute('data-save')){rows.forEach((r,i)=>r.priority=rows.length-i);onApply(rows);d.close();}else if(button.dataset.up||button.dataset.down){const id=button.dataset.up||button.dataset.down,i=rows.findIndex(r=>r.id===id),j=i+(button.dataset.up?-1:1);[rows[i],rows[j]]=[rows[j],rows[i]];draw();}else if(button.dataset.color){const id=button.closest('[data-level-colors]').dataset.levelColors;rows.find(r=>r.id===id).color=button.dataset.color;draw();}};draw();
}
root.BJP_APPEARANCE={family,levels};
})(window);

}
