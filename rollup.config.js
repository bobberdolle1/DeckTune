import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import { defineConfig } from "rollup";
import importAssets from "rollup-plugin-import-assets";
import externalGlobals from "rollup-plugin-external-globals";
import del from "rollup-plugin-delete";
import { readFileSync } from "fs";

const manifest = JSON.parse(readFileSync("./plugin.json", "utf-8"));

export default defineConfig({
  input: "./src/index.tsx",
  plugins: [
    del({ targets: "./dist/*", force: true }),
    commonjs(),
    nodeResolve({
      browser: true,
    }),
    externalGlobals({
      react: "SP_REACT",
      "react-dom": "SP_REACTDOM",
      "react/jsx-runtime": "SP_JSX",
      "@decky/ui": "DFL",
      "@decky/manifest": JSON.stringify(manifest),
    }),
    typescript(),
    json(),
    replace({
      preventAssignment: false,
      "process.env.NODE_ENV": JSON.stringify("production"),
    }),
    importAssets({
      publicPath: `http://127.0.0.1:1337/plugins/${manifest.name}/`,
    }),
  ],
  context: "window",
  external: ["react", "react-dom", "@decky/ui", "@decky/manifest"],
  output: {
    file: "dist/index.js",
    format: "iife",
    name: "plugin",
    sourcemap: true,
    sourcemapPathTransform: (relativeSourcePath) =>
      relativeSourcePath.replace(
        /^\.\.\//,
        `decky://decky/plugin/${encodeURIComponent(manifest.name)}/`
      ),
  },
});
