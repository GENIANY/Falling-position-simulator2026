/** Shared original-weather-window types; no UI or ensemble-planning dependency. */
export type HistoricalWindow={window_id:string;label:string;weather_source_id:string|null;launch_time_utc:string;reason:string;ordinal?:number;weather_snapshot?:Record<string,any>|null;availability?:string};
export type HistoricalSampling={mode:'historical_windows';variable:'original_weather_window';n:number;reason:string;interpretation:'explicit_historical_windows';pairing:'same_original_weather_window';weighting:'equal_explicit_windows'};
