import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { cpSync, mkdirSync, createReadStream, statSync } from 'node:fs';
import { resolve, sep } from 'node:path';
const cesium=resolve('node_modules/cesium/Build/Cesium');
let outputDirectory=resolve('dist'), copyBuildAssets=false;
const sceneAssets={name:'scene-assets',configResolved(config:any){outputDirectory=resolve(config.root,config.build.outDir);copyBuildAssets=config.command==='build';},configureServer(server:any){server.middlewares.use('/cesium',(req:any,res:any,next:any)=>{const file=resolve(cesium,'.'+decodeURIComponent((req.url??'/').split('?')[0]));if(!file.startsWith(cesium+sep))return next();try{if(!statSync(file).isFile())return next();if(file.endsWith('.js'))res.setHeader('Content-Type','text/javascript');if(file.endsWith('.css'))res.setHeader('Content-Type','text/css');createReadStream(file).pipe(res);}catch{next();}});},closeBundle(){if(!copyBuildAssets)return;mkdirSync(outputDirectory,{recursive:true});cpSync(cesium,resolve(outputDirectory,'cesium'),{recursive:true});cpSync('scene3d',resolve(outputDirectory,'scene3d'),{recursive:true});mkdirSync(resolve(outputDirectory,'assets/images'),{recursive:true});cpSync('node_modules/leaflet/dist/images',resolve(outputDirectory,'assets/images'),{recursive:true});}};

export default defineConfig({
  plugins: [react(), sceneAssets],
  server: {
    host: "127.0.0.1",
    port: 8450,
    strictPort: true,
    proxy: { "/api": "http://127.0.0.1:8451" },
  },
  preview: {
    host: "127.0.0.1",
    port: 8452,
    strictPort: true,
    proxy: { "/api": "http://127.0.0.1:8451" },
  },
  test: { environment: "node" },
});
