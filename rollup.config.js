import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import typescript from '@rollup/plugin-typescript';
import del from 'rollup-plugin-delete';
import importAssets from 'rollup-plugin-import-assets';
import externalGlobals from 'rollup-plugin-external-globals';
import { readFileSync } from 'fs';

// Read manifest directly
const manifest = JSON.parse(readFileSync('./plugin.json', 'utf-8'));

// Custom plugin to replace @decky/manifest import with the actual manifest
// Uses a virtual module that exports the full manifest without treeshaking
function manifestPlugin() {
    return {
        name: 'decky-manifest',
        resolveId(source) {
            if (source === '@decky/manifest') {
                return { id: '\0@decky/manifest', moduleSideEffects: 'no-treeshake' };
            }
            return null;
        },
        load(id) {
            if (id === '\0@decky/manifest') {
                return `const manifest = ${JSON.stringify(manifest)};\nexport default manifest;`;
            }
            return null;
        }
    };
}

export default {
    input: './src/index.tsx',
    plugins: [
        del({ targets: './dist/*', force: true }),
        manifestPlugin(),
        typescript(),
        json(),
        commonjs(),
        nodeResolve({
            browser: true
        }),
        externalGlobals({
            react: 'SP_REACT',
            'react/jsx-runtime': 'SP_JSX',
            'react-dom': 'SP_REACTDOM',
            '@decky/ui': 'DFL'
        }),
        replace({
            preventAssignment: false,
            'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production'),
        }),
        importAssets({
            publicPath: `http://127.0.0.1:1337/plugins/${manifest.name}/`
        })
    ],
    context: 'window',
    external: ['react', 'react-dom', '@decky/ui'],
    treeshake: {
        pureExternalImports: {
            pure: ['@decky/ui', '@decky/api']
        },
        preset: 'smallest'
    },
    output: {
        dir: 'dist',
        format: 'esm',
        sourcemap: true,
        sourcemapPathTransform: (relativeSourcePath) => relativeSourcePath.replace(/^\.\.\//, `decky://decky/plugin/${encodeURIComponent(manifest.name)}/`),
        exports: 'default'
    },
};
