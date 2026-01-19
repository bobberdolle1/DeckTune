// Test what dist/index.js exports
const fs = require('fs');
const path = require('path');

const distPath = process.argv[2] || 'dist/index.js';
const code = fs.readFileSync(distPath, 'utf8');

console.log('=== Testing Plugin Export ===');
console.log('File:', distPath);
console.log('Size:', code.length, 'bytes');
console.log();

// Mock window object
global.window = {
    SP_REACT: { createElement: () => ({}) },
    __DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit: () => ({
        connect: () => Promise.resolve({})
    })
};

try {
    // Eval the IIFE
    const result = eval(code);
    
    console.log('Export type:', typeof result);
    console.log('Is function:', typeof result === 'function');
    console.log();
    
    if (typeof result === 'function') {
        console.log('✓ Export is a function (correct!)');
        console.log('Calling it to get plugin object...');
        
        try {
            const plugin = result();
            console.log('Plugin type:', typeof plugin);
            console.log('Plugin keys:', Object.keys(plugin || {}));
            
            if (plugin && plugin.name) {
                console.log('✓ Plugin name:', plugin.name);
            }
        } catch (e) {
            console.log('✗ Error calling function:', e.message);
        }
    } else {
        console.log('✗ Export is NOT a function!');
        console.log('Actual value:', result);
        
        if (result && typeof result === 'object') {
            console.log('Object keys:', Object.keys(result));
        }
    }
} catch (e) {
    console.log('✗ Error evaluating code:', e.message);
    console.log(e.stack);
}
