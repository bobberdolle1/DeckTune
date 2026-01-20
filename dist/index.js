// Decky Loader will pass this api in, it's versioned to allow for backwards compatibility.
// @ts-ignore

// Prevents it from being duplicated in output.
const manifest = {"name":"DeckTune"};
const API_VERSION = 1;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
// Initialize
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
const api = internalAPIConnection.connect(API_VERSION, manifest.name);
const call = api.call;
api.callable;
const addEventListener = api.addEventListener;
const removeEventListener = api.removeEventListener;
api.routerHook;
api.toaster;
api.openFilePicker;
api.executeInTab;
api.injectCssIntoTab;
api.removeCssFromTab;
api.fetchNoCors;
api.getExternalResourceURL;
const definePlugin = (fn) => {
    return (...args) => {
        // TODO: Maybe wrap this
        return fn(...args);
    };
};

var DefaultContext = {
  color: undefined,
  size: undefined,
  className: undefined,
  style: undefined,
  attr: undefined
};
var IconContext = SP_REACT.createContext && /*#__PURE__*/SP_REACT.createContext(DefaultContext);

var _excluded = ["attr", "size", "title"];
function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }
function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } } return target; }
function _extends() { _extends = Object.assign ? Object.assign.bind() : function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; }; return _extends.apply(this, arguments); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), true).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == typeof i ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != typeof t || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r); if ("object" != typeof i) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function Tree2Element(tree) {
  return tree && tree.map((node, i) => /*#__PURE__*/SP_REACT.createElement(node.tag, _objectSpread({
    key: i
  }, node.attr), Tree2Element(node.child)));
}
function GenIcon(data) {
  return props => /*#__PURE__*/SP_REACT.createElement(IconBase, _extends({
    attr: _objectSpread({}, data.attr)
  }, props), Tree2Element(data.child));
}
function IconBase(props) {
  var elem = conf => {
    var {
        attr,
        size,
        title
      } = props,
      svgProps = _objectWithoutProperties(props, _excluded);
    var computedSize = size || conf.size || "1em";
    var className;
    if (conf.className) className = conf.className;
    if (props.className) className = (className ? className + " " : "") + props.className;
    return /*#__PURE__*/SP_REACT.createElement("svg", _extends({
      stroke: "currentColor",
      fill: "currentColor",
      strokeWidth: "0"
    }, conf.attr, attr, svgProps, {
      className: className,
      style: _objectSpread(_objectSpread({
        color: props.color || conf.color
      }, conf.style), props.style),
      height: computedSize,
      width: computedSize,
      xmlns: "http://www.w3.org/2000/svg"
    }), title && /*#__PURE__*/SP_REACT.createElement("title", null, title), props.children);
  };
  return IconContext !== undefined ? /*#__PURE__*/SP_REACT.createElement(IconContext.Consumer, null, conf => elem(conf)) : elem(DefaultContext);
}

// THIS FILE IS AUTO GENERATED
function FaArrowLeft (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M257.5 445.1l-22.2 22.2c-9.4 9.4-24.6 9.4-33.9 0L7 273c-9.4-9.4-9.4-24.6 0-33.9L201.4 44.7c9.4-9.4 24.6-9.4 33.9 0l22.2 22.2c9.5 9.5 9.3 25-.4 34.3L136.6 216H424c13.3 0 24 10.7 24 24v32c0 13.3-10.7 24-24 24H136.6l120.5 114.8c9.8 9.3 10 24.8.4 34.3z"},"child":[]}]})(props);
}function FaArrowRight (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M190.5 66.9l22.2-22.2c9.4-9.4 24.6-9.4 33.9 0L441 239c9.4 9.4 9.4 24.6 0 33.9L246.6 467.3c-9.4 9.4-24.6 9.4-33.9 0l-22.2-22.2c-9.5-9.5-9.3-25 .4-34.3L311.4 296H24c-13.3 0-24-10.7-24-24v-32c0-13.3 10.7-24 24-24h287.4L190.9 101.2c-9.8-9.3-10-24.8-.4-34.3z"},"child":[]}]})(props);
}function FaAward (props) {
  return GenIcon({"attr":{"viewBox":"0 0 384 512"},"child":[{"tag":"path","attr":{"d":"M97.12 362.63c-8.69-8.69-4.16-6.24-25.12-11.85-9.51-2.55-17.87-7.45-25.43-13.32L1.2 448.7c-4.39 10.77 3.81 22.47 15.43 22.03l52.69-2.01L105.56 507c8 8.44 22.04 5.81 26.43-4.96l52.05-127.62c-10.84 6.04-22.87 9.58-35.31 9.58-19.5 0-37.82-7.59-51.61-21.37zM382.8 448.7l-45.37-111.24c-7.56 5.88-15.92 10.77-25.43 13.32-21.07 5.64-16.45 3.18-25.12 11.85-13.79 13.78-32.12 21.37-51.62 21.37-12.44 0-24.47-3.55-35.31-9.58L252 502.04c4.39 10.77 18.44 13.4 26.43 4.96l36.25-38.28 52.69 2.01c11.62.44 19.82-11.27 15.43-22.03zM263 340c15.28-15.55 17.03-14.21 38.79-20.14 13.89-3.79 24.75-14.84 28.47-28.98 7.48-28.4 5.54-24.97 25.95-45.75 10.17-10.35 14.14-25.44 10.42-39.58-7.47-28.38-7.48-24.42 0-52.83 3.72-14.14-.25-29.23-10.42-39.58-20.41-20.78-18.47-17.36-25.95-45.75-3.72-14.14-14.58-25.19-28.47-28.98-27.88-7.61-24.52-5.62-44.95-26.41-10.17-10.35-25-14.4-38.89-10.61-27.87 7.6-23.98 7.61-51.9 0-13.89-3.79-28.72.25-38.89 10.61-20.41 20.78-17.05 18.8-44.94 26.41-13.89 3.79-24.75 14.84-28.47 28.98-7.47 28.39-5.54 24.97-25.95 45.75-10.17 10.35-14.15 25.44-10.42 39.58 7.47 28.36 7.48 24.4 0 52.82-3.72 14.14.25 29.23 10.42 39.59 20.41 20.78 18.47 17.35 25.95 45.75 3.72 14.14 14.58 25.19 28.47 28.98C104.6 325.96 106.27 325 121 340c13.23 13.47 33.84 15.88 49.74 5.82a39.676 39.676 0 0 1 42.53 0c15.89 10.06 36.5 7.65 49.73-5.82zM97.66 175.96c0-53.03 42.24-96.02 94.34-96.02s94.34 42.99 94.34 96.02-42.24 96.02-94.34 96.02-94.34-42.99-94.34-96.02z"},"child":[]}]})(props);
}function FaBalanceScale (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M256 336h-.02c0-16.18 1.34-8.73-85.05-181.51-17.65-35.29-68.19-35.36-85.87 0C-2.06 328.75.02 320.33.02 336H0c0 44.18 57.31 80 128 80s128-35.82 128-80zM128 176l72 144H56l72-144zm511.98 160c0-16.18 1.34-8.73-85.05-181.51-17.65-35.29-68.19-35.36-85.87 0-87.12 174.26-85.04 165.84-85.04 181.51H384c0 44.18 57.31 80 128 80s128-35.82 128-80h-.02zM440 320l72-144 72 144H440zm88 128H352V153.25c23.51-10.29 41.16-31.48 46.39-57.25H528c8.84 0 16-7.16 16-16V48c0-8.84-7.16-16-16-16H383.64C369.04 12.68 346.09 0 320 0s-49.04 12.68-63.64 32H112c-8.84 0-16 7.16-16 16v32c0 8.84 7.16 16 16 16h129.61c5.23 25.76 22.87 46.96 46.39 57.25V448H112c-8.84 0-16 7.16-16 16v32c0 8.84 7.16 16 16 16h416c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16z"},"child":[]}]})(props);
}function FaBan (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119.034 8 8 119.033 8 256s111.034 248 248 248 248-111.034 248-248S392.967 8 256 8zm130.108 117.892c65.448 65.448 70 165.481 20.677 235.637L150.47 105.216c70.204-49.356 170.226-44.735 235.638 20.676zM125.892 386.108c-65.448-65.448-70-165.481-20.677-235.637L361.53 406.784c-70.203 49.356-170.226 44.736-235.638-20.676z"},"child":[]}]})(props);
}function FaBatteryFull (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M544 160v64h32v64h-32v64H64V160h480m16-64H48c-26.51 0-48 21.49-48 48v224c0 26.51 21.49 48 48 48h512c26.51 0 48-21.49 48-48v-16h8c13.255 0 24-10.745 24-24V184c0-13.255-10.745-24-24-24h-8v-16c0-26.51-21.49-48-48-48zm-48 96H96v128h416V192z"},"child":[]}]})(props);
}function FaBolt (props) {
  return GenIcon({"attr":{"viewBox":"0 0 320 512"},"child":[{"tag":"path","attr":{"d":"M296 160H180.6l42.6-129.8C227.2 15 215.7 0 200 0H56C44 0 33.8 8.9 32.2 20.8l-32 240C-1.7 275.2 9.5 288 24 288h118.7L96.6 482.5c-3.6 15.2 8 29.5 23.3 29.5 8.4 0 16.4-4.4 20.8-12l176-304c9.3-15.9-2.2-36-20.7-36z"},"child":[]}]})(props);
}function FaCertificate (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M458.622 255.92l45.985-45.005c13.708-12.977 7.316-36.039-10.664-40.339l-62.65-15.99 17.661-62.015c4.991-17.838-11.829-34.663-29.661-29.671l-61.994 17.667-15.984-62.671C337.085.197 313.765-6.276 300.99 7.228L256 53.57 211.011 7.229c-12.63-13.351-36.047-7.234-40.325 10.668l-15.984 62.671-61.995-17.667C74.87 57.907 58.056 74.738 63.046 92.572l17.661 62.015-62.65 15.99C.069 174.878-6.31 197.944 7.392 210.915l45.985 45.005-45.985 45.004c-13.708 12.977-7.316 36.039 10.664 40.339l62.65 15.99-17.661 62.015c-4.991 17.838 11.829 34.663 29.661 29.671l61.994-17.667 15.984 62.671c4.439 18.575 27.696 24.018 40.325 10.668L256 458.61l44.989 46.001c12.5 13.488 35.987 7.486 40.325-10.668l15.984-62.671 61.994 17.667c17.836 4.994 34.651-11.837 29.661-29.671l-17.661-62.015 62.65-15.99c17.987-4.302 24.366-27.367 10.664-40.339l-45.984-45.004z"},"child":[]}]})(props);
}function FaChartLine (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M496 384H64V80c0-8.84-7.16-16-16-16H16C7.16 64 0 71.16 0 80v336c0 17.67 14.33 32 32 32h464c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16zM464 96H345.94c-21.38 0-32.09 25.85-16.97 40.97l32.4 32.4L288 242.75l-73.37-73.37c-12.5-12.5-32.76-12.5-45.25 0l-68.69 68.69c-6.25 6.25-6.25 16.38 0 22.63l22.62 22.62c6.25 6.25 16.38 6.25 22.63 0L192 237.25l73.37 73.37c12.5 12.5 32.76 12.5 45.25 0l96-96 32.4 32.4c15.12 15.12 40.97 4.41 40.97-16.97V112c.01-8.84-7.15-16-15.99-16z"},"child":[]}]})(props);
}function FaCheck (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M173.898 439.404l-166.4-166.4c-9.997-9.997-9.997-26.206 0-36.204l36.203-36.204c9.997-9.998 26.207-9.998 36.204 0L192 312.69 432.095 72.596c9.997-9.997 26.207-9.997 36.204 0l36.203 36.204c9.997 9.997 9.997 26.206 0 36.204l-294.4 294.401c-9.998 9.997-26.207 9.997-36.204-.001z"},"child":[]}]})(props);
}function FaCog (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M487.4 315.7l-42.6-24.6c4.3-23.2 4.3-47 0-70.2l42.6-24.6c4.9-2.8 7.1-8.6 5.5-14-11.1-35.6-30-67.8-54.7-94.6-3.8-4.1-10-5.1-14.8-2.3L380.8 110c-17.9-15.4-38.5-27.3-60.8-35.1V25.8c0-5.6-3.9-10.5-9.4-11.7-36.7-8.2-74.3-7.8-109.2 0-5.5 1.2-9.4 6.1-9.4 11.7V75c-22.2 7.9-42.8 19.8-60.8 35.1L88.7 85.5c-4.9-2.8-11-1.9-14.8 2.3-24.7 26.7-43.6 58.9-54.7 94.6-1.7 5.4.6 11.2 5.5 14L67.3 221c-4.3 23.2-4.3 47 0 70.2l-42.6 24.6c-4.9 2.8-7.1 8.6-5.5 14 11.1 35.6 30 67.8 54.7 94.6 3.8 4.1 10 5.1 14.8 2.3l42.6-24.6c17.9 15.4 38.5 27.3 60.8 35.1v49.2c0 5.6 3.9 10.5 9.4 11.7 36.7 8.2 74.3 7.8 109.2 0 5.5-1.2 9.4-6.1 9.4-11.7v-49.2c22.2-7.9 42.8-19.8 60.8-35.1l42.6 24.6c4.9 2.8 11 1.9 14.8-2.3 24.7-26.7 43.6-58.9 54.7-94.6 1.5-5.5-.7-11.3-5.6-14.1zM256 336c-44.1 0-80-35.9-80-80s35.9-80 80-80 80 35.9 80 80-35.9 80-80 80z"},"child":[]}]})(props);
}function FaDownload (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z"},"child":[]}]})(props);
}function FaExclamationCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 256c0 136.997-111.043 248-248 248S8 392.997 8 256C8 119.083 119.043 8 256 8s248 111.083 248 248zm-248 50c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"},"child":[]}]})(props);
}function FaExclamationTriangle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"},"child":[]}]})(props);
}function FaFan (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M352.57 128c-28.09 0-54.09 4.52-77.06 12.86l12.41-123.11C289 7.31 279.81-1.18 269.33.13 189.63 10.13 128 77.64 128 159.43c0 28.09 4.52 54.09 12.86 77.06L17.75 224.08C7.31 223-1.18 232.19.13 242.67c10 79.7 77.51 141.33 159.3 141.33 28.09 0 54.09-4.52 77.06-12.86l-12.41 123.11c-1.05 10.43 8.11 18.93 18.59 17.62 79.7-10 141.33-77.51 141.33-159.3 0-28.09-4.52-54.09-12.86-77.06l123.11 12.41c10.44 1.05 18.93-8.11 17.62-18.59-10-79.7-77.51-141.33-159.3-141.33zM256 288a32 32 0 1 1 32-32 32 32 0 0 1-32 32z"},"child":[]}]})(props);
}function FaGamepad (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M480.07 96H160a160 160 0 1 0 114.24 272h91.52A160 160 0 1 0 480.07 96zM248 268a12 12 0 0 1-12 12h-52v52a12 12 0 0 1-12 12h-24a12 12 0 0 1-12-12v-52H84a12 12 0 0 1-12-12v-24a12 12 0 0 1 12-12h52v-52a12 12 0 0 1 12-12h24a12 12 0 0 1 12 12v52h52a12 12 0 0 1 12 12zm216 76a40 40 0 1 1 40-40 40 40 0 0 1-40 40zm64-96a40 40 0 1 1 40-40 40 40 0 0 1-40 40z"},"child":[]}]})(props);
}function FaGlobe (props) {
  return GenIcon({"attr":{"viewBox":"0 0 496 512"},"child":[{"tag":"path","attr":{"d":"M336.5 160C322 70.7 287.8 8 248 8s-74 62.7-88.5 152h177zM152 256c0 22.2 1.2 43.5 3.3 64h185.3c2.1-20.5 3.3-41.8 3.3-64s-1.2-43.5-3.3-64H155.3c-2.1 20.5-3.3 41.8-3.3 64zm324.7-96c-28.6-67.9-86.5-120.4-158-141.6 24.4 33.8 41.2 84.7 50 141.6h108zM177.2 18.4C105.8 39.6 47.8 92.1 19.3 160h108c8.7-56.9 25.5-107.8 49.9-141.6zM487.4 192H372.7c2.1 21 3.3 42.5 3.3 64s-1.2 43-3.3 64h114.6c5.5-20.5 8.6-41.8 8.6-64s-3.1-43.5-8.5-64zM120 256c0-21.5 1.2-43 3.3-64H8.6C3.2 212.5 0 233.8 0 256s3.2 43.5 8.6 64h114.6c-2-21-3.2-42.5-3.2-64zm39.5 96c14.5 89.3 48.7 152 88.5 152s74-62.7 88.5-152h-177zm159.3 141.6c71.4-21.2 129.4-73.7 158-141.6h-108c-8.8 56.9-25.6 107.8-50 141.6zM19.3 352c28.6 67.9 86.5 120.4 158 141.6-24.4-33.8-41.2-84.7-50-141.6h-108z"},"child":[]}]})(props);
}function FaHistory (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 255.531c.253 136.64-111.18 248.372-247.82 248.468-59.015.042-113.223-20.53-155.822-54.911-11.077-8.94-11.905-25.541-1.839-35.607l11.267-11.267c8.609-8.609 22.353-9.551 31.891-1.984C173.062 425.135 212.781 440 256 440c101.705 0 184-82.311 184-184 0-101.705-82.311-184-184-184-48.814 0-93.149 18.969-126.068 49.932l50.754 50.754c10.08 10.08 2.941 27.314-11.313 27.314H24c-8.837 0-16-7.163-16-16V38.627c0-14.254 17.234-21.393 27.314-11.314l49.372 49.372C129.209 34.136 189.552 8 256 8c136.81 0 247.747 110.78 248 247.531zm-180.912 78.784l9.823-12.63c8.138-10.463 6.253-25.542-4.21-33.679L288 256.349V152c0-13.255-10.745-24-24-24h-16c-13.255 0-24 10.745-24 24v135.651l65.409 50.874c10.463 8.137 25.541 6.253 33.679-4.21z"},"child":[]}]})(props);
}function FaInfoCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm0 110c23.196 0 42 18.804 42 42s-18.804 42-42 42-42-18.804-42-42 18.804-42 42-42zm56 254c0 6.627-5.373 12-12 12h-88c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h12v-64h-12c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h64c6.627 0 12 5.373 12 12v100h12c6.627 0 12 5.373 12 12v24z"},"child":[]}]})(props);
}function FaLeaf (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M546.2 9.7c-5.6-12.5-21.6-13-28.3-1.2C486.9 62.4 431.4 96 368 96h-80C182 96 96 182 96 288c0 7 .8 13.7 1.5 20.5C161.3 262.8 253.4 224 384 224c8.8 0 16 7.2 16 16s-7.2 16-16 16C132.6 256 26 410.1 2.4 468c-6.6 16.3 1.2 34.9 17.5 41.6 16.4 6.8 35-1.1 41.8-17.3 1.5-3.6 20.9-47.9 71.9-90.6 32.4 43.9 94 85.8 174.9 77.2C465.5 467.5 576 326.7 576 154.3c0-50.2-10.8-102.2-29.8-144.6z"},"child":[]}]})(props);
}function FaList (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M80 368H16a16 16 0 0 0-16 16v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16v-64a16 16 0 0 0-16-16zm0-320H16A16 16 0 0 0 0 64v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16V64a16 16 0 0 0-16-16zm0 160H16a16 16 0 0 0-16 16v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16v-64a16 16 0 0 0-16-16zm416 176H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16zm0-320H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16V80a16 16 0 0 0-16-16zm0 160H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16z"},"child":[]}]})(props);
}function FaMagic (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M224 96l16-32 32-16-32-16-16-32-16 32-32 16 32 16 16 32zM80 160l26.66-53.33L160 80l-53.34-26.67L80 0 53.34 53.33 0 80l53.34 26.67L80 160zm352 128l-26.66 53.33L352 368l53.34 26.67L432 448l26.66-53.33L512 368l-53.34-26.67L432 288zm70.62-193.77L417.77 9.38C411.53 3.12 403.34 0 395.15 0c-8.19 0-16.38 3.12-22.63 9.38L9.38 372.52c-12.5 12.5-12.5 32.76 0 45.25l84.85 84.85c6.25 6.25 14.44 9.37 22.62 9.37 8.19 0 16.38-3.12 22.63-9.37l363.14-363.15c12.5-12.48 12.5-32.75 0-45.24zM359.45 203.46l-50.91-50.91 86.6-86.6 50.91 50.91-86.6 86.6z"},"child":[]}]})(props);
}function FaMedal (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M223.75 130.75L154.62 15.54A31.997 31.997 0 0 0 127.18 0H16.03C3.08 0-4.5 14.57 2.92 25.18l111.27 158.96c29.72-27.77 67.52-46.83 109.56-53.39zM495.97 0H384.82c-11.24 0-21.66 5.9-27.44 15.54l-69.13 115.21c42.04 6.56 79.84 25.62 109.56 53.38L509.08 25.18C516.5 14.57 508.92 0 495.97 0zM256 160c-97.2 0-176 78.8-176 176s78.8 176 176 176 176-78.8 176-176-78.8-176-176-176zm92.52 157.26l-37.93 36.96 8.97 52.22c1.6 9.36-8.26 16.51-16.65 12.09L256 393.88l-46.9 24.65c-8.4 4.45-18.25-2.74-16.65-12.09l8.97-52.22-37.93-36.96c-6.82-6.64-3.05-18.23 6.35-19.59l52.43-7.64 23.43-47.52c2.11-4.28 6.19-6.39 10.28-6.39 4.11 0 8.22 2.14 10.33 6.39l23.43 47.52 52.43 7.64c9.4 1.36 13.17 12.95 6.35 19.59z"},"child":[]}]})(props);
}function FaPlay (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M424.4 214.7L72.4 6.6C43.8-10.3 0 6.1 0 47.9V464c0 37.5 40.7 60.1 72.4 41.3l352-208c31.4-18.5 31.5-64.1 0-82.6z"},"child":[]}]})(props);
}function FaPlus (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z"},"child":[]}]})(props);
}function FaRedo (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M500.33 0h-47.41a12 12 0 0 0-12 12.57l4 82.76A247.42 247.42 0 0 0 256 8C119.34 8 7.9 119.53 8 256.19 8.1 393.07 119.1 504 256 504a247.1 247.1 0 0 0 166.18-63.91 12 12 0 0 0 .48-17.43l-34-34a12 12 0 0 0-16.38-.55A176 176 0 1 1 402.1 157.8l-101.53-4.87a12 12 0 0 0-12.57 12v47.41a12 12 0 0 0 12 12h200.33a12 12 0 0 0 12-12V12a12 12 0 0 0-12-12z"},"child":[]}]})(props);
}function FaRocket (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M505.12019,19.09375c-1.18945-5.53125-6.65819-11-12.207-12.1875C460.716,0,435.507,0,410.40747,0,307.17523,0,245.26909,55.20312,199.05238,128H94.83772c-16.34763.01562-35.55658,11.875-42.88664,26.48438L2.51562,253.29688A28.4,28.4,0,0,0,0,264a24.00867,24.00867,0,0,0,24.00582,24H127.81618l-22.47457,22.46875c-11.36521,11.36133-12.99607,32.25781,0,45.25L156.24582,406.625c11.15623,11.1875,32.15619,13.15625,45.27726,0l22.47457-22.46875V488a24.00867,24.00867,0,0,0,24.00581,24,28.55934,28.55934,0,0,0,10.707-2.51562l98.72834-49.39063c14.62888-7.29687,26.50776-26.5,26.50776-42.85937V312.79688c72.59753-46.3125,128.03493-108.40626,128.03493-211.09376C512.07526,76.5,512.07526,51.29688,505.12019,19.09375ZM384.04033,168A40,40,0,1,1,424.05,128,40.02322,40.02322,0,0,1,384.04033,168Z"},"child":[]}]})(props);
}function FaSlidersH (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M496 384H160v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h80v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h336c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160h-80v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h336v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h80c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160H288V48c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16C7.2 64 0 71.2 0 80v32c0 8.8 7.2 16 16 16h208v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h208c8.8 0 16-7.2 16-16V80c0-8.8-7.2-16-16-16z"},"child":[]}]})(props);
}function FaSpinner (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M304 48c0 26.51-21.49 48-48 48s-48-21.49-48-48 21.49-48 48-48 48 21.49 48 48zm-48 368c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zm208-208c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zM96 256c0-26.51-21.49-48-48-48S0 229.49 0 256s21.49 48 48 48 48-21.49 48-48zm12.922 99.078c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.491-48-48-48zm294.156 0c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.49-48-48-48zM108.922 60.922c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.491-48-48-48z"},"child":[]}]})(props);
}function FaStop (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M400 32H48C21.5 32 0 53.5 0 80v352c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V80c0-26.5-21.5-48-48-48z"},"child":[]}]})(props);
}function FaThermometerHalf (props) {
  return GenIcon({"attr":{"viewBox":"0 0 256 512"},"child":[{"tag":"path","attr":{"d":"M192 384c0 35.346-28.654 64-64 64s-64-28.654-64-64c0-23.685 12.876-44.349 32-55.417V224c0-17.673 14.327-32 32-32s32 14.327 32 32v104.583c19.124 11.068 32 31.732 32 55.417zm32-84.653c19.912 22.563 32 52.194 32 84.653 0 70.696-57.303 128-128 128-.299 0-.609-.001-.909-.003C56.789 511.509-.357 453.636.002 383.333.166 351.135 12.225 321.755 32 299.347V96c0-53.019 42.981-96 96-96s96 42.981 96 96v203.347zM208 384c0-34.339-19.37-52.19-32-66.502V96c0-26.467-21.533-48-48-48S80 69.533 80 96v221.498c-12.732 14.428-31.825 32.1-31.999 66.08-.224 43.876 35.563 80.116 79.423 80.42L128 464c44.112 0 80-35.888 80-80z"},"child":[]}]})(props);
}function FaTimes (props) {
  return GenIcon({"attr":{"viewBox":"0 0 352 512"},"child":[{"tag":"path","attr":{"d":"M242.72 256l100.07-100.07c12.28-12.28 12.28-32.19 0-44.48l-22.24-22.24c-12.28-12.28-32.19-12.28-44.48 0L176 189.28 75.93 89.21c-12.28-12.28-32.19-12.28-44.48 0L9.21 111.45c-12.28 12.28-12.28 32.19 0 44.48L109.28 256 9.21 356.07c-12.28 12.28-12.28 32.19 0 44.48l22.24 22.24c12.28 12.28 32.2 12.28 44.48 0L176 322.72l100.07 100.07c12.28 12.28 32.2 12.28 44.48 0l22.24-22.24c12.28-12.28 12.28-32.19 0-44.48L242.72 256z"},"child":[]}]})(props);
}function FaTrash (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M432 32H312l-9.4-18.7A24 24 0 0 0 281.1 0H166.8a23.72 23.72 0 0 0-21.4 13.3L136 32H16A16 16 0 0 0 0 48v32a16 16 0 0 0 16 16h416a16 16 0 0 0 16-16V48a16 16 0 0 0-16-16zM53.2 467a48 48 0 0 0 47.9 45h245.8a48 48 0 0 0 47.9-45L416 128H32z"},"child":[]}]})(props);
}function FaTrophy (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M552 64H448V24c0-13.3-10.7-24-24-24H152c-13.3 0-24 10.7-24 24v40H24C10.7 64 0 74.7 0 88v56c0 35.7 22.5 72.4 61.9 100.7 31.5 22.7 69.8 37.1 110 41.7C203.3 338.5 240 360 240 360v72h-48c-35.3 0-64 20.7-64 56v12c0 6.6 5.4 12 12 12h296c6.6 0 12-5.4 12-12v-12c0-35.3-28.7-56-64-56h-48v-72s36.7-21.5 68.1-73.6c40.3-4.6 78.6-19 110-41.7 39.3-28.3 61.9-65 61.9-100.7V88c0-13.3-10.7-24-24-24zM99.3 192.8C74.9 175.2 64 155.6 64 144v-16h64.2c1 32.6 5.8 61.2 12.8 86.2-15.1-5.2-29.2-12.4-41.7-21.4zM512 144c0 16.1-17.7 36.1-35.3 48.8-12.5 9-26.7 16.2-41.8 21.4 7-25 11.8-53.6 12.8-86.2H512v16z"},"child":[]}]})(props);
}function FaUndo (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M212.333 224.333H12c-6.627 0-12-5.373-12-12V12C0 5.373 5.373 0 12 0h48c6.627 0 12 5.373 12 12v78.112C117.773 39.279 184.26 7.47 258.175 8.007c136.906.994 246.448 111.623 246.157 248.532C504.041 393.258 393.12 504 256.333 504c-64.089 0-122.496-24.313-166.51-64.215-5.099-4.622-5.334-12.554-.467-17.42l33.967-33.967c4.474-4.474 11.662-4.717 16.401-.525C170.76 415.336 211.58 432 256.333 432c97.268 0 176-78.716 176-176 0-97.267-78.716-176-176-176-58.496 0-110.28 28.476-142.274 72.333h98.274c6.627 0 12 5.373 12 12v48c0 6.627-5.373 12-12 12z"},"child":[]}]})(props);
}function FaVial (props) {
  return GenIcon({"attr":{"viewBox":"0 0 480 512"},"child":[{"tag":"path","attr":{"d":"M477.7 186.1L309.5 18.3c-3.1-3.1-8.2-3.1-11.3 0l-34 33.9c-3.1 3.1-3.1 8.2 0 11.3l11.2 11.1L33 316.5c-38.8 38.7-45.1 102-9.4 143.5 20.6 24 49.5 36 78.4 35.9 26.4 0 52.8-10 72.9-30.1l246.3-245.7 11.2 11.1c3.1 3.1 8.2 3.1 11.3 0l34-33.9c3.1-3 3.1-8.1 0-11.2zM318 256H161l148-147.7 78.5 78.3L318 256z"},"child":[]}]})(props);
}

/**
 * API class for DeckTune frontend state management.
 *
 * Feature: decktune, Frontend State Management
 * Requirements: Frontend integration, State management
 *
 * This class manages frontend state and provides RPC methods for
 * communicating with the Python backend.
 */
class SimpleEventEmitter {
    constructor() {
        this.events = new Map();
    }
    on(event, handler) {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event).push(handler);
    }
    emit(event, ...args) {
        const handlers = this.events.get(event);
        if (handlers) {
            handlers.forEach(handler => handler(...args));
        }
    }
    removeListener(event, handler) {
        const handlers = this.events.get(event);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
            }
        }
    }
}
let apiInstance = null;
/**
 * Get or create the singleton Api instance.
 */
const getApiInstance = (initialState) => {
    if (!apiInstance) {
        apiInstance = new Api(initialState);
    }
    return apiInstance;
};
/**
 * Main API class for DeckTune frontend.
 *
 * Extends SimpleEventEmitter to provide state change notifications.
 * Implements all RPC methods for backend communication.
 */
class Api extends SimpleEventEmitter {
    constructor(initialState) {
        super();
        this.registeredListeners = [];
        this.state = initialState;
    }
    /**
     * Update state and emit change event.
     */
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.emit("state_change", this.state);
    }
    /**
     * Get current state.
     */
    getState() {
        return this.state;
    }
    /**
     * Initialize the API and register event listeners.
     */
    async init() {
        await call("init");
        await this.fetchConfig();
        await this.fetchPlatformInfo();
        await this.fetchTestHistory();
        // Register Steam client listeners (with fallbacks for API changes)
        try {
            if (SteamClient?.GameSessions?.RegisterForAppLifetimeNotifications) {
                this.registeredListeners.push(SteamClient.GameSessions.RegisterForAppLifetimeNotifications(this.onAppLifetimeNotification.bind(this)));
            }
        }
        catch (e) {
            console.warn("DeckTune: Failed to register app lifetime listener:", e);
        }
        try {
            if (SteamClient?.System?.RegisterForOnResumeFromSuspend) {
                this.registeredListeners.push(SteamClient.System.RegisterForOnResumeFromSuspend(this.onResumeFromSuspend.bind(this)));
            }
        }
        catch (e) {
            console.warn("DeckTune: Failed to register suspend listener:", e);
        }
        // Register backend event listeners
        addEventListener("tuning_progress", this.onTuningProgress.bind(this));
        addEventListener("tuning_complete", this.onTuningComplete.bind(this));
        addEventListener("test_complete", this.onTestComplete.bind(this));
        addEventListener("update_status", this.onStatusUpdate.bind(this));
        addEventListener("dynamic_status", this.onDynamicStatus.bind(this));
        addEventListener("binning_progress", this.onBinningProgress.bind(this));
        addEventListener("binning_complete", this.onBinningComplete.bind(this));
        addEventListener("binning_error", this.onBinningError.bind(this));
        addEventListener("profile_changed", this.onProfileChanged.bind(this));
        addEventListener("telemetry_sample", this.onTelemetrySample.bind(this));
        if (this.state.settings.isRunAutomatically && DFL.Router.MainRunningApp) {
            return await this.handleMainRunningApp();
        }
        if (this.state.settings.runAtStartup) {
            return await this.applyUndervolt(this.state.cores, this.state.settings.timeoutApply);
        }
        await this.disableUndervolt();
    }
    /**
     * Fetch configuration from backend.
     */
    async fetchConfig() {
        const config = (await call("fetch_config"));
        this.setState({
            dynamicSettings: config.dynamicSettings,
            globalCores: config.cores,
            cores: config.cores,
            settings: config.settings,
            presets: config.presets,
            status: config.status,
        });
    }
    /**
     * Fetch platform information from backend.
     * Requirements: Frontend integration
     */
    async fetchPlatformInfo() {
        const platformInfo = (await call("get_platform_info"));
        this.setState({ platformInfo });
        return platformInfo;
    }
    /**
     * Fetch test history from backend.
     * Requirements: Frontend integration
     */
    async fetchTestHistory() {
        const testHistory = (await call("get_test_history"));
        this.setState({ testHistory });
        return testHistory;
    }
    // ==================== Event Handlers ====================
    /**
     * Handle tuning progress events from backend.
     */
    onTuningProgress(progress) {
        this.setState({ autotuneProgress: progress });
    }
    /**
     * Handle tuning complete events from backend.
     */
    onTuningComplete(result) {
        this.setState({
            autotuneResult: result,
            autotuneProgress: null,
            isAutotuning: false,
        });
    }
    /**
     * Handle test complete events from backend.
     */
    onTestComplete(result) {
        this.setState({ currentTest: null, isTestRunning: false });
        // Refresh test history
        this.fetchTestHistory();
    }
    /**
     * Handle status update events from backend.
     */
    onStatusUpdate(status) {
        this.setState({ status });
    }
    /**
     * Handle dynamic status update events from backend.
     * Requirements: 15.1
     */
    onDynamicStatus(status) {
        this.setState({ dynamicStatus: status });
    }
    /**
     * Handle binning progress events from backend.
     * Requirements: 8.1, 8.2
     */
    onBinningProgress(progress) {
        this.setState({ binningProgress: progress });
    }
    /**
     * Handle binning complete events from backend.
     * Requirements: 8.3, 8.4
     */
    onBinningComplete(result) {
        this.setState({
            binningResult: result,
            binningProgress: null,
            isBinning: false,
        });
    }
    /**
     * Handle binning error events from backend.
     * Requirements: 8.3
     */
    onBinningError(error) {
        this.setState({
            isBinning: false,
            binningProgress: null,
        });
        // Error will be shown in UI via result or status
    }
    /**
     * Handle profile change events from backend.
     * Requirements: 4.4
     *
     * Updates state with active profile name and shows notification.
     */
    onProfileChanged(data) {
        // Update active profile in state
        if (data.app_id !== null) {
            // Find the profile in our local state
            const profile = this.state.gameProfiles?.find(p => p.app_id === data.app_id);
            if (profile) {
                this.setState({ activeProfile: profile });
            }
        }
        else {
            // Global default - clear active profile
            this.setState({ activeProfile: null });
        }
        // Show notification via Decky toast (if available)
        if (typeof DFL !== 'undefined' && DFL.Toaster) {
            DFL.Toaster.toast({
                title: "Profile Switched",
                body: `Now using: ${data.profile_name}`,
                duration: 3000,
            });
        }
    }
    /**
     * Handle telemetry sample events from backend.
     * Requirements: 2.1, 2.2, 2.3, 2.4
     *
     * Feature: decktune-3.1-reliability-ux
     * Adds new telemetry sample to state, maintaining 60-second window.
     */
    onTelemetrySample(sample) {
        const now = Date.now() / 1000;
        const cutoffTime = now - 60;
        // Filter old samples and add new one
        const currentSamples = this.state.telemetrySamples || [];
        const filteredSamples = currentSamples.filter(s => s.timestamp >= cutoffTime);
        const newSamples = [...filteredSamples, sample].slice(-60);
        this.setState({ telemetrySamples: newSamples });
    }
    /**
     * Handle app lifetime notifications from Steam.
     * Requirements: 5.2, 5.3
     *
     * Detects game launch via SteamClient and applies preset with timeout.
     * Shows status: "Using preset for <GameName>"
     */
    async onAppLifetimeNotification(app) {
        const gameId = app.unAppID;
        const gameInfo = appStore.GetAppOverviewByGameID(gameId);
        if (app.bRunning) {
            // Game is starting
            if (!this.state.settings.isRunAutomatically)
                return;
            await this.handleMainRunningApp(gameId, gameInfo.display_name);
        }
        else {
            // Game is closing - revert to global settings
            this.setState({
                runningAppName: null,
                runningAppId: null,
                cores: this.state.globalCores,
                currentPreset: null,
            });
            if (this.state.settings.isGlobal && this.state.status !== "disabled") {
                await this.applyUndervolt(this.state.globalCores);
                this.setState({ status: "Global" });
            }
            else {
                await this.disableUndervolt();
            }
        }
    }
    /**
     * Handle resume from suspend.
     */
    async onResumeFromSuspend() {
        if (this.state.status === "enabled" || this.state.status.startsWith("Using preset for")) {
            await this.applyUndervolt(this.state.cores, 5);
        }
    }
    /**
     * Handle main running app detection.
     * Requirements: 5.2, 5.3
     *
     * Applies preset for the running game and updates status.
     */
    async handleMainRunningApp(id, label) {
        if (DFL.Router.MainRunningApp || (id && label)) {
            const appName = label || DFL.Router.MainRunningApp?.display_name || null;
            const appId = id || Number(DFL.Router.MainRunningApp?.appid) || null;
            this.setState({
                runningAppName: appName,
                runningAppId: appId,
            });
            await this.applyUndervoltBasedOnPreset(appId, appName);
        }
        else {
            this.setState({ cores: this.state.globalCores });
        }
    }
    /**
     * Apply undervolt based on current preset.
     * Requirements: 5.2, 5.3
     *
     * Finds preset for the running game and applies it with timeout.
     * Updates status to "Using preset for <GameName>" or "Global".
     */
    async applyUndervoltBasedOnPreset(appId, appName) {
        const targetAppId = appId ?? this.state.runningAppId;
        const targetAppName = appName ?? this.state.runningAppName;
        const preset = this.state.presets.find((p) => p.app_id === targetAppId);
        if (preset) {
            // Found a preset for this game
            this.setState({
                cores: preset.value,
                currentPreset: preset,
            });
            const timeout = preset.use_timeout ? preset.timeout : 0;
            await this.applyUndervolt(preset.value, timeout);
            // Update status to show which preset is being used (Requirement 5.3)
            const statusString = `Using preset for ${preset.label || targetAppName || 'Unknown'}`;
            this.setState({ status: statusString });
        }
        else if (this.state.settings.isGlobal) {
            // No preset, but global mode is enabled - use global values
            this.setState({
                cores: this.state.globalCores,
                currentPreset: null,
            });
            await this.applyUndervolt(this.state.globalCores);
            this.setState({ status: "Global" });
        }
        else {
            // No preset and global mode disabled
            this.setState({
                currentPreset: null,
                status: "Disabled",
            });
        }
    }
    // ==================== Undervolt Control ====================
    /**
     * Apply undervolt values.
     */
    async applyUndervolt(core_values, timeout = 0) {
        this.setState({ cores: core_values });
        await call("apply_undervolt", core_values, timeout);
    }
    /**
     * Disable undervolt (reset to 0).
     */
    async disableUndervolt() {
        await call("disable_undervolt");
    }
    /**
     * Panic disable - emergency reset.
     */
    async panicDisable() {
        await call("panic_disable");
        this.setState({
            status: "disabled",
            isAutotuning: false,
            autotuneProgress: null,
        });
    }
    // ==================== Dynamic Mode ====================
    /**
     * Enable gymdeck dynamic mode.
     */
    async enableGymdeck() {
        await call("start_gymdeck", this.state.dynamicSettings);
        this.setState({ gymdeckRunning: true, status: "DYNAMIC RUNNING" });
    }
    /**
     * Disable gymdeck dynamic mode.
     */
    async disableGymdeck() {
        await call("stop_gymdeck");
        this.setState({ gymdeckRunning: false, status: "disabled", dynamicStatus: null });
    }
    /**
     * Get current dynamic mode status.
     * Requirements: 15.1
     */
    async getDynamicStatus() {
        const result = await call("get_dynamic_status");
        if (result.running && result.load) {
            const status = {
                running: result.running,
                load: result.load,
                values: result.values,
                strategy: result.strategy,
                uptime_ms: result.uptime_ms,
                error: result.error,
            };
            this.setState({ dynamicStatus: status });
            return status;
        }
        this.setState({ dynamicStatus: null });
        return null;
    }
    // ==================== Autotune Methods ====================
    // Requirements: Frontend integration
    /**
     * Start autotune process.
     * @param mode - "quick" or "thorough"
     */
    async startAutotune(mode = "quick") {
        const result = (await call("start_autotune", mode));
        if (result.success) {
            this.setState({
                isAutotuning: true,
                autotuneProgress: null,
                autotuneResult: null,
            });
        }
        return result;
    }
    /**
     * Stop running autotune.
     */
    async stopAutotune() {
        const result = (await call("stop_autotune"));
        if (result.success) {
            this.setState({
                isAutotuning: false,
                autotuneProgress: null,
            });
        }
        return result;
    }
    // ==================== Binning Methods ====================
    // Requirements: 8.1, 8.2, 8.3, 8.4, 10.1
    /**
     * Start silicon binning process.
     * Requirements: 8.1
     *
     * @param config - Optional binning configuration
     * @returns Promise with success status
     */
    async startBinning(config) {
        const result = (await call("start_binning", config || {}));
        if (result.success) {
            this.setState({
                isBinning: true,
                binningProgress: null,
                binningResult: null,
            });
        }
        return result;
    }
    /**
     * Stop running binning process.
     * Requirements: 8.1
     *
     * @returns Promise with success status
     */
    async stopBinning() {
        const result = (await call("stop_binning"));
        if (result.success) {
            this.setState({
                isBinning: false,
                binningProgress: null,
            });
        }
        return result;
    }
    /**
     * Get current binning status.
     * Requirements: 8.1
     *
     * @returns Current binning state or null
     */
    async getBinningStatus() {
        return (await call("get_binning_status"));
    }
    /**
     * Get binning configuration.
     * Requirements: 10.1
     *
     * @returns Current binning configuration
     */
    async getBinningConfig() {
        const config = (await call("get_binning_config"));
        this.setState({ binningConfig: config });
        return config;
    }
    /**
     * Update binning configuration.
     * Requirements: 10.1, 10.2, 10.3, 10.4
     *
     * @param config - Partial configuration to update
     * @returns Promise with success status
     */
    async updateBinningConfig(config) {
        const result = (await call("update_binning_config", config));
        if (result.success) {
            // Refresh config from backend
            await this.getBinningConfig();
        }
        return result;
    }
    /**
     * Tune for current game - run autotune and save as game preset.
     * Requirements: 5.4
     *
     * @param mode - "quick" or "thorough" autotune mode
     * @returns Promise with success status and the created preset
     */
    async tuneForCurrentGame(mode = "quick") {
        // Check if a game is currently running
        if (!this.state.runningAppId || !this.state.runningAppName) {
            return { success: false, error: "No game is currently running" };
        }
        const appId = this.state.runningAppId;
        const appName = this.state.runningAppName;
        // Start autotune
        const startResult = await this.startAutotune(mode);
        if (!startResult.success) {
            return { success: false, error: startResult.error };
        }
        // Wait for autotune to complete by watching state changes
        return new Promise((resolve) => {
            const checkComplete = () => {
                const state = this.getState();
                if (state.autotuneResult) {
                    // Autotune completed - save as preset
                    const result = state.autotuneResult;
                    if (result.stable) {
                        // Create and save preset for this game
                        const preset = {
                            app_id: appId,
                            label: appName,
                            value: result.cores,
                            timeout: 0,
                            use_timeout: false,
                            created_at: new Date().toISOString(),
                            tested: true, // Marked as tested since autotune validates stability
                        };
                        // Save the preset
                        this.saveAndApply(result.cores, true, preset).then(() => {
                            resolve({ success: true, preset });
                        }).catch((error) => {
                            resolve({ success: false, error: String(error) });
                        });
                    }
                    else {
                        resolve({
                            success: false,
                            error: "Autotune did not find stable values for all cores"
                        });
                    }
                    // Remove listener
                    this.removeListener("state_change", checkComplete);
                }
                else if (!state.isAutotuning && !state.autotuneResult) {
                    // Autotune was cancelled or failed
                    resolve({ success: false, error: "Autotune was cancelled or failed" });
                    this.removeListener("state_change", checkComplete);
                }
            };
            // Listen for state changes
            this.on("state_change", checkComplete);
        });
    }
    // ==================== Test Methods ====================
    // Requirements: Frontend integration
    /**
     * Check availability of required stress test binaries.
     * Call this on mount to show warnings if binaries are missing.
     *
     * @returns Object with binary status and list of missing binaries
     */
    async checkBinaries() {
        return (await call("check_binaries"));
    }
    /**
     * Run a specific stress test.
     * @param testName - Name of test (cpu_quick, cpu_long, ram_quick, ram_thorough, combo)
     */
    async runTest(testName) {
        this.setState({ currentTest: testName, isTestRunning: true });
        const result = (await call("run_test", testName));
        this.setState({ currentTest: null, isTestRunning: false });
        // Refresh test history after test completes
        await this.fetchTestHistory();
        return result;
    }
    /**
     * Get test history (last 10 results).
     */
    async getTestHistory() {
        return await this.fetchTestHistory();
    }
    // ==================== Diagnostics Methods ====================
    // Requirements: Frontend integration
    /**
     * Export diagnostics archive.
     * @returns Path to the created archive
     */
    async exportDiagnostics() {
        return (await call("export_diagnostics"));
    }
    /**
     * Get system information for diagnostics tab.
     */
    async getSystemInfo() {
        return await call("get_system_info");
    }
    // ==================== Preset Management ====================
    /**
     * Save and apply undervolt values.
     */
    async saveAndApply(core_values, use_as_preset, presetSettings) {
        if (use_as_preset) {
            const presetIndex = this.state.presets.findIndex((p) => p.app_id === this.state.runningAppId);
            let preset;
            const presets = [...this.state.presets];
            if (presetIndex !== -1) {
                presets[presetIndex] = {
                    ...presets[presetIndex],
                    ...presetSettings,
                    value: core_values,
                };
                preset = presets[presetIndex];
            }
            else {
                preset = {
                    ...presetSettings,
                    app_id: this.state.runningAppId,
                    value: core_values,
                    label: this.state.runningAppName || "",
                    timeout: presetSettings?.timeout || 0,
                    use_timeout: presetSettings?.use_timeout || false,
                };
                presets.push(preset);
            }
            this.setState({ presets, currentPreset: preset });
            await call("save_preset", preset);
        }
        else {
            this.setState({ cores: core_values, globalCores: core_values });
        }
        await this.applyUndervolt(core_values);
        if (!use_as_preset) {
            await call("save_setting", "cores", core_values);
        }
    }
    /**
     * Save settings.
     */
    async saveSettings(settings) {
        await call("save_settings", settings);
        this.setState({ settings });
    }
    /**
     * Save a single setting value.
     */
    async saveSetting(key, value) {
        await call("save_setting", key, value);
    }
    /**
     * Get a single setting value.
     */
    async getSetting(key) {
        return await call("get_setting", key);
    }
    /**
     * Reset configuration to defaults.
     */
    async resetConfig() {
        const result = (await call("reset_config"));
        this.setState({
            globalCores: result.cores,
            cores: result.cores,
            settings: result.settings,
            status: "disabled",
            currentPreset: null,
        });
        await this.disableUndervolt();
    }
    /**
     * Delete a preset.
     */
    async deletePreset(app_id) {
        const presets = [...this.state.presets];
        const presetIndex = presets.findIndex((p) => p.app_id === app_id);
        if (presetIndex !== -1) {
            presets.splice(presetIndex, 1);
        }
        this.setState({ presets });
        await call("delete_preset", app_id);
    }
    /**
     * Update a preset.
     */
    async updatePreset(preset) {
        const presets = [...this.state.presets];
        const presetIndex = presets.findIndex((p) => p.app_id === preset.app_id);
        if (presetIndex !== -1) {
            presets[presetIndex] = preset;
        }
        this.setState({ presets });
        await call("update_preset", preset);
        if (preset.app_id === this.state.runningAppId) {
            if (this.state.settings.isRunAutomatically) {
                await this.applyUndervolt(preset.value);
            }
        }
    }
    /**
     * Export all presets as JSON.
     */
    async exportPresets() {
        return (await call("export_presets"));
    }
    /**
     * Import presets from JSON.
     */
    async importPresets(jsonData) {
        const result = (await call("import_presets", jsonData));
        if (result.success) {
            // Refresh presets from backend
            await this.fetchConfig();
        }
        return result;
    }
    // ==================== Expert Mode Methods ====================
    // Requirements: 13.1-13.6
    /**
     * Enable Expert Overclocker Mode.
     * Requires explicit user confirmation of risks.
     *
     * @param confirmed - User has confirmed understanding of risks
     * @returns Object with success status and expert mode state
     */
    async enableExpertMode(confirmed = false) {
        const result = await call("enable_expert_mode", confirmed);
        if (result.success) {
            // Update state to reflect expert mode is active
            this.emit("expert_mode_changed", { enabled: true });
        }
        return result;
    }
    /**
     * Disable Expert Overclocker Mode.
     * Returns to safe platform limits.
     *
     * @returns Object with success status
     */
    async disableExpertMode() {
        const result = await call("disable_expert_mode");
        if (result.success) {
            // Update state to reflect expert mode is disabled
            this.emit("expert_mode_changed", { enabled: false });
        }
        return result;
    }
    /**
     * Get current Expert Mode status.
     *
     * @returns Object with expert mode state and limits
     */
    async getExpertModeStatus() {
        return await call("get_expert_mode_status");
    }
    // ==================== Profile Management Methods ====================
    // Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 9.1, 9.2
    /**
     * Create a new game profile.
     * Requirements: 3.1, 5.1
     *
     * @param profile - Profile data to create
     * @returns Promise with success status
     */
    async createProfile(profile) {
        const result = await call("create_profile", profile);
        if (result.success && result.profile) {
            // Add to local state
            const profiles = [...(this.state.gameProfiles || []), result.profile];
            this.setState({ gameProfiles: profiles });
        }
        return result;
    }
    /**
     * Get all game profiles.
     * Requirements: 3.2
     *
     * @returns Array of all game profiles
     */
    async getProfiles() {
        const profiles = await call("get_profiles");
        this.setState({ gameProfiles: profiles });
        return profiles;
    }
    /**
     * Update an existing game profile.
     * Requirements: 3.3
     *
     * @param appId - Steam AppID of the profile to update
     * @param updates - Partial profile data to update
     * @returns Promise with success status
     */
    async updateProfile(appId, updates) {
        const result = await call("update_profile", appId, updates);
        if (result.success && result.profile) {
            // Update local state
            const profiles = [...(this.state.gameProfiles || [])];
            const index = profiles.findIndex(p => p.app_id === appId);
            if (index !== -1) {
                profiles[index] = result.profile;
                this.setState({ gameProfiles: profiles });
            }
        }
        return result;
    }
    /**
     * Delete a game profile.
     * Requirements: 3.4
     *
     * @param appId - Steam AppID of the profile to delete
     * @returns Promise with success status
     */
    async deleteProfile(appId) {
        const result = await call("delete_profile", appId);
        if (result.success) {
            // Remove from local state
            const profiles = (this.state.gameProfiles || []).filter(p => p.app_id !== appId);
            this.setState({ gameProfiles: profiles });
            // If this was the active profile, clear it
            if (this.state.activeProfile?.app_id === appId) {
                this.setState({ activeProfile: null });
            }
        }
        return result;
    }
    /**
     * Create a profile for the currently running game.
     * Requirements: 5.1, 5.2, 5.3, 5.4
     *
     * Automatically populates app_id and game name from the running game.
     * Captures current undervolt and dynamic mode settings.
     *
     * @returns Promise with success status and created profile
     */
    async createProfileForCurrentGame() {
        if (!this.state.runningAppId || !this.state.runningAppName) {
            return {
                success: false,
                error: "No game is currently running"
            };
        }
        const result = await call("create_profile_for_current_game");
        if (result.success && result.profile) {
            // Add to local state
            const profiles = [...(this.state.gameProfiles || []), result.profile];
            this.setState({
                gameProfiles: profiles,
                activeProfile: result.profile
            });
        }
        return result;
    }
    /**
     * Export all game profiles as JSON.
     * Requirements: 9.1
     *
     * @returns JSON string containing all profiles
     */
    async exportGameProfiles() {
        return await call("export_profiles");
    }
    /**
     * Import game profiles from JSON.
     * Requirements: 9.2, 9.3, 9.4
     *
     * @param jsonData - JSON string containing profiles to import
     * @param mergeStrategy - How to handle conflicts: "skip", "overwrite", "rename"
     * @returns Promise with import result
     */
    async importGameProfiles(jsonData, mergeStrategy = "skip") {
        const result = await call("import_profiles", jsonData, mergeStrategy);
        if (result.success) {
            // Refresh profiles from backend
            await this.getProfiles();
        }
        return result;
    }
    // ==================== Benchmark Methods ====================
    // Requirements: 7.1, 7.3, 7.5
    /**
     * Run a 10-second benchmark using stress-ng.
     * Requirements: 7.1, 7.4
     *
     * Blocks other operations during execution.
     *
     * @returns Promise with benchmark result
     */
    async runBenchmark() {
        // Set running state before starting
        this.setState({ isBenchmarkRunning: true });
        const response = await call("run_benchmark");
        if (response.success && response.result) {
            // Update state with new result
            this.setState({
                isBenchmarkRunning: false,
                lastBenchmarkResult: response.result,
            });
            // Refresh benchmark history
            await this.getBenchmarkHistory();
        }
        else {
            // Clear running state on error
            this.setState({ isBenchmarkRunning: false });
        }
        return response;
    }
    /**
     * Get benchmark history (last 20 results).
     * Requirements: 7.5
     *
     * @returns Array of benchmark results with comparisons
     */
    async getBenchmarkHistory() {
        const history = await call("get_benchmark_history");
        this.setState({ benchmarkHistory: history });
        return history;
    }
    // ==================== Session History Methods ====================
    // Requirements: 8.4, 8.5, 8.6
    /**
     * Get session history.
     * Requirements: 8.4
     *
     * @param limit - Maximum number of sessions to return (default 30)
     * @returns Array of sessions, most recent first
     */
    async getSessionHistory(limit = 30) {
        const sessions = await call("get_session_history", limit);
        return sessions || [];
    }
    /**
     * Get a specific session by ID.
     * Requirements: 8.5
     *
     * @param sessionId - UUID of the session to retrieve
     * @returns Session if found, null otherwise
     */
    async getSession(sessionId) {
        return await call("get_session", sessionId);
    }
    /**
     * Compare two sessions and return metric differences.
     * Requirements: 8.6
     *
     * @param id1 - ID of first session
     * @param id2 - ID of second session
     * @returns Comparison result with diff values
     */
    async compareSessions(id1, id2) {
        return await call("compare_sessions", id1, id2);
    }
    // ==================== Fan Control Methods ====================
    /**
     * Get current fan control configuration.
     *
     * @returns Fan configuration with enabled status and curve points
     */
    async getFanConfig() {
        return await call("get_fan_config");
    }
    /**
     * Set fan control configuration.
     *
     * @param config - Fan configuration to apply
     * @returns Success status
     */
    async setFanConfig(config) {
        return await call("set_fan_config", config);
    }
    /**
     * Get current fan status (RPM, temperature).
     *
     * @returns Current fan status
     */
    async getFanStatus() {
        return await call("get_fan_status");
    }
    // ==================== Server Events ====================
    /**
     * Handle server events.
     */
    handleServerEvent({ type, data }) {
        switch (type) {
            case "update_status":
                this.setState({ status: data });
                break;
            case "tuning_progress":
                this.onTuningProgress(data);
                break;
            case "tuning_complete":
                this.onTuningComplete(data);
                break;
            case "test_complete":
                this.onTestComplete(data);
                break;
        }
    }
    // ==================== Cleanup ====================
    /**
     * Cleanup and unregister listeners.
     */
    destroy() {
        this.registeredListeners.forEach((listener) => {
            listener.unregister();
        });
        removeEventListener("tuning_progress", this.onTuningProgress.bind(this));
        removeEventListener("tuning_complete", this.onTuningComplete.bind(this));
        removeEventListener("test_complete", this.onTestComplete.bind(this));
        removeEventListener("update_status", this.onStatusUpdate.bind(this));
        removeEventListener("dynamic_status", this.onDynamicStatus.bind(this));
        removeEventListener("binning_progress", this.onBinningProgress.bind(this));
        removeEventListener("binning_complete", this.onBinningComplete.bind(this));
        removeEventListener("binning_error", this.onBinningError.bind(this));
        removeEventListener("profile_changed", this.onProfileChanged.bind(this));
        removeEventListener("telemetry_sample", this.onTelemetrySample.bind(this));
    }
}

/**
 * React context for DeckTune state management.
 *
 * Feature: decktune, Frontend State Management
 * Requirements: State management
 *
 * Provides state properties:
 * - autotuneProgress, autotuneResult
 * - testHistory, currentTest
 * - platformInfo
 */

/**
 * Initial state with all required properties.
 * Requirements: State management
 */
const initialState = {
    // Core state
    cores: [5, 5, 5, 5],
    globalCores: [],
    status: "disabled",
    // Platform info
    platformInfo: null,
    // Running app info
    runningAppName: null,
    runningAppId: null,
    // Presets
    presets: [],
    currentPreset: null,
    // Game Profiles (new in v3.0)
    gameProfiles: [],
    activeProfile: null,
    // Settings
    settings: {
        isGlobal: false,
        runAtStartup: false,
        isRunAutomatically: false,
        timeoutApply: 15,
    },
    dynamicSettings: {
        strategy: "DEFAULT",
        sample_interval: 50000,
        cores: [
            { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
            { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
            { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
            { maximum_value: 100, minimum_value: 0, threshold: 0, manual_points: [] },
        ],
    },
    // Dynamic mode
    gymdeckRunning: false,
    isDynamic: false,
    dynamicStatus: null,
    // Autotune state (new properties)
    autotuneProgress: null,
    autotuneResult: null,
    isAutotuning: false,
    // Binning state
    binningProgress: null,
    binningResult: null,
    isBinning: false,
    binningConfig: null,
    // Test state (new properties)
    testHistory: [],
    currentTest: null,
    isTestRunning: false,
    // Benchmark state (new in v3.0)
    benchmarkHistory: [],
    isBenchmarkRunning: false,
    lastBenchmarkResult: null,
    // Telemetry state (new in v3.1)
    // Requirements: 2.1, 2.2, 2.3, 2.4
    telemetrySamples: [],
    // Binary availability
    missingBinaries: [],
};
// Create context with null default
const DeckTuneContext = SP_REACT.createContext(null);
/**
 * Provider component for DeckTune context.
 */
const DeckTuneProvider = ({ children }) => {
    const api = getApiInstance(initialState);
    const [state, setState] = SP_REACT.useState(api.getState());
    SP_REACT.useEffect(() => {
        const handleStateChange = (newState) => {
            setState((prev) => ({ ...prev, ...newState }));
        };
        api.on("state_change", handleStateChange);
        return () => {
            api.removeListener("state_change", handleStateChange);
        };
    }, [api]);
    const contextValue = {
        state,
        api,
        // Convenience accessors for new state properties
        autotuneProgress: state.autotuneProgress,
        autotuneResult: state.autotuneResult,
        testHistory: state.testHistory,
        currentTest: state.currentTest,
        platformInfo: state.platformInfo,
        isAutotuning: state.isAutotuning,
        isTestRunning: state.isTestRunning,
    };
    return (window.SP_REACT.createElement(DeckTuneContext.Provider, { value: contextValue }, children));
};
/**
 * Hook to access DeckTune context.
 * @throws Error if used outside of DeckTuneProvider
 */
const useDeckTune = () => {
    const context = SP_REACT.useContext(DeckTuneContext);
    if (!context) {
        throw new Error("useDeckTune must be used within a DeckTuneProvider");
    }
    return context;
};
/**
 * Hook to access test state.
 */
const useTests = () => {
    const { testHistory, currentTest, isTestRunning, api } = useDeckTune();
    return {
        history: testHistory,
        currentTest,
        isRunning: isTestRunning,
        runTest: (testName) => api.runTest(testName),
        getHistory: () => api.getTestHistory(),
    };
};
/**
 * Hook to access platform info.
 */
const usePlatformInfo = () => {
    const { platformInfo, api } = useDeckTune();
    return {
        info: platformInfo,
        refresh: () => api.fetchPlatformInfo(),
    };
};
/**
 * Hook to check binary availability.
 * Returns missing binaries list and a function to refresh.
 */
const useBinaries = () => {
    const { state, api } = useDeckTune();
    const checkBinaries = async () => {
        const result = await api.checkBinaries();
        if (result.success) {
            api.setState({ missingBinaries: result.missing });
        }
        return result;
    };
    return {
        missing: state.missingBinaries,
        hasMissing: state.missingBinaries.length > 0,
        check: checkBinaries,
    };
};
/**
 * Hook to access profile management.
 * Requirements: 3.1, 3.2, 3.3, 3.4, 5.1
 */
const useProfiles = () => {
    const { state, api } = useDeckTune();
    return {
        profiles: state.gameProfiles || [],
        activeProfile: state.activeProfile,
        runningAppId: state.runningAppId,
        runningAppName: state.runningAppName,
        createProfile: (profile) => api.createProfile(profile),
        getProfiles: () => api.getProfiles(),
        updateProfile: (appId, updates) => api.updateProfile(appId, updates),
        deleteProfile: (appId) => api.deleteProfile(appId),
        createProfileForCurrentGame: () => api.createProfileForCurrentGame(),
        exportProfiles: () => api.exportGameProfiles(),
        importProfiles: (jsonData, strategy) => api.importGameProfiles(jsonData, strategy),
    };
};

/**
 * Settings Context for DeckTune persistent settings management.
 *
 * Feature: ui-refactor-settings
 * Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
 *
 * Provides centralized settings management with backend persistence:
 * - expertMode: Enable/disable dangerous limits
 * - applyOnStartup: Auto-apply last profile on boot
 * - gameOnlyMode: Apply undervolt only during games
 * - lastActiveProfile: Track last applied profile
 */

/**
 * Default settings values.
 */
const DEFAULT_SETTINGS = {
    expertMode: false,
    applyOnStartup: false,
    gameOnlyMode: false,
    lastActiveProfile: null,
    isLoaded: false,
};
// Create context with null default
const SettingsContext = SP_REACT.createContext(null);
/**
 * Provider component for Settings context.
 *
 * Loads settings from backend on mount and provides methods
 * to update settings with immediate persistence.
 *
 * Feature: ui-refactor-settings
 * Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
 */
const SettingsProvider = ({ children }) => {
    const [settings, setSettings] = SP_REACT.useState(DEFAULT_SETTINGS);
    /**
     * Load all settings from backend storage.
     *
     * Falls back to default values on error and displays user-friendly message.
     *
     * Validates: Requirements 3.2, 3.5, 10.4
     */
    const loadSettings = SP_REACT.useCallback(async () => {
        try {
            const response = await call("load_all_settings");
            if (response.success) {
                setSettings({
                    expertMode: response.settings.expert_mode ?? false,
                    applyOnStartup: response.settings.apply_on_startup ?? false,
                    gameOnlyMode: response.settings.game_only_mode ?? false,
                    lastActiveProfile: response.settings.last_active_profile ?? null,
                    isLoaded: true,
                });
                console.log("[SettingsContext] Settings loaded:", response.settings);
            }
            else {
                console.error("[SettingsContext] Failed to load settings:", response.error);
                // Fall back to defaults
                setSettings({ ...DEFAULT_SETTINGS, isLoaded: true });
                // TODO: Display user-friendly error toast when toast system is available
            }
        }
        catch (error) {
            console.error("[SettingsContext] Error loading settings:", error);
            // Fall back to defaults on any error
            setSettings({ ...DEFAULT_SETTINGS, isLoaded: true });
            // TODO: Display user-friendly error toast when toast system is available
        }
    }, []);
    /**
     * Set Expert Mode setting.
     *
     * Calls enable_expert_mode or disable_expert_mode RPC methods
     * with proper confirmation handling.
     *
     * Validates: Requirements 2.3, 2.4, 3.1, 3.5, 10.3
     */
    const setExpertMode = SP_REACT.useCallback(async (value) => {
        try {
            let response;
            if (value) {
                // Enabling - requires confirmation
                response = await call("enable_expert_mode", true);
            }
            else {
                // Disabling - no confirmation needed
                response = await call("disable_expert_mode");
            }
            if (response.success) {
                setSettings((prev) => ({ ...prev, expertMode: value }));
                console.log("[SettingsContext] Expert Mode updated:", value);
            }
            else {
                console.error("[SettingsContext] Failed to save Expert Mode:", response.error);
                // TODO: Display user-friendly error toast when toast system is available
                // For now, keep UI state unchanged
            }
        }
        catch (error) {
            console.error("[SettingsContext] Error saving Expert Mode:", error);
            // TODO: Display user-friendly error toast when toast system is available
        }
    }, []);
    /**
     * Set Apply on Startup setting.
     *
     * Retries once on failure and displays user-friendly error message.
     *
     * Validates: Requirements 4.1, 4.2, 3.1, 3.5, 10.3
     */
    const setApplyOnStartup = SP_REACT.useCallback(async (value) => {
        try {
            const response = await call("save_setting", "apply_on_startup", value);
            if (response.success) {
                setSettings((prev) => ({ ...prev, applyOnStartup: value }));
                console.log("[SettingsContext] Apply on Startup updated:", value);
            }
            else {
                console.error("[SettingsContext] Failed to save Apply on Startup:", response.error);
                // TODO: Display user-friendly error toast when toast system is available
            }
        }
        catch (error) {
            console.error("[SettingsContext] Error saving Apply on Startup:", error);
            // TODO: Display user-friendly error toast when toast system is available
        }
    }, []);
    /**
     * Set Game Only Mode setting.
     *
     * Retries once on failure and displays user-friendly error message.
     *
     * Validates: Requirements 5.1, 5.2, 3.1, 3.5, 10.3
     */
    const setGameOnlyMode = SP_REACT.useCallback(async (value) => {
        try {
            // Save the setting first
            const response = await call("save_setting", "game_only_mode", value);
            if (response.success) {
                // Enable or disable Game Only Mode on the backend
                if (value) {
                    const enableResponse = await call("enable_game_only_mode");
                    if (!enableResponse.success) {
                        console.error("[SettingsContext] Failed to enable Game Only Mode on backend:", enableResponse.error);
                        // TODO: Display user-friendly error toast when toast system is available
                        return;
                    }
                }
                else {
                    const disableResponse = await call("disable_game_only_mode");
                    if (!disableResponse.success) {
                        console.error("[SettingsContext] Failed to disable Game Only Mode on backend:", disableResponse.error);
                        // TODO: Display user-friendly error toast when toast system is available
                        return;
                    }
                }
                setSettings((prev) => ({ ...prev, gameOnlyMode: value }));
                console.log("[SettingsContext] Game Only Mode updated:", value);
            }
            else {
                console.error("[SettingsContext] Failed to save Game Only Mode:", response.error);
                // TODO: Display user-friendly error toast when toast system is available
            }
        }
        catch (error) {
            console.error("[SettingsContext] Error saving Game Only Mode:", error);
            // TODO: Display user-friendly error toast when toast system is available
        }
    }, []);
    /**
     * Set last active profile.
     *
     * Retries once on failure and displays user-friendly error message.
     *
     * Validates: Requirements 4.2, 3.1, 3.5, 10.3
     */
    const setLastActiveProfile = SP_REACT.useCallback(async (profile) => {
        try {
            const response = await call("save_setting", "last_active_profile", profile);
            if (response.success) {
                setSettings((prev) => ({ ...prev, lastActiveProfile: profile }));
                console.log("[SettingsContext] Last Active Profile updated:", profile);
            }
            else {
                console.error("[SettingsContext] Failed to save Last Active Profile:", response.error);
                // TODO: Display user-friendly error toast when toast system is available
            }
        }
        catch (error) {
            console.error("[SettingsContext] Error saving Last Active Profile:", error);
            // TODO: Display user-friendly error toast when toast system is available
        }
    }, []);
    // Load settings on mount  // Load settings on mount
    SP_REACT.useEffect(() => {
        loadSettings();
    }, [loadSettings]);
    const contextValue = {
        settings,
        setExpertMode,
        setApplyOnStartup,
        setGameOnlyMode,
        setLastActiveProfile,
        loadSettings,
    };
    return (window.SP_REACT.createElement(SettingsContext.Provider, { value: contextValue }, children));
};
/**
 * Hook to access Settings context.
 *
 * @throws Error if used outside of SettingsProvider
 *
 * Feature: ui-refactor-settings
 * Validates: Requirements 10.1, 10.2
 */
const useSettings = () => {
    const context = SP_REACT.useContext(SettingsContext);
    if (!context) {
        throw new Error("useSettings must be used within a SettingsProvider");
    }
    return context;
};

/**
 * Wizard Mode Context for DeckTune.
 *
 * Feature: Wizard Mode Refactoring
 *
 * Provides state management and API integration for the wizard workflow:
 * - Configuration and session management
 * - Real-time progress tracking
 * - Results history and visualization
 * - Crash recovery detection
 */

const WizardContext = SP_REACT.createContext(undefined);
// ==================== Provider ====================
const WizardProvider = ({ children }) => {
    const [isRunning, setIsRunning] = SP_REACT.useState(false);
    const [progress, setProgress] = SP_REACT.useState(null);
    const [result, setResult] = SP_REACT.useState(null);
    const [resultsHistory, setResultsHistory] = SP_REACT.useState([]);
    const [dirtyExit, setDirtyExit] = SP_REACT.useState(null);
    const [error, setError] = SP_REACT.useState(null);
    // ==================== Server Event Listener ====================
    SP_REACT.useEffect(() => {
        const handleServerEvent = (data) => {
            if (!data || !data.type)
                return;
            switch (data.type) {
                case "wizard_progress":
                    setProgress(data.data);
                    setIsRunning(true);
                    setError(null);
                    break;
                case "wizard_complete":
                    setResult(data.data);
                    setIsRunning(false);
                    setProgress(null);
                    loadResultsHistory();
                    break;
                case "wizard_error":
                    setError(data.data?.error || "Unknown wizard error");
                    setIsRunning(false);
                    setProgress(null);
                    break;
            }
        };
        addEventListener("server_event", handleServerEvent);
        return () => removeEventListener("server_event", handleServerEvent);
    }, []);
    // ==================== Actions ====================
    const startWizard = SP_REACT.useCallback(async (config) => {
        try {
            setError(null);
            setResult(null);
            const response = await call("start_wizard", config);
            if (response?.success) {
                setIsRunning(true);
            }
            else {
                const errorMsg = response?.error || "Failed to start wizard";
                setError(errorMsg);
                throw new Error(errorMsg);
            }
        }
        catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Failed to start wizard";
            setError(errorMsg);
            throw err;
        }
    }, []);
    const cancelWizard = SP_REACT.useCallback(async () => {
        try {
            const response = await call("cancel_wizard");
            if (response?.success) {
                setIsRunning(false);
                setProgress(null);
            }
            else {
                const errorMsg = response?.error || "Failed to cancel wizard";
                setError(errorMsg);
            }
        }
        catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Failed to cancel wizard";
            setError(errorMsg);
        }
    }, []);
    const applyResult = SP_REACT.useCallback(async (resultId, saveAsPreset, applyOnStartup = false, gameOnlyMode = false) => {
        try {
            setError(null);
            const response = await call("apply_wizard_result", resultId, saveAsPreset, applyOnStartup, gameOnlyMode);
            if (!response?.success) {
                const errorMsg = response?.error || "Failed to apply wizard result";
                setError(errorMsg);
                throw new Error(errorMsg);
            }
        }
        catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Failed to apply wizard result";
            setError(errorMsg);
            throw err;
        }
    }, []);
    const checkDirtyExit = SP_REACT.useCallback(async () => {
        try {
            const response = await call("check_wizard_dirty_exit");
            if (response?.dirty_exit) {
                setDirtyExit({
                    detected: true,
                    crashInfo: response.crash_info || null
                });
            }
            else {
                setDirtyExit({ detected: false, crashInfo: null });
            }
        }
        catch (err) {
            console.error("Failed to check wizard dirty exit:", err);
            setDirtyExit({ detected: false, crashInfo: null });
        }
    }, []);
    const loadResultsHistory = SP_REACT.useCallback(async () => {
        try {
            const response = await call("get_wizard_results_history");
            if (Array.isArray(response)) {
                setResultsHistory(response);
            }
        }
        catch (err) {
            console.error("Failed to load wizard results history:", err);
        }
    }, []);
    const clearError = SP_REACT.useCallback(() => {
        setError(null);
    }, []);
    // ==================== Initialization ====================
    SP_REACT.useEffect(() => {
        checkDirtyExit();
        loadResultsHistory();
    }, [checkDirtyExit, loadResultsHistory]);
    // ==================== Context Value ====================
    const value = {
        isRunning,
        progress,
        result,
        resultsHistory,
        dirtyExit,
        error,
        startWizard,
        cancelWizard,
        applyResult,
        checkDirtyExit,
        loadResultsHistory,
        clearError
    };
    return (window.SP_REACT.createElement(WizardContext.Provider, { value: value }, children));
};
// ==================== Hook ====================
const useWizard = () => {
    const context = SP_REACT.useContext(WizardContext);
    if (!context) {
        throw new Error("useWizard must be used within WizardProvider");
    }
    return context;
};

/**
 * Refactored WizardMode component for DeckTune.
 *
 * Feature: Wizard Mode Refactoring
 *
 * Complete redesign with:
 * - Configuration screen with aggressiveness/duration settings
 * - Real-time progress with ETA/OTA/heartbeat
 * - Results screen with curve visualization and chip grading
 * - Crash recovery modal
 * - Results history browser
 */

// ==================== Panic Disable Button ====================
const PanicDisableButton$1 = () => {
    const { api } = useDeckTune();
    const [isPanicking, setIsPanicking] = SP_REACT.useState(false);
    const handlePanicDisable = async () => {
        setIsPanicking(true);
        try {
            await api.panicDisable();
        }
        finally {
            setIsPanicking(false);
        }
    };
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handlePanicDisable, disabled: isPanicking, style: {
                backgroundColor: "#b71c1c",
                borderRadius: "4px",
                minHeight: "30px",
                padding: "4px 6px",
            } },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "4px",
                    color: "#fff",
                    fontWeight: "bold",
                    fontSize: "11px",
                } }, isPanicking ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 10 }),
                window.SP_REACT.createElement("span", null, "Disabling..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaExclamationTriangle, { size: 10 }),
                window.SP_REACT.createElement("span", null, "PANIC DISABLE"))))),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
// ==================== Crash Recovery Modal ====================
const CrashRecoveryModal = ({ crashInfo, onDismiss }) => {
    return (window.SP_REACT.createElement("div", { style: {
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
        } },
        window.SP_REACT.createElement("div", { style: {
                backgroundColor: "#1a1d24",
                borderRadius: "8px",
                padding: "20px",
                maxWidth: "400px",
                border: "2px solid #ff9800",
            } },
            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px" } },
                window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#ff9800", fontSize: "24px" } }),
                window.SP_REACT.createElement("h3", { style: { margin: 0, color: "#fff" } }, "Crash Detected")),
            window.SP_REACT.createElement("p", { style: { fontSize: "13px", color: "#ccc", marginBottom: "15px" } }, "The system crashed during wizard testing. This is normal when pushing limits."),
            window.SP_REACT.createElement("div", { style: { backgroundColor: "#2a2d34", padding: "10px", borderRadius: "4px", marginBottom: "15px" } },
                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginBottom: "5px" } }, "Crash Details:"),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#fff" } },
                    "Testing: ",
                    window.SP_REACT.createElement("strong", null,
                        crashInfo?.currentOffset,
                        "mV")),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#4caf50" } },
                    "Last Stable: ",
                    window.SP_REACT.createElement("strong", null,
                        crashInfo?.lastStable,
                        "mV"))),
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onDismiss },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" } },
                    window.SP_REACT.createElement(FaCheck, { size: 12 }),
                    window.SP_REACT.createElement("span", null, "Continue"))))));
};
// ==================== Configuration Screen ====================
const ConfigurationScreen = ({ onStart, platformInfo }) => {
    const [aggressiveness, setAggressiveness] = SP_REACT.useState("balanced");
    const [testDuration, setTestDuration] = SP_REACT.useState("short");
    const [isBenchmarking, setIsBenchmarking] = SP_REACT.useState(false);
    const [benchmarkResult, setBenchmarkResult] = SP_REACT.useState(null);
    const handleStart = () => {
        const config = {
            targetDomains: ["cpu"],
            aggressiveness,
            testDuration,
            safetyLimits: {
                cpu: platformInfo?.safe_limit || -100,
            },
        };
        onStart(config);
    };
    const handleRunBenchmark = async () => {
        setIsBenchmarking(true);
        setBenchmarkResult(null);
        try {
            const result = await call("run_wizard_benchmark", 10);
            if (result?.success) {
                setBenchmarkResult(result);
            }
        }
        catch (err) {
            console.error("Benchmark failed:", err);
        }
        finally {
            setIsBenchmarking(false);
        }
    };
    const getEstimatedTime = () => {
        const base = testDuration === "short" ? 5 : 15;
        const multiplier = aggressiveness === "safe" ? 2 : aggressiveness === "aggressive" ? 0.5 : 1;
        return Math.round(base * multiplier);
    };
    return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } },
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "13px", color: "#ccc", marginBottom: "10px" } }, "Automatically find the optimal undervolt for your chip through systematic testing.")),
        platformInfo && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", padding: "8px", backgroundColor: "#1a1d24", borderRadius: "4px" } },
                platformInfo.variant,
                " (",
                platformInfo.model,
                ") \u2022 Safety Limit: ",
                platformInfo.safe_limit,
                "mV"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Field, { label: "Aggressiveness" },
                window.SP_REACT.createElement(DFL.Dropdown, { rgOptions: [
                        { label: "Safe (2mV steps, +10mV margin)", data: "safe" },
                        { label: "Balanced (5mV steps, +5mV margin)", data: "balanced" },
                        { label: "Aggressive (10mV steps, +2mV margin)", data: "aggressive" },
                    ], selectedOption: aggressiveness, onChange: (option) => setAggressiveness(option.data) }))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Field, { label: "Test Duration" },
                window.SP_REACT.createElement(DFL.Dropdown, { rgOptions: [
                        { label: "Short (30s per test)", data: "short" },
                        { label: "Long (120s per test)", data: "long" },
                    ], selectedOption: testDuration, onChange: (option) => setTestDuration(option.data) }))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", textAlign: "center", padding: "5px" } },
                "Estimated time: ~",
                getEstimatedTime(),
                " minutes")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleRunBenchmark, disabled: isBenchmarking },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" } },
                    isBenchmarking ? window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 12 }) : window.SP_REACT.createElement(FaChartLine, { size: 12 }),
                    window.SP_REACT.createElement("span", null, isBenchmarking ? "Running..." : "Run Benchmark")))),
        isBenchmarking && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ProgressBarWithInfo, { label: "Running Benchmark", description: "Testing CPU performance...", nProgress: 50, sOperationText: "Please wait..." }))),
        benchmarkResult && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#4caf50", padding: "8px", backgroundColor: "#1a1d24", borderRadius: "4px" } },
                window.SP_REACT.createElement("div", null,
                    "Score: ",
                    benchmarkResult.score,
                    " ops/sec"),
                window.SP_REACT.createElement("div", null,
                    "Max Temp: ",
                    benchmarkResult.max_temp,
                    "\u00B0C"),
                window.SP_REACT.createElement("div", null,
                    "Max Freq: ",
                    benchmarkResult.max_freq,
                    " MHz")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleStart },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" } },
                    window.SP_REACT.createElement(FaPlay, { size: 12 }),
                    window.SP_REACT.createElement("span", null, "Start Wizard"))))));
};
// ==================== Progress Screen ====================
const ProgressScreen = ({ progress, onCancel }) => {
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    };
    const formatOTA = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };
    return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } },
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { textAlign: "center", marginBottom: "15px" } },
                window.SP_REACT.createElement(FaSpinner, { style: {
                        animation: "spin 1s linear infinite",
                        fontSize: "32px",
                        color: "#1a9fff",
                    } }))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ProgressBarWithInfo, { label: progress?.currentStage || "Initializing...", description: `Testing ${progress?.currentOffset}mV`, nProgress: progress?.progressPercent || 0, sOperationText: `ETA: ${formatTime(progress?.etaSeconds || 0)}` })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "11px",
                    color: "#8b929a",
                    padding: "8px",
                    backgroundColor: "#1a1d24",
                    borderRadius: "4px",
                } },
                window.SP_REACT.createElement("div", null,
                    window.SP_REACT.createElement("div", null,
                        "Elapsed: ",
                        formatOTA(progress?.otaSeconds || 0)),
                    window.SP_REACT.createElement("div", null,
                        "Iterations: ",
                        progress?.liveMetrics?.iterations || 0)),
                window.SP_REACT.createElement("div", { style: { textAlign: "right" } },
                    window.SP_REACT.createElement("div", null,
                        "Last Stable: ",
                        progress?.liveMetrics?.last_stable || 0,
                        "mV"),
                    window.SP_REACT.createElement("div", { style: { color: "#4caf50" } }, "\u25CF Active")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onCancel },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: "#f44336" } },
                    window.SP_REACT.createElement(FaStop, { size: 12 }),
                    window.SP_REACT.createElement("span", null, "Cancel"))))));
};
// ==================== Chip Grade Badge ====================
const ChipGradeBadge = ({ grade }) => {
    const getGradeConfig = () => {
        switch (grade) {
            case "Platinum":
                return { icon: FaTrophy, color: "#e5e4e2", glow: "#e5e4e2" };
            case "Gold":
                return { icon: FaMedal, color: "#ffd700", glow: "#ffd700" };
            case "Silver":
                return { icon: FaAward, color: "#c0c0c0", glow: "#c0c0c0" };
            default:
                return { icon: FaCertificate, color: "#cd7f32", glow: "#cd7f32" };
        }
    };
    const config = getGradeConfig();
    const Icon = config.icon;
    return (window.SP_REACT.createElement("div", { style: {
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
            padding: "15px",
            backgroundColor: "#1a1d24",
            borderRadius: "8px",
            border: `2px solid ${config.color}`,
            boxShadow: `0 0 15px ${config.glow}`,
        } },
        window.SP_REACT.createElement(Icon, { style: { fontSize: "32px", color: config.color } }),
        window.SP_REACT.createElement("div", null,
            window.SP_REACT.createElement("div", { style: { fontSize: "18px", fontWeight: "bold", color: config.color } }, grade),
            window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a" } }, "Chip Quality"))));
};
// ==================== Enhanced Interactive Curve Chart ====================
const EnhancedCurveChart = ({ data }) => {
    const [hoveredPoint, setHoveredPoint] = SP_REACT.useState(null);
    const [tooltipPos, setTooltipPos] = SP_REACT.useState({ x: 0, y: 0 });
    if (!data || data.length === 0)
        return null;
    const width = 320;
    const height = 180;
    const padding = { top: 20, right: 20, bottom: 40, left: 50 };
    const offsets = data.map((d) => d.offset);
    const temps = data.map((d) => d.temp);
    const xMin = Math.min(...offsets);
    const xMax = Math.max(...offsets);
    const yMin = 0;
    const yMax = Math.max(...temps, 100);
    const xScale = (x) => padding.left + ((x - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);
    const yScale = (y) => height - padding.bottom - ((y - yMin) / (yMax - yMin)) * (height - padding.top - padding.bottom);
    const handlePointHover = (index, event) => {
        setHoveredPoint(index);
        const rect = event.currentTarget.getBoundingClientRect();
        setTooltipPos({ x: event.clientX - rect.left, y: event.clientY - rect.top });
    };
    return (window.SP_REACT.createElement("div", { style: { position: "relative" } },
        window.SP_REACT.createElement("svg", { width: width, height: height, style: { backgroundColor: "#0d0f12", borderRadius: "4px" } },
            [0, 25, 50, 75, 100].map((temp) => (window.SP_REACT.createElement("g", { key: temp },
                window.SP_REACT.createElement("line", { x1: padding.left, y1: yScale(temp), x2: width - padding.right, y2: yScale(temp), stroke: "#2a2d34", strokeWidth: 1, strokeDasharray: "2,2" }),
                window.SP_REACT.createElement("text", { x: padding.left - 5, y: yScale(temp) + 3, fontSize: "9", fill: "#5a5d64", textAnchor: "end" },
                    temp,
                    "\u00B0C")))),
            window.SP_REACT.createElement("line", { x1: padding.left, y1: padding.top, x2: padding.left, y2: height - padding.bottom, stroke: "#3d4450", strokeWidth: 2 }),
            window.SP_REACT.createElement("line", { x1: padding.left, y1: height - padding.bottom, x2: width - padding.right, y2: height - padding.bottom, stroke: "#3d4450", strokeWidth: 2 }),
            window.SP_REACT.createElement("defs", null,
                window.SP_REACT.createElement("linearGradient", { id: "lineGradient", x1: "0%", y1: "0%", x2: "100%", y2: "0%" },
                    window.SP_REACT.createElement("stop", { offset: "0%", stopColor: "#4caf50" }),
                    window.SP_REACT.createElement("stop", { offset: "50%", stopColor: "#1a9fff" }),
                    window.SP_REACT.createElement("stop", { offset: "100%", stopColor: "#f44336" }))),
            window.SP_REACT.createElement("polyline", { points: data.map((d) => `${xScale(d.offset)},${yScale(d.temp)}`).join(" "), fill: "none", stroke: "url(#lineGradient)", strokeWidth: 2 }),
            data.map((point, i) => {
                const color = point.result === "pass" ? "#4caf50" :
                    point.result === "fail" ? "#ff9800" :
                        "#f44336";
                return (window.SP_REACT.createElement("g", { key: i },
                    window.SP_REACT.createElement("circle", { cx: xScale(point.offset), cy: yScale(point.temp), r: hoveredPoint === i ? 6 : 4, fill: color, stroke: "#fff", strokeWidth: hoveredPoint === i ? 2 : 1, style: { cursor: "pointer", transition: "all 0.2s" }, onMouseEnter: (e) => handlePointHover(i, e), onMouseLeave: () => setHoveredPoint(null) })));
            }),
            window.SP_REACT.createElement("text", { x: width / 2, y: height - 5, fontSize: "11", fill: "#8b929a", textAnchor: "middle", fontWeight: "bold" }, "Voltage Offset (mV)"),
            window.SP_REACT.createElement("text", { x: 15, y: height / 2, fontSize: "11", fill: "#8b929a", textAnchor: "middle", fontWeight: "bold", transform: `rotate(-90, 15, ${height / 2})` }, "Temperature (\u00B0C)"),
            window.SP_REACT.createElement("g", { transform: `translate(${width - 100}, 15)` },
                window.SP_REACT.createElement("circle", { cx: 0, cy: 0, r: 3, fill: "#4caf50" }),
                window.SP_REACT.createElement("text", { x: 8, y: 3, fontSize: "9", fill: "#8b929a" }, "Pass"),
                window.SP_REACT.createElement("circle", { cx: 0, cy: 12, r: 3, fill: "#ff9800" }),
                window.SP_REACT.createElement("text", { x: 8, y: 15, fontSize: "9", fill: "#8b929a" }, "Fail"),
                window.SP_REACT.createElement("circle", { cx: 0, cy: 24, r: 3, fill: "#f44336" }),
                window.SP_REACT.createElement("text", { x: 8, y: 27, fontSize: "9", fill: "#8b929a" }, "Crash"))),
        hoveredPoint !== null && (window.SP_REACT.createElement("div", { style: {
                position: "absolute",
                left: tooltipPos.x + 10,
                top: tooltipPos.y - 40,
                backgroundColor: "#1a1d24",
                border: "1px solid #3d4450",
                borderRadius: "4px",
                padding: "6px 10px",
                fontSize: "10px",
                color: "#fff",
                pointerEvents: "none",
                zIndex: 1000,
                boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
            } },
            window.SP_REACT.createElement("div", null,
                window.SP_REACT.createElement("strong", null,
                    data[hoveredPoint].offset,
                    "mV")),
            window.SP_REACT.createElement("div", null,
                "Temp: ",
                data[hoveredPoint].temp,
                "\u00B0C"),
            window.SP_REACT.createElement("div", { style: {
                    color: data[hoveredPoint].result === "pass" ? "#4caf50" :
                        data[hoveredPoint].result === "fail" ? "#ff9800" : "#f44336"
                } }, data[hoveredPoint].result.toUpperCase())))));
};
// ==================== Results Screen ====================
const ResultsScreen = ({ result, onApply, onStartOver }) => {
    const cpuOffset = result?.offsets?.cpu || 0;
    const [isApplying, setIsApplying] = SP_REACT.useState(false);
    const [applyOnStartup, setApplyOnStartup] = SP_REACT.useState(false);
    const [gameOnlyMode, setGameOnlyMode] = SP_REACT.useState(false);
    const handleApply = async () => {
        setIsApplying(true);
        try {
            await onApply(applyOnStartup, gameOnlyMode);
        }
        finally {
            setIsApplying(false);
        }
    };
    return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } },
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(ChipGradeBadge, { grade: result?.chipGrade || "Bronze" })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "10px" } },
                window.SP_REACT.createElement("div", { style: { fontSize: "32px", fontWeight: "bold", color: "#1a9fff" } },
                    cpuOffset,
                    "mV"),
                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a" } }, "Recommended Undervolt"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "center" } },
                window.SP_REACT.createElement(EnhancedCurveChart, { data: result?.curveData || [] }))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    fontSize: "10px",
                    color: "#8b929a",
                    padding: "8px",
                    backgroundColor: "#1a1d24",
                    borderRadius: "4px",
                } },
                window.SP_REACT.createElement("div", null,
                    "Duration: ",
                    Math.round(result?.duration || 0),
                    "s"),
                window.SP_REACT.createElement("div", null,
                    "Iterations: ",
                    result?.iterations || 0))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { label: "Apply on Startup", description: "Automatically apply this preset when DeckTune starts", checked: applyOnStartup, onChange: setApplyOnStartup })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { label: "Game Only Mode", description: "Only apply when a game is running", checked: gameOnlyMode, onChange: setGameOnlyMode })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleApply, disabled: isApplying },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: isApplying ? "#8b929a" : "#4caf50" } },
                    isApplying ? window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 12 }) : window.SP_REACT.createElement(FaCheck, { size: 12 }),
                    window.SP_REACT.createElement("span", null, isApplying ? "Applying..." : "Apply & Save as Wizard Preset")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onStartOver },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" } },
                    window.SP_REACT.createElement(FaHistory, { size: 12 }),
                    window.SP_REACT.createElement("span", null, "Start Over"))))));
};
// ==================== Wizard History View (Inline) ====================
const WizardHistoryView = ({ onClose }) => {
    const [presets, setPresets] = SP_REACT.useState([]);
    const [selectedPreset, setSelectedPreset] = SP_REACT.useState(null);
    const [isLoading, setIsLoading] = SP_REACT.useState(true);
    const loadPresets = async () => {
        setIsLoading(true);
        try {
            const result = await call("get_wizard_presets");
            setPresets(result || []);
        }
        catch (err) {
            console.error("Failed to load wizard presets:", err);
        }
        finally {
            setIsLoading(false);
        }
    };
    SP_REACT.useEffect(() => {
        loadPresets();
    }, []);
    const handleApply = async (preset) => {
        try {
            await call("apply_wizard_result", preset.id, true, preset.apply_on_startup, preset.game_only_mode);
            console.log("Applied wizard preset:", preset.id);
        }
        catch (err) {
            console.error("Failed to apply preset:", err);
        }
    };
    const handleDelete = async (presetId) => {
        try {
            await call("delete_wizard_preset", presetId);
            console.log("Deleted wizard preset:", presetId);
            setSelectedPreset(null);
            await loadPresets();
        }
        catch (err) {
            console.error("Failed to delete preset:", err);
        }
    };
    const handleUpdateOptions = async (presetId, applyOnStartup, gameOnlyMode) => {
        try {
            await call("update_wizard_preset_options", presetId, applyOnStartup, gameOnlyMode);
            console.log("Updated wizard preset options:", presetId);
            await loadPresets();
        }
        catch (err) {
            console.error("Failed to update preset options:", err);
        }
    };
    if (isLoading) {
        return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "20px" } },
                    window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { fontSize: "24px", color: "#1a9fff" } }),
                    window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginTop: "10px" } }, "Loading presets...")))));
    }
    if (selectedPreset) {
        const cpuOffset = selectedPreset.offsets?.cpu || 0;
        const [applyOnStartup, setApplyOnStartup] = SP_REACT.useState(selectedPreset.apply_on_startup);
        const [gameOnlyMode, setGameOnlyMode] = SP_REACT.useState(selectedPreset.game_only_mode);
        return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setSelectedPreset(null) },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "5px" } },
                        window.SP_REACT.createElement(FaHistory, { size: 10 }),
                        window.SP_REACT.createElement("span", null, "Back to List")))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(ChipGradeBadge, { grade: selectedPreset.chip_grade })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "10px" } },
                    window.SP_REACT.createElement("div", { style: { fontSize: "24px", fontWeight: "bold", color: "#1a9fff" } },
                        cpuOffset,
                        "mV"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } }, new Date(selectedPreset.timestamp).toLocaleString()))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ToggleField, { label: "Apply on Startup", checked: applyOnStartup, onChange: (val) => {
                        setApplyOnStartup(val);
                        handleUpdateOptions(selectedPreset.id, val, gameOnlyMode);
                    } })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ToggleField, { label: "Game Only Mode", checked: gameOnlyMode, onChange: (val) => {
                        setGameOnlyMode(val);
                        handleUpdateOptions(selectedPreset.id, applyOnStartup, val);
                    } })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => handleApply(selectedPreset) },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: "#4caf50" } },
                        window.SP_REACT.createElement(FaCheck, { size: 12 }),
                        window.SP_REACT.createElement("span", null, "Apply Preset")))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => handleDelete(selectedPreset.id) },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px", color: "#f44336" } },
                        window.SP_REACT.createElement(FaTimes, { size: 12 }),
                        window.SP_REACT.createElement("span", null, "Delete Preset"))))));
    }
    if (presets.length === 0) {
        return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "20px", color: "#8b929a", fontSize: "12px" } }, "No wizard presets found. Run the wizard to create your first preset."))));
    }
    return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "8px" } }, presets.map((preset) => {
        const cpuOffset = preset.offsets?.cpu || 0;
        const date = new Date(preset.timestamp).toLocaleDateString();
        return (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: preset.id },
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setSelectedPreset(preset) },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        window.SP_REACT.createElement("div", { style: { fontSize: "16px" } },
                            preset.chip_grade === "Platinum" && window.SP_REACT.createElement(FaTrophy, { style: { color: "#e5e4e2" } }),
                            preset.chip_grade === "Gold" && window.SP_REACT.createElement(FaMedal, { style: { color: "#ffd700" } }),
                            preset.chip_grade === "Silver" && window.SP_REACT.createElement(FaAward, { style: { color: "#c0c0c0" } }),
                            preset.chip_grade === "Bronze" && window.SP_REACT.createElement(FaCertificate, { style: { color: "#cd7f32" } })),
                        window.SP_REACT.createElement("div", null,
                            window.SP_REACT.createElement("div", { style: { fontSize: "11px", fontWeight: "bold" } },
                                preset.chip_grade,
                                " \u2022 ",
                                cpuOffset,
                                "mV"),
                            window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#8b929a" } }, date)))))));
    })));
};
// ==================== Main Component ====================
const WizardMode = () => {
    const { info: platformInfo } = usePlatformInfo();
    const { isRunning, progress, result, dirtyExit, startWizard, cancelWizard, applyResult, } = useWizard();
    const [showCrashModal, setShowCrashModal] = SP_REACT.useState(false);
    const [localResult, setLocalResult] = SP_REACT.useState(null);
    const [showHistory, setShowHistory] = SP_REACT.useState(false);
    SP_REACT.useEffect(() => {
        if (dirtyExit?.detected && !showCrashModal) {
            setShowCrashModal(true);
        }
    }, [dirtyExit]);
    SP_REACT.useEffect(() => {
        if (result) {
            setLocalResult(result);
        }
    }, [result]);
    const handleStart = async (config) => {
        try {
            setLocalResult(null);
            await startWizard(config);
        }
        catch (err) {
            console.error("Failed to start wizard:", err);
        }
    };
    const handleCancel = async () => {
        try {
            await cancelWizard();
        }
        catch (err) {
            console.error("Failed to cancel wizard:", err);
        }
    };
    const handleApply = async (applyOnStartup, gameOnlyMode) => {
        if (!localResult)
            return;
        try {
            await applyResult(localResult.id, true, applyOnStartup, gameOnlyMode);
            console.log(`Applied wizard result with options: startup=${applyOnStartup}, gameOnly=${gameOnlyMode}`);
        }
        catch (err) {
            console.error("Failed to apply result:", err);
        }
    };
    const handleStartOver = () => {
        setLocalResult(null);
    };
    return (window.SP_REACT.createElement(DFL.PanelSection, { title: "Wizard Mode" },
        window.SP_REACT.createElement(PanicDisableButton$1, null),
        !isRunning && !localResult && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setShowHistory(!showHistory) },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "5px" } },
                    window.SP_REACT.createElement(FaHistory, { size: 12 }),
                    window.SP_REACT.createElement("span", null, showHistory ? "Back to Wizard" : "View History"))))),
        showCrashModal && dirtyExit?.crashInfo && (window.SP_REACT.createElement(CrashRecoveryModal, { crashInfo: dirtyExit.crashInfo, onDismiss: () => setShowCrashModal(false) })),
        !isRunning && !localResult && !showHistory && (window.SP_REACT.createElement(ConfigurationScreen, { onStart: handleStart, platformInfo: platformInfo })),
        !isRunning && !localResult && showHistory && (window.SP_REACT.createElement(WizardHistoryView, { onClose: () => setShowHistory(false) })),
        isRunning && progress && (window.SP_REACT.createElement(ProgressScreen, { progress: progress, onCancel: handleCancel })),
        !isRunning && localResult && (window.SP_REACT.createElement(ResultsScreen, { result: localResult, onApply: handleApply, onStartOver: handleStartOver }))));
};

/**
 * FocusableButton - Custom button component with gamepad focus support.
 *
 * Replaces Decky UI's default square focus with custom rounded focus.
 * Uses inline styles to avoid CSS specificity issues.
 */


const FocusableButton = ({ children, onClick, onActivate, style = {}, focusColor = "#1a9fff", disabled = false, className = "", }) => {
    const [isFocused, setIsFocused] = SP_REACT.useState(false);
    const handleClick = () => {
        if (!disabled && onClick)
            onClick();
    };
    const handleActivate = () => {
        if (!disabled) {
            if (onActivate) {
                onActivate();
            }
            else if (onClick) {
                // Fallback to onClick if onActivate not provided
                onClick();
            }
        }
    };
    return (window.SP_REACT.createElement(DFL.Focusable, { onActivate: handleActivate, onClick: handleClick, onGamepadFocus: () => setIsFocused(true), onGamepadBlur: () => setIsFocused(false), className: className, style: {
            ...style,
            // Use border instead of outline for rounded corners
            border: isFocused && !disabled ? `3px solid ${focusColor}` : "3px solid transparent",
            borderRadius: "8px", // Rounded corners
            boxShadow: isFocused && !disabled ? `0 0 12px ${focusColor}99` : "none",
            transform: isFocused && !disabled ? "scale(1.05)" : "scale(1)",
            transition: "all 0.2s ease",
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled ? 0.5 : 1,
            // Remove any padding/margin that might cause issues
            padding: 0,
            margin: 0,
        } }, children));
};

/**
 * Redesigned Presets tab - compact and gamepad-friendly.
 *
 * Two sections:
 * 1. Game Profiles - auto-switching profiles per game
 * 2. Global Presets - manual presets you can apply anytime
 */

const PresetsTabNew = () => {
    const { state, api } = useDeckTune();
    const profilesHook = useProfiles();
    // Extra safety: ensure profiles is always an array
    const profiles = Array.isArray(profilesHook.profiles) ? profilesHook.profiles : [];
    const { activeProfile, runningAppId, runningAppName } = profilesHook;
    const [activeSection, setActiveSection] = SP_REACT.useState("profiles");
    // Load profiles on mount
    SP_REACT.useEffect(() => {
        const loadProfiles = async () => {
            try {
                await api.getProfiles();
            }
            catch (e) {
                console.error("Failed to load profiles:", e);
            }
        };
        loadProfiles();
    }, [api]);
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    gap: "4px",
                    marginBottom: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "4px",
                    padding: "2px",
                }, "flow-children": "horizontal" },
                window.SP_REACT.createElement(FocusableButton, { onClick: () => setActiveSection("profiles"), style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "6px",
                            fontSize: "10px",
                            backgroundColor: activeSection === "profiles" ? "#1a9fff" : "transparent",
                            borderRadius: "4px",
                            color: activeSection === "profiles" ? "#fff" : "#8b929a",
                        } },
                        window.SP_REACT.createElement(FaGamepad, { size: 10 }),
                        window.SP_REACT.createElement("span", null, "Game Profiles"))),
                window.SP_REACT.createElement(FocusableButton, { onClick: () => setActiveSection("presets"), style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "6px",
                            fontSize: "10px",
                            backgroundColor: activeSection === "presets" ? "#1a9fff" : "transparent",
                            borderRadius: "4px",
                            color: activeSection === "presets" ? "#fff" : "#8b929a",
                        } },
                        window.SP_REACT.createElement(FaGlobe, { size: 10 }),
                        window.SP_REACT.createElement("span", null, "Global Presets"))))),
        activeSection === "profiles" ? (window.SP_REACT.createElement(GameProfilesSection, { profiles: profiles, activeProfile: activeProfile, runningAppId: runningAppId, runningAppName: runningAppName, api: api })) : (window.SP_REACT.createElement(GlobalPresetsSection, { presets: state.presets, api: api })),
        window.SP_REACT.createElement("style", null, `
          .section-button {
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            background-color: transparent;
            color: #8b929a;
          }
          .section-button.active {
            background-color: #1a9fff;
            color: #fff;
          }
          .section-button.gpfocus {
            border: 2px solid #1a9fff;
            box-shadow: 0 0 8px rgba(26, 159, 255, 0.6);
          }
          .section-button:hover {
            background-color: rgba(26, 159, 255, 0.2);
          }
          
          .preset-action-btn {
            border-radius: 4px;
            transition: all 0.2s ease;
          }
          .preset-action-btn.gpfocus {
            transform: scale(1.05);
            box-shadow: 0 0 8px rgba(26, 159, 255, 0.6);
          }
          .preset-apply.gpfocus > div {
            background-color: #1585d8 !important;
          }
          .preset-delete.gpfocus > div {
            background-color: #3a3d45 !important;
          }
          
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
const GameProfilesSection = ({ profiles, activeProfile, runningAppId, runningAppName, api }) => {
    const [isCreating, setIsCreating] = SP_REACT.useState(false);
    const handleQuickCreate = async () => {
        if (!runningAppId || !runningAppName)
            return;
        setIsCreating(true);
        try {
            const result = await api.createProfileForCurrentGame();
            if (!result.success) {
                alert(`Failed: ${result.error}`);
            }
        }
        finally {
            setIsCreating(false);
        }
    };
    const handleDelete = async (appId, name) => {
        DFL.showModal(window.SP_REACT.createElement(DFL.ConfirmModal, { strTitle: "Delete Profile", strDescription: `Delete profile for ${name}?`, strOKButtonText: "Delete", strCancelButtonText: "Cancel", onOK: async () => {
                await api.deleteProfile(appId);
            } }));
    };
    const formatCores = (cores) => {
        const allSame = cores.every(v => v === cores[0]);
        return allSame ? `${cores[0]}mV` : cores.map(v => `${v}`).join("/");
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        runningAppId && runningAppName && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(FocusableButton, { onClick: handleQuickCreate, disabled: isCreating, style: { width: "100%", marginBottom: "8px" } },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "6px",
                        fontSize: "10px",
                        padding: "10px",
                        backgroundColor: "#1a9fff",
                        borderRadius: "6px",
                        fontWeight: "bold"
                    } },
                    isCreating ? window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 10 }) : window.SP_REACT.createElement(FaPlus, { size: 10 }),
                    window.SP_REACT.createElement("span", null,
                        "Save for ",
                        runningAppName))))),
        profiles.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "11px" } },
                "No game profiles yet.",
                runningAppId && window.SP_REACT.createElement("div", { style: { marginTop: "4px" } }, "Click above to create one!")))) : (profiles.map((profile) => {
            const isActive = activeProfile?.app_id === profile.app_id || runningAppId === profile.app_id;
            return (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: profile.app_id },
                window.SP_REACT.createElement("div", { style: { marginBottom: "6px" } },
                    window.SP_REACT.createElement("div", { style: {
                            padding: "6px 8px",
                            backgroundColor: isActive ? "#1a3a5c" : "#23262e",
                            borderRadius: "6px 6px 0 0",
                            border: isActive ? "2px solid #1a9fff" : "none",
                            borderBottom: "1px solid #3d4450"
                        } },
                        window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "6px" } },
                            window.SP_REACT.createElement("span", { style: { fontSize: "11px", fontWeight: "bold", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" } }, profile.name),
                            isActive && (window.SP_REACT.createElement("span", { style: { fontSize: "8px", padding: "1px 4px", backgroundColor: "#4caf50", borderRadius: "2px", fontWeight: "bold" } }, "ACTIVE"))),
                        window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#8b929a", marginTop: "2px" } },
                            formatCores(profile.cores),
                            profile.dynamic_enabled && window.SP_REACT.createElement("span", { style: { marginLeft: "6px", color: "#4caf50" } }, "\u26A1 Dynamic"))),
                    window.SP_REACT.createElement(DFL.Focusable, { style: {
                            backgroundColor: "#1a1d24",
                            borderRadius: "0 0 6px 6px",
                            padding: "6px",
                        } },
                        window.SP_REACT.createElement(DFL.Focusable, { className: "preset-action-btn preset-delete", focusClassName: "gpfocus", onActivate: () => handleDelete(profile.app_id, profile.name), onClick: () => handleDelete(profile.app_id, profile.name) },
                            window.SP_REACT.createElement("div", { style: {
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    gap: "4px",
                                    padding: "6px 8px",
                                    fontSize: "9px",
                                    fontWeight: "600",
                                    borderRadius: "4px",
                                    backgroundColor: "#2a2d35",
                                    color: "#f44336",
                                    cursor: "pointer",
                                    transition: "all 0.2s ease"
                                } },
                                window.SP_REACT.createElement(FaTrash, { size: 8 }),
                                window.SP_REACT.createElement("span", null, "Delete Profile")))))));
        })),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
const GlobalPresetsSection = ({ presets, api }) => {
    const [isApplying, setIsApplying] = SP_REACT.useState(null);
    const [isSaving, setIsSaving] = SP_REACT.useState(false);
    const handleApply = async (preset) => {
        setIsApplying(preset.app_id);
        try {
            await api.applyUndervolt(preset.value);
        }
        finally {
            setIsApplying(null);
        }
    };
    const handleDelete = async (appId, label) => {
        DFL.showModal(window.SP_REACT.createElement(DFL.ConfirmModal, { strTitle: "Delete Preset", strDescription: `Delete preset "${label}"?`, strOKButtonText: "Delete", strCancelButtonText: "Cancel", onOK: async () => {
                await api.deletePreset(appId);
            } }));
    };
    const handleQuickSave = async () => {
        setIsSaving(true);
        try {
            const timestamp = new Date().toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
            const label = `Preset ${timestamp}`;
            // Get current cores from API state
            const cores = api.state.cores || [0, 0, 0, 0];
            // Create preset object
            const preset = {
                app_id: Date.now(), // Use timestamp as unique ID
                label: label,
                value: cores,
                timeout: 0,
                use_timeout: false,
                tested: false,
            };
            console.log("Saving preset:", preset);
            // Call backend to save preset
            const result = await call("save_preset", preset);
            console.log("Save result:", result);
            if (result.success) {
                // Reload presets directly
                const updatedPresets = await call("get_presets");
                console.log("Updated presets:", updatedPresets);
                // Use setState to properly trigger React re-render
                api.setState({ presets: updatedPresets });
            }
        }
        catch (e) {
            console.error("Failed to save preset:", e);
            alert(`Failed to save: ${e}`);
        }
        finally {
            setIsSaving(false);
        }
    };
    const formatCores = (cores) => {
        const allSame = cores.every(v => v === cores[0]);
        return allSame ? `${cores[0]}mV` : cores.map(v => `${v}`).join("/");
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(FocusableButton, { onClick: handleQuickSave, disabled: isSaving, style: { width: "100%", marginBottom: "8px" } },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "6px",
                        fontSize: "10px",
                        padding: "10px",
                        backgroundColor: "#1a9fff",
                        borderRadius: "6px",
                        fontWeight: "bold"
                    } },
                    isSaving ? window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 10 }) : window.SP_REACT.createElement(FaPlus, { size: 10 }),
                    window.SP_REACT.createElement("span", null, "Save Current Values")))),
        presets.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "11px" } },
                "No global presets saved.",
                window.SP_REACT.createElement("div", { style: { marginTop: "4px" } }, "Click above to save your current values!")))) : (presets.map((preset) => {
            const isApplyingThis = isApplying === preset.app_id;
            return (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: preset.app_id },
                window.SP_REACT.createElement("div", { style: { marginBottom: "6px" } },
                    window.SP_REACT.createElement("div", { style: { padding: "6px 8px", backgroundColor: "#23262e", borderRadius: "6px 6px 0 0", borderBottom: "1px solid #3d4450" } },
                        window.SP_REACT.createElement("div", { style: { fontSize: "11px", fontWeight: "bold", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" } }, preset.label),
                        window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#8b929a", marginTop: "2px" } },
                            formatCores(preset.value),
                            preset.tested && window.SP_REACT.createElement("span", { style: { marginLeft: "6px", color: "#4caf50" } }, "\u2713 Tested"))),
                    window.SP_REACT.createElement(DFL.Focusable, { style: {
                            display: "flex",
                            gap: "4px",
                            backgroundColor: "#1a1d24",
                            borderRadius: "0 0 6px 6px",
                            padding: "6px",
                        }, "flow-children": "horizontal" },
                        window.SP_REACT.createElement(DFL.Focusable, { style: { flex: 1 }, className: "preset-action-btn preset-apply", focusClassName: "gpfocus", onActivate: () => handleApply(preset), onClick: () => handleApply(preset) },
                            window.SP_REACT.createElement("div", { style: {
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    gap: "4px",
                                    padding: "6px 8px",
                                    fontSize: "9px",
                                    fontWeight: "600",
                                    borderRadius: "4px",
                                    backgroundColor: "#1a9fff",
                                    color: "#fff",
                                    cursor: "pointer",
                                    transition: "all 0.2s ease"
                                } },
                                isApplyingThis ? window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 9 }) : window.SP_REACT.createElement(FaCheck, { size: 9 }),
                                window.SP_REACT.createElement("span", null, "Apply"))),
                        window.SP_REACT.createElement(DFL.Focusable, { style: { flex: 1 }, className: "preset-action-btn preset-delete", focusClassName: "gpfocus", onActivate: () => handleDelete(preset.app_id, preset.label), onClick: () => handleDelete(preset.app_id, preset.label) },
                            window.SP_REACT.createElement("div", { style: {
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    gap: "4px",
                                    padding: "6px 8px",
                                    fontSize: "9px",
                                    fontWeight: "600",
                                    borderRadius: "4px",
                                    backgroundColor: "#2a2d35",
                                    color: "#f44336",
                                    cursor: "pointer",
                                    transition: "all 0.2s ease"
                                } },
                                window.SP_REACT.createElement(FaTrash, { size: 8 }),
                                window.SP_REACT.createElement("span", null, "Delete")))))));
        })),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};

/**
 * Redesigned Tests tab - compact and gamepad-friendly.
 *
 * Feature: decktune, Frontend UI Components - Expert Mode
 * Requirements: 7.4
 *
 * Two sections:
 * 1. Run Tests - test selection and execution with progress
 * 2. Test History - last 10 test results
 */

/**
 * Available test options with compact labels and estimated durations.
 */
const TEST_OPTIONS = [
    { value: "cpu_quick", label: "CPU Quick", duration: "30s", durationSeconds: 30, icon: "⚡" },
    { value: "cpu_long", label: "CPU Long", duration: "5m", durationSeconds: 300, icon: "🔥" },
    { value: "ram_quick", label: "RAM Quick", duration: "2m", durationSeconds: 120, icon: "💾" },
    { value: "ram_thorough", label: "RAM Thorough", duration: "15m", durationSeconds: 900, icon: "🧠" },
    { value: "combo", label: "Combo Stress", duration: "5m", durationSeconds: 300, icon: "💪" },
    { value: "cpu_loop", label: "CPU Loop", duration: "∞", durationSeconds: 0, icon: "🔁" },
];
const TestsTabNew = () => {
    const { history, currentTest, isRunning, runTest } = useTests();
    const { missing: missingBinaries, hasMissing, check: checkBinaries } = useBinaries();
    const [activeSection, setActiveSection] = SP_REACT.useState("run");
    // NUCLEAR CACHE BUST - v3.1.19-20260118-2230
    SP_REACT.useEffect(() => {
        const buildId = "v3.1.19-20260118-2230-FOCUSABLE-BUTTON";
        console.log(`[DeckTune CACHE BUST] ${buildId} - TestsTabNew with FocusableButton`);
        window.__DECKTUNE_BUILD_ID__ = buildId;
        window.__DECKTUNE_TESTS_TAB_VERSION__ = "FOCUSABLE_BUTTON";
    }, []);
    // Check binaries on mount
    SP_REACT.useEffect(() => {
        checkBinaries();
    }, []);
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    gap: "4px",
                    marginBottom: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "4px",
                    padding: "2px",
                }, "flow-children": "horizontal" },
                window.SP_REACT.createElement(FocusableButton, { onClick: () => setActiveSection("run"), style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "6px",
                            fontSize: "10px",
                            backgroundColor: activeSection === "run" ? "#1a9fff" : "transparent",
                            borderRadius: "4px",
                            color: activeSection === "run" ? "#fff" : "#8b929a",
                        } },
                        window.SP_REACT.createElement(FaPlay, { style: { fontSize: "10px" } }),
                        window.SP_REACT.createElement("span", null, "Run Tests"))),
                window.SP_REACT.createElement(FocusableButton, { onClick: () => setActiveSection("history"), style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "6px",
                            fontSize: "10px",
                            backgroundColor: activeSection === "history" ? "#1a9fff" : "transparent",
                            borderRadius: "4px",
                            color: activeSection === "history" ? "#fff" : "#8b929a",
                        } },
                        window.SP_REACT.createElement(FaHistory, { style: { fontSize: "10px" } }),
                        window.SP_REACT.createElement("span", null, "History"))))),
        activeSection === "run" ? (window.SP_REACT.createElement(RunTestsSection, { isRunning: isRunning, currentTest: currentTest, runTest: runTest, hasMissing: hasMissing, missingBinaries: missingBinaries })) : (window.SP_REACT.createElement(TestHistorySection, { history: history })),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
const RunTestsSection = ({ isRunning, currentTest, runTest, hasMissing, missingBinaries }) => {
    const [progress, setProgress] = SP_REACT.useState(0);
    const [startTime, setStartTime] = SP_REACT.useState(null);
    const [estimatedDuration, setEstimatedDuration] = SP_REACT.useState(0);
    const [testResult, setTestResult] = SP_REACT.useState(null);
    const [elapsedTime, setElapsedTime] = SP_REACT.useState(0);
    // Progress tracking
    SP_REACT.useEffect(() => {
        if (!isRunning || !currentTest) {
            setProgress(0);
            setStartTime(null);
            setElapsedTime(0);
            return;
        }
        // Set start time and estimated duration
        const testOption = TEST_OPTIONS.find(t => t.value === currentTest);
        if (testOption && !startTime) {
            setStartTime(Date.now());
            setEstimatedDuration(testOption.durationSeconds);
            setTestResult(null);
        }
        // Update progress every second
        const interval = setInterval(() => {
            if (startTime) {
                const elapsed = (Date.now() - startTime) / 1000;
                setElapsedTime(Math.floor(elapsed));
                if (estimatedDuration > 0) {
                    const newProgress = Math.min((elapsed / estimatedDuration) * 100, 99);
                    setProgress(newProgress);
                }
                else {
                    // Loop test - show elapsed time only
                    setProgress(0);
                }
            }
        }, 1000);
        return () => clearInterval(interval);
    }, [isRunning, currentTest, startTime, estimatedDuration]);
    const handleRunTest = async (testValue) => {
        if (isRunning)
            return;
        setProgress(0);
        setStartTime(null);
        setTestResult(null);
        try {
            const result = await runTest(testValue);
            setProgress(100);
            setTestResult({ passed: result?.passed ?? true });
        }
        catch (error) {
            setTestResult({ passed: false, error: error?.message || "Test failed" });
        }
    };
    const getTestLabel = (value) => {
        return TEST_OPTIONS.find((t) => t.value === value)?.label || value;
    };
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (mins > 0) {
            return `${mins}m ${secs}s`;
        }
        return `${secs}s`;
    };
    const getRemainingTime = () => {
        if (!startTime || !estimatedDuration)
            return "";
        const remaining = Math.max(0, estimatedDuration - elapsedTime);
        return formatTime(remaining) + " left";
    };
    const isLoopTest = currentTest && TEST_OPTIONS.find(t => t.value === currentTest)?.durationSeconds === 0;
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        hasMissing && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "8px",
                    padding: "10px",
                    backgroundColor: "#5c4813",
                    borderRadius: "6px",
                    marginBottom: "12px",
                    border: "1px solid #ff9800",
                } },
                window.SP_REACT.createElement(FaExclamationCircle, { style: { color: "#ff9800", fontSize: "14px", flexShrink: 0, marginTop: "1px" } }),
                window.SP_REACT.createElement("div", null,
                    window.SP_REACT.createElement("div", { style: { fontWeight: "bold", color: "#ffb74d", marginBottom: "3px", fontSize: "10px" } }, "Missing Components"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#ffe0b2" } },
                        "Required: ",
                        window.SP_REACT.createElement("strong", null, missingBinaries.join(", "))))))),
        testResult && !isRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "10px",
                    backgroundColor: testResult.passed ? "#1b5e20" : "#5c1313",
                    borderRadius: "6px",
                    marginBottom: "12px",
                    border: `1px solid ${testResult.passed ? "#4caf50" : "#f44336"}`,
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "6px", marginBottom: testResult.error ? "4px" : "0" } },
                    testResult.passed ? (window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50", fontSize: "12px" } })) : (window.SP_REACT.createElement(FaTimes, { style: { color: "#f44336", fontSize: "12px" } })),
                    window.SP_REACT.createElement("span", { style: { fontSize: "10px", fontWeight: "bold" } }, testResult.passed ? "Test Passed!" : "Test Failed")),
                testResult.error && (window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#ffcdd2", marginTop: "4px" } }, testResult.error))))),
        isRunning && currentTest && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1a3a5c",
                    borderRadius: "6px",
                    marginBottom: "12px",
                    border: "1px solid #1a9fff",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "6px" } },
                        window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { color: "#1a9fff", fontSize: "12px" } }),
                        window.SP_REACT.createElement("span", { style: { fontSize: "10px", fontWeight: "bold" } }, getTestLabel(currentTest))),
                    window.SP_REACT.createElement("span", { style: { fontSize: "9px", color: "#8b929a" } }, isLoopTest ? `${formatTime(elapsedTime)} elapsed` : getRemainingTime())),
                !isLoopTest && (window.SP_REACT.createElement("div", null,
                    window.SP_REACT.createElement("div", { style: {
                            width: "100%",
                            height: "6px",
                            backgroundColor: "#23262e",
                            borderRadius: "3px",
                            overflow: "hidden"
                        } },
                        window.SP_REACT.createElement("div", { style: {
                                width: `${progress}%`,
                                height: "100%",
                                backgroundColor: "#1a9fff",
                                transition: "width 0.3s ease",
                                borderRadius: "3px"
                            } })),
                    window.SP_REACT.createElement("div", { style: { fontSize: "8px", color: "#8b929a", marginTop: "4px", textAlign: "center" } },
                        Math.round(progress),
                        "%"))),
                isLoopTest && (window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#8b929a", textAlign: "center", marginTop: "4px" } }, "Running until manually stopped (restart plugin to cancel)"))))),
        !isRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "6px",
                } }, TEST_OPTIONS.map((test) => (window.SP_REACT.createElement(FocusableButton, { key: test.value, onClick: () => !hasMissing && handleRunTest(test.value), disabled: hasMissing },
                window.SP_REACT.createElement("div", { style: {
                        padding: "10px 8px",
                        backgroundColor: "#23262e",
                        borderRadius: "6px",
                    } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "4px", marginBottom: "4px" } },
                        window.SP_REACT.createElement("span", { style: { fontSize: "14px" } }, test.icon),
                        window.SP_REACT.createElement("span", { style: { fontSize: "10px", fontWeight: "bold" } }, test.label)),
                    window.SP_REACT.createElement("div", { style: { fontSize: "8px", color: "#8b929a" } }, test.durationSeconds === 0 ? "Until cancelled" : `Duration: ${test.duration}`))))))))));
};
const TestHistorySection = ({ history }) => {
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        if (mins > 0) {
            return `${mins}m ${secs}s`;
        }
        return `${secs}s`;
    };
    const formatTimestamp = (timestamp) => {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        }
        catch {
            return timestamp;
        }
    };
    const getTestLabel = (value) => {
        return TEST_OPTIONS.find((t) => t.value === value)?.label || value;
    };
    const getTestIcon = (value) => {
        return TEST_OPTIONS.find((t) => t.value === value)?.icon || "🔧";
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null, history.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "24px", fontSize: "11px" } },
            "No tests run yet.",
            window.SP_REACT.createElement("div", { style: { marginTop: "4px", fontSize: "9px" } }, "Switch to \"Run Tests\" to start!")))) : (history.slice(0, 10).map((entry, index) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: index },
        window.SP_REACT.createElement(DFL.Focusable, { focusClassName: "gpfocus", style: {
                marginBottom: "6px",
            } },
            window.SP_REACT.createElement("div", { style: {
                    padding: "8px 10px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    borderLeft: `3px solid ${entry.passed ? "#4caf50" : "#f44336"}`,
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "6px" } },
                        window.SP_REACT.createElement("span", { style: { fontSize: "12px" } }, getTestIcon(entry.test_name)),
                        entry.passed ? (window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50", fontSize: "10px" } })) : (window.SP_REACT.createElement(FaTimes, { style: { color: "#f44336", fontSize: "10px" } })),
                        window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "10px" } }, getTestLabel(entry.test_name))),
                    window.SP_REACT.createElement("span", { style: { fontSize: "9px", color: "#8b929a" } }, formatDuration(entry.duration))),
                window.SP_REACT.createElement("div", { style: { fontSize: "8px", color: "#8b929a", marginBottom: "2px" } }, formatTimestamp(entry.timestamp)),
                window.SP_REACT.createElement("div", { style: { fontSize: "8px", color: "#8b929a" } },
                    "Cores: [",
                    entry.cores_tested.join(", "),
                    "]")))))))));
};

/**
 * FanCurveEditor component for visual fan curve editing.
 *
 * Feature: Fan Control Integration (Phase 4)
 *
 * Provides an interactive SVG graph for editing fan curve points.
 * Supports drag-and-drop point manipulation, add/remove points,
 * and real-time preview of the curve.
 */

// Graph dimensions
const GRAPH_WIDTH = 280;
const GRAPH_HEIGHT = 160;
const MARGIN = { top: 20, right: 30, bottom: 30, left: 40 };
const INNER_WIDTH = GRAPH_WIDTH - MARGIN.left - MARGIN.right;
const INNER_HEIGHT = GRAPH_HEIGHT - MARGIN.top - MARGIN.bottom;
// Temperature and speed ranges
const TEMP_MIN = 30;
const TEMP_MAX = 95;
const SPEED_MIN = 0;
const SPEED_MAX = 100;
// Point interaction
const POINT_RADIUS = 8;
const POINT_HIT_RADIUS = 15;
/** Default fan curve */
const DEFAULT_CURVE = [
    { temp_c: 40, speed_percent: 20 },
    { temp_c: 50, speed_percent: 30 },
    { temp_c: 60, speed_percent: 45 },
    { temp_c: 70, speed_percent: 60 },
    { temp_c: 80, speed_percent: 80 },
    { temp_c: 85, speed_percent: 100 },
];
/**
 * Convert temperature to X coordinate
 */
const tempToX = (temp) => {
    const normalized = (temp - TEMP_MIN) / (TEMP_MAX - TEMP_MIN);
    return MARGIN.left + normalized * INNER_WIDTH;
};
/**
 * Convert speed to Y coordinate (inverted - 0% at bottom)
 */
const speedToY = (speed) => {
    const normalized = (speed - SPEED_MIN) / (SPEED_MAX - SPEED_MIN);
    return MARGIN.top + INNER_HEIGHT - normalized * INNER_HEIGHT;
};
/**
 * Convert X coordinate to temperature
 */
const xToTemp = (x) => {
    const normalized = (x - MARGIN.left) / INNER_WIDTH;
    return Math.round(TEMP_MIN + normalized * (TEMP_MAX - TEMP_MIN));
};
/**
 * Convert Y coordinate to speed
 */
const yToSpeed = (y) => {
    const normalized = 1 - (y - MARGIN.top) / INNER_HEIGHT;
    return Math.round(SPEED_MIN + normalized * (SPEED_MAX - SPEED_MIN));
};
/**
 * Clamp value to range
 */
const clamp = (value, min, max) => {
    return Math.max(min, Math.min(max, value));
};
/**
 * Generate SVG path for the curve
 */
const generateCurvePath = (points) => {
    if (points.length === 0)
        return "";
    const sorted = [...points].sort((a, b) => a.temp_c - b.temp_c);
    // Start from left edge at first point's speed
    let path = `M ${MARGIN.left} ${speedToY(sorted[0].speed_percent)}`;
    path += ` L ${tempToX(sorted[0].temp_c)} ${speedToY(sorted[0].speed_percent)}`;
    // Connect all points
    for (let i = 1; i < sorted.length; i++) {
        path += ` L ${tempToX(sorted[i].temp_c)} ${speedToY(sorted[i].speed_percent)}`;
    }
    // Extend to right edge at last point's speed
    const lastPoint = sorted[sorted.length - 1];
    path += ` L ${MARGIN.left + INNER_WIDTH} ${speedToY(lastPoint.speed_percent)}`;
    return path;
};
/**
 * FanCurveEditor component
 */
const FanCurveEditor = ({ config, status, onConfigChange, onSave, isLoading = false, }) => {
    const svgRef = SP_REACT.useRef(null);
    const [draggingIndex, setDraggingIndex] = SP_REACT.useState(null);
    const [hasChanges, setHasChanges] = SP_REACT.useState(false);
    const [isSaving, setIsSaving] = SP_REACT.useState(false);
    // Handle point drag start
    const handlePointMouseDown = SP_REACT.useCallback((index, e) => {
        e.preventDefault();
        e.stopPropagation();
        setDraggingIndex(index);
    }, []);
    // Handle mouse move for dragging
    const handleMouseMove = SP_REACT.useCallback((e) => {
        if (draggingIndex === null || !svgRef.current)
            return;
        const svg = svgRef.current;
        const rect = svg.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const newTemp = clamp(xToTemp(x), TEMP_MIN, TEMP_MAX);
        const newSpeed = clamp(yToSpeed(y), SPEED_MIN, SPEED_MAX);
        const newCurve = [...config.curve];
        newCurve[draggingIndex] = { temp_c: newTemp, speed_percent: newSpeed };
        onConfigChange({ ...config, curve: newCurve });
        setHasChanges(true);
    }, [draggingIndex, config, onConfigChange]);
    // Handle mouse up to stop dragging
    const handleMouseUp = SP_REACT.useCallback(() => {
        setDraggingIndex(null);
    }, []);
    // Handle click on graph to add point
    const handleGraphClick = SP_REACT.useCallback((e) => {
        if (draggingIndex !== null || !svgRef.current)
            return;
        if (config.mode !== "custom")
            return;
        const svg = svgRef.current;
        const rect = svg.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        // Check if click is within graph area
        if (x < MARGIN.left || x > MARGIN.left + INNER_WIDTH)
            return;
        if (y < MARGIN.top || y > MARGIN.top + INNER_HEIGHT)
            return;
        // Check if click is near existing point
        const clickTemp = xToTemp(x);
        const isNearExisting = config.curve.some(p => Math.abs(p.temp_c - clickTemp) < 5);
        if (isNearExisting)
            return;
        const newPoint = {
            temp_c: clamp(clickTemp, TEMP_MIN, TEMP_MAX),
            speed_percent: clamp(yToSpeed(y), SPEED_MIN, SPEED_MAX),
        };
        const newCurve = [...config.curve, newPoint].sort((a, b) => a.temp_c - b.temp_c);
        onConfigChange({ ...config, curve: newCurve });
        setHasChanges(true);
    }, [draggingIndex, config, onConfigChange]);
    // Handle point removal
    const handleRemovePoint = SP_REACT.useCallback((index) => {
        if (config.curve.length <= 2)
            return; // Keep at least 2 points
        const newCurve = config.curve.filter((_, i) => i !== index);
        onConfigChange({ ...config, curve: newCurve });
        setHasChanges(true);
    }, [config, onConfigChange]);
    // Reset to default curve
    const handleReset = SP_REACT.useCallback(() => {
        onConfigChange({ ...config, curve: [...DEFAULT_CURVE] });
        setHasChanges(true);
    }, [config, onConfigChange]);
    // Save configuration
    const handleSave = SP_REACT.useCallback(async () => {
        setIsSaving(true);
        try {
            await onSave(config);
            setHasChanges(false);
        }
        finally {
            setIsSaving(false);
        }
    }, [config, onSave]);
    // Mode options for dropdown
    const modeOptions = [
        { data: "default", label: "Default (BIOS)" },
        { data: "custom", label: "Custom Curve" },
        { data: "fixed", label: "Fixed Speed" },
    ];
    // Sort curve for display
    const sortedCurve = [...config.curve].sort((a, b) => a.temp_c - b.temp_c);
    return (window.SP_REACT.createElement(DFL.PanelSection, { title: "Fan Control" },
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { label: "Enable Fan Control", description: "Take manual control of the fan", checked: config.enabled, onChange: (enabled) => {
                    onConfigChange({ ...config, enabled });
                    setHasChanges(true);
                }, disabled: isLoading })),
        config.enabled && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.DropdownItem, { label: "Fan Mode", rgOptions: modeOptions, selectedOption: config.mode, onChange: (option) => {
                        onConfigChange({ ...config, mode: option.data });
                        setHasChanges(true);
                    }, disabled: isLoading })),
            status && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "8px 12px",
                        backgroundColor: "#23262e",
                        borderRadius: "8px",
                        fontSize: "13px",
                    } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        window.SP_REACT.createElement(FaFan, { style: {
                                color: status.safety_override ? "#f44336" : "#4caf50",
                                animation: status.speed_percent > 0 ? "spin 1s linear infinite" : "none",
                            } }),
                        window.SP_REACT.createElement("span", null,
                            status.temp_c,
                            "\u00B0C")),
                    window.SP_REACT.createElement("div", { style: { color: "#8b929a" } },
                        status.speed_percent,
                        "% ",
                        status.rpm ? `(${status.rpm} RPM)` : ""),
                    status.safety_override && (window.SP_REACT.createElement("span", { style: { color: "#f44336", fontSize: "11px" } }, "Safety Override"))))),
            config.mode === "custom" && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        backgroundColor: "#1a1d23",
                        borderRadius: "8px",
                        padding: "8px",
                    } },
                    window.SP_REACT.createElement("svg", { ref: svgRef, width: GRAPH_WIDTH, height: GRAPH_HEIGHT, style: { cursor: draggingIndex !== null ? "grabbing" : "crosshair" }, onMouseMove: handleMouseMove, onMouseUp: handleMouseUp, onMouseLeave: handleMouseUp, onClick: handleGraphClick },
                        window.SP_REACT.createElement("g", { stroke: "#3d4450", strokeWidth: "1" },
                            [0, 25, 50, 75, 100].map(speed => (window.SP_REACT.createElement("line", { key: `h-${speed}`, x1: MARGIN.left, y1: speedToY(speed), x2: MARGIN.left + INNER_WIDTH, y2: speedToY(speed) }))),
                            [40, 50, 60, 70, 80, 90].map(temp => (window.SP_REACT.createElement("line", { key: `v-${temp}`, x1: tempToX(temp), y1: MARGIN.top, x2: tempToX(temp), y2: MARGIN.top + INNER_HEIGHT })))),
                        window.SP_REACT.createElement("g", { fill: "#8b929a", fontSize: "10" },
                            [0, 50, 100].map(speed => (window.SP_REACT.createElement("text", { key: `y-${speed}`, x: MARGIN.left - 5, y: speedToY(speed) + 3, textAnchor: "end" },
                                speed,
                                "%"))),
                            [40, 60, 80].map(temp => (window.SP_REACT.createElement("text", { key: `x-${temp}`, x: tempToX(temp), y: MARGIN.top + INNER_HEIGHT + 15, textAnchor: "middle" },
                                temp,
                                "\u00B0C")))),
                        window.SP_REACT.createElement("rect", { x: tempToX(85), y: MARGIN.top, width: MARGIN.left + INNER_WIDTH - tempToX(85), height: INNER_HEIGHT, fill: "rgba(244, 67, 54, 0.1)" }),
                        status && (window.SP_REACT.createElement("line", { x1: tempToX(status.temp_c), y1: MARGIN.top, x2: tempToX(status.temp_c), y2: MARGIN.top + INNER_HEIGHT, stroke: "#4caf50", strokeWidth: "2", strokeDasharray: "4,4" })),
                        window.SP_REACT.createElement("path", { d: generateCurvePath(sortedCurve), fill: "none", stroke: "#1a9fff", strokeWidth: "2" }),
                        window.SP_REACT.createElement("path", { d: `${generateCurvePath(sortedCurve)} L ${MARGIN.left + INNER_WIDTH} ${MARGIN.top + INNER_HEIGHT} L ${MARGIN.left} ${MARGIN.top + INNER_HEIGHT} Z`, fill: "rgba(26, 159, 255, 0.1)" }),
                        sortedCurve.map((point, index) => (window.SP_REACT.createElement("g", { key: index },
                            window.SP_REACT.createElement("circle", { cx: tempToX(point.temp_c), cy: speedToY(point.speed_percent), r: POINT_HIT_RADIUS, fill: "transparent", style: { cursor: "grab" }, onMouseDown: (e) => handlePointMouseDown(config.curve.findIndex(p => p.temp_c === point.temp_c && p.speed_percent === point.speed_percent), e), onDoubleClick: () => handleRemovePoint(config.curve.findIndex(p => p.temp_c === point.temp_c && p.speed_percent === point.speed_percent)) }),
                            window.SP_REACT.createElement("circle", { cx: tempToX(point.temp_c), cy: speedToY(point.speed_percent), r: POINT_RADIUS, fill: "#1a9fff", stroke: "#fff", strokeWidth: "2", style: { pointerEvents: "none" } }),
                            window.SP_REACT.createElement("text", { x: tempToX(point.temp_c), y: speedToY(point.speed_percent) - 12, fill: "#fff", fontSize: "9", textAnchor: "middle", style: { pointerEvents: "none" } },
                                point.temp_c,
                                "\u00B0/",
                                point.speed_percent,
                                "%"))))),
                    window.SP_REACT.createElement("div", { style: {
                            fontSize: "10px",
                            color: "#8b929a",
                            textAlign: "center",
                            marginTop: "4px",
                        } }, "Click to add point \u2022 Drag to move \u2022 Double-click to remove")))),
            config.mode === "fixed" && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.SliderField, { label: "Fixed Fan Speed", value: config.curve[0]?.speed_percent ?? 50, min: 0, max: 100, step: 5, showValue: true, onChange: (value) => {
                        onConfigChange({
                            ...config,
                            curve: [{ temp_c: 0, speed_percent: value }],
                        });
                        setHasChanges(true);
                    }, disabled: isLoading }))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ToggleField, { label: "Zero RPM Mode", description: "Allow fan to stop below 45\u00B0C (risky!)", checked: config.zero_rpm_enabled, onChange: (zero_rpm_enabled) => {
                        onConfigChange({ ...config, zero_rpm_enabled });
                        setHasChanges(true);
                    }, disabled: isLoading })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.SliderField, { label: "Temperature Hysteresis", description: "Prevents rapid speed changes", value: config.hysteresis_temp, min: 1, max: 10, step: 1, showValue: true, valueSuffix: "\u00B0C", onChange: (hysteresis_temp) => {
                        onConfigChange({ ...config, hysteresis_temp });
                        setHasChanges(true);
                    }, disabled: isLoading })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleReset, disabled: isLoading || isSaving },
                        window.SP_REACT.createElement(FaUndo, { style: { marginRight: "4px" } }),
                        "Reset"),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleSave, disabled: isLoading || isSaving || !hasChanges }, isSaving ? "Saving..." : "Save")))))));
};

/**
 * FanTab component for fan control in Expert Mode.
 *
 * Feature: decktune-critical-fixes
 * Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
 *
 * Provides fan curve editing and control through the FanCurveEditor component.
 */

/**
 * FanTab component for Expert Mode.
 *
 * Feature: decktune-critical-fixes
 * Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
 */
const FanTab = () => {
    const { api } = useDeckTune();
    const [config, setConfig] = SP_REACT.useState(null);
    const [status, setStatus] = SP_REACT.useState(null);
    const [isLoading, setIsLoading] = SP_REACT.useState(true);
    const [error, setError] = SP_REACT.useState(null);
    const [isSaving, setIsSaving] = SP_REACT.useState(false);
    // Load fan configuration on mount
    SP_REACT.useEffect(() => {
        const loadFanConfig = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const result = await api.getFanConfig();
                if (result.success && result.config) {
                    setConfig(result.config);
                }
                else {
                    setError(result.error || "Failed to load fan configuration");
                }
            }
            catch (e) {
                setError(`Error loading fan config: ${e}`);
            }
            finally {
                setIsLoading(false);
            }
        };
        loadFanConfig();
    }, [api]);
    // Poll fan status periodically
    SP_REACT.useEffect(() => {
        if (!config?.enabled)
            return;
        const pollStatus = async () => {
            try {
                const result = await api.getFanStatus();
                if (result.success && result.status) {
                    setStatus(result.status);
                }
            }
            catch (e) {
                console.error("Error polling fan status:", e);
            }
        };
        // Initial poll
        pollStatus();
        // Poll every 2 seconds
        const interval = setInterval(pollStatus, 2000);
        return () => clearInterval(interval);
    }, [api, config?.enabled]);
    const handleConfigChange = (newConfig) => {
        setConfig(newConfig);
    };
    const handleSave = async (newConfig) => {
        setIsSaving(true);
        setError(null);
        try {
            const result = await api.setFanConfig(newConfig);
            if (result.success) {
                setConfig(newConfig);
            }
            else {
                setError(result.error || "Failed to save fan configuration");
            }
        }
        catch (e) {
            setError(`Error saving fan config: ${e}`);
        }
        finally {
            setIsSaving(false);
        }
    };
    // Loading state
    if (isLoading) {
        return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    padding: "24px",
                    color: "#8b929a",
                } },
                window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                window.SP_REACT.createElement("span", null, "\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u043A\u043E\u043D\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u0438 \u0432\u0435\u043D\u0442\u0438\u043B\u044F\u0442\u043E\u0440\u0430...")),
            window.SP_REACT.createElement("style", null, `
            .spin {
              animation: spin 1s linear infinite;
            }
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `)));
    }
    // Error state
    if (error && !config) {
        return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "12px",
                    padding: "16px",
                    backgroundColor: "#5c1313",
                    borderRadius: "8px",
                    border: "1px solid #f44336",
                } },
                window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#f44336", fontSize: "24px" } }),
                window.SP_REACT.createElement("div", { style: { color: "#ffcdd2", textAlign: "center", fontSize: "12px" } }, error),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => window.location.reload() }, "\u041F\u043E\u043F\u0440\u043E\u0431\u043E\u0432\u0430\u0442\u044C \u0441\u043D\u043E\u0432\u0430"))));
    }
    // No config available
    if (!config) {
        return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    textAlign: "center",
                    padding: "24px",
                    color: "#8b929a",
                } }, "\u041A\u043E\u043D\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044F \u0432\u0435\u043D\u0442\u0438\u043B\u044F\u0442\u043E\u0440\u0430 \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u043D\u0430")));
    }
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        error && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "8px 12px",
                    backgroundColor: "#5c1313",
                    borderRadius: "6px",
                    marginBottom: "8px",
                    fontSize: "11px",
                    color: "#ffcdd2",
                    border: "1px solid #f44336",
                } }, error))),
        window.SP_REACT.createElement(FanCurveEditor, { config: config, status: status || undefined, onConfigChange: handleConfigChange, onSave: handleSave, isLoading: isSaving })));
};

/**
 * ExpertMode component for DeckTune.
 *
 * Feature: decktune, Frontend UI Components - Expert Mode
 * Requirements: 4.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2
 *
 * Feature: decktune-critical-fixes
 * Validates: Requirements 2.1, 2.2, 2.3, 2.5, 2.6
 *
 * Provides detailed manual controls and diagnostics for power users:
 * - Manual tab: Per-core sliders, Apply/Test/Disable buttons, live metrics
 * - Presets tab: Preset list with edit/delete/export, import
 * - Tests tab: Test selection, run button, history
 * - Diagnostics tab: System info, logs, export
 * - Panic Disable button: Always visible emergency reset (Requirement 4.5)
 *
 * v3.1.19: Complete focus system refactor with FocusableButton
 */

const TABS = [
    { id: "manual", label: "Manual", icon: FaSlidersH },
    { id: "presets", label: "Presets", icon: FaList },
    { id: "tests", label: "Tests", icon: FaVial },
    { id: "fan", label: "Fan", icon: FaFan },
    { id: "diagnostics", label: "Diagnostics", icon: FaInfoCircle },
];
/**
 * Panic Disable Button component - compact emergency reset.
 * Requirements: 4.5
 *
 * Features:
 * - Compact red button with white focus outline
 * - Immediate reset to 0 on click
 * - Uses FocusableButton for custom focus
 */
const PanicDisableButton = () => {
    const { api } = useDeckTune();
    const [isPanicking, setIsPanicking] = SP_REACT.useState(false);
    const [isFocused, setIsFocused] = SP_REACT.useState(false);
    const handlePanicDisable = async () => {
        setIsPanicking(true);
        try {
            await api.panicDisable();
        }
        finally {
            setIsPanicking(false);
        }
    };
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement(DFL.Focusable, { onActivate: handlePanicDisable, onGamepadFocus: () => setIsFocused(true), onGamepadBlur: () => setIsFocused(false), style: {
                padding: 0,
                margin: 0,
            } },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    padding: "12px 16px",
                    backgroundColor: "#b71c1c",
                    borderRadius: "8px",
                    color: "#fff",
                    fontWeight: "bold",
                    fontSize: "12px",
                    border: isFocused && !isPanicking ? "3px solid #fff" : "3px solid transparent",
                    boxShadow: isFocused && !isPanicking ? "0 0 12px rgba(255, 255, 255, 0.6)" : "none",
                    transform: isFocused && !isPanicking ? "scale(1.05)" : "scale(1)",
                    transition: "all 0.2s ease",
                    cursor: isPanicking ? "not-allowed" : "pointer",
                    opacity: isPanicking ? 0.5 : 1,
                } }, isPanicking ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { fontSize: "12px" } }),
                window.SP_REACT.createElement("span", null, "Disabling..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaExclamationTriangle, { style: { fontSize: "12px" } }),
                window.SP_REACT.createElement("span", null, "PANIC DISABLE")))))));
};
/**
 * ExpertMode component - detailed controls for power users.
 * Requirements: 4.5, 7.1
 */
const ExpertMode = ({ initialTab = "manual" }) => {
    const [activeTab, setActiveTab] = SP_REACT.useState(initialTab);
    // NUCLEAR CACHE BUST - v3.1.19-20260118-2230
    SP_REACT.useEffect(() => {
        const buildId = "v3.1.19-20260118-2230-FOCUSABLE-BUTTON";
        console.log(`[DeckTune CACHE BUST] ${buildId} - FocusableButton refactor complete`);
        window.__DECKTUNE_BUILD_ID__ = buildId;
        window.__DECKTUNE_EXPERT_MODE_VERSION__ = "FOCUSABLE_BUTTON_V1";
    }, []);
    return (window.SP_REACT.createElement(DFL.PanelSection, { title: "Expert Mode" },
        window.SP_REACT.createElement(PanicDisableButton, null),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(TabNavigation, { activeTab: activeTab, onTabChange: setActiveTab })),
        window.SP_REACT.createElement("div", { key: activeTab },
            activeTab === "manual" && window.SP_REACT.createElement(ManualTab, null),
            activeTab === "presets" && window.SP_REACT.createElement(PresetsTabNew, null),
            activeTab === "tests" && window.SP_REACT.createElement(TestsTabNew, null),
            activeTab === "fan" && window.SP_REACT.createElement(FanTab, null),
            activeTab === "diagnostics" && window.SP_REACT.createElement(DiagnosticsTab, null))));
};
const TabNavigation = ({ activeTab, onTabChange }) => {
    return (window.SP_REACT.createElement(DFL.Focusable, { style: {
            display: "flex",
            marginBottom: "8px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            padding: "2px",
            gap: "2px",
        }, "flow-children": "horizontal" }, TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (window.SP_REACT.createElement(FocusableButton, { key: tab.id, onClick: () => onTabChange(tab.id), focusColor: isActive ? "#1a9fff" : "#666", style: {
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "1px",
                padding: "4px 2px",
                borderRadius: "3px",
                backgroundColor: isActive ? "#1a9fff" : "transparent",
                color: isActive ? "#fff" : "#8b929a",
            } },
            window.SP_REACT.createElement(Icon, null),
            window.SP_REACT.createElement("span", { style: { fontSize: "8px", fontWeight: isActive ? "600" : "400" } }, tab.label)));
    })));
};
/**
 * Manual tab component with simple/per-core modes.
 *
 * Feature: ui-refactor-settings
 * Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
 */
const ManualTab = () => {
    const { state, api } = useDeckTune();
    const { info: platformInfo } = usePlatformInfo();
    const { settings, setApplyOnStartup, setGameOnlyMode } = useSettings();
    const [coreValues, setCoreValues] = SP_REACT.useState([...state.cores]);
    const [simpleMode, setSimpleMode] = SP_REACT.useState(true);
    const [simpleValue, setSimpleValue] = SP_REACT.useState(-25);
    const [isApplying, setIsApplying] = SP_REACT.useState(false);
    const safeLimit = platformInfo?.safe_limit ?? -30;
    const currentMinLimit = settings.expertMode ? -100 : safeLimit;
    // Sync with state.cores
    SP_REACT.useEffect(() => {
        setCoreValues([...state.cores]);
        const avg = Math.round(state.cores.reduce((sum, val) => sum + val, 0) / 4);
        setSimpleValue(avg);
    }, [state.cores]);
    /**
     * Handle simple mode toggle.
     */
    const handleSimpleModeToggle = () => {
        if (!simpleMode) {
            // Switching to simple: use average
            const avg = Math.round(coreValues.reduce((sum, val) => sum + val, 0) / 4);
            setSimpleValue(avg);
        }
        else {
            // Switching to per-core: copy simple value to all cores
            setCoreValues([simpleValue, simpleValue, simpleValue, simpleValue]);
        }
        setSimpleMode(!simpleMode);
    };
    /**
     * Handle simple slider change.
     */
    const handleSimpleValueChange = (value) => {
        setSimpleValue(value);
        setCoreValues([value, value, value, value]);
    };
    /**
     * Handle slider value change for a specific core.
     */
    const handleCoreChange = (core, value) => {
        const newValues = [...coreValues];
        newValues[core] = value;
        setCoreValues(newValues);
    };
    /**
     * Apply current values.
     */
    const handleApply = async () => {
        setIsApplying(true);
        try {
            await api.applyUndervolt(coreValues);
        }
        finally {
            setIsApplying(false);
        }
    };
    /**
     * Disable undervolt (reset to 0 on backend, but keep UI values).
     */
    const handleDisable = async () => {
        await api.disableUndervolt();
        // Don't reset UI values - user can re-enable with same values
    };
    /**
     * Reset UI values to 0.
     */
    const handleReset = () => {
        setCoreValues([0, 0, 0, 0]);
        setSimpleValue(0);
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        platformInfo && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginBottom: "6px" } },
                platformInfo.variant,
                " (",
                platformInfo.model,
                ") \u2022 Limit: ",
                platformInfo.safe_limit,
                "mV"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "12px", fontWeight: "bold", marginBottom: "8px", marginTop: "4px" } }, "Startup Behavior")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: { marginBottom: "8px" } },
                window.SP_REACT.createElement(FocusableButton, { onClick: () => setApplyOnStartup(!settings.applyOnStartup), style: { width: "100%" } },
                    window.SP_REACT.createElement("div", { style: {
                            padding: "10px",
                            backgroundColor: settings.applyOnStartup ? "#1a9fff" : "#3d4450",
                            borderRadius: "6px",
                            display: "flex",
                            flexDirection: "column",
                            gap: "4px",
                        } },
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "11px",
                                fontWeight: "bold",
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                            } },
                            settings.applyOnStartup ? "✓" : "○",
                            " Apply on Startup"),
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "9px",
                                color: settings.applyOnStartup ? "#e0e0e0" : "#8b929a",
                                lineHeight: "1.3",
                            } }, "Automatically apply last profile when Steam Deck boots"))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: { marginBottom: "12px" } },
                window.SP_REACT.createElement(FocusableButton, { onClick: () => setGameOnlyMode(!settings.gameOnlyMode), style: { width: "100%" } },
                    window.SP_REACT.createElement("div", { style: {
                            padding: "10px",
                            backgroundColor: settings.gameOnlyMode ? "#1a9fff" : "#3d4450",
                            borderRadius: "6px",
                            display: "flex",
                            flexDirection: "column",
                            gap: "4px",
                        } },
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "11px",
                                fontWeight: "bold",
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                            } },
                            settings.gameOnlyMode ? "✓" : "○",
                            " Game Only Mode"),
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "9px",
                                color: settings.gameOnlyMode ? "#e0e0e0" : "#8b929a",
                                lineHeight: "1.3",
                            } }, "Apply undervolt only when games are running, reset in Steam menu"))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: { marginBottom: "8px" } },
                window.SP_REACT.createElement(FocusableButton, { onClick: handleSimpleModeToggle, style: { width: "100%" } },
                    window.SP_REACT.createElement("div", { style: {
                            padding: "6px",
                            backgroundColor: simpleMode ? "#1a9fff" : "#3d4450",
                            borderRadius: "4px",
                            fontSize: "9px",
                            fontWeight: "bold",
                            textAlign: "center",
                        } }, simpleMode ? "✓ Simple Mode" : "Per-Core Mode")))),
        settings.expertMode && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "6px",
                    backgroundColor: "#5c1313",
                    borderRadius: "4px",
                    border: "1px solid #ff6b6b",
                    marginBottom: "8px"
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "9px", color: "#ff9800", display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement(FaExclamationTriangle, { size: 9 }),
                    window.SP_REACT.createElement("span", null, "Expert mode active \u2022 Range: -100mV"))))),
        simpleMode ? (
        /* Simple Mode: Single slider for all cores */
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { label: "All Cores", value: simpleValue, min: currentMinLimit, max: 0, step: 1, showValue: true, onChange: handleSimpleValueChange, valueSuffix: " mV", bottomSeparator: "none" }))) : (
        /* Per-core sliders */
        [0, 1, 2, 3].map((core) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: core },
            window.SP_REACT.createElement(DFL.SliderField, { label: `Core ${core}`, value: coreValues[core], min: currentMinLimit, max: 0, step: 1, showValue: true, onChange: (value) => handleCoreChange(core, value), valueSuffix: " mV", bottomSeparator: "none" }))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "6px", marginTop: "8px" }, "flow-children": "horizontal" },
                window.SP_REACT.createElement(FocusableButton, { onClick: handleApply, disabled: isApplying, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "8px",
                            backgroundColor: "#1a9fff",
                            borderRadius: "6px",
                            fontSize: "10px",
                            fontWeight: "bold",
                        } },
                        isApplying ? window.SP_REACT.createElement(FaSpinner, { className: "spin", size: 10 }) : window.SP_REACT.createElement(FaCheck, { size: 10 }),
                        window.SP_REACT.createElement("span", null, "Apply"))),
                window.SP_REACT.createElement(FocusableButton, { onClick: handleDisable, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "8px",
                            backgroundColor: "#3d4450",
                            borderRadius: "6px",
                            fontSize: "10px",
                            fontWeight: "bold"
                        } },
                        window.SP_REACT.createElement(FaBan, { size: 10 }),
                        window.SP_REACT.createElement("span", null, "Disable"))),
                window.SP_REACT.createElement(FocusableButton, { onClick: handleReset, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "8px",
                            backgroundColor: "#5c4813",
                            borderRadius: "6px",
                            fontSize: "10px",
                            fontWeight: "bold",
                            color: "#ff9800"
                        } },
                        window.SP_REACT.createElement(FaTimes, { size: 10 }),
                        window.SP_REACT.createElement("span", null, "Reset"))))),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
/**
 * Diagnostics tab component.
 * Requirements: 7.5, 8.1, 8.2
 *
 * Features:
 * - System info display (platform, SteamOS version)
 * - Log viewer
 * - Export Diagnostics button
 */
const DiagnosticsTab = () => {
    const { api } = useDeckTune();
    const { info: platformInfo } = usePlatformInfo();
    const [systemInfo, setSystemInfo] = SP_REACT.useState(null);
    const [isExporting, setIsExporting] = SP_REACT.useState(false);
    const [exportResult, setExportResult] = SP_REACT.useState(null);
    const [isLoading, setIsLoading] = SP_REACT.useState(true);
    // Fetch system info on mount
    SP_REACT.useEffect(() => {
        const fetchSystemInfo = async () => {
            setIsLoading(true);
            try {
                const info = await api.getSystemInfo();
                setSystemInfo(info);
            }
            catch (e) {
                console.error("Failed to fetch system info:", e);
            }
            finally {
                setIsLoading(false);
            }
        };
        fetchSystemInfo();
    }, [api]);
    /**
     * Handle export diagnostics button click.
     */
    const handleExportDiagnostics = async () => {
        setIsExporting(true);
        setExportResult(null);
        try {
            const result = await api.exportDiagnostics();
            setExportResult(result);
        }
        catch (e) {
            setExportResult({ success: false, error: "Export failed" });
        }
        finally {
            setIsExporting(false);
        }
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "System Information")),
        isLoading ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", color: "#8b929a" } },
                window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                window.SP_REACT.createElement("span", null, "Loading system info...")))) : (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                } },
                window.SP_REACT.createElement(InfoRow, { label: "Platform", value: platformInfo ? `${platformInfo.variant} (${platformInfo.model})` : "Unknown" }),
                window.SP_REACT.createElement(InfoRow, { label: "Safe Limit", value: platformInfo ? `${platformInfo.safe_limit} mV` : "Unknown" }),
                window.SP_REACT.createElement(InfoRow, { label: "Detection", value: platformInfo?.detected ? "Successful" : "Failed" }),
                systemInfo && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement("div", { style: { borderTop: "1px solid #3d4450", margin: "8px 0" } }),
                    window.SP_REACT.createElement(InfoRow, { label: "SteamOS Version", value: systemInfo.steamos_version || "Unknown" }),
                    window.SP_REACT.createElement(InfoRow, { label: "Kernel", value: systemInfo.kernel || "Unknown" }),
                    window.SP_REACT.createElement(InfoRow, { label: "Hostname", value: systemInfo.hostname || "Unknown" }),
                    systemInfo.uptime && (window.SP_REACT.createElement(InfoRow, { label: "Uptime", value: formatUptime(systemInfo.uptime) }))))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Current Configuration")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                } }, systemInfo?.config ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(InfoRow, { label: "Active Cores", value: `[${systemInfo.config.cores?.join(", ") || "0, 0, 0, 0"}]` }),
                window.SP_REACT.createElement(InfoRow, { label: "LKG Cores", value: `[${systemInfo.config.lkg_cores?.join(", ") || "0, 0, 0, 0"}]` }),
                window.SP_REACT.createElement(InfoRow, { label: "Status", value: systemInfo.config.status || "Unknown" }),
                window.SP_REACT.createElement(InfoRow, { label: "Presets Count", value: String(systemInfo.config.presets_count || 0) }))) : (window.SP_REACT.createElement("div", { style: { color: "#8b929a" } }, "Configuration not available")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Recent Logs")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "8px",
                    backgroundColor: "#1a1d23",
                    borderRadius: "8px",
                    maxHeight: "150px",
                    overflowY: "auto",
                    fontFamily: "monospace",
                    fontSize: "10px",
                    color: "#8b929a",
                } }, systemInfo?.logs ? (systemInfo.logs.split("\n").slice(-20).map((line, index) => (window.SP_REACT.createElement("div", { key: index, style: { marginBottom: "2px" } }, line)))) : (window.SP_REACT.createElement("div", null, "No logs available")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { marginTop: "16px" } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExportDiagnostics, disabled: isExporting },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } }, isExporting ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                        window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                        window.SP_REACT.createElement("span", null, "Exporting..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                        window.SP_REACT.createElement(FaDownload, null),
                        window.SP_REACT.createElement("span", null, "Export Diagnostics"))))))),
        exportResult && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: exportResult.success ? "#1b5e20" : "#b71c1c",
                    borderRadius: "8px",
                    marginTop: "8px",
                } }, exportResult.success ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement("div", { style: { fontWeight: "bold", marginBottom: "4px" } },
                    window.SP_REACT.createElement(FaCheck, { style: { marginRight: "8px" } }),
                    "Export Successful"),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", wordBreak: "break-all" } },
                    "Saved to: ",
                    exportResult.path))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement("div", { style: { fontWeight: "bold" } },
                    window.SP_REACT.createElement(FaTimes, { style: { marginRight: "8px" } }),
                    "Export Failed"),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px" } }, exportResult.error)))))),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
const InfoRow = ({ label, value }) => (window.SP_REACT.createElement("div", { style: {
        display: "flex",
        justifyContent: "space-between",
        marginBottom: "6px",
        fontSize: "12px",
    } },
    window.SP_REACT.createElement("span", { style: { color: "#8b929a" } },
        label,
        ":"),
    window.SP_REACT.createElement("span", { style: { color: "#fff" } }, value)));
/**
 * Format uptime seconds to human readable string.
 */
const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const parts = [];
    if (days > 0)
        parts.push(`${days}d`);
    if (hours > 0)
        parts.push(`${hours}h`);
    if (mins > 0)
        parts.push(`${mins}m`);
    return parts.length > 0 ? parts.join(" ") : "< 1m";
};

/**
 * SetupWizard component for DeckTune first-run experience.
 *
 * Feature: decktune-3.1-reliability-ux, Setup Wizard
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
 *
 * Provides a guided setup process for new users:
 * - Step 1: Welcome with introduction
 * - Step 2: Explanation of undervolting benefits/risks
 * - Step 3: Goal selection with estimates
 * - Step 4: Confirmation and completion
 */

// ============================================================================
// Constants
// Requirements: 5.4
// ============================================================================
/**
 * Goal estimates for each preset goal.
 * Requirements: 5.4
 *
 * These estimates are based on typical Steam Deck undervolting results.
 * Actual results vary based on silicon quality and workload.
 */
const GOAL_ESTIMATES = {
    quiet: {
        batteryImprovement: "+10-15%",
        tempReduction: "-8-12°C",
        description: "Prioritizes lower temperatures and quieter fan operation. Best for casual gaming and media consumption.",
    },
    balanced: {
        batteryImprovement: "+15-20%",
        tempReduction: "-5-8°C",
        description: "Good balance between performance, battery life, and thermals. Recommended for most users.",
    },
    battery: {
        batteryImprovement: "+20-30%",
        tempReduction: "-3-5°C",
        description: "Maximizes battery life with aggressive power savings. Ideal for long gaming sessions away from power.",
    },
    performance: {
        batteryImprovement: "+5-10%",
        tempReduction: "-2-4°C",
        description: "Finds the most aggressive stable undervolt for maximum efficiency. For users who want every bit of optimization.",
    },
};
/**
 * Goal display information.
 * Requirements: 5.3
 */
const GOAL_INFO = {
    quiet: {
        label: "Quiet/Cool",
        icon: FaLeaf,
        color: "#4caf50",
    },
    balanced: {
        label: "Balanced",
        icon: FaBalanceScale,
        color: "#2196f3",
    },
    battery: {
        label: "Max Battery",
        icon: FaBatteryFull,
        color: "#ff9800",
    },
    performance: {
        label: "Max Performance",
        icon: FaRocket,
        color: "#f44336",
    },
};
const STEP_ORDER = ['welcome', 'explanation', 'goal', 'confirm'];
const StepIndicator = ({ currentStep }) => {
    const steps = [
        { id: 'welcome', label: 'Welcome' },
        { id: 'explanation', label: 'Learn' },
        { id: 'goal', label: 'Goal' },
        { id: 'confirm', label: 'Confirm' },
    ];
    const currentIndex = STEP_ORDER.indexOf(currentStep);
    return (window.SP_REACT.createElement(DFL.Focusable, { style: {
            display: "flex",
            justifyContent: "center",
            gap: "8px",
            marginBottom: "16px",
        } }, steps.map((s, index) => (window.SP_REACT.createElement("div", { key: s.id, style: {
            display: "flex",
            alignItems: "center",
            gap: "4px",
        } },
        window.SP_REACT.createElement("div", { style: {
                width: "24px",
                height: "24px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: currentIndex >= index ? "#1a9fff" : "#3d4450",
                color: currentIndex >= index ? "#fff" : "#8b929a",
                fontWeight: "bold",
                fontSize: "12px",
            } }, currentIndex > index ? window.SP_REACT.createElement(FaCheck, { size: 10 }) : index + 1),
        window.SP_REACT.createElement("span", { style: {
                color: currentIndex >= index ? "#fff" : "#8b929a",
                fontSize: "10px",
                display: index < steps.length - 1 ? "none" : "inline",
            } }, s.label),
        index < steps.length - 1 && (window.SP_REACT.createElement("div", { style: {
                width: "16px",
                height: "2px",
                backgroundColor: currentIndex > index ? "#1a9fff" : "#3d4450",
            } })))))));
};
const WelcomeStep = ({ onNext, onSkip }) => {
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    textAlign: "center",
                    padding: "16px",
                } },
                window.SP_REACT.createElement(FaBolt, { style: {
                        fontSize: "48px",
                        color: "#1a9fff",
                        marginBottom: "16px",
                    } }),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "18px",
                        fontWeight: "bold",
                        marginBottom: "8px",
                    } }, "Welcome to DeckTune!"),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "13px",
                        color: "#8b929a",
                        lineHeight: "1.5",
                    } }, "Let's set up your Steam Deck for optimal performance and battery life. This wizard will guide you through the process."))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onNext },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        color: "#1a9fff",
                    } },
                    window.SP_REACT.createElement("span", null, "Get Started"),
                    window.SP_REACT.createElement(FaArrowRight, null)))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onSkip },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        color: "#8b929a",
                        fontSize: "12px",
                    } },
                    window.SP_REACT.createElement("span", null, "Skip Setup"))))));
};
const ExplanationStep = ({ onNext, onBack, onSkip }) => {
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1a3a5c",
                    borderRadius: "8px",
                    marginBottom: "12px",
                } },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        marginBottom: "8px",
                    } },
                    window.SP_REACT.createElement(FaInfoCircle, { style: { color: "#1a9fff" } }),
                    window.SP_REACT.createElement("span", { style: { fontWeight: "bold" } }, "What is Undervolting?")),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "12px",
                        color: "#b0bec5",
                        lineHeight: "1.5",
                    } }, "Undervolting reduces the voltage supplied to your CPU while maintaining the same performance. This results in lower temperatures, quieter fans, and longer battery life."))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    gap: "8px",
                    marginBottom: "12px",
                } },
                window.SP_REACT.createElement("div", { style: {
                        flex: 1,
                        padding: "12px",
                        backgroundColor: "#1b5e20",
                        borderRadius: "8px",
                    } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            marginBottom: "6px",
                        } },
                        window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50" } }),
                        window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "12px" } }, "Benefits")),
                    window.SP_REACT.createElement("ul", { style: {
                            fontSize: "10px",
                            color: "#a5d6a7",
                            margin: 0,
                            paddingLeft: "16px",
                            lineHeight: "1.6",
                        } },
                        window.SP_REACT.createElement("li", null, "Lower temperatures"),
                        window.SP_REACT.createElement("li", null, "Quieter fan operation"),
                        window.SP_REACT.createElement("li", null, "Extended battery life"),
                        window.SP_REACT.createElement("li", null, "Same performance"))),
                window.SP_REACT.createElement("div", { style: {
                        flex: 1,
                        padding: "12px",
                        backgroundColor: "#5c4813",
                        borderRadius: "8px",
                    } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            marginBottom: "6px",
                        } },
                        window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#ff9800" } }),
                        window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "12px" } }, "Risks")),
                    window.SP_REACT.createElement("ul", { style: {
                            fontSize: "10px",
                            color: "#ffe0b2",
                            margin: 0,
                            paddingLeft: "16px",
                            lineHeight: "1.6",
                        } },
                        window.SP_REACT.createElement("li", null, "System instability if too aggressive"),
                        window.SP_REACT.createElement("li", null, "Requires testing"),
                        window.SP_REACT.createElement("li", null, "Results vary by chip"))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "10px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    fontSize: "11px",
                    color: "#8b929a",
                    textAlign: "center",
                } },
                window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50", marginRight: "6px" } }),
                "DeckTune includes automatic safety features and crash recovery.")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onBack, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                        } },
                        window.SP_REACT.createElement(FaArrowLeft, null),
                        window.SP_REACT.createElement("span", null, "Back"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onNext, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                            color: "#1a9fff",
                        } },
                        window.SP_REACT.createElement("span", null, "Next"),
                        window.SP_REACT.createElement(FaArrowRight, null))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onSkip },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#8b929a",
                        fontSize: "12px",
                    } },
                    window.SP_REACT.createElement("span", null, "Skip Setup"))))));
};
const GoalStep = ({ selectedGoal, onSelectGoal, onNext, onBack, onSkip, }) => {
    const goals = ['quiet', 'balanced', 'battery', 'performance'];
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    fontSize: "14px",
                    fontWeight: "bold",
                    marginBottom: "8px",
                } }, "Choose Your Goal"),
            window.SP_REACT.createElement("div", { style: {
                    fontSize: "11px",
                    color: "#8b929a",
                    marginBottom: "12px",
                } }, "Select what matters most to you. You can change this later.")),
        goals.map((goal) => {
            const info = GOAL_INFO[goal];
            const estimate = GOAL_ESTIMATES[goal];
            const Icon = info.icon;
            const isSelected = selectedGoal === goal;
            return (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: goal },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => onSelectGoal(goal), style: {
                        border: isSelected ? `2px solid ${info.color}` : "2px solid transparent",
                        borderRadius: "8px",
                    } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "flex-start",
                            gap: "12px",
                            padding: "4px",
                        } },
                        window.SP_REACT.createElement("div", { style: {
                                width: "36px",
                                height: "36px",
                                borderRadius: "8px",
                                backgroundColor: isSelected ? info.color : "#3d4450",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                flexShrink: 0,
                            } },
                            window.SP_REACT.createElement(Icon, { style: { color: "#fff", fontSize: "16px" } })),
                        window.SP_REACT.createElement("div", { style: { flex: 1, textAlign: "left" } },
                            window.SP_REACT.createElement("div", { style: {
                                    fontWeight: "bold",
                                    fontSize: "13px",
                                    color: isSelected ? info.color : "#fff",
                                } }, info.label),
                            window.SP_REACT.createElement("div", { style: {
                                    fontSize: "10px",
                                    color: "#8b929a",
                                    marginTop: "2px",
                                } },
                                estimate.description.split('.')[0],
                                ".")),
                        isSelected && (window.SP_REACT.createElement(FaCheck, { style: { color: info.color, fontSize: "14px" } }))))));
        }),
        selectedGoal && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginTop: "8px",
                } },
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "12px",
                        fontWeight: "bold",
                        marginBottom: "8px",
                        color: GOAL_INFO[selectedGoal].color,
                    } }, "Estimated Improvements"),
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        gap: "16px",
                    } },
                    window.SP_REACT.createElement("div", { style: { flex: 1 } },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                marginBottom: "4px",
                            } },
                            window.SP_REACT.createElement(FaBatteryFull, { style: { color: "#4caf50", fontSize: "12px" } }),
                            window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#8b929a" } }, "Battery")),
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "16px",
                                fontWeight: "bold",
                                color: "#4caf50",
                            } }, GOAL_ESTIMATES[selectedGoal].batteryImprovement)),
                    window.SP_REACT.createElement("div", { style: { flex: 1 } },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                marginBottom: "4px",
                            } },
                            window.SP_REACT.createElement(FaThermometerHalf, { style: { color: "#2196f3", fontSize: "12px" } }),
                            window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#8b929a" } }, "Temperature")),
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "16px",
                                fontWeight: "bold",
                                color: "#2196f3",
                            } }, GOAL_ESTIMATES[selectedGoal].tempReduction))),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "9px",
                        color: "#666",
                        marginTop: "8px",
                        fontStyle: "italic",
                    } }, "* Actual results vary based on silicon quality and workload")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onBack, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                        } },
                        window.SP_REACT.createElement(FaArrowLeft, null),
                        window.SP_REACT.createElement("span", null, "Back"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onNext, disabled: !selectedGoal, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                            color: selectedGoal ? "#1a9fff" : "#8b929a",
                            opacity: selectedGoal ? 1 : 0.5,
                        } },
                        window.SP_REACT.createElement("span", null, "Next"),
                        window.SP_REACT.createElement(FaArrowRight, null))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onSkip },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#8b929a",
                        fontSize: "12px",
                    } },
                    window.SP_REACT.createElement("span", null, "Skip Setup"))))));
};
const ConfirmStep = ({ selectedGoal, onConfirm, onBack, onCancel, isLoading, }) => {
    const info = GOAL_INFO[selectedGoal];
    const Icon = info.icon;
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    textAlign: "center",
                    padding: "16px",
                } },
                window.SP_REACT.createElement("div", { style: {
                        width: "64px",
                        height: "64px",
                        borderRadius: "50%",
                        backgroundColor: info.color,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        margin: "0 auto 16px",
                    } },
                    window.SP_REACT.createElement(Icon, { style: { color: "#fff", fontSize: "28px" } })),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "16px",
                        fontWeight: "bold",
                        marginBottom: "8px",
                    } }, "Ready to Start!"),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "12px",
                        color: "#8b929a",
                    } },
                    "You've selected ",
                    window.SP_REACT.createElement("strong", { style: { color: info.color } }, info.label)))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginBottom: "8px" } }, "What happens next:"),
                window.SP_REACT.createElement("ul", { style: {
                        fontSize: "11px",
                        color: "#b0bec5",
                        margin: 0,
                        paddingLeft: "20px",
                        lineHeight: "1.8",
                    } },
                    window.SP_REACT.createElement("li", null, "Your preferences will be saved"),
                    window.SP_REACT.createElement("li", null, "DeckTune will be configured for your goal"),
                    window.SP_REACT.createElement("li", null, "You can run autotune to find optimal values"),
                    window.SP_REACT.createElement("li", null, "Settings can be changed anytime in Expert mode")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onConfirm, disabled: isLoading, style: { marginTop: "12px" } },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        color: "#4caf50",
                    } },
                    window.SP_REACT.createElement(FaCheck, null),
                    window.SP_REACT.createElement("span", null, isLoading ? "Saving..." : "Complete Setup")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px" } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onBack, disabled: isLoading, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                        } },
                        window.SP_REACT.createElement(FaArrowLeft, null),
                        window.SP_REACT.createElement("span", null, "Back"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onCancel, disabled: isLoading, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                            color: "#ff6b6b",
                        } },
                        window.SP_REACT.createElement(FaTimes, null),
                        window.SP_REACT.createElement("span", null, "Cancel")))))));
};
// ============================================================================
// Main Component
// Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
// ============================================================================
/**
 * SetupWizard component - guided first-run experience.
 *
 * Requirements:
 * - 5.1: Display welcome wizard on first run
 * - 5.2: Explain undervolting benefits/risks
 * - 5.3: Offer preset goals with explanations
 * - 5.4: Show estimated improvements for selected goal
 * - 5.5: Save preferences on completion
 * - 5.6: Allow re-running wizard from settings
 * - 5.7: Allow skip/cancel without applying changes
 */
const SetupWizard = ({ onComplete, onCancel, onSkip, }) => {
    const { api } = useDeckTune();
    const { info: platformInfo } = usePlatformInfo();
    const [wizardState, setWizardState] = SP_REACT.useState({
        step: 'welcome',
        selectedGoal: null,
    });
    const [isLoading, setIsLoading] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState(null);
    /**
     * Navigate to next step.
     */
    const goToNextStep = () => {
        const stepOrder = ['welcome', 'explanation', 'goal', 'confirm'];
        const currentIndex = stepOrder.indexOf(wizardState.step);
        if (currentIndex < stepOrder.length - 1) {
            setWizardState((prev) => ({
                ...prev,
                step: stepOrder[currentIndex + 1],
            }));
        }
    };
    /**
     * Navigate to previous step.
     */
    const goToPreviousStep = () => {
        const stepOrder = ['welcome', 'explanation', 'goal', 'confirm'];
        const currentIndex = stepOrder.indexOf(wizardState.step);
        if (currentIndex > 0) {
            setWizardState((prev) => ({
                ...prev,
                step: stepOrder[currentIndex - 1],
            }));
        }
    };
    /**
     * Handle goal selection.
     * Requirements: 5.3
     */
    const handleSelectGoal = (goal) => {
        setWizardState((prev) => ({
            ...prev,
            selectedGoal: goal,
        }));
    };
    /**
     * Handle wizard completion.
     * Requirements: 5.5
     *
     * Saves preferences and marks first_run_complete.
     */
    const handleComplete = async () => {
        if (!wizardState.selectedGoal)
            return;
        setIsLoading(true);
        setError(null);
        try {
            // Save wizard settings via RPC
            await api.saveSetting('wizard_goal', wizardState.selectedGoal);
            await api.saveSetting('wizard_completed_at', new Date().toISOString());
            await api.saveSetting('first_run_complete', true);
            setWizardState((prev) => ({
                ...prev,
                step: 'complete',
            }));
            onComplete?.(wizardState.selectedGoal);
        }
        catch (e) {
            setError(String(e));
        }
        finally {
            setIsLoading(false);
        }
    };
    /**
     * Handle wizard cancellation.
     * Requirements: 5.7
     *
     * Does not modify any settings or apply any values.
     */
    const handleCancel = () => {
        // Reset state without saving anything
        setWizardState({
            step: 'welcome',
            selectedGoal: null,
        });
        onCancel?.();
    };
    /**
     * Handle wizard skip.
     * Requirements: 5.7
     *
     * Marks first_run_complete but doesn't apply any settings.
     */
    const handleSkip = async () => {
        try {
            // Only mark as complete, don't save any goal
            await api.saveSetting('first_run_complete', true);
            onSkip?.();
        }
        catch (e) {
            // Silently fail - user can still use the plugin
            onSkip?.();
        }
    };
    return (window.SP_REACT.createElement(DFL.PanelSection, { title: "Setup Wizard" },
        platformInfo && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    fontSize: "10px",
                    color: "#8b929a",
                    textAlign: "center",
                    marginBottom: "8px",
                } },
                "Detected: ",
                platformInfo.variant,
                " (",
                platformInfo.model,
                ")"))),
        wizardState.step !== 'complete' && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(StepIndicator, { currentStep: wizardState.step }))),
        error && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "8px",
                    backgroundColor: "#b71c1c",
                    borderRadius: "4px",
                    fontSize: "11px",
                    color: "#fff",
                    textAlign: "center",
                } }, error))),
        wizardState.step === 'welcome' && (window.SP_REACT.createElement(WelcomeStep, { onNext: goToNextStep, onSkip: handleSkip })),
        wizardState.step === 'explanation' && (window.SP_REACT.createElement(ExplanationStep, { onNext: goToNextStep, onBack: goToPreviousStep, onSkip: handleSkip })),
        wizardState.step === 'goal' && (window.SP_REACT.createElement(GoalStep, { selectedGoal: wizardState.selectedGoal, onSelectGoal: handleSelectGoal, onNext: goToNextStep, onBack: goToPreviousStep, onSkip: handleSkip })),
        wizardState.step === 'confirm' && wizardState.selectedGoal && (window.SP_REACT.createElement(ConfirmStep, { selectedGoal: wizardState.selectedGoal, onConfirm: handleComplete, onBack: goToPreviousStep, onCancel: handleCancel, isLoading: isLoading })),
        wizardState.step === 'complete' && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        textAlign: "center",
                        padding: "24px",
                    } },
                    window.SP_REACT.createElement("div", { style: {
                            width: "64px",
                            height: "64px",
                            borderRadius: "50%",
                            backgroundColor: "#4caf50",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            margin: "0 auto 16px",
                        } },
                        window.SP_REACT.createElement(FaCheck, { style: { color: "#fff", fontSize: "28px" } })),
                    window.SP_REACT.createElement("div", { style: {
                            fontSize: "18px",
                            fontWeight: "bold",
                            marginBottom: "8px",
                        } }, "Setup Complete!"),
                    window.SP_REACT.createElement("div", { style: {
                            fontSize: "12px",
                            color: "#8b929a",
                        } }, "DeckTune is ready to use. Head to Wizard mode to run autotune and find your optimal undervolt values.")))))));
};

/**
 * FanControl component for fan curve management.
 *
 * Feature: fan-control-curves
 * Requirements: 4.1, 4.2, 4.3
 *
 * Provides UI for:
 * - Preset selection (Stock, Silent, Turbo)
 * - Custom curve creation and management
 * - Real-time status display
 * - Navigation back to admin panel
 */

/**
 * FanControl component
 * Requirements: 4.1, 4.2, 4.3
 */
const FanControl = ({ onBack }) => {
    const [status, setStatus] = SP_REACT.useState(null);
    const [presets, setPresets] = SP_REACT.useState([]);
    const [customCurves, setCustomCurves] = SP_REACT.useState([]);
    const [isLoading, setIsLoading] = SP_REACT.useState(true);
    const [error, setError] = SP_REACT.useState(null);
    const [isApplying, setIsApplying] = SP_REACT.useState(false);
    const [showCustomEditor, setShowCustomEditor] = SP_REACT.useState(false);
    const [customCurveName, setCustomCurveName] = SP_REACT.useState("");
    const [customPoints, setCustomPoints] = SP_REACT.useState([
        { temp: 40, speed: 20 },
        { temp: 60, speed: 50 },
        { temp: 80, speed: 100 },
    ]);
    const [validationError, setValidationError] = SP_REACT.useState(null);
    // Load initial data
    SP_REACT.useEffect(() => {
        loadInitialData();
    }, []);
    // Poll status every 2 seconds
    SP_REACT.useEffect(() => {
        const interval = setInterval(() => {
            loadStatus();
        }, 2000);
        return () => clearInterval(interval);
    }, []);
    const loadInitialData = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Load presets
            const presetsResult = await call("fan_list_presets");
            if (presetsResult.success && presetsResult.presets) {
                setPresets(presetsResult.presets);
            }
            // Load custom curves
            const customResult = await call("fan_list_custom");
            if (customResult.success && customResult.curves) {
                setCustomCurves(customResult.curves);
            }
            // Load status
            await loadStatus();
        }
        catch (e) {
            setError(`Failed to load fan control data: ${e}`);
        }
        finally {
            setIsLoading(false);
        }
    };
    const loadStatus = async () => {
        try {
            const result = await call("fan_get_status");
            if (result.success && result.status) {
                setStatus(result.status);
            }
        }
        catch (e) {
            console.error("Failed to load fan status:", e);
        }
    };
    const applyPreset = async (presetName) => {
        setIsApplying(true);
        setError(null);
        try {
            const result = await call("fan_apply_preset", presetName);
            if (!result.success) {
                setError(result.error || "Failed to apply preset");
            }
            else {
                await loadStatus();
            }
        }
        catch (e) {
            setError(`Error applying preset: ${e}`);
        }
        finally {
            setIsApplying(false);
        }
    };
    const loadCustomCurve = async (curveName) => {
        setIsApplying(true);
        setError(null);
        try {
            const result = await call("fan_load_custom", curveName);
            if (!result.success) {
                setError(result.error || "Failed to load custom curve");
            }
            else {
                await loadStatus();
            }
        }
        catch (e) {
            setError(`Error loading custom curve: ${e}`);
        }
        finally {
            setIsApplying(false);
        }
    };
    const deleteCustomCurve = async (curveName) => {
        setError(null);
        try {
            const result = await call("fan_delete_custom", curveName);
            if (!result.success) {
                setError(result.error || "Failed to delete custom curve");
            }
            else {
                // Refresh custom curves list
                const customResult = await call("fan_list_custom");
                if (customResult.success && customResult.curves) {
                    setCustomCurves(customResult.curves);
                }
            }
        }
        catch (e) {
            setError(`Error deleting custom curve: ${e}`);
        }
    };
    const validatePoints = (points) => {
        // Check point count (3-10)
        if (points.length < 3) {
            return "Curve must have at least 3 points";
        }
        if (points.length > 10) {
            return "Curve cannot have more than 10 points";
        }
        // Check each point
        for (const point of points) {
            if (point.temp < 0 || point.temp > 120) {
                return `Temperature ${point.temp}°C is out of range [0, 120]`;
            }
            if (point.speed < 0 || point.speed > 100) {
                return `Speed ${point.speed}% is out of range [0, 100]`;
            }
        }
        return null;
    };
    const addPoint = () => {
        if (customPoints.length >= 10) {
            setValidationError("Cannot add more than 10 points");
            return;
        }
        // Add a new point between the last two points
        const lastPoint = customPoints[customPoints.length - 1];
        const secondLastPoint = customPoints[customPoints.length - 2];
        const newTemp = Math.round((lastPoint.temp + secondLastPoint.temp) / 2);
        const newSpeed = Math.round((lastPoint.speed + secondLastPoint.speed) / 2);
        setCustomPoints([...customPoints, { temp: newTemp, speed: newSpeed }]);
        setValidationError(null);
    };
    const removePoint = (index) => {
        if (customPoints.length <= 3) {
            setValidationError("Curve must have at least 3 points");
            return;
        }
        const newPoints = customPoints.filter((_, i) => i !== index);
        setCustomPoints(newPoints);
        setValidationError(null);
    };
    const updatePoint = (index, field, value) => {
        const numValue = parseInt(value, 10);
        if (isNaN(numValue))
            return;
        const newPoints = [...customPoints];
        newPoints[index] = { ...newPoints[index], [field]: numValue };
        setCustomPoints(newPoints);
        // Validate
        const error = validatePoints(newPoints);
        setValidationError(error);
    };
    const saveCustomCurve = async () => {
        // Validate curve name
        if (!customCurveName.trim()) {
            setValidationError("Please enter a curve name");
            return;
        }
        // Validate points
        const error = validatePoints(customPoints);
        if (error) {
            setValidationError(error);
            return;
        }
        setIsApplying(true);
        setValidationError(null);
        try {
            const result = await call("fan_create_custom", customCurveName.trim(), customPoints);
            if (!result.success) {
                setValidationError(result.error || "Failed to create custom curve");
            }
            else {
                // Refresh custom curves list
                const customResult = await call("fan_list_custom");
                if (customResult.success && customResult.curves) {
                    setCustomCurves(customResult.curves);
                }
                // Close editor
                setShowCustomEditor(false);
                setCustomCurveName("");
                setCustomPoints([
                    { temp: 40, speed: 20 },
                    { temp: 60, speed: 50 },
                    { temp: 80, speed: 100 },
                ]);
            }
        }
        catch (e) {
            setValidationError(`Error creating custom curve: ${e}`);
        }
        finally {
            setIsApplying(false);
        }
    };
    const openCustomEditor = () => {
        setShowCustomEditor(true);
        setValidationError(null);
        setCustomCurveName("");
        setCustomPoints([
            { temp: 40, speed: 20 },
            { temp: 60, speed: 50 },
            { temp: 80, speed: 100 },
        ]);
    };
    // Loading state
    if (isLoading) {
        return (window.SP_REACT.createElement(DFL.PanelSection, { title: "Fan Control" },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        padding: "24px",
                        color: "#8b929a",
                    } },
                    window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                    window.SP_REACT.createElement("span", null, "Loading fan control...")),
                window.SP_REACT.createElement("style", null, `
              .spin {
                animation: spin 1s linear infinite;
              }
              @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
              }
            `))));
    }
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSection, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.Focusable, null,
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onBack, style: {
                            minHeight: "40px",
                            padding: "8px 12px",
                            backgroundColor: "rgba(61, 68, 80, 0.5)",
                            borderRadius: "8px",
                        } },
                        window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                            window.SP_REACT.createElement(FaArrowLeft, { size: 14 }),
                            window.SP_REACT.createElement("span", null, "Back to Main View"))))),
            error && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        padding: "8px 12px",
                        backgroundColor: "#5c1313",
                        borderRadius: "6px",
                        marginBottom: "8px",
                        fontSize: "11px",
                        color: "#ffcdd2",
                        border: "1px solid #f44336",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                    } },
                    window.SP_REACT.createElement(FaExclamationTriangle, null),
                    error))),
            status && !status.hwmon_available && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        padding: "8px 12px",
                        backgroundColor: "#5c4813",
                        borderRadius: "6px",
                        marginBottom: "8px",
                        fontSize: "11px",
                        color: "#fff3cd",
                        border: "1px solid #ff9800",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                    } },
                    window.SP_REACT.createElement(FaExclamationTriangle, null),
                    "Hardware interface unavailable - fan control disabled")))),
        status && (window.SP_REACT.createElement(DFL.PanelSection, { title: "Current Status" },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "space-between",
                        padding: "8px 12px",
                        backgroundColor: "#23262e",
                        borderRadius: "8px",
                        fontSize: "13px",
                    } },
                    window.SP_REACT.createElement("div", null,
                        window.SP_REACT.createElement("div", { style: { color: "#8b929a", fontSize: "11px" } }, "Temperature"),
                        window.SP_REACT.createElement("div", { style: { fontWeight: "bold" } },
                            status.current_temp.toFixed(1),
                            "\u00B0C")),
                    window.SP_REACT.createElement("div", null,
                        window.SP_REACT.createElement("div", { style: { color: "#8b929a", fontSize: "11px" } }, "Current Speed"),
                        window.SP_REACT.createElement("div", { style: { fontWeight: "bold" } },
                            status.current_speed,
                            "%")),
                    window.SP_REACT.createElement("div", null,
                        window.SP_REACT.createElement("div", { style: { color: "#8b929a", fontSize: "11px" } }, "Target Speed"),
                        window.SP_REACT.createElement("div", { style: { fontWeight: "bold" } },
                            status.target_speed,
                            "%")))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        padding: "6px 12px",
                        backgroundColor: "#1a1d23",
                        borderRadius: "6px",
                        fontSize: "11px",
                        color: "#8b929a",
                        textAlign: "center",
                    } },
                    "Active: ",
                    status.active_curve,
                    " (",
                    status.curve_type,
                    ")")))),
        window.SP_REACT.createElement(DFL.PanelSection, { title: "Presets" }, presets.map((preset) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: preset },
            window.SP_REACT.createElement(DFL.Focusable, null,
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => applyPreset(preset), disabled: isApplying || (status && !status.hwmon_available), style: {
                        minHeight: "40px",
                        padding: "8px 12px",
                        backgroundColor: status?.active_curve === preset && status?.curve_type === "preset"
                            ? "#1a9fff"
                            : "rgba(61, 68, 80, 0.5)",
                        borderRadius: "8px",
                        border: status?.active_curve === preset && status?.curve_type === "preset"
                            ? "2px solid rgba(26, 159, 255, 0.5)"
                            : "2px solid transparent",
                    } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                        } },
                        window.SP_REACT.createElement("span", { style: { textTransform: "capitalize" } }, preset),
                        status?.active_curve === preset && status?.curve_type === "preset" && (window.SP_REACT.createElement("span", { style: { fontSize: "11px", color: "#4caf50" } }, "\u25CF Active"))))))))),
        window.SP_REACT.createElement(DFL.PanelSection, { title: "Custom Curves" },
            customCurves.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        textAlign: "center",
                        padding: "16px",
                        color: "#8b929a",
                        fontSize: "12px",
                    } }, "No custom curves created yet"))) : (customCurves.map((curve) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: curve },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        gap: "8px",
                        alignItems: "center",
                    } },
                    window.SP_REACT.createElement(DFL.Focusable, { style: { flex: 1 } },
                        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => loadCustomCurve(curve), disabled: isApplying || (status && !status.hwmon_available), style: {
                                minHeight: "40px",
                                padding: "8px 12px",
                                backgroundColor: status?.active_curve === curve && status?.curve_type === "custom"
                                    ? "#1a9fff"
                                    : "rgba(61, 68, 80, 0.5)",
                                borderRadius: "8px",
                                border: status?.active_curve === curve && status?.curve_type === "custom"
                                    ? "2px solid rgba(26, 159, 255, 0.5)"
                                    : "2px solid transparent",
                            } },
                            window.SP_REACT.createElement("div", { style: {
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                } },
                                window.SP_REACT.createElement("span", null, curve),
                                status?.active_curve === curve && status?.curve_type === "custom" && (window.SP_REACT.createElement("span", { style: { fontSize: "11px", color: "#4caf50" } }, "\u25CF Active"))))),
                    window.SP_REACT.createElement(DFL.Focusable, null,
                        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => deleteCustomCurve(curve), disabled: isApplying, style: {
                                minHeight: "40px",
                                padding: "8px 12px",
                                backgroundColor: "#5c1313",
                                borderRadius: "8px",
                                border: "1px solid #f44336",
                            } }, "Delete"))))))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.Focusable, null,
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: openCustomEditor, disabled: status && !status.hwmon_available, style: {
                            minHeight: "40px",
                            padding: "8px 12px",
                            backgroundColor: "rgba(26, 159, 255, 0.2)",
                            borderRadius: "8px",
                            border: "1px solid #1a9fff",
                        } }, "Edit Curve")))),
        showCustomEditor && (window.SP_REACT.createElement(DFL.ModalRoot, { onCancel: () => setShowCustomEditor(false) },
            window.SP_REACT.createElement(DFL.ModalHeader, null, "Create Custom Fan Curve"),
            window.SP_REACT.createElement(DFL.ModalBody, null,
                window.SP_REACT.createElement("div", { style: { padding: "16px" } },
                    window.SP_REACT.createElement("div", { style: { marginBottom: "16px" } },
                        window.SP_REACT.createElement("div", { style: { marginBottom: "8px", fontSize: "13px", color: "#8b929a" } }, "Curve Name"),
                        window.SP_REACT.createElement(DFL.TextField, { value: customCurveName, onChange: (e) => setCustomCurveName(e.target.value), placeholder: "Enter curve name", style: {
                                width: "100%",
                                padding: "8px",
                                backgroundColor: "#23262e",
                                border: "1px solid #3d4450",
                                borderRadius: "4px",
                                color: "#fff",
                            } })),
                    window.SP_REACT.createElement("div", { style: { marginBottom: "16px" } },
                        window.SP_REACT.createElement("div", { style: {
                                marginBottom: "8px",
                                fontSize: "13px",
                                color: "#8b929a",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                            } },
                            window.SP_REACT.createElement("span", null, "Curve Points (3-10)"),
                            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: addPoint, disabled: customPoints.length >= 10, style: {
                                    padding: "4px 8px",
                                    fontSize: "11px",
                                    backgroundColor: "rgba(76, 175, 80, 0.2)",
                                    border: "1px solid #4caf50",
                                    borderRadius: "4px",
                                } },
                                window.SP_REACT.createElement(FaPlus, { size: 10, style: { marginRight: "4px" } }),
                                "Add Point")),
                        customPoints.map((point, index) => (window.SP_REACT.createElement("div", { key: index, style: {
                                display: "flex",
                                gap: "8px",
                                marginBottom: "8px",
                                alignItems: "center",
                            } },
                            window.SP_REACT.createElement("div", { style: { flex: 1 } },
                                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginBottom: "4px" } }, "Temp (\u00B0C)"),
                                window.SP_REACT.createElement(DFL.TextField, { value: point.temp.toString(), onChange: (e) => updatePoint(index, "temp", e.target.value), type: "number", min: 0, max: 120, style: {
                                        width: "100%",
                                        padding: "6px",
                                        backgroundColor: "#23262e",
                                        border: "1px solid #3d4450",
                                        borderRadius: "4px",
                                        color: "#fff",
                                    } })),
                            window.SP_REACT.createElement("div", { style: { flex: 1 } },
                                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginBottom: "4px" } }, "Speed (%)"),
                                window.SP_REACT.createElement(DFL.TextField, { value: point.speed.toString(), onChange: (e) => updatePoint(index, "speed", e.target.value), type: "number", min: 0, max: 100, style: {
                                        width: "100%",
                                        padding: "6px",
                                        backgroundColor: "#23262e",
                                        border: "1px solid #3d4450",
                                        borderRadius: "4px",
                                        color: "#fff",
                                    } })),
                            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => removePoint(index), disabled: customPoints.length <= 3, style: {
                                    padding: "6px 8px",
                                    marginTop: "16px",
                                    backgroundColor: "rgba(244, 67, 54, 0.2)",
                                    border: "1px solid #f44336",
                                    borderRadius: "4px",
                                } },
                                window.SP_REACT.createElement(FaTrash, { size: 12 })))))),
                    validationError && (window.SP_REACT.createElement("div", { style: {
                            padding: "8px 12px",
                            backgroundColor: "#5c1313",
                            borderRadius: "6px",
                            marginBottom: "8px",
                            fontSize: "11px",
                            color: "#ffcdd2",
                            border: "1px solid #f44336",
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                        } },
                        window.SP_REACT.createElement(FaExclamationTriangle, null),
                        validationError)))),
            window.SP_REACT.createElement(DFL.ModalFooter, null,
                window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px", justifyContent: "flex-end" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setShowCustomEditor(false), disabled: isApplying, style: {
                            padding: "8px 16px",
                            backgroundColor: "rgba(61, 68, 80, 0.5)",
                            borderRadius: "4px",
                        } }, "Cancel"),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: saveCustomCurve, disabled: isApplying || !!validationError || !customCurveName.trim(), style: {
                            padding: "8px 16px",
                            backgroundColor: "#1a9fff",
                            borderRadius: "4px",
                        } }, isApplying ? "Saving..." : "Save Curve")))))));
};

/**
 * HeaderBar component for DeckTune.
 *
 * Feature: ui-refactor-settings
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 *
 * Provides compact navigation to Fan Control and Settings:
 * - Fan Control icon button (FaFan)
 * - Settings icon button (FaCog)
 * - Compact display with 20px icons
 * - Gamepad navigation support via FocusableButton
 */
/**
 * HeaderBar component - compact navigation for Fan Control and Settings.
 *
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 *
 * Features:
 * - Positioned at top of DeckTuneApp
 * - Two icon buttons: Fan Control (FaFan) and Settings (FaCog)
 * - Icons sized at 20px for compact display (Requirement 1.5)
 * - Gamepad navigation support via FocusableButton
 * - Hover and focus states for accessibility
 */
const HeaderBar = ({ onFanControlClick, onSettingsClick, }) => {
    return (window.SP_REACT.createElement("div", { style: {
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            gap: "8px",
            padding: "8px 12px",
            backgroundColor: "rgba(26, 29, 35, 0.5)",
            borderRadius: "8px",
            marginBottom: "12px",
        }, role: "navigation", "aria-label": "Quick navigation" },
        window.SP_REACT.createElement(FocusableButton, { onClick: onFanControlClick, style: { padding: 0 }, "aria-label": "Open Fan Control" },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "36px",
                    height: "36px",
                    backgroundColor: "rgba(61, 68, 80, 0.5)",
                    borderRadius: "6px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                } },
                window.SP_REACT.createElement(FaFan, { size: 20, color: "#8b929a", "aria-hidden": "true", style: { transition: "color 0.2s ease" } }))),
        window.SP_REACT.createElement(FocusableButton, { onClick: onSettingsClick, style: { padding: 0 }, "aria-label": "Open Settings" },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "36px",
                    height: "36px",
                    backgroundColor: "rgba(61, 68, 80, 0.5)",
                    borderRadius: "6px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                } },
                window.SP_REACT.createElement(FaCog, { size: 20, color: "#8b929a", "aria-hidden": "true", style: { transition: "color 0.2s ease" } })))));
};

/**
 * SettingsMenu component for DeckTune.
 *
 * Feature: ui-refactor-settings
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 *
 * Provides centralized settings management interface:
 * - Expert Mode toggle with confirmation dialog
 * - Binning Settings (test duration, step size, start value)
 * - Modal overlay with backdrop dismiss
 * - Gamepad navigation support
 * - Accessibility compliant (WCAG AA)
 */

/**
 * Expert Mode Warning Dialog component.
 *
 * Requirements: 2.3, 2.4, 9.3
 *
 * Displays warning about risks and requires explicit confirmation
 * before enabling Expert Mode.
 */
const ExpertWarningDialog = ({ isOpen, onConfirm, onCancel, }) => {
    if (!isOpen)
        return null;
    return (window.SP_REACT.createElement("div", { style: {
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.9)",
            zIndex: 10000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
        }, role: "dialog", "aria-modal": "true", "aria-labelledby": "expert-warning-title", "aria-describedby": "expert-warning-description" },
        window.SP_REACT.createElement("div", { style: {
                backgroundColor: "#1a1d23",
                borderRadius: "8px",
                padding: "16px",
                maxWidth: "400px",
                border: "2px solid #ff6b6b",
            } },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    marginBottom: "12px",
                } },
                window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#ff6b6b", fontSize: "20px" }, "aria-hidden": "true" }),
                window.SP_REACT.createElement("div", { id: "expert-warning-title", style: {
                        fontSize: "14px",
                        fontWeight: "bold",
                        color: "#ff6b6b",
                    } }, "Expert Undervolter Mode")),
            window.SP_REACT.createElement("div", { id: "expert-warning-description", style: {
                    fontSize: "11px",
                    lineHeight: "1.5",
                    marginBottom: "12px",
                    color: "#e0e0e0",
                } },
                window.SP_REACT.createElement("p", { style: { marginBottom: "8px" } },
                    window.SP_REACT.createElement("strong", null, "\u26A0\uFE0F WARNING:"),
                    " Expert mode removes safety limits."),
                window.SP_REACT.createElement("p", { style: { marginBottom: "8px", color: "#ff9800" } },
                    window.SP_REACT.createElement("strong", null, "Risks:"),
                    " System instability, crashes, data loss, hardware damage."),
                window.SP_REACT.createElement("p", { style: { color: "#f44336", fontWeight: "bold", fontSize: "10px" } }, "Use at your own risk!")),
            window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px" }, "flow-children": "horizontal" },
                window.SP_REACT.createElement(FocusableButton, { onClick: onConfirm, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "8px",
                            backgroundColor: "#b71c1c",
                            borderRadius: "4px",
                            fontSize: "10px",
                            fontWeight: "bold",
                        } },
                        window.SP_REACT.createElement(FaCheck, { size: 10, "aria-hidden": "true" }),
                        window.SP_REACT.createElement("span", null, "I Understand"))),
                window.SP_REACT.createElement(FocusableButton, { onClick: onCancel, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                            padding: "8px",
                            backgroundColor: "#3d4450",
                            borderRadius: "4px",
                            fontSize: "10px",
                            fontWeight: "bold",
                        } },
                        window.SP_REACT.createElement(FaTimes, { size: 10, "aria-hidden": "true" }),
                        window.SP_REACT.createElement("span", null, "Cancel")))))));
};
/**
 * SettingsMenu component - centralized settings management.
 *
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5
 *
 * Features:
 * - Modal overlay with backdrop dismiss
 * - Expert Mode toggle with confirmation
 * - Binning Settings (test duration, step size, start value)
 * - Auto-save on changes (Requirement 9.4)
 * - Gamepad navigation support
 * - WCAG AA compliant
 */
const SettingsMenu = ({ isOpen, onClose }) => {
    const { settings, setExpertMode } = useSettings();
    const [showExpertWarning, setShowExpertWarning] = SP_REACT.useState(false);
    // Binning config state
    const [binningConfig, setBinningConfig] = SP_REACT.useState({
        test_duration: 60,
        step_size: 5,
        start_value: -10,
    });
    const [binningLoaded, setBinningLoaded] = SP_REACT.useState(false);
    // Load binning config on mount
    SP_REACT.useEffect(() => {
        if (isOpen && !binningLoaded) {
            loadBinningConfig();
        }
    }, [isOpen]);
    const loadBinningConfig = async () => {
        try {
            const response = await call("get_binning_config");
            if (response.success && response.config) {
                setBinningConfig({
                    test_duration: response.config.test_duration || 60,
                    step_size: response.config.step_size || 5,
                    start_value: response.config.start_value || -10,
                });
                setBinningLoaded(true);
            }
        }
        catch (err) {
            console.error("Failed to load binning config:", err);
        }
    };
    const updateBinningConfig = async (updates) => {
        const newConfig = { ...binningConfig, ...updates };
        setBinningConfig(newConfig);
        try {
            await call("update_binning_config", newConfig);
        }
        catch (err) {
            console.error("Failed to update binning config:", err);
        }
    };
    if (!isOpen)
        return null;
    /**
     * Handle Expert Mode toggle.
     *
     * Requirements: 2.3, 2.4
     * Shows confirmation dialog when enabling, directly disables when turning off.
     */
    const handleExpertModeToggle = () => {
        if (!settings.expertMode) {
            // Enabling - show warning dialog
            setShowExpertWarning(true);
        }
        else {
            // Disabling - no confirmation needed
            setExpertMode(false);
        }
    };
    /**
     * Handle Expert Mode confirmation.
     *
     * Requirements: 2.4, 9.4
     */
    const handleExpertModeConfirm = async () => {
        await setExpertMode(true);
        setShowExpertWarning(false);
    };
    /**
     * Handle Expert Mode cancellation.
     *
     * Requirements: 2.4
     */
    const handleExpertModeCancel = () => {
        setShowExpertWarning(false);
    };
    /**
     * Handle backdrop click to close menu.
     *
     * Requirements: 2.1, 9.5
     */
    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement("div", { style: {
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(0, 0, 0, 0.85)",
                zIndex: 9999,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px",
            }, onClick: handleBackdropClick, role: "dialog", "aria-modal": "true", "aria-labelledby": "settings-menu-title" },
            window.SP_REACT.createElement("div", { style: {
                    backgroundColor: "#1a1d23",
                    borderRadius: "8px",
                    padding: "16px",
                    maxWidth: "400px",
                    width: "100%",
                    border: "1px solid #3d4450",
                }, onClick: (e) => e.stopPropagation() },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        marginBottom: "16px",
                    } },
                    window.SP_REACT.createElement("h2", { id: "settings-menu-title", style: {
                            fontSize: "16px",
                            fontWeight: "bold",
                            color: "#fff",
                            margin: 0,
                        } }, "Settings"),
                    window.SP_REACT.createElement(FocusableButton, { onClick: onClose },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                width: "32px",
                                height: "32px",
                                backgroundColor: "#3d4450",
                                borderRadius: "4px",
                                cursor: "pointer",
                            }, "aria-label": "Close settings" },
                            window.SP_REACT.createElement(FaTimes, { size: 14, color: "#fff", "aria-hidden": "true" })))),
                window.SP_REACT.createElement(DFL.PanelSection, null,
                    window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                        window.SP_REACT.createElement("div", { style: { marginBottom: "16px" } },
                            window.SP_REACT.createElement("div", { style: {
                                    fontSize: "12px",
                                    fontWeight: "bold",
                                    color: "#fff",
                                    marginBottom: "8px",
                                } }, "Expert Mode"),
                            window.SP_REACT.createElement("div", { style: {
                                    fontSize: "10px",
                                    color: "#8b929a",
                                    marginBottom: "8px",
                                    lineHeight: "1.4",
                                } }, "Removes safety limits for advanced undervolting. Use with caution."),
                            window.SP_REACT.createElement(FocusableButton, { onClick: handleExpertModeToggle, style: { width: "100%" } },
                                window.SP_REACT.createElement("div", { style: {
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "space-between",
                                        padding: "10px 12px",
                                        backgroundColor: settings.expertMode
                                            ? "#b71c1c"
                                            : "#3d4450",
                                        borderRadius: "4px",
                                        fontSize: "11px",
                                        fontWeight: "bold",
                                    }, role: "switch", "aria-checked": settings.expertMode, "aria-label": "Expert Mode toggle" },
                                    window.SP_REACT.createElement("span", null, settings.expertMode ? "⚠ Expert Mode" : "Expert Mode"),
                                    window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#8b929a" } }, settings.expertMode ? "ON" : "OFF"))))),
                    window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                        window.SP_REACT.createElement("div", { style: { marginBottom: "16px" } },
                            window.SP_REACT.createElement("div", { style: {
                                    fontSize: "12px",
                                    fontWeight: "bold",
                                    color: "#fff",
                                    marginBottom: "8px",
                                } }, "Wizard Settings"),
                            window.SP_REACT.createElement("div", { style: {
                                    fontSize: "10px",
                                    color: "#8b929a",
                                    marginBottom: "12px",
                                    lineHeight: "1.4",
                                } }, "Advanced configuration for Wizard Mode testing algorithm."),
                            window.SP_REACT.createElement("div", { style: { display: "flex", flexDirection: "column", gap: "12px" } },
                                window.SP_REACT.createElement("div", null,
                                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginBottom: "4px" } },
                                        "Test Duration: ",
                                        binningConfig.test_duration,
                                        "s"),
                                    window.SP_REACT.createElement("input", { type: "range", min: 30, max: 300, step: 10, value: binningConfig.test_duration, onChange: (e) => updateBinningConfig({ test_duration: parseInt(e.target.value) }), style: { width: "100%" } })),
                                window.SP_REACT.createElement("div", null,
                                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginBottom: "4px" } },
                                        "Step Size: ",
                                        binningConfig.step_size,
                                        "mV"),
                                    window.SP_REACT.createElement("input", { type: "range", min: 1, max: 10, step: 1, value: binningConfig.step_size, onChange: (e) => updateBinningConfig({ step_size: parseInt(e.target.value) }), style: { width: "100%" } })),
                                window.SP_REACT.createElement("div", null,
                                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginBottom: "4px" } },
                                        "Start Value: ",
                                        binningConfig.start_value,
                                        "mV"),
                                    window.SP_REACT.createElement("input", { type: "range", min: 5, max: 20, step: 5, value: Math.abs(binningConfig.start_value), onChange: (e) => updateBinningConfig({ start_value: -parseInt(e.target.value) }), style: { width: "100%" } }))))),
                    window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                        window.SP_REACT.createElement("div", { style: {
                                fontSize: "9px",
                                color: "#4caf50",
                                textAlign: "center",
                                padding: "4px",
                            } }, "\u2713 Changes saved automatically"))))),
        window.SP_REACT.createElement(ExpertWarningDialog, { isOpen: showExpertWarning, onConfirm: handleExpertModeConfirm, onCancel: handleExpertModeCancel })));
};

/**
 * DeckTuneApp - Main application component.
 *
 * Feature: ui-refactor-settings
 * Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.3, 8.4, 8.5
 */

/**
 * Main content component with mode switching and first-run detection.
 *
 * Feature: ui-refactor-settings
 * Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.3, 8.4, 8.5
 */
const DeckTuneContent = () => {
    // Load saved mode from localStorage, default to wizard
    // Requirements: 8.1, 8.2 - Fan Control accessed only via header, not in mode list
    const [mode, setMode] = SP_REACT.useState(() => {
        try {
            const saved = localStorage.getItem('decktune_ui_mode');
            return (saved === "expert" || saved === "wizard" || saved === "fan") ? saved : "wizard";
        }
        catch {
            return "wizard";
        }
    });
    // Settings Menu visibility state - Requirements: 1.3
    const [showSettingsMenu, setShowSettingsMenu] = SP_REACT.useState(false);
    const [showSetupWizard, setShowSetupWizard] = SP_REACT.useState(false);
    const [isFirstRun, setIsFirstRun] = SP_REACT.useState(null);
    const { state, api } = useDeckTune();
    // Save mode to localStorage whenever it changes
    // Requirements: 8.5 - Preserve mode state when navigating to/from Fan Control
    SP_REACT.useEffect(() => {
        try {
            localStorage.setItem('decktune_ui_mode', mode);
            // Save last non-fan mode for back navigation
            if (mode !== "fan") {
                localStorage.setItem('decktune_last_mode', mode);
            }
        }
        catch (e) {
            console.error("Failed to save UI mode:", e);
        }
    }, [mode]);
    SP_REACT.useEffect(() => {
        const checkFirstRun = async () => {
            try {
                const firstRunComplete = await api.getSetting('first_run_complete');
                const isNew = firstRunComplete !== true;
                setIsFirstRun(isNew);
                if (isNew) {
                    setShowSetupWizard(true);
                }
            }
            catch {
                setIsFirstRun(true);
                setShowSetupWizard(true);
            }
        };
        checkFirstRun();
    }, [api]);
    const handleSetupComplete = () => {
        setShowSetupWizard(false);
        setIsFirstRun(false);
    };
    const handleSetupCancel = () => {
        setShowSetupWizard(false);
    };
    const handleSetupSkip = () => {
        setShowSetupWizard(false);
        setIsFirstRun(false);
    };
    /**
     * Handle Fan Control navigation from header.
     * Requirements: 1.2, 8.3, 8.5
     */
    const handleFanControlClick = () => {
        setMode("fan");
    };
    /**
     * Handle Settings navigation from header.
     * Requirements: 1.3
     */
    const handleSettingsClick = () => {
        setShowSettingsMenu(true);
    };
    /**
     * Handle back navigation from Fan Control.
     * Requirements: 8.4, 8.5 - Preserve previously selected mode
     */
    const handleFanControlBack = () => {
        // Return to the last non-fan mode (wizard or expert)
        const lastMode = localStorage.getItem('decktune_last_mode');
        if (lastMode === "expert" || lastMode === "wizard") {
            setMode(lastMode);
        }
        else {
            setMode("wizard");
        }
    };
    if (showSetupWizard) {
        return (window.SP_REACT.createElement(SetupWizard, { onComplete: handleSetupComplete, onCancel: handleSetupCancel, onSkip: handleSetupSkip }));
    }
    if (isFirstRun === null) {
        return (window.SP_REACT.createElement(DFL.PanelSection, { title: "DeckTune" },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "16px", color: "#8b929a" } },
                    window.SP_REACT.createElement("div", { className: "loading-spinner" }),
                    "Loading..."))));
    }
    const getStatusColor = () => {
        if (state.status === "enabled" || state.status === "DYNAMIC RUNNING")
            return "#4caf50";
        if (state.status === "error")
            return "#f44336";
        return "#8b929a";
    };
    const getStatusText = () => {
        if (state.status === "DYNAMIC RUNNING")
            return "DYN";
        if (state.status === "enabled")
            return "ON";
        if (state.status === "error")
            return "ERR";
        return "OFF";
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement("style", null, `
          @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
          
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
          }
          
          @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px rgba(26, 159, 255, 0.3); }
            50% { box-shadow: 0 0 20px rgba(26, 159, 255, 0.6); }
          }
          
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          
          .mode-button {
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          }
          
          .mode-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
          }
          
          .mode-button:hover::before {
            left: 100%;
          }
          
          .mode-button.active {
            background: linear-gradient(135deg, #1a9fff 0%, #0d7fd8 100%);
            animation: glow 2s ease-in-out infinite;
          }
          
          .status-badge {
            animation: pulse 2s ease-in-out infinite;
          }
          
          .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(139, 146, 154, 0.3);
            border-top-color: #1a9fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 8px;
          }
          
          .fade-in {
            animation: fadeInUp 0.5s ease-out;
          }
        `),
        window.SP_REACT.createElement(HeaderBar, { onFanControlClick: handleFanControlClick, onSettingsClick: handleSettingsClick }),
        window.SP_REACT.createElement(SettingsMenu, { isOpen: showSettingsMenu, onClose: () => setShowSettingsMenu(false) }),
        window.SP_REACT.createElement(DFL.PanelSection, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", flexDirection: "column", gap: "6px" } },
                    window.SP_REACT.createElement(DFL.Focusable, { className: "fade-in", style: {
                            minHeight: "40px",
                            padding: "8px 12px",
                            backgroundColor: mode === "wizard" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                            borderRadius: "8px",
                            border: mode === "wizard" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
                            position: "relative",
                            overflow: "hidden",
                            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                            cursor: "pointer",
                        }, onActivate: () => setMode("wizard"), onClick: () => setMode("wizard") },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                fontSize: "12px",
                                fontWeight: mode === "wizard" ? "bold" : "normal",
                                color: mode === "wizard" ? "#fff" : "#8b929a"
                            } },
                            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                                window.SP_REACT.createElement(FaMagic, { size: 14, style: {
                                        filter: mode === "wizard" ? "drop-shadow(0 0 4px rgba(255,255,255,0.5))" : "none"
                                    } }),
                                window.SP_REACT.createElement("span", null, "Wizard Mode")),
                            mode === "wizard" && (window.SP_REACT.createElement("div", { className: "status-badge", style: {
                                    fontSize: "9px",
                                    color: "#fff",
                                    padding: "3px 6px",
                                    backgroundColor: getStatusColor(),
                                    borderRadius: "4px",
                                    fontWeight: "bold",
                                    boxShadow: `0 0 10px ${getStatusColor()}`,
                                } }, getStatusText())))),
                    window.SP_REACT.createElement(DFL.Focusable, { className: "fade-in", style: {
                            minHeight: "40px",
                            padding: "8px 12px",
                            backgroundColor: mode === "expert" ? "#1a9fff" : "rgba(61, 68, 80, 0.5)",
                            borderRadius: "8px",
                            border: mode === "expert" ? "2px solid rgba(26, 159, 255, 0.5)" : "2px solid transparent",
                            position: "relative",
                            overflow: "hidden",
                            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                            cursor: "pointer",
                            animationDelay: "0.1s"
                        }, onActivate: () => setMode("expert"), onClick: () => setMode("expert") },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                fontSize: "12px",
                                fontWeight: mode === "expert" ? "bold" : "normal",
                                color: mode === "expert" ? "#fff" : "#8b929a"
                            } },
                            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                                window.SP_REACT.createElement(FaCog, { size: 14, style: {
                                        filter: mode === "expert" ? "drop-shadow(0 0 4px rgba(255,255,255,0.5))" : "none",
                                        animation: mode === "expert" ? "spin 3s linear infinite" : "none"
                                    } }),
                                window.SP_REACT.createElement("span", null, "Expert Mode")),
                            mode === "expert" && (window.SP_REACT.createElement("div", { className: "status-badge", style: {
                                    fontSize: "9px",
                                    color: "#fff",
                                    padding: "3px 6px",
                                    backgroundColor: getStatusColor(),
                                    borderRadius: "4px",
                                    fontWeight: "bold",
                                    boxShadow: `0 0 10px ${getStatusColor()}`,
                                } }, getStatusText()))))))),
        window.SP_REACT.createElement("div", { className: "fade-in", style: { animationDelay: "0.3s" } }, mode === "wizard" ? (window.SP_REACT.createElement(WizardMode, null)) : mode === "expert" ? (window.SP_REACT.createElement(ExpertMode, null)) : (window.SP_REACT.createElement(FanControl, { onBack: handleFanControlBack })))));
};
/**
 * Main app component with initialization.
 * Wrapped with SettingsProvider for persistent settings management.
 *
 * Feature: ui-refactor-settings
 * Requirements: 10.1, 10.5
 */
const DeckTuneApp = () => {
    const [initialized, setInitialized] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState(null);
    SP_REACT.useEffect(() => {
        const initPlugin = async () => {
            try {
                const api = getApiInstance(initialState);
                await api.init();
                setInitialized(true);
            }
            catch (e) {
                console.error("DeckTune init error:", e);
                setError(String(e));
            }
        };
        initPlugin();
        const handleServerEvent = (event) => {
            const api = getApiInstance(initialState);
            api.handleServerEvent(event);
        };
        addEventListener("server_event", handleServerEvent);
        return () => {
            removeEventListener("server_event", handleServerEvent);
            const api = getApiInstance(initialState);
            api.destroy();
        };
    }, []);
    if (error) {
        return (window.SP_REACT.createElement(DFL.PanelSection, { title: "DeckTune" },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { color: "#f44336", textAlign: "center", padding: "16px" } },
                    "Failed to initialize: ",
                    error))));
    }
    if (!initialized) {
        return (window.SP_REACT.createElement(DFL.PanelSection, { title: "DeckTune" },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "16px", color: "#8b929a" } }, "Loading..."))));
    }
    // Wrap content with SettingsProvider - Requirements: 10.1, 10.5
    return (window.SP_REACT.createElement(SettingsProvider, null,
        window.SP_REACT.createElement(DeckTuneContent, null)));
};

/**
 * ErrorBoundary component for DeckTune.
 *
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 *
 * Catches React render errors and displays a fallback UI instead of crashing.
 */

/**
 * Error Boundary component that catches render errors.
 *
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 */
class DeckTuneErrorBoundary extends SP_REACT.Component {
    constructor(props) {
        super(props);
        this.handleReset = () => {
            this.setState({
                hasError: false,
                error: null,
                errorInfo: null,
            });
        };
        this.handleGoBack = () => {
            // Reset error and try to navigate back
            this.setState({
                hasError: false,
                error: null,
                errorInfo: null,
            });
            // Force parent to re-render by triggering a state change
            window.history.back();
        };
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error("DeckTune render error:", error, errorInfo);
        this.setState({ errorInfo });
    }
    render() {
        if (this.state.hasError) {
            // Custom fallback if provided
            if (this.props.fallback) {
                return this.props.fallback;
            }
            // Default fallback UI
            return (window.SP_REACT.createElement(DFL.PanelSection, { title: "DeckTune" },
                window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: "12px",
                            padding: "16px",
                            backgroundColor: "#5c1313",
                            borderRadius: "8px",
                            border: "1px solid #f44336",
                        } },
                        window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#f44336", fontSize: "32px" } }),
                        window.SP_REACT.createElement("div", { style: {
                                color: "#ffcdd2",
                                textAlign: "center",
                                fontSize: "14px",
                            } }, "\u041F\u0440\u043E\u0438\u0437\u043E\u0448\u043B\u0430 \u043E\u0448\u0438\u0431\u043A\u0430 \u0440\u0435\u043D\u0434\u0435\u0440\u0438\u043D\u0433\u0430"),
                        window.SP_REACT.createElement("div", { style: {
                                color: "#ef9a9a",
                                textAlign: "center",
                                fontSize: "11px",
                                maxWidth: "280px",
                                wordBreak: "break-word",
                            } }, this.state.error?.message || "Unknown error"))),
                window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: this.handleReset, style: { marginTop: "8px" } },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: "8px",
                            } },
                            window.SP_REACT.createElement(FaRedo, null),
                            window.SP_REACT.createElement("span", null, "\u041F\u043E\u043F\u0440\u043E\u0431\u043E\u0432\u0430\u0442\u044C \u0441\u043D\u043E\u0432\u0430"))))));
        }
        return this.props.children;
    }
}

// NUCLEAR CACHE BUST - Force new module evaluation
const BUILD_TIMESTAMP = "20260118-2115";
const BUILD_VERSION = "v3.1.16-INLINE-FOCUS";
console.log(`[DeckTune CACHE BUST] Plugin index.tsx loaded - ${BUILD_VERSION} - ${BUILD_TIMESTAMP}`);
window.__DECKTUNE_BUILD_TIMESTAMP__ = BUILD_TIMESTAMP;
window.__DECKTUNE_BUILD_VERSION__ = BUILD_VERSION;
// Inject global CSS to disable ALL default focus styles
if (typeof document !== 'undefined') {
    const styleId = 'decktune-no-default-focus';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
      /* Disable ALL default Decky UI focus styles */
      .decktune-plugin * {
        outline: none !important;
      }
      
      .decktune-plugin *:focus,
      .decktune-plugin *:focus-visible,
      .decktune-plugin .gpfocus {
        outline: none !important;
        box-shadow: none !important;
      }
      
      /* Disable focus ring on all Focusable components */
      .decktune-plugin [class*="Focusable"]:focus {
        outline: none !important;
      }
    `;
        document.head.appendChild(style);
        console.log('[DeckTune] Global focus styles disabled');
    }
}
/**
 * Title view component that shows status badge in plugin list.
 */
const DeckTuneTitleView = () => {
    const { state } = useDeckTune();
    const getStatusColor = () => {
        if (state.status === "enabled" || state.status === "DYNAMIC RUNNING")
            return "#4caf50";
        if (state.status === "error")
            return "#f44336";
        return "#8b929a";
    };
    const getStatusText = () => {
        if (state.status === "DYNAMIC RUNNING")
            return "DYN";
        if (state.status === "enabled")
            return "ON";
        if (state.status === "error")
            return "ERR";
        return "OFF";
    };
    return (window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
        window.SP_REACT.createElement("span", null, "DeckTune"),
        window.SP_REACT.createElement("div", { style: {
                fontSize: "9px",
                fontWeight: "bold",
                color: "#fff",
                padding: "2px 6px",
                backgroundColor: getStatusColor(),
                borderRadius: "4px",
                boxShadow: `0 0 8px ${getStatusColor()}`,
                animation: state.status === "enabled" || state.status === "DYNAMIC RUNNING" ? "pulse 2s ease-in-out infinite" : "none"
            } }, getStatusText()),
        window.SP_REACT.createElement("style", null, `
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `)));
};
/**
 * DeckTune plugin entry point.
 *
 * Feature: decktune-critical-fixes
 * Validates: Requirements 4.5
 */
var index = definePlugin(() => {
    return {
        name: "DeckTune",
        titleView: (window.SP_REACT.createElement(DeckTuneErrorBoundary, null,
            window.SP_REACT.createElement(DeckTuneProvider, null,
                window.SP_REACT.createElement(WizardProvider, null,
                    window.SP_REACT.createElement(DeckTuneTitleView, null))))),
        content: (window.SP_REACT.createElement(DeckTuneErrorBoundary, null,
            window.SP_REACT.createElement(DeckTuneProvider, null,
                window.SP_REACT.createElement(WizardProvider, null,
                    window.SP_REACT.createElement("div", { className: "decktune-plugin" },
                        window.SP_REACT.createElement(DeckTuneApp, null)))))),
        icon: window.SP_REACT.createElement(FaMagic, null),
        onDismount() {
            console.log("DeckTune unloaded");
        },
    };
});

export { index as default };
//# sourceMappingURL=index.js.map
