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
}function FaBalanceScale (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M256 336h-.02c0-16.18 1.34-8.73-85.05-181.51-17.65-35.29-68.19-35.36-85.87 0C-2.06 328.75.02 320.33.02 336H0c0 44.18 57.31 80 128 80s128-35.82 128-80zM128 176l72 144H56l72-144zm511.98 160c0-16.18 1.34-8.73-85.05-181.51-17.65-35.29-68.19-35.36-85.87 0-87.12 174.26-85.04 165.84-85.04 181.51H384c0 44.18 57.31 80 128 80s128-35.82 128-80h-.02zM440 320l72-144 72 144H440zm88 128H352V153.25c23.51-10.29 41.16-31.48 46.39-57.25H528c8.84 0 16-7.16 16-16V48c0-8.84-7.16-16-16-16H383.64C369.04 12.68 346.09 0 320 0s-49.04 12.68-63.64 32H112c-8.84 0-16 7.16-16 16v32c0 8.84 7.16 16 16 16h129.61c5.23 25.76 22.87 46.96 46.39 57.25V448H112c-8.84 0-16 7.16-16 16v32c0 8.84 7.16 16 16 16h416c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16z"},"child":[]}]})(props);
}function FaBan (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119.034 8 8 119.033 8 256s111.034 248 248 248 248-111.034 248-248S392.967 8 256 8zm130.108 117.892c65.448 65.448 70 165.481 20.677 235.637L150.47 105.216c70.204-49.356 170.226-44.735 235.638 20.676zM125.892 386.108c-65.448-65.448-70-165.481-20.677-235.637L361.53 406.784c-70.203 49.356-170.226 44.736-235.638-20.676z"},"child":[]}]})(props);
}function FaBatteryFull (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M544 160v64h32v64h-32v64H64V160h480m16-64H48c-26.51 0-48 21.49-48 48v224c0 26.51 21.49 48 48 48h512c26.51 0 48-21.49 48-48v-16h8c13.255 0 24-10.745 24-24V184c0-13.255-10.745-24-24-24h-8v-16c0-26.51-21.49-48-48-48zm-48 96H96v128h416V192z"},"child":[]}]})(props);
}function FaBolt (props) {
  return GenIcon({"attr":{"viewBox":"0 0 320 512"},"child":[{"tag":"path","attr":{"d":"M296 160H180.6l42.6-129.8C227.2 15 215.7 0 200 0H56C44 0 33.8 8.9 32.2 20.8l-32 240C-1.7 275.2 9.5 288 24 288h118.7L96.6 482.5c-3.6 15.2 8 29.5 23.3 29.5 8.4 0 16.4-4.4 20.8-12l176-304c9.3-15.9-2.2-36-20.7-36z"},"child":[]}]})(props);
}function FaCheck (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M173.898 439.404l-166.4-166.4c-9.997-9.997-9.997-26.206 0-36.204l36.203-36.204c9.997-9.998 26.207-9.998 36.204 0L192 312.69 432.095 72.596c9.997-9.997 26.207-9.997 36.204 0l36.203 36.204c9.997 9.997 9.997 26.206 0 36.204l-294.4 294.401c-9.998 9.997-26.207 9.997-36.204-.001z"},"child":[]}]})(props);
}function FaCog (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M487.4 315.7l-42.6-24.6c4.3-23.2 4.3-47 0-70.2l42.6-24.6c4.9-2.8 7.1-8.6 5.5-14-11.1-35.6-30-67.8-54.7-94.6-3.8-4.1-10-5.1-14.8-2.3L380.8 110c-17.9-15.4-38.5-27.3-60.8-35.1V25.8c0-5.6-3.9-10.5-9.4-11.7-36.7-8.2-74.3-7.8-109.2 0-5.5 1.2-9.4 6.1-9.4 11.7V75c-22.2 7.9-42.8 19.8-60.8 35.1L88.7 85.5c-4.9-2.8-11-1.9-14.8 2.3-24.7 26.7-43.6 58.9-54.7 94.6-1.7 5.4.6 11.2 5.5 14L67.3 221c-4.3 23.2-4.3 47 0 70.2l-42.6 24.6c-4.9 2.8-7.1 8.6-5.5 14 11.1 35.6 30 67.8 54.7 94.6 3.8 4.1 10 5.1 14.8 2.3l42.6-24.6c17.9 15.4 38.5 27.3 60.8 35.1v49.2c0 5.6 3.9 10.5 9.4 11.7 36.7 8.2 74.3 7.8 109.2 0 5.5-1.2 9.4-6.1 9.4-11.7v-49.2c22.2-7.9 42.8-19.8 60.8-35.1l42.6 24.6c4.9 2.8 11 1.9 14.8-2.3 24.7-26.7 43.6-58.9 54.7-94.6 1.5-5.5-.7-11.3-5.6-14.1zM256 336c-44.1 0-80-35.9-80-80s35.9-80 80-80 80 35.9 80 80-35.9 80-80 80z"},"child":[]}]})(props);
}function FaDownload (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z"},"child":[]}]})(props);
}function FaEdit (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M402.6 83.2l90.2 90.2c3.8 3.8 3.8 10 0 13.8L274.4 405.6l-92.8 10.3c-12.4 1.4-22.9-9.1-21.5-21.5l10.3-92.8L388.8 83.2c3.8-3.8 10-3.8 13.8 0zm162-22.9l-48.8-48.8c-15.2-15.2-39.9-15.2-55.2 0l-35.4 35.4c-3.8 3.8-3.8 10 0 13.8l90.2 90.2c3.8 3.8 10 3.8 13.8 0l35.4-35.4c15.2-15.3 15.2-40 0-55.2zM384 346.2V448H64V128h229.8c3.2 0 6.2-1.3 8.5-3.5l40-40c7.6-7.6 2.2-20.5-8.5-20.5H48C21.5 64 0 85.5 0 112v352c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V306.2c0-10.7-12.9-16-20.5-8.5l-40 40c-2.2 2.3-3.5 5.3-3.5 8.5z"},"child":[]}]})(props);
}function FaExclamationCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 256c0 136.997-111.043 248-248 248S8 392.997 8 256C8 119.083 119.043 8 256 8s248 111.083 248 248zm-248 50c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"},"child":[]}]})(props);
}function FaExclamationTriangle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"},"child":[]}]})(props);
}function FaInfoCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm0 110c23.196 0 42 18.804 42 42s-18.804 42-42 42-42-18.804-42-42 18.804-42 42-42zm56 254c0 6.627-5.373 12-12 12h-88c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h12v-64h-12c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h64c6.627 0 12 5.373 12 12v100h12c6.627 0 12 5.373 12 12v24z"},"child":[]}]})(props);
}function FaLeaf (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M546.2 9.7c-5.6-12.5-21.6-13-28.3-1.2C486.9 62.4 431.4 96 368 96h-80C182 96 96 182 96 288c0 7 .8 13.7 1.5 20.5C161.3 262.8 253.4 224 384 224c8.8 0 16 7.2 16 16s-7.2 16-16 16C132.6 256 26 410.1 2.4 468c-6.6 16.3 1.2 34.9 17.5 41.6 16.4 6.8 35-1.1 41.8-17.3 1.5-3.6 20.9-47.9 71.9-90.6 32.4 43.9 94 85.8 174.9 77.2C465.5 467.5 576 326.7 576 154.3c0-50.2-10.8-102.2-29.8-144.6z"},"child":[]}]})(props);
}function FaList (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M80 368H16a16 16 0 0 0-16 16v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16v-64a16 16 0 0 0-16-16zm0-320H16A16 16 0 0 0 0 64v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16V64a16 16 0 0 0-16-16zm0 160H16a16 16 0 0 0-16 16v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16v-64a16 16 0 0 0-16-16zm416 176H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16zm0-320H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16V80a16 16 0 0 0-16-16zm0 160H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16z"},"child":[]}]})(props);
}function FaMagic (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M224 96l16-32 32-16-32-16-16-32-16 32-32 16 32 16 16 32zM80 160l26.66-53.33L160 80l-53.34-26.67L80 0 53.34 53.33 0 80l53.34 26.67L80 160zm352 128l-26.66 53.33L352 368l53.34 26.67L432 448l26.66-53.33L512 368l-53.34-26.67L432 288zm70.62-193.77L417.77 9.38C411.53 3.12 403.34 0 395.15 0c-8.19 0-16.38 3.12-22.63 9.38L9.38 372.52c-12.5 12.5-12.5 32.76 0 45.25l84.85 84.85c6.25 6.25 14.44 9.37 22.62 9.37 8.19 0 16.38-3.12 22.63-9.37l363.14-363.15c12.5-12.48 12.5-32.75 0-45.24zM359.45 203.46l-50.91-50.91 86.6-86.6 50.91 50.91-86.6 86.6z"},"child":[]}]})(props);
}function FaMicrochip (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M416 48v416c0 26.51-21.49 48-48 48H144c-26.51 0-48-21.49-48-48V48c0-26.51 21.49-48 48-48h224c26.51 0 48 21.49 48 48zm96 58v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42V88h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zM30 376h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6z"},"child":[]}]})(props);
}function FaPlay (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M424.4 214.7L72.4 6.6C43.8-10.3 0 6.1 0 47.9V464c0 37.5 40.7 60.1 72.4 41.3l352-208c31.4-18.5 31.5-64.1 0-82.6z"},"child":[]}]})(props);
}function FaRocket (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M505.12019,19.09375c-1.18945-5.53125-6.65819-11-12.207-12.1875C460.716,0,435.507,0,410.40747,0,307.17523,0,245.26909,55.20312,199.05238,128H94.83772c-16.34763.01562-35.55658,11.875-42.88664,26.48438L2.51562,253.29688A28.4,28.4,0,0,0,0,264a24.00867,24.00867,0,0,0,24.00582,24H127.81618l-22.47457,22.46875c-11.36521,11.36133-12.99607,32.25781,0,45.25L156.24582,406.625c11.15623,11.1875,32.15619,13.15625,45.27726,0l22.47457-22.46875V488a24.00867,24.00867,0,0,0,24.00581,24,28.55934,28.55934,0,0,0,10.707-2.51562l98.72834-49.39063c14.62888-7.29687,26.50776-26.5,26.50776-42.85937V312.79688c72.59753-46.3125,128.03493-108.40626,128.03493-211.09376C512.07526,76.5,512.07526,51.29688,505.12019,19.09375ZM384.04033,168A40,40,0,1,1,424.05,128,40.02322,40.02322,0,0,1,384.04033,168Z"},"child":[]}]})(props);
}function FaSlidersH (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M496 384H160v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h80v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h336c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160h-80v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h336v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h80c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160H288V48c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16C7.2 64 0 71.2 0 80v32c0 8.8 7.2 16 16 16h208v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h208c8.8 0 16-7.2 16-16V80c0-8.8-7.2-16-16-16z"},"child":[]}]})(props);
}function FaSpinner (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M304 48c0 26.51-21.49 48-48 48s-48-21.49-48-48 21.49-48 48-48 48 21.49 48 48zm-48 368c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zm208-208c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zM96 256c0-26.51-21.49-48-48-48S0 229.49 0 256s21.49 48 48 48 48-21.49 48-48zm12.922 99.078c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.491-48-48-48zm294.156 0c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.49-48-48-48zM108.922 60.922c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.491-48-48-48z"},"child":[]}]})(props);
}function FaThermometerHalf (props) {
  return GenIcon({"attr":{"viewBox":"0 0 256 512"},"child":[{"tag":"path","attr":{"d":"M192 384c0 35.346-28.654 64-64 64s-64-28.654-64-64c0-23.685 12.876-44.349 32-55.417V224c0-17.673 14.327-32 32-32s32 14.327 32 32v104.583c19.124 11.068 32 31.732 32 55.417zm32-84.653c19.912 22.563 32 52.194 32 84.653 0 70.696-57.303 128-128 128-.299 0-.609-.001-.909-.003C56.789 511.509-.357 453.636.002 383.333.166 351.135 12.225 321.755 32 299.347V96c0-53.019 42.981-96 96-96s96 42.981 96 96v203.347zM208 384c0-34.339-19.37-52.19-32-66.502V96c0-26.467-21.533-48-48-48S80 69.533 80 96v221.498c-12.732 14.428-31.825 32.1-31.999 66.08-.224 43.876 35.563 80.116 79.423 80.42L128 464c44.112 0 80-35.888 80-80z"},"child":[]}]})(props);
}function FaTimes (props) {
  return GenIcon({"attr":{"viewBox":"0 0 352 512"},"child":[{"tag":"path","attr":{"d":"M242.72 256l100.07-100.07c12.28-12.28 12.28-32.19 0-44.48l-22.24-22.24c-12.28-12.28-32.19-12.28-44.48 0L176 189.28 75.93 89.21c-12.28-12.28-32.19-12.28-44.48 0L9.21 111.45c-12.28 12.28-12.28 32.19 0 44.48L109.28 256 9.21 356.07c-12.28 12.28-12.28 32.19 0 44.48l22.24 22.24c12.28 12.28 32.2 12.28 44.48 0L176 322.72l100.07 100.07c12.28 12.28 32.2 12.28 44.48 0l22.24-22.24c12.28-12.28 12.28-32.19 0-44.48L242.72 256z"},"child":[]}]})(props);
}function FaTrash (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M432 32H312l-9.4-18.7A24 24 0 0 0 281.1 0H166.8a23.72 23.72 0 0 0-21.4 13.3L136 32H16A16 16 0 0 0 0 48v32a16 16 0 0 0 16 16h416a16 16 0 0 0 16-16V48a16 16 0 0 0-16-16zM53.2 467a48 48 0 0 0 47.9 45h245.8a48 48 0 0 0 47.9-45L416 128H32z"},"child":[]}]})(props);
}function FaUpload (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M296 384h-80c-13.3 0-24-10.7-24-24V192h-87.7c-17.8 0-26.7-21.5-14.1-34.1L242.3 5.7c7.5-7.5 19.8-7.5 27.3 0l152.2 152.2c12.6 12.6 3.7 34.1-14.1 34.1H320v168c0 13.3-10.7 24-24 24zm216-8v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h136v8c0 30.9 25.1 56 56 56h80c30.9 0 56-25.1 56-56v-8h136c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z"},"child":[]}]})(props);
}function FaVial (props) {
  return GenIcon({"attr":{"viewBox":"0 0 480 512"},"child":[{"tag":"path","attr":{"d":"M477.7 186.1L309.5 18.3c-3.1-3.1-8.2-3.1-11.3 0l-34 33.9c-3.1 3.1-3.1 8.2 0 11.3l11.2 11.1L33 316.5c-38.8 38.7-45.1 102-9.4 143.5 20.6 24 49.5 36 78.4 35.9 26.4 0 52.8-10 72.9-30.1l246.3-245.7 11.2 11.1c3.1 3.1 8.2 3.1 11.3 0l34-33.9c3.1-3 3.1-8.1 0-11.2zM318 256H161l148-147.7 78.5 78.3L318 256z"},"child":[]}]})(props);
}function FaWrench (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M507.73 109.1c-2.24-9.03-13.54-12.09-20.12-5.51l-74.36 74.36-67.88-11.31-11.31-67.88 74.36-74.36c6.62-6.62 3.43-17.9-5.66-20.16-47.38-11.74-99.55.91-136.58 37.93-39.64 39.64-50.55 97.1-34.05 147.2L18.74 402.76c-24.99 24.99-24.99 65.51 0 90.5 24.99 24.99 65.51 24.99 90.5 0l213.21-213.21c50.12 16.71 107.47 5.68 147.37-34.22 37.07-37.07 49.7-89.32 37.91-136.73zM64 472c-13.25 0-24-10.75-24-24 0-13.26 10.75-24 24-24s24 10.74 24 24c0 13.25-10.75 24-24 24z"},"child":[]}]})(props);
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
 * Hook to access autotune state.
 */
const useAutotune = () => {
    const { autotuneProgress, autotuneResult, isAutotuning, api } = useDeckTune();
    return {
        progress: autotuneProgress,
        result: autotuneResult,
        isRunning: isAutotuning,
        start: (mode) => api.startAutotune(mode),
        stop: () => api.stopAutotune(),
    };
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
 * Hook to access binning state.
 * Requirements: 8.1, 8.2, 8.3, 8.4
 */
const useBinning = () => {
    const { state, api } = useDeckTune();
    return {
        progress: state.binningProgress,
        result: state.binningResult,
        isRunning: state.isBinning,
        config: state.binningConfig,
        start: (config) => api.startBinning(config),
        stop: () => api.stopBinning(),
        getConfig: () => api.getBinningConfig(),
        updateConfig: (config) => api.updateBinningConfig(config),
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
 * WizardMode component for DeckTune.
 *
 * Feature: decktune, Frontend UI Components - Wizard Mode
 * Requirements: 4.5, 6.1, 6.2, 6.3, 6.4, 6.5
 *
 * Provides a 3-step wizard interface for beginner users:
 * - Step 1: Goal selection (Quiet/Cool, Balanced, Max Battery, Max Performance)
 * - Step 2: Autotune progress with phase, core, ETA
 * - Step 3: Results display with per-core values and Apply & Save
 * - Panic Disable button: Always visible emergency reset (Requirement 4.5)
 */

const GOAL_OPTIONS = [
    {
        id: "quiet_cool",
        label: "Quiet/Cool",
        description: "Lower temperatures and fan noise",
        icon: FaLeaf,
        mode: "quick",
    },
    {
        id: "balanced",
        label: "Balanced",
        description: "Good balance of performance and efficiency",
        icon: FaBalanceScale,
        mode: "quick",
    },
    {
        id: "max_battery",
        label: "Max Battery",
        description: "Maximize battery life",
        icon: FaBatteryFull,
        mode: "thorough",
    },
    {
        id: "max_performance",
        label: "Max Performance",
        description: "Find the most aggressive stable undervolt",
        icon: FaRocket,
        mode: "thorough",
    },
];
/**
 * Panic Disable Button component - always visible emergency reset.
 * Requirements: 4.5
 *
 * Features:
 * - Always visible red button
 * - Immediate reset to 0 on click
 */
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
                borderRadius: "8px",
            } },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    color: "#fff",
                    fontWeight: "bold",
                } }, isPanicking ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                window.SP_REACT.createElement("span", null, "Disabling..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaExclamationTriangle, null),
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
/**
 * WizardMode component - 3-step wizard for beginner users.
 * Requirements: 4.5, 5.4, 6.1, 8.1
 */
const WizardMode = ({ onComplete, onCancel }) => {
    const [step, setStep] = SP_REACT.useState(1);
    const [selectedGoal, setSelectedGoal] = SP_REACT.useState(null);
    const { progress, result, isRunning, start, stop } = useAutotune();
    const { progress: binningProgress, result: binningResult, isRunning: isBinningRunning, start: startBinning, stop: stopBinning } = useBinning();
    const { info: platformInfo } = usePlatformInfo();
    const { api, state } = useDeckTune();
    const { missing: missingBinaries, hasMissing, check: checkBinaries } = useBinaries();
    // Check binaries on mount
    SP_REACT.useEffect(() => {
        checkBinaries();
    }, []);
    // Handle autotune completion - move to step 3
    SP_REACT.useEffect(() => {
        if (result && step === 2) {
            setStep(3);
        }
    }, [result, step]);
    // Handle binning completion - move to step 3
    SP_REACT.useEffect(() => {
        if (binningResult && step === 2) {
            setStep(3);
        }
    }, [binningResult, step]);
    /**
     * Handle goal selection and start autotune.
     * Requirements: 6.2, 6.3
     */
    const handleGoalSelect = async (goal) => {
        setSelectedGoal(goal);
        const goalOption = GOAL_OPTIONS.find((g) => g.id === goal);
        if (goalOption) {
            setStep(2);
            await start(goalOption.mode);
        }
    };
    /**
     * Handle binning button click.
     * Requirements: 8.1
     */
    const handleBinningClick = async () => {
        setSelectedGoal(null);
        setStep(2);
        await startBinning();
    };
    /**
     * Handle benchmark button click.
     * Requirements: 7.1, 7.4
     */
    const handleBenchmarkClick = async () => {
        await api.runBenchmark();
    };
    /**
     * Handle cancel button click.
     * Requirements: 6.3, 8.1
     */
    const handleCancel = async () => {
        if (isRunning) {
            await stop();
        }
        if (isBinningRunning) {
            await stopBinning();
        }
        setStep(1);
        setSelectedGoal(null);
        onCancel?.();
    };
    /**
     * Handle Apply & Save button click.
     * Requirements: 5.4, 6.4
     *
     * If a game is running, saves the result as a game-specific preset.
     */
    const handleApplyAndSave = async () => {
        if (result) {
            // Check if a game is running - save as game preset (Requirement 5.4)
            if (state.runningAppId && state.runningAppName) {
                const preset = {
                    app_id: state.runningAppId,
                    label: state.runningAppName,
                    value: result.cores,
                    timeout: 0,
                    use_timeout: false,
                    created_at: new Date().toISOString(),
                    tested: true,
                };
                await api.saveAndApply(result.cores, true, preset);
            }
            else {
                // No game running - apply as global values
                await api.applyUndervolt(result.cores);
            }
            onComplete?.(result);
        }
    };
    /**
     * Handle Apply Recommended button click for binning results.
     * Requirements: 8.4
     */
    const handleApplyBinningResult = async () => {
        if (binningResult) {
            // Apply the recommended value (max_stable + 5mV safety margin)
            const cores = [binningResult.recommended, binningResult.recommended, binningResult.recommended, binningResult.recommended];
            // Check if a game is running - save as game preset
            if (state.runningAppId && state.runningAppName) {
                const preset = {
                    app_id: state.runningAppId,
                    label: state.runningAppName,
                    value: cores,
                    timeout: 0,
                    use_timeout: false,
                    created_at: new Date().toISOString(),
                    tested: true,
                };
                await api.saveAndApply(cores, true, preset);
            }
            else {
                // No game running - apply as global values
                await api.applyUndervolt(cores);
            }
        }
    };
    /**
     * Reset wizard to start over.
     */
    const handleStartOver = () => {
        setStep(1);
        setSelectedGoal(null);
    };
    return (window.SP_REACT.createElement(DFL.PanelSection, { title: "DeckTune Wizard" },
        window.SP_REACT.createElement(PanicDisableButton$1, null),
        hasMissing && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                    padding: "12px",
                    backgroundColor: "#5c4813",
                    borderRadius: "8px",
                    marginBottom: "12px",
                    border: "1px solid #ff9800",
                } },
                window.SP_REACT.createElement(FaExclamationCircle, { style: { color: "#ff9800", fontSize: "18px", flexShrink: 0, marginTop: "2px" } }),
                window.SP_REACT.createElement("div", null,
                    window.SP_REACT.createElement("div", { style: { fontWeight: "bold", color: "#ffb74d", marginBottom: "4px" } }, "Missing Components"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#ffe0b2" } },
                        "Required tools not found: ",
                        window.SP_REACT.createElement("strong", null, missingBinaries.join(", "))),
                    window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#ffcc80", marginTop: "4px" } }, "Autotune and stress tests are unavailable. Please reinstall the plugin or add missing binaries to bin/ folder."))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(StepIndicator$1, { currentStep: step })),
        step === 1 && (window.SP_REACT.createElement(GoalSelectionStep, { onSelect: handleGoalSelect, onBinningClick: handleBinningClick, onBenchmarkClick: handleBenchmarkClick, platformInfo: platformInfo, disabled: hasMissing, isBinningRunning: isBinningRunning })),
        step === 2 && !isBinningRunning && (window.SP_REACT.createElement(AutotuneProgressStep, { progress: progress, isRunning: isRunning, onCancel: handleCancel, selectedGoal: selectedGoal })),
        step === 2 && isBinningRunning && (window.SP_REACT.createElement(BinningProgressStep, { progress: binningProgress, isRunning: isBinningRunning, onCancel: handleCancel })),
        step === 3 && result && !binningResult && (window.SP_REACT.createElement(ResultsStep, { result: result, platformInfo: platformInfo, onApplyAndSave: handleApplyAndSave, onStartOver: handleStartOver })),
        step === 3 && binningResult && (window.SP_REACT.createElement(BinningResultsStep, { result: binningResult, platformInfo: platformInfo, onApplyRecommended: handleApplyBinningResult, onStartOver: handleStartOver }))));
};
const StepIndicator$1 = ({ currentStep }) => {
    const steps = [
        { num: 1, label: "Goal" },
        { num: 2, label: "Tuning" },
        { num: 3, label: "Results" },
    ];
    return (window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", justifyContent: "center", gap: "16px", marginBottom: "16px" } }, steps.map((s, index) => (window.SP_REACT.createElement("div", { key: s.num, style: {
            display: "flex",
            alignItems: "center",
            gap: "8px",
        } },
        window.SP_REACT.createElement("div", { style: {
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: currentStep >= s.num ? "#1a9fff" : "#3d4450",
                color: currentStep >= s.num ? "#fff" : "#8b929a",
                fontWeight: "bold",
                fontSize: "14px",
            } }, currentStep > s.num ? window.SP_REACT.createElement(FaCheck, { size: 12 }) : s.num),
        window.SP_REACT.createElement("span", { style: {
                color: currentStep >= s.num ? "#fff" : "#8b929a",
                fontSize: "12px",
            } }, s.label),
        index < steps.length - 1 && (window.SP_REACT.createElement("div", { style: {
                width: "24px",
                height: "2px",
                backgroundColor: currentStep > s.num ? "#1a9fff" : "#3d4450",
                marginLeft: "8px",
            } })))))));
};
const BinningConfigDialog = ({ config, onSave, onClose }) => {
    const [testDuration, setTestDuration] = SP_REACT.useState(config?.test_duration || 60);
    const [stepSize, setStepSize] = SP_REACT.useState(config?.step_size || 5);
    const [startValue, setStartValue] = SP_REACT.useState(config?.start_value || -10);
    const [isSaving, setIsSaving] = SP_REACT.useState(false);
    const handleSave = async () => {
        setIsSaving(true);
        try {
            await onSave({
                test_duration: testDuration,
                step_size: stepSize,
                start_value: startValue,
            });
            onClose();
        }
        finally {
            setIsSaving(false);
        }
    };
    return (window.SP_REACT.createElement("div", { style: { padding: "16px" } },
        window.SP_REACT.createElement("div", { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "16px" } }, "Binning Advanced Settings"),
        window.SP_REACT.createElement("div", { style: { marginBottom: "16px" } },
            window.SP_REACT.createElement(DFL.SliderField, { label: "Test Duration", description: `${testDuration} seconds per test`, value: testDuration, min: 30, max: 300, step: 10, onChange: (value) => setTestDuration(value), showValue: true })),
        window.SP_REACT.createElement("div", { style: { marginBottom: "16px" } },
            window.SP_REACT.createElement(DFL.SliderField, { label: "Step Size", description: `${stepSize}mV increments`, value: stepSize, min: 1, max: 10, step: 1, onChange: (value) => setStepSize(value), showValue: true })),
        window.SP_REACT.createElement("div", { style: { marginBottom: "24px" } },
            window.SP_REACT.createElement(DFL.SliderField, { label: "Starting Value", description: `Begin testing at ${startValue}mV`, value: startValue, min: -20, max: 0, step: 1, onChange: (value) => setStartValue(value), showValue: true })),
        window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px" } },
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleSave, disabled: isSaving, style: { flex: 1 } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#4caf50" } },
                    window.SP_REACT.createElement(FaCheck, null),
                    window.SP_REACT.createElement("span", null, isSaving ? "Saving..." : "Save"))),
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onClose, disabled: isSaving, style: { flex: 1 } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                    window.SP_REACT.createElement(FaTimes, null),
                    window.SP_REACT.createElement("span", null, "Cancel"))))));
};
const GoalSelectionStep = ({ onSelect, onBinningClick, onBenchmarkClick, platformInfo, disabled = false, isBinningRunning = false }) => {
    const { state } = useDeckTune();
    const { config, getConfig, updateConfig } = useBinning();
    const [showConfigDialog, setShowConfigDialog] = SP_REACT.useState(false);
    const isGameRunning = state.runningAppId !== null && state.runningAppName !== null;
    // Load config on mount
    SP_REACT.useEffect(() => {
        getConfig();
    }, []);
    const handleConfigClick = () => {
        setShowConfigDialog(true);
    };
    const handleConfigSave = async (newConfig) => {
        await updateConfig(newConfig);
        setShowConfigDialog(false);
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        platformInfo && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginBottom: "8px" } },
                "Detected: ",
                platformInfo.variant,
                " (",
                platformInfo.model,
                ") \u2022 Safe limit: ",
                platformInfo.safe_limit))),
        isGameRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "8px 12px",
                    backgroundColor: "#1a3a5c",
                    borderRadius: "6px",
                    marginBottom: "12px",
                    fontSize: "12px",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                    window.SP_REACT.createElement(FaRocket, { style: { color: "#1a9fff" } }),
                    window.SP_REACT.createElement("span", null,
                        "Running: ",
                        window.SP_REACT.createElement("strong", null, state.runningAppName))),
                window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginTop: "4px" } }, "Tuning will be saved as a preset for this game")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", gap: "8px" } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onBinningClick, disabled: disabled || isBinningRunning, description: "Automatically discover your chip's maximum stable undervolt", style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", opacity: (disabled || isBinningRunning) ? 0.5 : 1 } },
                        window.SP_REACT.createElement(FaMicrochip, { style: { color: "#ff9800" } }),
                        window.SP_REACT.createElement("span", null, "Find Max Undervolt"),
                        window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#8b929a", marginLeft: "auto" } }, "~5-15 min"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleConfigClick, disabled: disabled || isBinningRunning, style: { width: "48px", padding: "0" } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", opacity: (disabled || isBinningRunning) ? 0.5 : 1 } },
                        window.SP_REACT.createElement(FaCog, null))))),
        showConfigDialog && (window.SP_REACT.createElement(DFL.ConfirmModal, { strTitle: "Binning Settings", onOK: () => { }, onCancel: () => setShowConfigDialog(false), bOKDisabled: true, bCancelDisabled: true },
            window.SP_REACT.createElement(BinningConfigDialog, { config: config, onSave: handleConfigSave, onClose: () => setShowConfigDialog(false) }))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onBenchmarkClick, disabled: disabled || isBinningRunning || state.isBenchmarkRunning, description: "Run a 10-second performance benchmark", style: { marginTop: "8px" } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", opacity: (disabled || isBinningRunning || state.isBenchmarkRunning) ? 0.5 : 1 } },
                    state.isBenchmarkRunning ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                        window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { color: "#4caf50" } }),
                        window.SP_REACT.createElement("span", null, "Running..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                        window.SP_REACT.createElement(FaVial, { style: { color: "#4caf50" } }),
                        window.SP_REACT.createElement("span", null, "Run Benchmark"))),
                    window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#8b929a", marginLeft: "auto" } }, "10 sec")))),
        state.isBenchmarkRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1b5e20",
                    borderRadius: "8px",
                    marginTop: "8px",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" } },
                    window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { color: "#4caf50" } }),
                    window.SP_REACT.createElement("span", { style: { fontWeight: "bold" } }, "Running benchmark...")),
                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#a5d6a7", textAlign: "center" } }, "Testing performance (~10 seconds)")))),
        state.lastBenchmarkResult && !state.isBenchmarkRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1b5e20",
                    borderRadius: "8px",
                    marginTop: "8px",
                    borderLeft: "4px solid #4caf50",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" } },
                    window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "13px" } }, "Benchmark Complete"),
                    window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50" } })),
                window.SP_REACT.createElement("div", { style: { marginBottom: "6px" } },
                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#a5d6a7" } }, "Score"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "18px", fontWeight: "bold", color: "#4caf50" } },
                        state.lastBenchmarkResult.score.toFixed(2),
                        " bogo ops/s")),
                state.benchmarkHistory && state.benchmarkHistory.length > 1 && (() => {
                    const current = state.benchmarkHistory[0];
                    const previous = state.benchmarkHistory[1];
                    const scoreDiff = current.score - previous.score;
                    const percentChange = ((scoreDiff / previous.score) * 100);
                    const improvement = scoreDiff > 0;
                    return (window.SP_REACT.createElement("div", { style: { marginTop: "6px", paddingTop: "6px", borderTop: "1px solid #2e7d32" } },
                        window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#a5d6a7", marginBottom: "4px" } }, "vs Previous"),
                        window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "6px" } },
                            improvement ? (window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50", fontSize: "12px" } })) : (window.SP_REACT.createElement(FaTimes, { style: { color: "#ff6b6b", fontSize: "12px" } })),
                            window.SP_REACT.createElement("span", { style: { fontSize: "12px", color: improvement ? "#4caf50" : "#ff6b6b", fontWeight: "bold" } },
                                improvement ? "+" : "",
                                percentChange.toFixed(2),
                                "%"),
                            window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#a5d6a7" } }, improvement ? "improvement" : "degradation"))));
                })()))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", marginBottom: "12px", marginTop: "12px" } }, "Or select your tuning goal:")),
        GOAL_OPTIONS.map((goal) => {
            const Icon = goal.icon;
            return (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: goal.id },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => onSelect(goal.id), description: goal.description, disabled: disabled || isBinningRunning },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", opacity: (disabled || isBinningRunning) ? 0.5 : 1 } },
                        window.SP_REACT.createElement(Icon, null),
                        window.SP_REACT.createElement("span", null, goal.label),
                        window.SP_REACT.createElement("span", { style: { fontSize: "10px", color: "#8b929a", marginLeft: "auto" } }, goal.mode === "thorough" ? "~10 min" : "~3 min")))));
        })));
};
const AutotuneProgressStep = ({ progress, isRunning, onCancel, selectedGoal, }) => {
    const goalLabel = GOAL_OPTIONS.find((g) => g.id === selectedGoal)?.label || "Unknown";
    // Calculate progress percentage
    const calculateProgress = () => {
        if (!progress)
            return 0;
        // Phase A: cores 0-3 (0-50%), Phase B: cores 0-3 (50-100%)
        const phaseOffset = progress.phase === "B" ? 50 : 0;
        const coreProgress = (progress.core / 4) * 50;
        return Math.min(phaseOffset + coreProgress, 100);
    };
    // Format ETA
    const formatEta = (seconds) => {
        if (seconds <= 0)
            return "Almost done...";
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (mins > 0) {
            return `${mins}m ${secs}s remaining`;
        }
        return `${secs}s remaining`;
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { textAlign: "center", marginBottom: "16px" } },
                window.SP_REACT.createElement(FaSpinner, { style: {
                        animation: "spin 1s linear infinite",
                        fontSize: "24px",
                        color: "#1a9fff",
                    } }),
                window.SP_REACT.createElement("style", null, `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } },
                "Tuning for: ",
                goalLabel)),
        progress && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ProgressBarWithInfo, { label: `Phase ${progress.phase} - Core ${progress.core}`, description: `Testing value: ${progress.value}`, nProgress: calculateProgress(), sOperationText: formatEta(progress.eta) })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: "12px",
                        color: "#8b929a",
                        marginTop: "8px",
                    } },
                    window.SP_REACT.createElement("span", null,
                        "Phase: ",
                        progress.phase === "A" ? "Coarse Search" : "Fine Tuning"),
                    window.SP_REACT.createElement("span", null,
                        "Core: ",
                        progress.core + 1,
                        "/4"))))),
        !progress && isRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { textAlign: "center", color: "#8b929a" } }, "Initializing autotune..."))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onCancel, style: { marginTop: "16px" } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" } },
                    window.SP_REACT.createElement(FaTimes, null),
                    window.SP_REACT.createElement("span", null, "Cancel"))))));
};
const ResultsStep = ({ result, platformInfo, onApplyAndSave, onStartOver, }) => {
    /**
     * Get color indicator based on value and stability.
     * Requirements: 6.5
     * - Green: stable/applied
     * - Yellow: moderate undervolt
     * - Red: aggressive undervolt near limit
     */
    const getValueColor = (value) => {
        if (!platformInfo)
            return "#8b929a";
        const limit = platformInfo.safe_limit;
        const ratio = Math.abs(value) / Math.abs(limit);
        if (ratio < 0.5)
            return "#4caf50"; // Green - conservative
        if (ratio < 0.8)
            return "#ff9800"; // Yellow - moderate
        return "#f44336"; // Red - aggressive
    };
    /**
     * Get status label for value.
     */
    const getValueStatus = (value) => {
        if (!platformInfo)
            return "";
        const limit = platformInfo.safe_limit;
        const ratio = Math.abs(value) / Math.abs(limit);
        if (ratio < 0.5)
            return "Conservative";
        if (ratio < 0.8)
            return "Moderate";
        return "Aggressive";
    };
    // Format duration
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        return `${mins}m ${secs}s`;
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    padding: "12px",
                    backgroundColor: result.stable ? "#1b5e20" : "#b71c1c",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                result.stable ? window.SP_REACT.createElement(FaCheck, null) : window.SP_REACT.createElement(FaTimes, null),
                window.SP_REACT.createElement("span", { style: { fontWeight: "bold" } }, result.stable ? "Tuning Complete!" : "Tuning Incomplete"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    justifyContent: "space-around",
                    fontSize: "12px",
                    color: "#8b929a",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("span", null,
                    "Duration: ",
                    formatDuration(result.duration)),
                window.SP_REACT.createElement("span", null,
                    "Tests: ",
                    result.tests_run))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Optimal Values Found:")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(2, 1fr)",
                    gap: "8px",
                } }, result.cores.map((value, index) => (window.SP_REACT.createElement("div", { key: index, style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    borderLeft: `4px solid ${getValueColor(value)}`,
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } },
                    "Core ",
                    index),
                window.SP_REACT.createElement("div", { style: {
                        fontSize: "20px",
                        fontWeight: "bold",
                        color: getValueColor(value),
                    } }, value),
                window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } }, getValueStatus(value))))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    justifyContent: "center",
                    gap: "16px",
                    fontSize: "10px",
                    color: "#8b929a",
                    marginTop: "8px",
                } },
                window.SP_REACT.createElement("span", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement("div", { style: { width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#4caf50" } }),
                    "Conservative"),
                window.SP_REACT.createElement("span", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement("div", { style: { width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#ff9800" } }),
                    "Moderate"),
                window.SP_REACT.createElement("span", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement("div", { style: { width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#f44336" } }),
                    "Aggressive"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onApplyAndSave, style: { marginTop: "16px" } },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        color: "#4caf50",
                    } },
                    window.SP_REACT.createElement(FaCheck, null),
                    window.SP_REACT.createElement("span", null, "Apply & Save")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onStartOver },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                    window.SP_REACT.createElement("span", null, "Start Over"))))));
};
const BinningProgressStep = ({ progress, isRunning, onCancel, }) => {
    // Format ETA
    const formatEta = (seconds) => {
        if (seconds <= 0)
            return "Almost done...";
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (mins > 0) {
            return `${mins}:${secs.toString().padStart(2, '0')} remaining`;
        }
        return `${secs}s remaining`;
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { textAlign: "center", marginBottom: "16px" } },
                window.SP_REACT.createElement(FaSpinner, { style: {
                        animation: "spin 1s linear infinite",
                        fontSize: "24px",
                        color: "#ff9800",
                    } }),
                window.SP_REACT.createElement("style", null, `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Finding Maximum Undervolt")),
        progress && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ProgressBarWithInfo, { label: `Iteration ${progress.iteration}`, description: `Testing: ${progress.current_value}mV`, nProgress: Math.min((progress.iteration / 20) * 100, 100), sOperationText: formatEta(progress.eta) })),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: "12px",
                        color: "#8b929a",
                        marginTop: "8px",
                    } },
                    window.SP_REACT.createElement("span", null,
                        "Current: ",
                        progress.current_value,
                        "mV"),
                    window.SP_REACT.createElement("span", null,
                        "Last Stable: ",
                        progress.last_stable,
                        "mV"))))),
        !progress && isRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { textAlign: "center", color: "#8b929a" } }, "Initializing binning..."))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onCancel, style: { marginTop: "16px" } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" } },
                    window.SP_REACT.createElement(FaTimes, null),
                    window.SP_REACT.createElement("span", null, "Stop"))))));
};
const BinningResultsStep = ({ result, platformInfo, onApplyRecommended, onStartOver, }) => {
    // Format duration
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        return `${mins}m ${secs}s`;
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    padding: "12px",
                    backgroundColor: result.aborted ? "#b71c1c" : "#1b5e20",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                result.aborted ? window.SP_REACT.createElement(FaTimes, null) : window.SP_REACT.createElement(FaCheck, null),
                window.SP_REACT.createElement("span", { style: { fontWeight: "bold" } }, result.aborted ? "Binning Incomplete" : "Binning Complete!"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    justifyContent: "space-around",
                    fontSize: "12px",
                    color: "#8b929a",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("span", null,
                    "Duration: ",
                    formatDuration(result.duration)),
                window.SP_REACT.createElement("span", null,
                    "Iterations: ",
                    result.iterations))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Discovered Values:")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                } },
                window.SP_REACT.createElement("div", { style: {
                        padding: "16px",
                        backgroundColor: "#23262e",
                        borderRadius: "8px",
                        borderLeft: `4px solid #ff9800`,
                    } },
                    window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } }, "Maximum Stable"),
                    window.SP_REACT.createElement("div", { style: {
                            fontSize: "24px",
                            fontWeight: "bold",
                            color: "#ff9800",
                        } },
                        result.max_stable,
                        "mV"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } }, "Most aggressive stable value found")),
                window.SP_REACT.createElement("div", { style: {
                        padding: "16px",
                        backgroundColor: "#23262e",
                        borderRadius: "8px",
                        borderLeft: `4px solid #4caf50`,
                    } },
                    window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } }, "Recommended (with 5mV safety margin)"),
                    window.SP_REACT.createElement("div", { style: {
                            fontSize: "24px",
                            fontWeight: "bold",
                            color: "#4caf50",
                        } },
                        result.recommended,
                        "mV"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } }, "Conservative value for daily use")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onApplyRecommended, style: { marginTop: "16px" } },
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        color: "#4caf50",
                    } },
                    window.SP_REACT.createElement(FaCheck, null),
                    window.SP_REACT.createElement("span", null, "Apply Recommended")))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: onStartOver },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                    window.SP_REACT.createElement("span", null, "Start Over"))))));
};

/**
 * LoadGraph component for displaying real-time CPU load and undervolt values.
 *
 * Feature: decktune-3.0-automation
 * Requirements: 6.3, 6.4
 *
 * Displays per-core CPU load percentages and applied undervolt values.
 * Shows historical data with dual Y-axes and profile change markers.
 * Implements 60-second rolling window with 1-second resolution.
 */

const MAX_HISTORY_POINTS = 60; // Keep 60 data points (1 minute at 1Hz)
const GRAPH_HEIGHT = 120;
const GRAPH_WIDTH = 300;
const MARGIN_LEFT = 35;
const MARGIN_RIGHT = 35;
/**
 * Get color for a specific core (load lines).
 */
const getCoreColor = (coreIndex) => {
    const colors = ["#1a9fff", "#4caf50", "#ff9800", "#f44336"];
    return colors[coreIndex] || "#8b929a";
};
/**
 * Get color for undervolt value lines (orange tones).
 */
const getValueColor = (coreIndex) => {
    const colors = ["#ff9800", "#ffb74d", "#ffa726", "#ff8a65"];
    return colors[coreIndex] || "#ff9800";
};
/**
 * LoadGraph component - displays real-time CPU load and undervolt values.
 * Requirements: 6.3, 6.4
 */
const LoadGraph = ({ load, values, isActive, activeProfile }) => {
    const [history, setHistory] = SP_REACT.useState([]);
    const [previousProfile, setPreviousProfile] = SP_REACT.useState(activeProfile);
    const canvasRef = SP_REACT.useRef(null);
    const updateIntervalRef = SP_REACT.useRef(null);
    // Update history at 1-second intervals (Requirements: 6.3)
    SP_REACT.useEffect(() => {
        if (!isActive || load.length !== 4 || values.length !== 4) {
            // Clear history when not active
            setHistory([]);
            setPreviousProfile(undefined);
            if (updateIntervalRef.current) {
                clearInterval(updateIntervalRef.current);
                updateIntervalRef.current = null;
            }
            return;
        }
        // Detect profile change
        const profileChanged = activeProfile !== previousProfile && previousProfile !== undefined;
        // Add new data point
        const addDataPoint = () => {
            setHistory((prev) => {
                const newPoint = {
                    timestamp: Date.now(),
                    load: [...load],
                    values: [...values],
                    profile: profileChanged ? activeProfile : undefined,
                };
                const newHistory = [...prev, newPoint];
                // Keep only the last MAX_HISTORY_POINTS (60-second rolling window)
                if (newHistory.length > MAX_HISTORY_POINTS) {
                    return newHistory.slice(-MAX_HISTORY_POINTS);
                }
                return newHistory;
            });
            if (profileChanged) {
                setPreviousProfile(activeProfile);
            }
        };
        // Add initial point immediately
        addDataPoint();
        // Set up 1-second interval
        updateIntervalRef.current = setInterval(addDataPoint, 1000);
        return () => {
            if (updateIntervalRef.current) {
                clearInterval(updateIntervalRef.current);
            }
        };
    }, [load, values, isActive, activeProfile, previousProfile]);
    // Draw the graph on canvas with dual Y-axes (Requirements: 6.3, 6.4)
    SP_REACT.useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || history.length === 0) {
            return;
        }
        const ctx = canvas.getContext("2d");
        if (!ctx) {
            return;
        }
        // Clear canvas
        ctx.clearRect(0, 0, GRAPH_WIDTH, GRAPH_HEIGHT);
        // Draw background grid
        ctx.strokeStyle = "#3d4450";
        ctx.lineWidth = 1;
        // Horizontal grid lines (every 25%)
        for (let i = 0; i <= 4; i++) {
            const y = (i * GRAPH_HEIGHT) / 4;
            ctx.beginPath();
            ctx.moveTo(MARGIN_LEFT, y);
            ctx.lineTo(GRAPH_WIDTH - MARGIN_RIGHT, y);
            ctx.stroke();
        }
        // Calculate graph area
        const graphWidth = GRAPH_WIDTH - MARGIN_LEFT - MARGIN_RIGHT;
        const pointSpacing = graphWidth / (MAX_HISTORY_POINTS - 1);
        // Draw profile change markers (Requirements: 6.3)
        history.forEach((point, index) => {
            if (point.profile) {
                const x = MARGIN_LEFT + index * pointSpacing;
                // Draw vertical line
                ctx.strokeStyle = "#4caf50";
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 3]);
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, GRAPH_HEIGHT);
                ctx.stroke();
                ctx.setLineDash([]);
                // Draw label
                ctx.fillStyle = "#4caf50";
                ctx.font = "9px sans-serif";
                ctx.save();
                ctx.translate(x + 2, GRAPH_HEIGHT - 5);
                ctx.rotate(-Math.PI / 2);
                ctx.fillText(point.profile || "Profile", 0, 0);
                ctx.restore();
            }
        });
        // Draw load lines for each core (blue tones, left Y-axis)
        for (let coreIndex = 0; coreIndex < 4; coreIndex++) {
            ctx.strokeStyle = getCoreColor(coreIndex);
            ctx.lineWidth = 2;
            ctx.beginPath();
            let firstPoint = true;
            history.forEach((point, index) => {
                const x = MARGIN_LEFT + index * pointSpacing;
                const loadValue = point.load[coreIndex] || 0;
                // Invert Y axis (0% at bottom, 100% at top)
                const y = GRAPH_HEIGHT - (loadValue / 100) * GRAPH_HEIGHT;
                if (firstPoint) {
                    ctx.moveTo(x, y);
                    firstPoint = false;
                }
                else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
        }
        // Draw undervolt value lines (orange tones, right Y-axis)
        // Requirements: 6.3, 6.4
        const minValue = -50; // Minimum expected undervolt value
        const maxValue = 0; // Maximum expected undervolt value
        const valueRange = maxValue - minValue;
        for (let coreIndex = 0; coreIndex < 4; coreIndex++) {
            ctx.strokeStyle = getValueColor(coreIndex);
            ctx.lineWidth = 1.5;
            ctx.setLineDash([3, 2]);
            ctx.beginPath();
            let firstPoint = true;
            history.forEach((point, index) => {
                const x = MARGIN_LEFT + index * pointSpacing;
                const value = point.values[coreIndex] || 0;
                // Map value to graph height (0mV at top, -50mV at bottom)
                const normalizedValue = (value - minValue) / valueRange;
                const y = GRAPH_HEIGHT - normalizedValue * GRAPH_HEIGHT;
                if (firstPoint) {
                    ctx.moveTo(x, y);
                    firstPoint = false;
                }
                else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
            ctx.setLineDash([]);
        }
        // If dynamic mode is inactive, draw static line (Requirements: 6.4)
        if (!isActive && values.length === 4) {
            const avgValue = values.reduce((sum, v) => sum + v, 0) / values.length;
            const normalizedValue = (avgValue - minValue) / valueRange;
            const y = GRAPH_HEIGHT - normalizedValue * GRAPH_HEIGHT;
            ctx.strokeStyle = "#ff9800";
            ctx.lineWidth = 2;
            ctx.setLineDash([]);
            ctx.beginPath();
            ctx.moveTo(MARGIN_LEFT, y);
            ctx.lineTo(GRAPH_WIDTH - MARGIN_RIGHT, y);
            ctx.stroke();
        }
    }, [history, isActive, values]);
    if (!isActive && values.length === 0) {
        return null;
    }
    return (window.SP_REACT.createElement("div", { style: {
            padding: "12px",
            backgroundColor: "#23262e",
            borderRadius: "8px",
            marginBottom: "16px",
        } },
        window.SP_REACT.createElement("div", { style: {
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "12px",
            } },
            window.SP_REACT.createElement(FaMicrochip, { style: { color: "#1a9fff" } }),
            window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "14px" } }, isActive ? "CPU Load & Undervolt (Real-time)" : "Undervolt Values (Manual Mode)")),
        window.SP_REACT.createElement("div", { style: {
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "8px",
                marginBottom: "12px",
            } }, load.map((loadValue, index) => (window.SP_REACT.createElement("div", { key: index, style: {
                padding: "6px",
                backgroundColor: "#1a1d23",
                borderRadius: "4px",
                textAlign: "center",
                borderLeft: `3px solid ${getCoreColor(index)}`,
            } },
            window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } },
                "Core ",
                index),
            isActive && (window.SP_REACT.createElement("div", { style: {
                    fontSize: "16px",
                    fontWeight: "bold",
                    color: getCoreColor(index),
                } },
                loadValue.toFixed(1),
                "%")),
            window.SP_REACT.createElement("div", { style: {
                    fontSize: isActive ? "11px" : "16px",
                    fontWeight: isActive ? "normal" : "bold",
                    color: getValueColor(index),
                } },
                values[index] || 0,
                "mV"))))),
        window.SP_REACT.createElement("div", { style: {
                position: "relative",
                width: "100%",
                height: `${GRAPH_HEIGHT}px`,
                backgroundColor: "#1a1d23",
                borderRadius: "4px",
                overflow: "hidden",
            } },
            window.SP_REACT.createElement("canvas", { ref: canvasRef, width: GRAPH_WIDTH, height: GRAPH_HEIGHT, style: {
                    width: "100%",
                    height: "100%",
                } }),
            window.SP_REACT.createElement("div", { style: {
                    position: "absolute",
                    top: 0,
                    left: 0,
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    padding: "2px 4px",
                    pointerEvents: "none",
                } }, [100, 75, 50, 25, 0].map((value) => (window.SP_REACT.createElement("div", { key: value, style: {
                    fontSize: "9px",
                    color: "#1a9fff",
                    lineHeight: "1",
                } },
                value,
                "%")))),
            window.SP_REACT.createElement("div", { style: {
                    position: "absolute",
                    top: 0,
                    right: 0,
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    padding: "2px 4px",
                    pointerEvents: "none",
                } }, [0, -12, -25, -37, -50].map((value) => (window.SP_REACT.createElement("div", { key: value, style: {
                    fontSize: "9px",
                    color: "#ff9800",
                    lineHeight: "1",
                    textAlign: "right",
                } }, value))))),
        window.SP_REACT.createElement("div", { style: {
                display: "flex",
                justifyContent: "center",
                gap: "12px",
                marginTop: "8px",
                fontSize: "10px",
                flexWrap: "wrap",
            } },
            isActive && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement("div", { style: {
                            width: "16px",
                            height: "3px",
                            backgroundColor: "#1a9fff",
                            borderRadius: "2px",
                        } }),
                    window.SP_REACT.createElement("span", { style: { color: "#8b929a" } }, "Load (solid)")),
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement("div", { style: {
                            width: "16px",
                            height: "2px",
                            background: "repeating-linear-gradient(to right, #ff9800 0, #ff9800 3px, transparent 3px, transparent 5px)",
                            borderRadius: "2px",
                        } }),
                    window.SP_REACT.createElement("span", { style: { color: "#8b929a" } }, "Undervolt (dashed)")),
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    window.SP_REACT.createElement("div", { style: {
                            width: "3px",
                            height: "16px",
                            background: "repeating-linear-gradient(to bottom, #4caf50 0, #4caf50 5px, transparent 5px, transparent 8px)",
                            borderRadius: "2px",
                        } }),
                    window.SP_REACT.createElement("span", { style: { color: "#8b929a" } }, "Profile change")))),
            !isActive && (window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                window.SP_REACT.createElement("div", { style: {
                        width: "16px",
                        height: "3px",
                        backgroundColor: "#ff9800",
                        borderRadius: "2px",
                    } }),
                window.SP_REACT.createElement("span", { style: { color: "#8b929a" } }, "Manual undervolt"))))));
};

/**
 * Updated Presets tab component with Game Profile management.
 * Requirements: 3.2, 5.1, 5.4, 7.3, 9.1, 9.2
 *
 * Features:
 * - Game profile list with edit/delete
 * - Quick-create button when game is running
 * - Import/export profile buttons
 * - Legacy preset list with edit/delete/export
 * - Import preset button
 */

const PresetsTabNew = () => {
    const { state, api } = useDeckTune();
    const { profiles, activeProfile, runningAppId, runningAppName, createProfileForCurrentGame, deleteProfile, exportProfiles, importProfiles } = useProfiles();
    const [editingPreset, setEditingPreset] = SP_REACT.useState(null);
    const [editingProfile, setEditingProfile] = SP_REACT.useState(null);
    const [isImporting, setIsImporting] = SP_REACT.useState(false);
    const [isImportingProfiles, setIsImportingProfiles] = SP_REACT.useState(false);
    const [importJson, setImportJson] = SP_REACT.useState("");
    const [importProfileJson, setImportProfileJson] = SP_REACT.useState("");
    const [importError, setImportError] = SP_REACT.useState(null);
    const [importProfileError, setImportProfileError] = SP_REACT.useState(null);
    const [mergeStrategy, setMergeStrategy] = SP_REACT.useState("skip");
    const [isCreatingProfile, setIsCreatingProfile] = SP_REACT.useState(false);
    const [showCreateDialog, setShowCreateDialog] = SP_REACT.useState(false);
    const [newProfileData, setNewProfileData] = SP_REACT.useState({
        app_id: 0,
        name: "",
        cores: [...state.cores],
        dynamic_enabled: false,
    });
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
    /**
     * Handle quick-create profile for current game.
     * Requirements: 5.1, 5.3, 5.4
     */
    const handleQuickCreate = async () => {
        setIsCreatingProfile(true);
        try {
            const result = await createProfileForCurrentGame();
            if (result.success) {
                alert(`Profile created for ${runningAppName}`);
            }
            else {
                alert(`Failed to create profile: ${result.error}`);
            }
        }
        catch (e) {
            alert(`Error creating profile: ${String(e)}`);
        }
        finally {
            setIsCreatingProfile(false);
        }
    };
    /**
     * Handle profile deletion.
     * Requirements: 3.4
     */
    const handleDeleteProfile = async (appId) => {
        if (confirm("Are you sure you want to delete this profile?")) {
            try {
                const result = await deleteProfile(appId);
                if (!result.success) {
                    alert(`Failed to delete profile: ${result.error}`);
                }
            }
            catch (e) {
                alert(`Error deleting profile: ${String(e)}`);
            }
        }
    };
    /**
     * Handle profile export (all profiles).
     * Requirements: 9.1
     */
    const handleExportProfiles = async () => {
        try {
            const result = await exportProfiles();
            if (result.success && result.json) {
                console.log("Export profiles:", result.json);
                alert(`Profiles exported successfully!\n\nPath: ${result.path || "clipboard"}`);
            }
            else {
                alert(`Failed to export profiles: ${result.error}`);
            }
        }
        catch (e) {
            alert(`Error exporting profiles: ${String(e)}`);
        }
    };
    /**
     * Handle profile import.
     * Requirements: 9.2, 9.3, 9.4
     */
    const handleImportProfiles = async () => {
        setImportProfileError(null);
        try {
            const result = await importProfiles(importProfileJson, mergeStrategy);
            if (result.success) {
                setIsImportingProfiles(false);
                setImportProfileJson("");
                alert(`Successfully imported ${result.imported_count} profile(s)${result.conflicts.length > 0 ? `\nConflicts: ${result.conflicts.length}` : ""}`);
            }
            else {
                setImportProfileError(result.error || "Import failed");
            }
        }
        catch (e) {
            setImportProfileError("Invalid JSON format");
        }
    };
    /**
     * Handle preset deletion.
     */
    const handleDelete = async (appId) => {
        await api.deletePreset(appId);
    };
    /**
     * Handle preset export (single preset).
     */
    const handleExportSingle = async (preset) => {
        const json = JSON.stringify([preset], null, 2);
        console.log("Export preset:", json);
        alert(`Preset exported:\n${json}`);
    };
    /**
     * Handle export all presets.
     */
    const handleExportAll = async () => {
        const json = await api.exportPresets();
        console.log("Export all presets:", json);
        alert(`All presets exported:\n${json}`);
    };
    /**
     * Handle import presets.
     */
    const handleImport = async () => {
        setImportError(null);
        try {
            const result = await api.importPresets(importJson);
            if (result.success) {
                setIsImporting(false);
                setImportJson("");
                alert(`Successfully imported ${result.imported_count} preset(s)`);
            }
            else {
                setImportError(result.error || "Import failed");
            }
        }
        catch (e) {
            setImportError("Invalid JSON format");
        }
    };
    /**
     * Handle preset edit save.
     */
    const handleSaveEdit = async () => {
        if (editingPreset) {
            await api.updatePreset(editingPreset);
            setEditingPreset(null);
        }
    };
    /**
     * Handle profile edit save.
     * Requirements: 3.3
     */
    const handleSaveProfileEdit = async () => {
        if (editingProfile) {
            try {
                const result = await api.updateProfile(editingProfile.app_id, {
                    name: editingProfile.name,
                    cores: editingProfile.cores,
                    dynamic_enabled: editingProfile.dynamic_enabled,
                });
                if (result.success) {
                    setEditingProfile(null);
                }
                else {
                    alert(`Failed to update profile: ${result.error}`);
                }
            }
            catch (e) {
                alert(`Error updating profile: ${String(e)}`);
            }
        }
    };
    /**
     * Handle create profile dialog.
     * Requirements: 3.1, 5.1
     */
    const handleCreateProfile = async () => {
        if (!newProfileData.name || newProfileData.app_id === 0) {
            alert("Please enter a game name and AppID");
            return;
        }
        try {
            const result = await api.createProfile({
                app_id: newProfileData.app_id,
                name: newProfileData.name,
                cores: newProfileData.cores,
                dynamic_enabled: newProfileData.dynamic_enabled,
                dynamic_config: newProfileData.dynamic_enabled ? state.dynamicSettings : null,
            });
            if (result.success) {
                setShowCreateDialog(false);
                setNewProfileData({
                    app_id: 0,
                    name: "",
                    cores: [...state.cores],
                    dynamic_enabled: false,
                });
                alert(`Profile created for ${newProfileData.name}`);
            }
            else {
                alert(`Failed to create profile: ${result.error}`);
            }
        }
        catch (e) {
            alert(`Error creating profile: ${String(e)}`);
        }
    };
    /**
     * Format core values for display.
     */
    const formatCoreValues = (values) => {
        return values.map((v, i) => `C${i}:${v}`).join(" ");
    };
    // Check if a game is currently running
    const isGameRunning = runningAppId !== null && runningAppName !== null;
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "12px", marginTop: "8px" } }, "Game Profiles")),
        isGameRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleQuickCreate, disabled: isCreatingProfile, style: {
                    backgroundColor: "#1a9fff",
                    marginBottom: "12px",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } }, isCreatingProfile ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                    window.SP_REACT.createElement("span", null, "Creating..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaRocket, null),
                    window.SP_REACT.createElement("span", null,
                        "Save as Profile for ",
                        runningAppName))))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    gap: "8px",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setShowCreateDialog(true), style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        window.SP_REACT.createElement(FaEdit, null),
                        window.SP_REACT.createElement("span", null, "Create Profile"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExportProfiles, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        window.SP_REACT.createElement(FaDownload, null),
                        window.SP_REACT.createElement("span", null, "Export All"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setIsImportingProfiles(true), style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        window.SP_REACT.createElement(FaUpload, null),
                        window.SP_REACT.createElement("span", null, "Import"))))),
        showCreateDialog && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Create New Profile"),
                window.SP_REACT.createElement(DFL.TextField, { label: "Game Name", value: newProfileData.name, onChange: (e) => setNewProfileData({ ...newProfileData, name: e.target.value }), style: { marginBottom: "8px" } }),
                window.SP_REACT.createElement(DFL.TextField, { label: "Steam AppID", value: String(newProfileData.app_id), onChange: (e) => setNewProfileData({ ...newProfileData, app_id: parseInt(e.target.value) || 0 }), style: { marginBottom: "8px" } }),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginBottom: "8px" } },
                    "Cores: ",
                    formatCoreValues(newProfileData.cores)),
                window.SP_REACT.createElement(DFL.ToggleField, { label: "Enable Dynamic Mode", checked: newProfileData.dynamic_enabled, onChange: (checked) => setNewProfileData({ ...newProfileData, dynamic_enabled: checked }) }),
                window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleCreateProfile },
                        window.SP_REACT.createElement("span", null, "Create")),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setShowCreateDialog(false) },
                        window.SP_REACT.createElement("span", null, "Cancel")))))),
        isImportingProfiles && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Import Profiles"),
                window.SP_REACT.createElement(DFL.TextField, { label: "JSON Data", value: importProfileJson, onChange: (e) => setImportProfileJson(e.target.value), style: { marginBottom: "8px" } }),
                window.SP_REACT.createElement(DFL.DropdownItem, { label: "Merge Strategy", menuLabel: "Merge Strategy", rgOptions: [
                        { data: "skip", label: "Skip conflicts (keep existing)" },
                        { data: "overwrite", label: "Overwrite conflicts" },
                        { data: "rename", label: "Rename conflicts" },
                    ], selectedOption: mergeStrategy, onChange: (option) => setMergeStrategy(option.data) }),
                importProfileError && (window.SP_REACT.createElement("div", { style: { color: "#f44336", fontSize: "12px", marginBottom: "8px", marginTop: "8px" } }, importProfileError)),
                window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleImportProfiles },
                        window.SP_REACT.createElement("span", null, "Import")),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => { setIsImportingProfiles(false); setImportProfileJson(""); setImportProfileError(null); } },
                        window.SP_REACT.createElement("span", null, "Cancel")))))),
        editingProfile && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } },
                    "Edit Profile: ",
                    editingProfile.name),
                window.SP_REACT.createElement(DFL.TextField, { label: "Game Name", value: editingProfile.name, onChange: (e) => setEditingProfile({ ...editingProfile, name: e.target.value }), style: { marginBottom: "8px" } }),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginBottom: "8px" } },
                    "Cores: ",
                    formatCoreValues(editingProfile.cores)),
                window.SP_REACT.createElement(DFL.ToggleField, { label: "Enable Dynamic Mode", checked: editingProfile.dynamic_enabled, onChange: (checked) => setEditingProfile({ ...editingProfile, dynamic_enabled: checked }) }),
                window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleSaveProfileEdit },
                        window.SP_REACT.createElement("span", null, "Save")),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setEditingProfile(null) },
                        window.SP_REACT.createElement("span", null, "Cancel")))))),
        profiles.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "12px" } },
                "No game profiles yet. ",
                isGameRunning ? "Click the button above to create one!" : "Launch a game and create a profile."))) : (profiles.map((profile) => {
            const isActive = activeProfile?.app_id === profile.app_id || runningAppId === profile.app_id;
            return (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: profile.app_id },
                window.SP_REACT.createElement("div", { style: {
                        padding: "12px",
                        backgroundColor: isActive ? "#1a3a5c" : "#23262e",
                        borderRadius: "8px",
                        marginBottom: "8px",
                        border: isActive ? "2px solid #1a9fff" : "none",
                    } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
                        window.SP_REACT.createElement("div", { style: { flex: 1 } },
                            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                                window.SP_REACT.createElement("div", { style: { fontWeight: "bold", fontSize: "14px" } }, profile.name),
                                isActive && (window.SP_REACT.createElement("div", { style: {
                                        fontSize: "10px",
                                        padding: "2px 6px",
                                        backgroundColor: "#1a9fff",
                                        borderRadius: "4px",
                                        fontWeight: "bold",
                                    } }, "ACTIVE"))),
                            window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginTop: "2px" } },
                                "AppID: ",
                                profile.app_id),
                            window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginTop: "4px" } }, formatCoreValues(profile.cores)),
                            profile.dynamic_enabled && (window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#4caf50", marginTop: "2px" } }, "\u26A1 Dynamic Mode Enabled"))),
                        window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px" } },
                            window.SP_REACT.createElement("button", { onClick: () => setEditingProfile(profile), style: {
                                    padding: "8px",
                                    backgroundColor: "transparent",
                                    border: "none",
                                    color: "#1a9fff",
                                    cursor: "pointer",
                                }, title: "Edit profile" },
                                window.SP_REACT.createElement(FaEdit, null)),
                            window.SP_REACT.createElement("button", { onClick: () => handleDeleteProfile(profile.app_id), style: {
                                    padding: "8px",
                                    backgroundColor: "transparent",
                                    border: "none",
                                    color: "#f44336",
                                    cursor: "pointer",
                                }, title: "Delete profile" },
                                window.SP_REACT.createElement(FaTrash, null)))))));
        })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { borderTop: "1px solid #3d4450", margin: "16px 0" } })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "12px" } }, "Legacy Presets")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExportAll },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        window.SP_REACT.createElement(FaDownload, null),
                        window.SP_REACT.createElement("span", null, "Export All"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setIsImporting(true) },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        window.SP_REACT.createElement(FaUpload, null),
                        window.SP_REACT.createElement("span", null, "Import"))))),
        isImporting && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Import Presets"),
                window.SP_REACT.createElement(DFL.TextField, { label: "JSON Data", value: importJson, onChange: (e) => setImportJson(e.target.value), style: { marginBottom: "8px" } }),
                importError && (window.SP_REACT.createElement("div", { style: { color: "#f44336", fontSize: "12px", marginBottom: "8px" } }, importError)),
                window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleImport },
                        window.SP_REACT.createElement("span", null, "Import")),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => { setIsImporting(false); setImportJson(""); setImportError(null); } },
                        window.SP_REACT.createElement("span", null, "Cancel")))))),
        editingPreset && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } },
                    "Edit Preset: ",
                    editingPreset.label),
                window.SP_REACT.createElement(DFL.TextField, { label: "Label", value: editingPreset.label, onChange: (e) => setEditingPreset({ ...editingPreset, label: e.target.value }), style: { marginBottom: "8px" } }),
                window.SP_REACT.createElement(DFL.ToggleField, { label: "Use Timeout", checked: editingPreset.use_timeout, onChange: (checked) => setEditingPreset({ ...editingPreset, use_timeout: checked }) }),
                editingPreset.use_timeout && (window.SP_REACT.createElement(DFL.SliderField, { label: "Timeout (seconds)", value: editingPreset.timeout, min: 0, max: 60, step: 5, showValue: true, onChange: (value) => setEditingPreset({ ...editingPreset, timeout: value }) })),
                window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleSaveEdit },
                        window.SP_REACT.createElement("span", null, "Save")),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setEditingPreset(null) },
                        window.SP_REACT.createElement("span", null, "Cancel")))))),
        state.presets.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "12px" } }, "No legacy presets saved."))) : (state.presets.map((preset) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: preset.app_id },
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "8px",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
                    window.SP_REACT.createElement("div", null,
                        window.SP_REACT.createElement("div", { style: { fontWeight: "bold", fontSize: "14px" } }, preset.label),
                        window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } }, formatCoreValues(preset.value)),
                        preset.use_timeout && (window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#ff9800" } },
                            "Timeout: ",
                            preset.timeout,
                            "s")),
                        preset.tested && (window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#4caf50" } }, "\u2713 Tested"))),
                    window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px" } },
                        window.SP_REACT.createElement("button", { onClick: () => setEditingPreset(preset), style: {
                                padding: "8px",
                                backgroundColor: "transparent",
                                border: "none",
                                color: "#1a9fff",
                                cursor: "pointer",
                            } },
                            window.SP_REACT.createElement(FaEdit, null)),
                        window.SP_REACT.createElement("button", { onClick: () => handleExportSingle(preset), style: {
                                padding: "8px",
                                backgroundColor: "transparent",
                                border: "none",
                                color: "#8b929a",
                                cursor: "pointer",
                            } },
                            window.SP_REACT.createElement(FaDownload, null)),
                        window.SP_REACT.createElement("button", { onClick: () => handleDelete(preset.app_id), style: {
                                padding: "8px",
                                backgroundColor: "transparent",
                                border: "none",
                                color: "#f44336",
                                cursor: "pointer",
                            } },
                            window.SP_REACT.createElement(FaTrash, null))))))))),
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
 * ExpertMode component for DeckTune.
 *
 * Feature: decktune, Frontend UI Components - Expert Mode
 * Requirements: 4.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2
 *
 * Provides detailed manual controls and diagnostics for power users:
 * - Manual tab: Per-core sliders, Apply/Test/Disable buttons, live metrics
 * - Presets tab: Preset list with edit/delete/export, import
 * - Tests tab: Test selection, run button, history
 * - Diagnostics tab: System info, logs, export
 * - Panic Disable button: Always visible emergency reset (Requirement 4.5)
 */

const TABS = [
    { id: "manual", label: "Manual", icon: FaSlidersH },
    { id: "presets", label: "Presets", icon: FaList },
    { id: "tests", label: "Tests", icon: FaVial },
    { id: "diagnostics", label: "Diagnostics", icon: FaInfoCircle },
];
/**
 * Panic Disable Button component - always visible emergency reset.
 * Requirements: 4.5
 *
 * Features:
 * - Always visible red button
 * - Immediate reset to 0 on click
 */
const PanicDisableButton = () => {
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
                borderRadius: "8px",
            } },
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    color: "#fff",
                    fontWeight: "bold",
                } }, isPanicking ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                window.SP_REACT.createElement("span", null, "Disabling..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                window.SP_REACT.createElement(FaExclamationTriangle, null),
                window.SP_REACT.createElement("span", null, "PANIC DISABLE")))))));
};
/**
 * ExpertMode component - detailed controls for power users.
 * Requirements: 4.5, 7.1
 */
const ExpertMode = ({ initialTab = "manual" }) => {
    const [activeTab, setActiveTab] = SP_REACT.useState(initialTab);
    return (window.SP_REACT.createElement(DFL.PanelSection, { title: "Expert Mode" },
        window.SP_REACT.createElement(PanicDisableButton, null),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(TabNavigation, { activeTab: activeTab, onTabChange: setActiveTab })),
        activeTab === "manual" && window.SP_REACT.createElement(ManualTab, null),
        activeTab === "presets" && window.SP_REACT.createElement(PresetsTab, null),
        activeTab === "tests" && window.SP_REACT.createElement(TestsTab, null),
        activeTab === "diagnostics" && window.SP_REACT.createElement(DiagnosticsTab, null)));
};
const TabNavigation = ({ activeTab, onTabChange }) => {
    return (window.SP_REACT.createElement(DFL.Focusable, { style: {
            display: "flex",
            justifyContent: "space-around",
            marginBottom: "16px",
            backgroundColor: "#23262e",
            borderRadius: "8px",
            padding: "4px",
        } }, TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (window.SP_REACT.createElement("button", { key: tab.id, onClick: () => onTabChange(tab.id), style: {
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "4px",
                padding: "8px 4px",
                backgroundColor: isActive ? "#1a9fff" : "transparent",
                border: "none",
                borderRadius: "6px",
                color: isActive ? "#fff" : "#8b929a",
                cursor: "pointer",
                transition: "all 0.2s ease",
            } },
            window.SP_REACT.createElement(Icon, null),
            window.SP_REACT.createElement("span", { style: { fontSize: "10px" } }, tab.label)));
    })));
};
/**
 * Manual tab component.
 * Requirements: 5.4, 7.2, 13.3-13.6, 14.1, 14.2
 *
 * Features:
 * - Expert Overclocker Mode toggle with warning (Requirements 13.3-13.6)
 * - Simple Mode toggle (Requirements 14.1, 14.2)
 * - Per-core sliders with current values
 * - Apply, Test, Disable buttons
 * - Live temperature and frequency display
 * - "Tune for this game" button (Requirement 5.4)
 */
const ManualTab = () => {
    const { state, api } = useDeckTune();
    const { info: platformInfo } = usePlatformInfo();
    const [coreValues, setCoreValues] = SP_REACT.useState([...state.cores]);
    const [isApplying, setIsApplying] = SP_REACT.useState(false);
    const [isTesting, setIsTesting] = SP_REACT.useState(false);
    const [isTuning, setIsTuning] = SP_REACT.useState(false);
    const [simpleMode, setSimpleMode] = SP_REACT.useState(false);
    const [simpleValue, setSimpleValue] = SP_REACT.useState(-25);
    const [systemMetrics, setSystemMetrics] = SP_REACT.useState(null);
    // Expert Mode state (Requirements 13.3-13.6)
    const [expertMode, setExpertMode] = SP_REACT.useState(false);
    const [expertModeActive, setExpertModeActive] = SP_REACT.useState(false);
    const [showExpertWarning, setShowExpertWarning] = SP_REACT.useState(false);
    const [isTogglingExpert, setIsTogglingExpert] = SP_REACT.useState(false);
    // Fetch system metrics periodically
    SP_REACT.useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const info = await api.getSystemInfo();
                if (info.temps && info.freqs) {
                    setSystemMetrics({ temps: info.temps, freqs: info.freqs });
                }
            }
            catch (e) {
                // Ignore errors
            }
        };
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 2000);
        return () => clearInterval(interval);
    }, [api]);
    // Load expert mode status on mount (Requirements 13.3-13.6)
    SP_REACT.useEffect(() => {
        const loadExpertMode = async () => {
            try {
                const status = await api.getExpertModeStatus();
                setExpertMode(status.expert_mode);
                setExpertModeActive(status.active);
            }
            catch (e) {
                // Ignore errors, use default (false)
            }
        };
        loadExpertMode();
        // Listen for expert mode changes
        const handleExpertModeChange = (data) => {
            setExpertMode(data.enabled);
            setExpertModeActive(data.enabled);
        };
        api.on("expert_mode_changed", handleExpertModeChange);
        return () => {
            api.removeListener("expert_mode_changed", handleExpertModeChange);
        };
    }, [api]);
    // Initialize simpleValue from current cores (average) and load saved preference
    SP_REACT.useEffect(() => {
        if (coreValues.length === 4) {
            const avg = Math.round(coreValues.reduce((sum, val) => sum + val, 0) / 4);
            setSimpleValue(avg);
        }
        // Load saved simple_mode preference
        const loadSimpleMode = async () => {
            try {
                const saved = await api.getSetting("simple_mode");
                if (saved !== null && saved !== undefined) {
                    setSimpleMode(saved);
                }
            }
            catch (e) {
                // Ignore errors, use default (false)
            }
        };
        loadSimpleMode();
    }, []);
    const safeLimit = platformInfo?.safe_limit ?? -30;
    // Determine current limit based on expert mode (Requirements 13.2, 13.6)
    const currentMinLimit = expertModeActive ? -100 : safeLimit;
    /**
     * Handle Expert Mode toggle.
     * Requirements: 13.3, 13.4, 13.5
     */
    const handleExpertModeToggle = async (enabled) => {
        if (enabled) {
            // Show warning dialog (Requirement 13.3)
            setShowExpertWarning(true);
        }
        else {
            // Disable expert mode
            setIsTogglingExpert(true);
            try {
                const result = await api.disableExpertMode();
                if (result.success) {
                    setExpertMode(false);
                    setExpertModeActive(false);
                }
            }
            finally {
                setIsTogglingExpert(false);
            }
        }
    };
    /**
     * Confirm expert mode activation.
     * Requirements: 13.4
     */
    const handleExpertModeConfirm = async () => {
        setIsTogglingExpert(true);
        try {
            const result = await api.enableExpertMode(true);
            if (result.success) {
                setExpertMode(true);
                setExpertModeActive(true);
                setShowExpertWarning(false);
            }
            else {
                // Show error if confirmation failed
                alert(result.error || "Failed to enable expert mode");
            }
        }
        finally {
            setIsTogglingExpert(false);
        }
    };
    /**
     * Cancel expert mode activation.
     */
    const handleExpertModeCancel = () => {
        setShowExpertWarning(false);
    };
    /**
     * Handle Simple Mode toggle.
     * Requirements: 14.4, 14.5
     */
    const handleSimpleModeToggle = (enabled) => {
        if (enabled) {
            // Switching to Simple Mode: use average of current values (Requirement 14.4)
            const avg = Math.round(coreValues.reduce((sum, val) => sum + val, 0) / 4);
            setSimpleValue(avg);
        }
        else {
            // Switching to per-core mode: copy current simple value to all cores (Requirement 14.5)
            setCoreValues([simpleValue, simpleValue, simpleValue, simpleValue]);
        }
        setSimpleMode(enabled);
        // Save preference
        api.saveSetting("simple_mode", enabled);
    };
    /**
     * Handle simple slider value change.
     * Requirements: 14.3
     */
    const handleSimpleValueChange = (value) => {
        setSimpleValue(value);
        // Apply same value to all cores (Requirement 14.3)
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
     * Run quick test with current values.
     */
    const handleTest = async () => {
        setIsTesting(true);
        try {
            await api.applyUndervolt(coreValues);
            await api.runTest("cpu_quick");
        }
        finally {
            setIsTesting(false);
        }
    };
    /**
     * Disable undervolt (reset to 0).
     */
    const handleDisable = async () => {
        await api.disableUndervolt();
        setCoreValues([0, 0, 0, 0]);
    };
    /**
     * Tune for current game - run autotune and save as preset.
     * Requirements: 5.4
     */
    const handleTuneForGame = async () => {
        if (!state.runningAppId || !state.runningAppName) {
            return;
        }
        setIsTuning(true);
        try {
            const result = await api.tuneForCurrentGame("quick");
            if (result.success && result.preset) {
                setCoreValues(result.preset.value);
            }
        }
        finally {
            setIsTuning(false);
        }
    };
    /**
     * Run benchmark - 10 second stress test.
     * Requirements: 7.1, 7.4
     */
    const handleRunBenchmark = async () => {
        try {
            await api.runBenchmark();
        }
        catch (e) {
            console.error("Benchmark failed:", e);
        }
    };
    /**
     * Get color for value indicator.
     */
    const getValueColor = (value) => {
        const ratio = Math.abs(value) / Math.abs(safeLimit);
        if (ratio < 0.5)
            return "#4caf50";
        if (ratio < 0.8)
            return "#ff9800";
        return "#f44336";
    };
    // Check if a game is currently running
    const isGameRunning = state.runningAppId !== null && state.runningAppName !== null;
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        showExpertWarning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
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
                } },
                window.SP_REACT.createElement("div", { style: {
                        backgroundColor: "#1a1d23",
                        borderRadius: "12px",
                        padding: "24px",
                        maxWidth: "500px",
                        border: "2px solid #ff6b6b",
                        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
                    } },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            gap: "12px",
                            marginBottom: "16px",
                        } },
                        window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#ff6b6b", fontSize: "32px" } }),
                        window.SP_REACT.createElement("div", { style: { fontSize: "20px", fontWeight: "bold", color: "#ff6b6b" } }, "Expert Overclocker Mode")),
                    window.SP_REACT.createElement("div", { style: { fontSize: "14px", lineHeight: "1.6", marginBottom: "20px", color: "#e0e0e0" } },
                        window.SP_REACT.createElement("p", { style: { marginBottom: "12px" } },
                            window.SP_REACT.createElement("strong", null, "\u26A0\uFE0F WARNING:"),
                            " You are about to enable Expert Overclocker Mode, which removes all safety limits."),
                        window.SP_REACT.createElement("p", { style: { marginBottom: "12px" } },
                            "This mode allows undervolt values up to ",
                            window.SP_REACT.createElement("strong", null, "-100mV"),
                            ", far beyond the safe limits for your device."),
                        window.SP_REACT.createElement("p", { style: { marginBottom: "12px", color: "#ff9800" } },
                            window.SP_REACT.createElement("strong", null, "Risks include:")),
                        window.SP_REACT.createElement("ul", { style: { marginLeft: "20px", marginBottom: "12px", color: "#ffb74d" } },
                            window.SP_REACT.createElement("li", null, "System instability and crashes"),
                            window.SP_REACT.createElement("li", null, "Data loss from unexpected shutdowns"),
                            window.SP_REACT.createElement("li", null, "Potential hardware damage"),
                            window.SP_REACT.createElement("li", null, "Voiding of warranty")),
                        window.SP_REACT.createElement("p", { style: { color: "#f44336", fontWeight: "bold" } }, "Use at your own risk. The developers are not responsible for any damage.")),
                    window.SP_REACT.createElement(DFL.Focusable, { style: { display: "flex", gap: "12px" } },
                        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExpertModeConfirm, disabled: isTogglingExpert, style: {
                                flex: 1,
                                backgroundColor: "#b71c1c",
                            } },
                            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } }, isTogglingExpert ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                                window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                                window.SP_REACT.createElement("span", null, "Enabling..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                                window.SP_REACT.createElement(FaCheck, null),
                                window.SP_REACT.createElement("span", null, "I Understand, Enable"))))),
                        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExpertModeCancel, disabled: isTogglingExpert, style: { flex: 1 } },
                            window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                                window.SP_REACT.createElement(FaTimes, null),
                                window.SP_REACT.createElement("span", null, "Cancel")))))))),
        platformInfo && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginBottom: "8px" } },
                platformInfo.variant,
                " (",
                platformInfo.model,
                ") \u2022 Safe limit: ",
                safeLimit))),
        state.dynamicStatus && state.dynamicStatus.running && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(LoadGraph, { load: state.dynamicStatus.load, isActive: state.dynamicStatus.running }))),
        expertModeActive && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "12px",
                    backgroundColor: "#5c1313",
                    borderRadius: "8px",
                    marginBottom: "12px",
                    border: "2px solid #ff6b6b",
                    animation: "pulse 2s ease-in-out infinite",
                } },
                window.SP_REACT.createElement(FaExclamationTriangle, { style: { color: "#ff6b6b", fontSize: "20px", flexShrink: 0 } }),
                window.SP_REACT.createElement("div", null,
                    window.SP_REACT.createElement("div", { style: { fontWeight: "bold", color: "#ff6b6b", marginBottom: "2px" } }, "Expert Overclocker Mode Active"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#ffb74d" } }, "Extended range enabled: 0 to -100mV \u2022 Use with extreme caution"))))),
        systemMetrics && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(4, 1fr)",
                    gap: "8px",
                    marginBottom: "16px",
                } }, [0, 1, 2, 3].map((core) => (window.SP_REACT.createElement("div", { key: core, style: {
                    padding: "8px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    textAlign: "center",
                } },
                window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } },
                    "Core ",
                    core),
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", marginTop: "4px" } },
                    window.SP_REACT.createElement(FaThermometerHalf, { style: { color: "#ff9800", fontSize: "10px" } }),
                    window.SP_REACT.createElement("span", { style: { fontSize: "12px" } },
                        systemMetrics.temps[core] ?? "--",
                        "\u00B0C")),
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "4px" } },
                    window.SP_REACT.createElement(FaMicrochip, { style: { color: "#1a9fff", fontSize: "10px" } }),
                    window.SP_REACT.createElement("span", { style: { fontSize: "12px" } }, systemMetrics.freqs[core] ? `${(systemMetrics.freqs[core] / 1000).toFixed(1)}GHz` : "--")))))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" } },
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold" } }, "Undervolt Values"),
                window.SP_REACT.createElement("div", { style: { display: "flex", gap: "12px", alignItems: "center" } },
                    window.SP_REACT.createElement(DFL.ToggleField, { label: "Expert Mode", description: "Remove safety limits (-100mV)", checked: expertMode, onChange: handleExpertModeToggle, disabled: isTogglingExpert }),
                    window.SP_REACT.createElement(DFL.ToggleField, { label: "Simple Mode", description: "Control all cores with one slider", checked: simpleMode, onChange: handleSimpleModeToggle })))),
        simpleMode ? (
        /* Simple Mode: Single slider for all cores - Requirements: 14.2, 14.3 */
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { label: "All Cores", value: simpleValue, min: currentMinLimit, max: 0, step: 1, showValue: true, onChange: handleSimpleValueChange, valueSuffix: "", description: window.SP_REACT.createElement("span", { style: { color: getValueColor(simpleValue) } },
                    simpleValue === 0 ? "Disabled" : `${simpleValue} mV (applies to all 4 cores)`,
                    expertModeActive && simpleValue < safeLimit && (window.SP_REACT.createElement("span", { style: { color: "#ff6b6b", marginLeft: "8px" } }, "\u26A0\uFE0F EXPERT"))) }))) : (
        /* Per-core mode: Individual sliders */
        [0, 1, 2, 3].map((core) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: core },
            window.SP_REACT.createElement(DFL.SliderField, { label: `Core ${core}`, value: coreValues[core], min: currentMinLimit, max: 0, step: 1, showValue: true, onChange: (value) => handleCoreChange(core, value), valueSuffix: "", description: window.SP_REACT.createElement("span", { style: { color: getValueColor(coreValues[core]) } },
                    coreValues[core] === 0 ? "Disabled" : `${coreValues[core]} mV`,
                    expertModeActive && coreValues[core] < safeLimit && (window.SP_REACT.createElement("span", { style: { color: "#ff6b6b", marginLeft: "8px" } }, "\u26A0\uFE0F EXPERT"))) }))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    gap: "8px",
                    marginTop: "16px",
                } },
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleApply, disabled: isApplying || isTesting || isTuning, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        isApplying ? window.SP_REACT.createElement(FaSpinner, { className: "spin" }) : window.SP_REACT.createElement(FaCheck, null),
                        window.SP_REACT.createElement("span", null, "Apply"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleTest, disabled: isApplying || isTesting || isTuning, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        isTesting ? window.SP_REACT.createElement(FaSpinner, { className: "spin" }) : window.SP_REACT.createElement(FaVial, null),
                        window.SP_REACT.createElement("span", null, "Test"))),
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleDisable, disabled: isApplying || isTesting || isTuning, style: { flex: 1 } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" } },
                        window.SP_REACT.createElement(FaBan, null),
                        window.SP_REACT.createElement("span", null, "Disable"))))),
        isGameRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleTuneForGame, disabled: isApplying || isTesting || isTuning, style: { marginTop: "8px" } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#1a9fff" } }, isTuning ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                    window.SP_REACT.createElement("span", null,
                        "Tuning for ",
                        state.runningAppName,
                        "..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaRocket, null),
                    window.SP_REACT.createElement("span", null,
                        "Tune for ",
                        state.runningAppName))))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleRunBenchmark, disabled: isApplying || isTesting || isTuning || state.isBenchmarkRunning, style: { marginTop: "8px" } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff9800" } }, state.isBenchmarkRunning ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                    window.SP_REACT.createElement("span", null, "Running Benchmark..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaVial, null),
                    window.SP_REACT.createElement("span", null, "Run Benchmark")))))),
        state.isBenchmarkRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginTop: "8px",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" } },
                    window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { color: "#ff9800" } }),
                    window.SP_REACT.createElement("span", { style: { fontWeight: "bold" } }, "Running benchmark...")),
                window.SP_REACT.createElement(DFL.ProgressBarWithInfo, { label: "Benchmark Progress", description: "Testing performance with stress-ng", nProgress: 50, sOperationText: "~10 seconds" }),
                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginTop: "8px", textAlign: "center" } }, "All tuning controls are disabled during benchmark")))),
        state.lastBenchmarkResult && !state.isBenchmarkRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1b5e20",
                    borderRadius: "8px",
                    marginTop: "8px",
                    borderLeft: "4px solid #4caf50",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" } },
                    window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "14px" } }, "Latest Benchmark"),
                    window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50" } })),
                window.SP_REACT.createElement("div", { style: { marginBottom: "8px" } },
                    window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#a5d6a7" } }, "Score"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "20px", fontWeight: "bold", color: "#4caf50" } },
                        state.lastBenchmarkResult.score.toFixed(2),
                        " bogo ops/s")),
                window.SP_REACT.createElement("div", { style: { marginBottom: "8px" } },
                    window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#a5d6a7", marginBottom: "4px" } }, "Undervolt Values Used"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#c8e6c9" } },
                        "[",
                        state.lastBenchmarkResult.cores_used.join(", "),
                        "] mV")),
                state.benchmarkHistory && state.benchmarkHistory.length > 1 && (() => {
                    const current = state.benchmarkHistory[0];
                    const previous = state.benchmarkHistory[1];
                    const scoreDiff = current.score - previous.score;
                    const percentChange = ((scoreDiff / previous.score) * 100);
                    const improvement = scoreDiff > 0;
                    return (window.SP_REACT.createElement("div", { style: { marginTop: "8px", paddingTop: "8px", borderTop: "1px solid #2e7d32" } },
                        window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#a5d6a7", marginBottom: "4px" } }, "Comparison with Previous Run"),
                        window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                            improvement ? (window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50" } })) : (window.SP_REACT.createElement(FaTimes, { style: { color: "#ff6b6b" } })),
                            window.SP_REACT.createElement("span", { style: { fontSize: "13px", color: improvement ? "#4caf50" : "#ff6b6b", fontWeight: "bold" } },
                                improvement ? "+" : "",
                                percentChange.toFixed(2),
                                "%"),
                            window.SP_REACT.createElement("span", { style: { fontSize: "11px", color: "#a5d6a7" } },
                                "(",
                                improvement ? "+" : "",
                                scoreDiff.toFixed(2),
                                " bogo ops/s)"))));
                })(),
                window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#81c784", marginTop: "8px" } }, new Date(state.lastBenchmarkResult.timestamp).toLocaleString())))),
        state.benchmarkHistory && state.benchmarkHistory.length > 0 && (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Benchmark History (Last 10)")),
            state.benchmarkHistory.slice(0, 10).map((result, index) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: index },
                window.SP_REACT.createElement("div", { style: {
                        padding: "10px",
                        backgroundColor: "#23262e",
                        borderRadius: "6px",
                        marginBottom: "6px",
                        borderLeft: `3px solid #4caf50`,
                    } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
                        window.SP_REACT.createElement("div", null,
                            window.SP_REACT.createElement("div", { style: { fontWeight: "bold", fontSize: "13px", color: "#4caf50" } },
                                result.score.toFixed(2),
                                " bogo ops/s"),
                            window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginTop: "2px" } },
                                "Cores: [",
                                result.cores_used.join(", "),
                                "] mV")),
                        window.SP_REACT.createElement("div", { style: { textAlign: "right" } },
                            window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a" } }, new Date(result.timestamp).toLocaleDateString()),
                            window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } }, new Date(result.timestamp).toLocaleTimeString()))))))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    marginTop: "12px",
                    padding: "8px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    fontSize: "12px",
                    textAlign: "center",
                } },
                "Status: ",
                window.SP_REACT.createElement("span", { style: { color: state.status === "enabled" ? "#4caf50" : "#8b929a" } }, state.status))),
        window.SP_REACT.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `)));
};
/**
 * Presets tab component - now uses PresetsTabNew with profile management.
 * Requirements: 3.2, 5.1, 5.4, 7.3, 9.1, 9.2
 */
const PresetsTab = PresetsTabNew;
/**
 * Available test options.
 */
const TEST_OPTIONS = [
    { value: "cpu_quick", label: "CPU Quick (30s)" },
    { value: "cpu_long", label: "CPU Long (5m)" },
    { value: "ram_quick", label: "RAM Quick (2m)" },
    { value: "ram_thorough", label: "RAM Thorough (15m)" },
    { value: "combo", label: "Combo Stress (5m)" },
];
/**
 * Tests tab component.
 * Requirements: 7.4
 *
 * Features:
 * - Test selection dropdown
 * - Run test button with progress
 * - Last 10 test results history
 * - Warning banner if binaries missing
 */
const TestsTab = () => {
    const { history, currentTest, isRunning, runTest } = useTests();
    const { missing: missingBinaries, hasMissing, check: checkBinaries } = useBinaries();
    const [selectedTest, setSelectedTest] = SP_REACT.useState("cpu_quick");
    // Check binaries on mount
    SP_REACT.useEffect(() => {
        checkBinaries();
    }, []);
    /**
     * Handle run test button click.
     */
    const handleRunTest = async () => {
        await runTest(selectedTest);
    };
    /**
     * Format duration for display.
     */
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        if (mins > 0) {
            return `${mins}m ${secs}s`;
        }
        return `${secs}s`;
    };
    /**
     * Format timestamp for display.
     */
    const formatTimestamp = (timestamp) => {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        }
        catch {
            return timestamp;
        }
    };
    /**
     * Get test label from value.
     */
    const getTestLabel = (value) => {
        return TEST_OPTIONS.find((t) => t.value === value)?.label || value;
    };
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        hasMissing && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                    padding: "12px",
                    backgroundColor: "#5c4813",
                    borderRadius: "8px",
                    marginBottom: "12px",
                    border: "1px solid #ff9800",
                } },
                window.SP_REACT.createElement(FaExclamationCircle, { style: { color: "#ff9800", fontSize: "18px", flexShrink: 0, marginTop: "2px" } }),
                window.SP_REACT.createElement("div", null,
                    window.SP_REACT.createElement("div", { style: { fontWeight: "bold", color: "#ffb74d", marginBottom: "4px" } }, "Missing Components"),
                    window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#ffe0b2" } },
                        "Required tools not found: ",
                        window.SP_REACT.createElement("strong", null, missingBinaries.join(", "))),
                    window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#ffcc80", marginTop: "4px" } }, "Stress tests are unavailable until binaries are installed."))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Run Stress Test")),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.DropdownItem, { label: "Select Test", menuLabel: "Select Test", rgOptions: TEST_OPTIONS.map((t) => ({
                    data: t.value,
                    label: t.label,
                })), selectedOption: selectedTest, onChange: (option) => setSelectedTest(option.data), disabled: hasMissing })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleRunTest, disabled: isRunning || hasMissing },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", opacity: hasMissing ? 0.5 : 1 } }, isRunning ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                    window.SP_REACT.createElement("span", null,
                        "Running ",
                        getTestLabel(currentTest || selectedTest),
                        "..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaPlay, null),
                    window.SP_REACT.createElement("span", null, "Run Test")))))),
        isRunning && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1a3a5c",
                    borderRadius: "8px",
                    marginTop: "8px",
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" } },
                    window.SP_REACT.createElement(FaSpinner, { className: "spin", style: { color: "#1a9fff" } }),
                    window.SP_REACT.createElement("span", null, "Test in progress...")),
                window.SP_REACT.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } },
                    "Running: ",
                    getTestLabel(currentTest || selectedTest))))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Test History (Last 10)")),
        history.length === 0 ? (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px" } }, "No tests run yet."))) : (history.slice(0, 10).map((entry, index) => (window.SP_REACT.createElement(DFL.PanelSectionRow, { key: index },
            window.SP_REACT.createElement("div", { style: {
                    padding: "10px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    marginBottom: "6px",
                    borderLeft: `3px solid ${entry.passed ? "#4caf50" : "#f44336"}`,
                } },
                window.SP_REACT.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
                    window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        entry.passed ? (window.SP_REACT.createElement(FaCheck, { style: { color: "#4caf50" } })) : (window.SP_REACT.createElement(FaTimes, { style: { color: "#f44336" } })),
                        window.SP_REACT.createElement("span", { style: { fontWeight: "bold", fontSize: "13px" } }, getTestLabel(entry.test_name))),
                    window.SP_REACT.createElement("span", { style: { fontSize: "11px", color: "#8b929a" } }, formatDuration(entry.duration))),
                window.SP_REACT.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginTop: "4px" } }, formatTimestamp(entry.timestamp)),
                window.SP_REACT.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginTop: "2px" } },
                    "Cores: [",
                    entry.cores_tested.join(", "),
                    "]")))))),
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
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExportDiagnostics, disabled: isExporting, style: { marginTop: "16px" } },
                window.SP_REACT.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } }, isExporting ? (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaSpinner, { className: "spin" }),
                    window.SP_REACT.createElement("span", null, "Exporting..."))) : (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
                    window.SP_REACT.createElement(FaDownload, null),
                    window.SP_REACT.createElement("span", null, "Export Diagnostics")))))),
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
 * DeckTuneApp - Main application component.
 */

/**
 * Main content component with mode switching and first-run detection.
 */
const DeckTuneContent = () => {
    const [mode, setMode] = SP_REACT.useState("wizard");
    const [showSetupWizard, setShowSetupWizard] = SP_REACT.useState(false);
    const [isFirstRun, setIsFirstRun] = SP_REACT.useState(null);
    const { state, api } = useDeckTune();
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
    const handleRunSetupWizard = () => {
        setShowSetupWizard(true);
    };
    if (showSetupWizard) {
        return (window.SP_REACT.createElement(SetupWizard, { onComplete: handleSetupComplete, onCancel: handleSetupCancel, onSkip: handleSetupSkip }));
    }
    if (isFirstRun === null) {
        return (window.SP_REACT.createElement(DFL.PanelSection, { title: "DeckTune" },
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: { textAlign: "center", padding: "16px", color: "#8b929a" } }, "Loading..."))));
    }
    return (window.SP_REACT.createElement(window.SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSection, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "center",
                        gap: "8px",
                        marginBottom: "8px",
                    } },
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setMode("wizard") },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: "6px",
                                color: mode === "wizard" ? "#1a9fff" : "#8b929a"
                            } },
                            window.SP_REACT.createElement(FaMagic, null),
                            window.SP_REACT.createElement("span", null, "Wizard"))),
                    window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setMode("expert") },
                        window.SP_REACT.createElement("div", { style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: "6px",
                                color: mode === "expert" ? "#1a9fff" : "#8b929a"
                            } },
                            window.SP_REACT.createElement(FaCog, null),
                            window.SP_REACT.createElement("span", null, "Expert"))))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement("div", { style: {
                        textAlign: "center",
                        fontSize: "12px",
                        color: "#8b929a",
                        padding: "4px 8px",
                        backgroundColor: "#23262e",
                        borderRadius: "4px",
                    } },
                    "Status: ",
                    window.SP_REACT.createElement("span", { style: {
                            color: state.status === "enabled" || state.status === "DYNAMIC RUNNING"
                                ? "#4caf50"
                                : state.status === "error"
                                    ? "#f44336"
                                    : "#8b929a"
                        } }, state.status))),
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleRunSetupWizard },
                    window.SP_REACT.createElement("div", { style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "6px",
                            color: "#8b929a",
                            fontSize: "11px"
                        } },
                        window.SP_REACT.createElement(FaWrench, null),
                        window.SP_REACT.createElement("span", null, "Run Setup Wizard"))))),
        mode === "wizard" ? window.SP_REACT.createElement(WizardMode, null) : window.SP_REACT.createElement(ExpertMode, null)));
};
/**
 * Main app component with initialization.
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
    return window.SP_REACT.createElement(DeckTuneContent, null);
};

var index = definePlugin(() => {
    return {
        name: "DeckTune",
        content: (window.SP_REACT.createElement(DeckTuneProvider, null,
            window.SP_REACT.createElement(DeckTuneApp, null))),
        icon: window.SP_REACT.createElement(FaMagic, null),
        onDismount() {
            console.log("DeckTune unloaded");
        },
    };
});

export { index as default };
//# sourceMappingURL=index.js.map
