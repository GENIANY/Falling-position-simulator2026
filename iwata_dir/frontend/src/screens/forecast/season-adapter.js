// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;const WindFixture=window.WindFixture;
'use strict';
window.SEASON_ADAPTER={evaluate:o=>{if(!window.WindFixture?.generateSeason)throw Error('季節試算の共有アダプターを読み込めません。');const r=WindFixture.generateSeason({lat:o.origin[0],lon:o.origin[1],years:o.years,hours:o.validHours,period:o.period,calendar:o.calendar||WindFixture.calendarDefinition.version,idPrefix:'S'});return{...r,provenance:{...o,weatherHoursJST:o.validHours},label:r.definition};}};

}
