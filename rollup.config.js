import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import { defineConfig } from "rollup";
import importAssets from "rollup-plugin-import-assets";
import externalGlobals from 'rollup-plugin-external-globals';

import manifest from './plugin.json' with { type: 'json' };

export default defineConfig({
  input: "./src/index.tsx",
  plugins: [
    typescript({
      tsconfig: './tsconfig.json',
      include: ['src/**/*.ts', 'src/**/*.tsx'],
      sourceMap: true,
      inlineSources: true
    }),
    commonjs(),
    nodeResolve({
      browser: true,
      extensions: ['.js', '.jsx', '.ts', '.tsx']
    }),
    externalGlobals({
      react: 'SP_REACT',
      'react-dom': 'SP_REACTDOM',
      '@decky/ui': 'DFL',
      '@decky/manifest': JSON.stringify(manifest)
    }),
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
    file: 'dist/index.js',
    format: 'es',
    sourcemap: true,
    sourcemapPathTransform: (relativeSourcePath) => relativeSourcePath.replace(/^\.\.\//, `decky://decky/plugin/${encodeURIComponent(manifest.name)}/`),
  },
  onwarn: () => undefined,
});
