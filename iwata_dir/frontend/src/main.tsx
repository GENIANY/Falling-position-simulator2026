import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import leafletStyleUrl from "leaflet/dist/leaflet.css?url";

// One separately addressable local sheet supports computed-style verification
// and transactional recovery on the 3D-to-2D return in both Vite and production.
const style = document.createElement('link');
style.id = 'leafletStyle'; style.rel = 'stylesheet'; style.href = leafletStyleUrl;
let mounted = false;
const mount = () => { if (mounted) return; mounted = true; createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>); };
style.addEventListener('load', mount, {once:true});
style.addEventListener('error', mount, {once:true});
document.head.append(style);
