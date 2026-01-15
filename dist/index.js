const manifest = {"name":"DeckTune"};
const API_VERSION = 2;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
let api;
try {
    api = internalAPIConnection.connect(API_VERSION, manifest.name);
}
catch {
    api = internalAPIConnection.connect(1, manifest.name);
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version 1. Some features may not work.`);
}
if (api._version != API_VERSION) {
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version ${api._version}. Some features may not work.`);
}
const call = api.call;
const addEventListener = api.addEventListener;
const removeEventListener = api.removeEventListener;

var DefaultContext = {
  color: undefined,
  size: undefined,
  className: undefined,
  style: undefined,
  attr: undefined
};
var IconContext = SP_REACT.createContext && SP_REACT.createContext(DefaultContext);

var __assign = window && window.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
var __rest = window && window.__rest || function (s, e) {
  var t = {};
  for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0) t[p] = s[p];
  if (s != null && typeof Object.getOwnPropertySymbols === "function") for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
    if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i])) t[p[i]] = s[p[i]];
  }
  return t;
};
function Tree2Element(tree) {
  return tree && tree.map(function (node, i) {
    return SP_REACT.createElement(node.tag, __assign({
      key: i
    }, node.attr), Tree2Element(node.child));
  });
}
function GenIcon(data) {
  // eslint-disable-next-line react/display-name
  return function (props) {
    return SP_REACT.createElement(IconBase, __assign({
      attr: __assign({}, data.attr)
    }, props), Tree2Element(data.child));
  };
}
function IconBase(props) {
  var elem = function (conf) {
    var attr = props.attr,
      size = props.size,
      title = props.title,
      svgProps = __rest(props, ["attr", "size", "title"]);
    var computedSize = size || conf.size || "1em";
    var className;
    if (conf.className) className = conf.className;
    if (props.className) className = (className ? className + " " : "") + props.className;
    return SP_REACT.createElement("svg", __assign({
      stroke: "currentColor",
      fill: "currentColor",
      strokeWidth: "0"
    }, conf.attr, attr, svgProps, {
      className: className,
      style: __assign(__assign({
        color: props.color || conf.color
      }, conf.style), props.style),
      height: computedSize,
      width: computedSize,
      xmlns: "http://www.w3.org/2000/svg"
    }), title && SP_REACT.createElement("title", null, title), props.children);
  };
  return IconContext !== undefined ? SP_REACT.createElement(IconContext.Consumer, null, function (conf) {
    return elem(conf);
  }) : elem(DefaultContext);
}

// THIS FILE IS AUTO GENERATED
function FaBalanceScale (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M256 336h-.02c0-16.18 1.34-8.73-85.05-181.51-17.65-35.29-68.19-35.36-85.87 0C-2.06 328.75.02 320.33.02 336H0c0 44.18 57.31 80 128 80s128-35.82 128-80zM128 176l72 144H56l72-144zm511.98 160c0-16.18 1.34-8.73-85.05-181.51-17.65-35.29-68.19-35.36-85.87 0-87.12 174.26-85.04 165.84-85.04 181.51H384c0 44.18 57.31 80 128 80s128-35.82 128-80h-.02zM440 320l72-144 72 144H440zm88 128H352V153.25c23.51-10.29 41.16-31.48 46.39-57.25H528c8.84 0 16-7.16 16-16V48c0-8.84-7.16-16-16-16H383.64C369.04 12.68 346.09 0 320 0s-49.04 12.68-63.64 32H112c-8.84 0-16 7.16-16 16v32c0 8.84 7.16 16 16 16h129.61c5.23 25.76 22.87 46.96 46.39 57.25V448H112c-8.84 0-16 7.16-16 16v32c0 8.84 7.16 16 16 16h416c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16z"}}]})(props);
}function FaBan (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119.034 8 8 119.033 8 256s111.034 248 248 248 248-111.034 248-248S392.967 8 256 8zm130.108 117.892c65.448 65.448 70 165.481 20.677 235.637L150.47 105.216c70.204-49.356 170.226-44.735 235.638 20.676zM125.892 386.108c-65.448-65.448-70-165.481-20.677-235.637L361.53 406.784c-70.203 49.356-170.226 44.736-235.638-20.676z"}}]})(props);
}function FaBatteryFull (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M544 160v64h32v64h-32v64H64V160h480m16-64H48c-26.51 0-48 21.49-48 48v224c0 26.51 21.49 48 48 48h512c26.51 0 48-21.49 48-48v-16h8c13.255 0 24-10.745 24-24V184c0-13.255-10.745-24-24-24h-8v-16c0-26.51-21.49-48-48-48zm-48 96H96v128h416V192z"}}]})(props);
}function FaCheck (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M173.898 439.404l-166.4-166.4c-9.997-9.997-9.997-26.206 0-36.204l36.203-36.204c9.997-9.998 26.207-9.998 36.204 0L192 312.69 432.095 72.596c9.997-9.997 26.207-9.997 36.204 0l36.203 36.204c9.997 9.997 9.997 26.206 0 36.204l-294.4 294.401c-9.998 9.997-26.207 9.997-36.204-.001z"}}]})(props);
}function FaCog (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M487.4 315.7l-42.6-24.6c4.3-23.2 4.3-47 0-70.2l42.6-24.6c4.9-2.8 7.1-8.6 5.5-14-11.1-35.6-30-67.8-54.7-94.6-3.8-4.1-10-5.1-14.8-2.3L380.8 110c-17.9-15.4-38.5-27.3-60.8-35.1V25.8c0-5.6-3.9-10.5-9.4-11.7-36.7-8.2-74.3-7.8-109.2 0-5.5 1.2-9.4 6.1-9.4 11.7V75c-22.2 7.9-42.8 19.8-60.8 35.1L88.7 85.5c-4.9-2.8-11-1.9-14.8 2.3-24.7 26.7-43.6 58.9-54.7 94.6-1.7 5.4.6 11.2 5.5 14L67.3 221c-4.3 23.2-4.3 47 0 70.2l-42.6 24.6c-4.9 2.8-7.1 8.6-5.5 14 11.1 35.6 30 67.8 54.7 94.6 3.8 4.1 10 5.1 14.8 2.3l42.6-24.6c17.9 15.4 38.5 27.3 60.8 35.1v49.2c0 5.6 3.9 10.5 9.4 11.7 36.7 8.2 74.3 7.8 109.2 0 5.5-1.2 9.4-6.1 9.4-11.7v-49.2c22.2-7.9 42.8-19.8 60.8-35.1l42.6 24.6c4.9 2.8 11 1.9 14.8-2.3 24.7-26.7 43.6-58.9 54.7-94.6 1.5-5.5-.7-11.3-5.6-14.1zM256 336c-44.1 0-80-35.9-80-80s35.9-80 80-80 80 35.9 80 80-35.9 80-80 80z"}}]})(props);
}function FaDownload (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z"}}]})(props);
}function FaEdit (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M402.6 83.2l90.2 90.2c3.8 3.8 3.8 10 0 13.8L274.4 405.6l-92.8 10.3c-12.4 1.4-22.9-9.1-21.5-21.5l10.3-92.8L388.8 83.2c3.8-3.8 10-3.8 13.8 0zm162-22.9l-48.8-48.8c-15.2-15.2-39.9-15.2-55.2 0l-35.4 35.4c-3.8 3.8-3.8 10 0 13.8l90.2 90.2c3.8 3.8 10 3.8 13.8 0l35.4-35.4c15.2-15.3 15.2-40 0-55.2zM384 346.2V448H64V128h229.8c3.2 0 6.2-1.3 8.5-3.5l40-40c7.6-7.6 2.2-20.5-8.5-20.5H48C21.5 64 0 85.5 0 112v352c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V306.2c0-10.7-12.9-16-20.5-8.5l-40 40c-2.2 2.3-3.5 5.3-3.5 8.5z"}}]})(props);
}function FaExclamationCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 256c0 136.997-111.043 248-248 248S8 392.997 8 256C8 119.083 119.043 8 256 8s248 111.083 248 248zm-248 50c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"}}]})(props);
}function FaExclamationTriangle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"}}]})(props);
}function FaInfoCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm0 110c23.196 0 42 18.804 42 42s-18.804 42-42 42-42-18.804-42-42 18.804-42 42-42zm56 254c0 6.627-5.373 12-12 12h-88c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h12v-64h-12c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h64c6.627 0 12 5.373 12 12v100h12c6.627 0 12 5.373 12 12v24z"}}]})(props);
}function FaLeaf (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M546.2 9.7c-5.6-12.5-21.6-13-28.3-1.2C486.9 62.4 431.4 96 368 96h-80C182 96 96 182 96 288c0 7 .8 13.7 1.5 20.5C161.3 262.8 253.4 224 384 224c8.8 0 16 7.2 16 16s-7.2 16-16 16C132.6 256 26 410.1 2.4 468c-6.6 16.3 1.2 34.9 17.5 41.6 16.4 6.8 35-1.1 41.8-17.3 1.5-3.6 20.9-47.9 71.9-90.6 32.4 43.9 94 85.8 174.9 77.2C465.5 467.5 576 326.7 576 154.3c0-50.2-10.8-102.2-29.8-144.6z"}}]})(props);
}function FaList (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M80 368H16a16 16 0 0 0-16 16v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16v-64a16 16 0 0 0-16-16zm0-320H16A16 16 0 0 0 0 64v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16V64a16 16 0 0 0-16-16zm0 160H16a16 16 0 0 0-16 16v64a16 16 0 0 0 16 16h64a16 16 0 0 0 16-16v-64a16 16 0 0 0-16-16zm416 176H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16zm0-320H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16V80a16 16 0 0 0-16-16zm0 160H176a16 16 0 0 0-16 16v32a16 16 0 0 0 16 16h320a16 16 0 0 0 16-16v-32a16 16 0 0 0-16-16z"}}]})(props);
}function FaMagic (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M224 96l16-32 32-16-32-16-16-32-16 32-32 16 32 16 16 32zM80 160l26.66-53.33L160 80l-53.34-26.67L80 0 53.34 53.33 0 80l53.34 26.67L80 160zm352 128l-26.66 53.33L352 368l53.34 26.67L432 448l26.66-53.33L512 368l-53.34-26.67L432 288zm70.62-193.77L417.77 9.38C411.53 3.12 403.34 0 395.15 0c-8.19 0-16.38 3.12-22.63 9.38L9.38 372.52c-12.5 12.5-12.5 32.76 0 45.25l84.85 84.85c6.25 6.25 14.44 9.37 22.62 9.37 8.19 0 16.38-3.12 22.63-9.37l363.14-363.15c12.5-12.48 12.5-32.75 0-45.24zM359.45 203.46l-50.91-50.91 86.6-86.6 50.91 50.91-86.6 86.6z"}}]})(props);
}function FaMicrochip (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M416 48v416c0 26.51-21.49 48-48 48H144c-26.51 0-48-21.49-48-48V48c0-26.51 21.49-48 48-48h224c26.51 0 48 21.49 48 48zm96 58v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42V88h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zM30 376h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6z"}}]})(props);
}function FaPlay (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M424.4 214.7L72.4 6.6C43.8-10.3 0 6.1 0 47.9V464c0 37.5 40.7 60.1 72.4 41.3l352-208c31.4-18.5 31.5-64.1 0-82.6z"}}]})(props);
}function FaRocket (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M505.12019,19.09375c-1.18945-5.53125-6.65819-11-12.207-12.1875C460.716,0,435.507,0,410.40747,0,307.17523,0,245.26909,55.20312,199.05238,128H94.83772c-16.34763.01562-35.55658,11.875-42.88664,26.48438L2.51562,253.29688A28.4,28.4,0,0,0,0,264a24.00867,24.00867,0,0,0,24.00582,24H127.81618l-22.47457,22.46875c-11.36521,11.36133-12.99607,32.25781,0,45.25L156.24582,406.625c11.15623,11.1875,32.15619,13.15625,45.27726,0l22.47457-22.46875V488a24.00867,24.00867,0,0,0,24.00581,24,28.55934,28.55934,0,0,0,10.707-2.51562l98.72834-49.39063c14.62888-7.29687,26.50776-26.5,26.50776-42.85937V312.79688c72.59753-46.3125,128.03493-108.40626,128.03493-211.09376C512.07526,76.5,512.07526,51.29688,505.12019,19.09375ZM384.04033,168A40,40,0,1,1,424.05,128,40.02322,40.02322,0,0,1,384.04033,168Z"}}]})(props);
}function FaSlidersH (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M496 384H160v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h80v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h336c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160h-80v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h336v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h80c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160H288V48c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16C7.2 64 0 71.2 0 80v32c0 8.8 7.2 16 16 16h208v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h208c8.8 0 16-7.2 16-16V80c0-8.8-7.2-16-16-16z"}}]})(props);
}function FaSpinner (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M304 48c0 26.51-21.49 48-48 48s-48-21.49-48-48 21.49-48 48-48 48 21.49 48 48zm-48 368c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zm208-208c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.49-48-48-48zM96 256c0-26.51-21.49-48-48-48S0 229.49 0 256s21.49 48 48 48 48-21.49 48-48zm12.922 99.078c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.491-48-48-48zm294.156 0c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48c0-26.509-21.49-48-48-48zM108.922 60.922c-26.51 0-48 21.49-48 48s21.49 48 48 48 48-21.49 48-48-21.491-48-48-48z"}}]})(props);
}function FaThermometerHalf (props) {
  return GenIcon({"attr":{"viewBox":"0 0 256 512"},"child":[{"tag":"path","attr":{"d":"M192 384c0 35.346-28.654 64-64 64s-64-28.654-64-64c0-23.685 12.876-44.349 32-55.417V224c0-17.673 14.327-32 32-32s32 14.327 32 32v104.583c19.124 11.068 32 31.732 32 55.417zm32-84.653c19.912 22.563 32 52.194 32 84.653 0 70.696-57.303 128-128 128-.299 0-.609-.001-.909-.003C56.789 511.509-.357 453.636.002 383.333.166 351.135 12.225 321.755 32 299.347V96c0-53.019 42.981-96 96-96s96 42.981 96 96v203.347zM208 384c0-34.339-19.37-52.19-32-66.502V96c0-26.467-21.533-48-48-48S80 69.533 80 96v221.498c-12.732 14.428-31.825 32.1-31.999 66.08-.224 43.876 35.563 80.116 79.423 80.42L128 464c44.112 0 80-35.888 80-80z"}}]})(props);
}function FaTimes (props) {
  return GenIcon({"attr":{"viewBox":"0 0 352 512"},"child":[{"tag":"path","attr":{"d":"M242.72 256l100.07-100.07c12.28-12.28 12.28-32.19 0-44.48l-22.24-22.24c-12.28-12.28-32.19-12.28-44.48 0L176 189.28 75.93 89.21c-12.28-12.28-32.19-12.28-44.48 0L9.21 111.45c-12.28 12.28-12.28 32.19 0 44.48L109.28 256 9.21 356.07c-12.28 12.28-12.28 32.19 0 44.48l22.24 22.24c12.28 12.28 32.2 12.28 44.48 0L176 322.72l100.07 100.07c12.28 12.28 32.2 12.28 44.48 0l22.24-22.24c12.28-12.28 12.28-32.19 0-44.48L242.72 256z"}}]})(props);
}function FaTrash (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M432 32H312l-9.4-18.7A24 24 0 0 0 281.1 0H166.8a23.72 23.72 0 0 0-21.4 13.3L136 32H16A16 16 0 0 0 0 48v32a16 16 0 0 0 16 16h416a16 16 0 0 0 16-16V48a16 16 0 0 0-16-16zM53.2 467a48 48 0 0 0 47.9 45h245.8a48 48 0 0 0 47.9-45L416 128H32z"}}]})(props);
}function FaUpload (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M296 384h-80c-13.3 0-24-10.7-24-24V192h-87.7c-17.8 0-26.7-21.5-14.1-34.1L242.3 5.7c7.5-7.5 19.8-7.5 27.3 0l152.2 152.2c12.6 12.6 3.7 34.1-14.1 34.1H320v168c0 13.3-10.7 24-24 24zm216-8v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h136v8c0 30.9 25.1 56 56 56h80c30.9 0 56-25.1 56-56v-8h136c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z"}}]})(props);
}function FaVial (props) {
  return GenIcon({"attr":{"viewBox":"0 0 480 512"},"child":[{"tag":"path","attr":{"d":"M477.7 186.1L309.5 18.3c-3.1-3.1-8.2-3.1-11.3 0l-34 33.9c-3.1 3.1-3.1 8.2 0 11.3l11.2 11.1L33 316.5c-38.8 38.7-45.1 102-9.4 143.5 20.6 24 49.5 36 78.4 35.9 26.4 0 52.8-10 72.9-30.1l246.3-245.7 11.2 11.1c3.1 3.1 8.2 3.1 11.3 0l34-33.9c3.1-3 3.1-8.1 0-11.2zM318 256H161l148-147.7 78.5 78.3L318 256z"}}]})(props);
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
        // Register Steam client listeners
        this.registeredListeners.push(SteamClient.GameSessions.RegisterForAppLifetimeNotifications(this.onAppLifetimeNotification.bind(this)));
        this.registeredListeners.push(SteamClient.System.RegisterForOnResumeFromSuspend(this.onResumeFromSuspend.bind(this)));
        // Register backend event listeners
        addEventListener("tuning_progress", this.onTuningProgress.bind(this));
        addEventListener("tuning_complete", this.onTuningComplete.bind(this));
        addEventListener("test_complete", this.onTestComplete.bind(this));
        addEventListener("update_status", this.onStatusUpdate.bind(this));
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
        this.setState({ gymdeckRunning: false, status: "disabled" });
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
    // Autotune state (new properties)
    autotuneProgress: null,
    autotuneResult: null,
    isAutotuning: false,
    // Test state (new properties)
    testHistory: [],
    currentTest: null,
    isTestRunning: false,
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
    return (React.createElement(DeckTuneContext.Provider, { value: contextValue }, children));
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
    return (React.createElement(DFL.PanelSectionRow, null,
        React.createElement(DFL.ButtonItem, { layout: "below", onClick: handlePanicDisable, disabled: isPanicking, style: {
                backgroundColor: "#b71c1c",
                borderRadius: "8px",
            } },
            React.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    color: "#fff",
                    fontWeight: "bold",
                } }, isPanicking ? (React.createElement(React.Fragment, null,
                React.createElement(FaSpinner, { className: "spin" }),
                React.createElement("span", null, "Disabling..."))) : (React.createElement(React.Fragment, null,
                React.createElement(FaExclamationTriangle, null),
                React.createElement("span", null, "PANIC DISABLE"))))),
        React.createElement("style", null, `
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
 * Requirements: 4.5, 5.4, 6.1
 */
const WizardMode = ({ onComplete, onCancel }) => {
    const [step, setStep] = SP_REACT.useState(1);
    const [selectedGoal, setSelectedGoal] = SP_REACT.useState(null);
    const { progress, result, isRunning, start, stop } = useAutotune();
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
     * Handle cancel button click.
     * Requirements: 6.3
     */
    const handleCancel = async () => {
        if (isRunning) {
            await stop();
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
     * Reset wizard to start over.
     */
    const handleStartOver = () => {
        setStep(1);
        setSelectedGoal(null);
    };
    return (React.createElement(DFL.PanelSection, { title: "DeckTune Wizard" },
        React.createElement(PanicDisableButton$1, null),
        hasMissing && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                    padding: "12px",
                    backgroundColor: "#5c4813",
                    borderRadius: "8px",
                    marginBottom: "12px",
                    border: "1px solid #ff9800",
                } },
                React.createElement(FaExclamationCircle, { style: { color: "#ff9800", fontSize: "18px", flexShrink: 0, marginTop: "2px" } }),
                React.createElement("div", null,
                    React.createElement("div", { style: { fontWeight: "bold", color: "#ffb74d", marginBottom: "4px" } }, "Missing Components"),
                    React.createElement("div", { style: { fontSize: "12px", color: "#ffe0b2" } },
                        "Required tools not found: ",
                        React.createElement("strong", null, missingBinaries.join(", "))),
                    React.createElement("div", { style: { fontSize: "11px", color: "#ffcc80", marginTop: "4px" } }, "Autotune and stress tests are unavailable. Please reinstall the plugin or add missing binaries to bin/ folder."))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(StepIndicator, { currentStep: step })),
        step === 1 && (React.createElement(GoalSelectionStep, { onSelect: handleGoalSelect, platformInfo: platformInfo, disabled: hasMissing })),
        step === 2 && (React.createElement(AutotuneProgressStep, { progress: progress, isRunning: isRunning, onCancel: handleCancel, selectedGoal: selectedGoal })),
        step === 3 && result && (React.createElement(ResultsStep, { result: result, platformInfo: platformInfo, onApplyAndSave: handleApplyAndSave, onStartOver: handleStartOver }))));
};
const StepIndicator = ({ currentStep }) => {
    const steps = [
        { num: 1, label: "Goal" },
        { num: 2, label: "Tuning" },
        { num: 3, label: "Results" },
    ];
    return (React.createElement(DFL.Focusable, { style: { display: "flex", justifyContent: "center", gap: "16px", marginBottom: "16px" } }, steps.map((s, index) => (React.createElement("div", { key: s.num, style: {
            display: "flex",
            alignItems: "center",
            gap: "8px",
        } },
        React.createElement("div", { style: {
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
            } }, currentStep > s.num ? React.createElement(FaCheck, { size: 12 }) : s.num),
        React.createElement("span", { style: {
                color: currentStep >= s.num ? "#fff" : "#8b929a",
                fontSize: "12px",
            } }, s.label),
        index < steps.length - 1 && (React.createElement("div", { style: {
                width: "24px",
                height: "2px",
                backgroundColor: currentStep > s.num ? "#1a9fff" : "#3d4450",
                marginLeft: "8px",
            } })))))));
};
const GoalSelectionStep = ({ onSelect, platformInfo, disabled = false }) => {
    const { state } = useDeckTune();
    const isGameRunning = state.runningAppId !== null && state.runningAppName !== null;
    return (React.createElement(React.Fragment, null,
        platformInfo && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginBottom: "8px" } },
                "Detected: ",
                platformInfo.variant,
                " (",
                platformInfo.model,
                ") \u2022 Safe limit: ",
                platformInfo.safe_limit))),
        isGameRunning && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "8px 12px",
                    backgroundColor: "#1a3a5c",
                    borderRadius: "6px",
                    marginBottom: "12px",
                    fontSize: "12px",
                } },
                React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                    React.createElement(FaRocket, { style: { color: "#1a9fff" } }),
                    React.createElement("span", null,
                        "Running: ",
                        React.createElement("strong", null, state.runningAppName))),
                React.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginTop: "4px" } }, "Tuning will be saved as a preset for this game")))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", marginBottom: "12px" } }, "Select your tuning goal:")),
        GOAL_OPTIONS.map((goal) => {
            const Icon = goal.icon;
            return (React.createElement(DFL.PanelSectionRow, { key: goal.id },
                React.createElement(DFL.ButtonItem, { layout: "below", onClick: () => onSelect(goal.id), description: goal.description, disabled: disabled },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", opacity: disabled ? 0.5 : 1 } },
                        React.createElement(Icon, null),
                        React.createElement("span", null, goal.label),
                        React.createElement("span", { style: { fontSize: "10px", color: "#8b929a", marginLeft: "auto" } }, goal.mode === "thorough" ? "~10 min" : "~3 min")))));
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
    return (React.createElement(React.Fragment, null,
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { textAlign: "center", marginBottom: "16px" } },
                React.createElement(FaSpinner, { style: {
                        animation: "spin 1s linear infinite",
                        fontSize: "24px",
                        color: "#1a9fff",
                    } }),
                React.createElement("style", null, `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } },
                "Tuning for: ",
                goalLabel)),
        progress && (React.createElement(React.Fragment, null,
            React.createElement(DFL.PanelSectionRow, null,
                React.createElement(DFL.ProgressBarWithInfo, { label: `Phase ${progress.phase} - Core ${progress.core}`, description: `Testing value: ${progress.value}`, nProgress: calculateProgress(), sOperationText: formatEta(progress.eta) })),
            React.createElement(DFL.PanelSectionRow, null,
                React.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: "12px",
                        color: "#8b929a",
                        marginTop: "8px",
                    } },
                    React.createElement("span", null,
                        "Phase: ",
                        progress.phase === "A" ? "Coarse Search" : "Fine Tuning"),
                    React.createElement("span", null,
                        "Core: ",
                        progress.core + 1,
                        "/4"))))),
        !progress && isRunning && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { textAlign: "center", color: "#8b929a" } }, "Initializing autotune..."))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.ButtonItem, { layout: "below", onClick: onCancel, style: { marginTop: "16px" } },
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" } },
                    React.createElement(FaTimes, null),
                    React.createElement("span", null, "Cancel"))))));
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
    return (React.createElement(React.Fragment, null,
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    padding: "12px",
                    backgroundColor: result.stable ? "#1b5e20" : "#b71c1c",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                result.stable ? React.createElement(FaCheck, null) : React.createElement(FaTimes, null),
                React.createElement("span", { style: { fontWeight: "bold" } }, result.stable ? "Tuning Complete!" : "Tuning Incomplete"))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    display: "flex",
                    justifyContent: "space-around",
                    fontSize: "12px",
                    color: "#8b929a",
                    marginBottom: "16px",
                } },
                React.createElement("span", null,
                    "Duration: ",
                    formatDuration(result.duration)),
                React.createElement("span", null,
                    "Tests: ",
                    result.tests_run))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Optimal Values Found:")),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.Focusable, { style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(2, 1fr)",
                    gap: "8px",
                } }, result.cores.map((value, index) => (React.createElement("div", { key: index, style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    borderLeft: `4px solid ${getValueColor(value)}`,
                } },
                React.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } },
                    "Core ",
                    index),
                React.createElement("div", { style: {
                        fontSize: "20px",
                        fontWeight: "bold",
                        color: getValueColor(value),
                    } }, value),
                React.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } }, getValueStatus(value))))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    display: "flex",
                    justifyContent: "center",
                    gap: "16px",
                    fontSize: "10px",
                    color: "#8b929a",
                    marginTop: "8px",
                } },
                React.createElement("span", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    React.createElement("div", { style: { width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#4caf50" } }),
                    "Conservative"),
                React.createElement("span", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    React.createElement("div", { style: { width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#ff9800" } }),
                    "Moderate"),
                React.createElement("span", { style: { display: "flex", alignItems: "center", gap: "4px" } },
                    React.createElement("div", { style: { width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#f44336" } }),
                    "Aggressive"))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.ButtonItem, { layout: "below", onClick: onApplyAndSave, style: { marginTop: "16px" } },
                React.createElement("div", { style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        color: "#4caf50",
                    } },
                    React.createElement(FaCheck, null),
                    React.createElement("span", null, "Apply & Save")))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.ButtonItem, { layout: "below", onClick: onStartOver },
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                    React.createElement("span", null, "Start Over"))))));
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
    return (React.createElement(DFL.PanelSectionRow, null,
        React.createElement(DFL.ButtonItem, { layout: "below", onClick: handlePanicDisable, disabled: isPanicking, style: {
                backgroundColor: "#b71c1c",
                borderRadius: "8px",
            } },
            React.createElement("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    color: "#fff",
                    fontWeight: "bold",
                } }, isPanicking ? (React.createElement(React.Fragment, null,
                React.createElement(FaSpinner, { className: "spin" }),
                React.createElement("span", null, "Disabling..."))) : (React.createElement(React.Fragment, null,
                React.createElement(FaExclamationTriangle, null),
                React.createElement("span", null, "PANIC DISABLE")))))));
};
/**
 * ExpertMode component - detailed controls for power users.
 * Requirements: 4.5, 7.1
 */
const ExpertMode = ({ initialTab = "manual" }) => {
    const [activeTab, setActiveTab] = SP_REACT.useState(initialTab);
    return (React.createElement(DFL.PanelSection, { title: "Expert Mode" },
        React.createElement(PanicDisableButton, null),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(TabNavigation, { activeTab: activeTab, onTabChange: setActiveTab })),
        activeTab === "manual" && React.createElement(ManualTab, null),
        activeTab === "presets" && React.createElement(PresetsTab, null),
        activeTab === "tests" && React.createElement(TestsTab, null),
        activeTab === "diagnostics" && React.createElement(DiagnosticsTab, null)));
};
const TabNavigation = ({ activeTab, onTabChange }) => {
    return (React.createElement(DFL.Focusable, { style: {
            display: "flex",
            justifyContent: "space-around",
            marginBottom: "16px",
            backgroundColor: "#23262e",
            borderRadius: "8px",
            padding: "4px",
        } }, TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (React.createElement("button", { key: tab.id, onClick: () => onTabChange(tab.id), style: {
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
            React.createElement(Icon, null),
            React.createElement("span", { style: { fontSize: "10px" } }, tab.label)));
    })));
};
/**
 * Manual tab component.
 * Requirements: 5.4, 7.2
 *
 * Features:
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
    const [systemMetrics, setSystemMetrics] = SP_REACT.useState(null);
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
    const safeLimit = platformInfo?.safe_limit ?? -30;
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
    return (React.createElement(React.Fragment, null,
        platformInfo && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "12px", color: "#8b929a", marginBottom: "8px" } },
                platformInfo.variant,
                " (",
                platformInfo.model,
                ") \u2022 Safe limit: ",
                safeLimit))),
        systemMetrics && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.Focusable, { style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(4, 1fr)",
                    gap: "8px",
                    marginBottom: "16px",
                } }, [0, 1, 2, 3].map((core) => (React.createElement("div", { key: core, style: {
                    padding: "8px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    textAlign: "center",
                } },
                React.createElement("div", { style: { fontSize: "10px", color: "#8b929a" } },
                    "Core ",
                    core),
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", marginTop: "4px" } },
                    React.createElement(FaThermometerHalf, { style: { color: "#ff9800", fontSize: "10px" } }),
                    React.createElement("span", { style: { fontSize: "12px" } },
                        systemMetrics.temps[core] ?? "--",
                        "\u00B0C")),
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "4px" } },
                    React.createElement(FaMicrochip, { style: { color: "#1a9fff", fontSize: "10px" } }),
                    React.createElement("span", { style: { fontSize: "12px" } }, systemMetrics.freqs[core] ? `${(systemMetrics.freqs[core] / 1000).toFixed(1)}GHz` : "--")))))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Undervolt Values")),
        [0, 1, 2, 3].map((core) => (React.createElement(DFL.PanelSectionRow, { key: core },
            React.createElement(DFL.SliderField, { label: `Core ${core}`, value: coreValues[core], min: safeLimit, max: 0, step: 1, showValue: true, onChange: (value) => handleCoreChange(core, value), valueSuffix: "", description: React.createElement("span", { style: { color: getValueColor(coreValues[core]) } }, coreValues[core] === 0 ? "Disabled" : `${coreValues[core]} mV`) })))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    gap: "8px",
                    marginTop: "16px",
                } },
                React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleApply, disabled: isApplying || isTesting || isTuning, style: { flex: 1 } },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        isApplying ? React.createElement(FaSpinner, { className: "spin" }) : React.createElement(FaCheck, null),
                        React.createElement("span", null, "Apply"))),
                React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleTest, disabled: isApplying || isTesting || isTuning, style: { flex: 1 } },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } },
                        isTesting ? React.createElement(FaSpinner, { className: "spin" }) : React.createElement(FaVial, null),
                        React.createElement("span", null, "Test"))),
                React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleDisable, disabled: isApplying || isTesting || isTuning, style: { flex: 1 } },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#ff6b6b" } },
                        React.createElement(FaBan, null),
                        React.createElement("span", null, "Disable"))))),
        isGameRunning && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleTuneForGame, disabled: isApplying || isTesting || isTuning, style: { marginTop: "8px" } },
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "#1a9fff" } }, isTuning ? (React.createElement(React.Fragment, null,
                    React.createElement(FaSpinner, { className: "spin" }),
                    React.createElement("span", null,
                        "Tuning for ",
                        state.runningAppName,
                        "..."))) : (React.createElement(React.Fragment, null,
                    React.createElement(FaRocket, null),
                    React.createElement("span", null,
                        "Tune for ",
                        state.runningAppName))))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    marginTop: "12px",
                    padding: "8px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    fontSize: "12px",
                    textAlign: "center",
                } },
                "Status: ",
                React.createElement("span", { style: { color: state.status === "enabled" ? "#4caf50" : "#8b929a" } }, state.status))),
        React.createElement("style", null, `
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
 * Presets tab component.
 * Requirements: 7.3
 *
 * Features:
 * - Preset list with edit/delete/export
 * - Import preset button
 */
const PresetsTab = () => {
    const { state, api } = useDeckTune();
    const [editingPreset, setEditingPreset] = SP_REACT.useState(null);
    const [isImporting, setIsImporting] = SP_REACT.useState(false);
    const [importJson, setImportJson] = SP_REACT.useState("");
    const [importError, setImportError] = SP_REACT.useState(null);
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
        // In a real implementation, this would trigger a file download
        console.log("Export preset:", json);
        // For now, copy to clipboard simulation
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
     * Format core values for display.
     */
    const formatCoreValues = (values) => {
        return values.map((v, i) => `C${i}:${v}`).join(" ");
    };
    return (React.createElement(React.Fragment, null,
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.Focusable, { style: {
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "16px",
                } },
                React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExportAll },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        React.createElement(FaDownload, null),
                        React.createElement("span", null, "Export All"))),
                React.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setIsImporting(true) },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        React.createElement(FaUpload, null),
                        React.createElement("span", null, "Import"))))),
        isImporting && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Import Presets"),
                React.createElement(DFL.TextField, { label: "JSON Data", value: importJson, onChange: (e) => setImportJson(e.target.value), style: { marginBottom: "8px" } }),
                importError && (React.createElement("div", { style: { color: "#f44336", fontSize: "12px", marginBottom: "8px" } }, importError)),
                React.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px" } },
                    React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleImport },
                        React.createElement("span", null, "Import")),
                    React.createElement(DFL.ButtonItem, { layout: "below", onClick: () => { setIsImporting(false); setImportJson(""); setImportError(null); } },
                        React.createElement("span", null, "Cancel")))))),
        editingPreset && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "16px",
                } },
                React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } },
                    "Edit Preset: ",
                    editingPreset.label),
                React.createElement(DFL.TextField, { label: "Label", value: editingPreset.label, onChange: (e) => setEditingPreset({ ...editingPreset, label: e.target.value }), style: { marginBottom: "8px" } }),
                React.createElement(DFL.ToggleField, { label: "Use Timeout", checked: editingPreset.use_timeout, onChange: (checked) => setEditingPreset({ ...editingPreset, use_timeout: checked }) }),
                editingPreset.use_timeout && (React.createElement(DFL.SliderField, { label: "Timeout (seconds)", value: editingPreset.timeout, min: 0, max: 60, step: 5, showValue: true, onChange: (value) => setEditingPreset({ ...editingPreset, timeout: value }) })),
                React.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px", marginTop: "12px" } },
                    React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleSaveEdit },
                        React.createElement("span", null, "Save")),
                    React.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setEditingPreset(null) },
                        React.createElement("span", null, "Cancel")))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } },
                "Saved Presets (",
                state.presets.length,
                ")")),
        state.presets.length === 0 ? (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px" } }, "No presets saved yet. Use \"Tune for this game\" or save from Manual tab."))) : (state.presets.map((preset) => (React.createElement(DFL.PanelSectionRow, { key: preset.app_id },
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                    marginBottom: "8px",
                } },
                React.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
                    React.createElement("div", null,
                        React.createElement("div", { style: { fontWeight: "bold", fontSize: "14px" } }, preset.label),
                        React.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } }, formatCoreValues(preset.value)),
                        preset.use_timeout && (React.createElement("div", { style: { fontSize: "10px", color: "#ff9800" } },
                            "Timeout: ",
                            preset.timeout,
                            "s")),
                        preset.tested && (React.createElement("div", { style: { fontSize: "10px", color: "#4caf50" } }, "\u2713 Tested"))),
                    React.createElement(DFL.Focusable, { style: { display: "flex", gap: "8px" } },
                        React.createElement("button", { onClick: () => setEditingPreset(preset), style: {
                                padding: "8px",
                                backgroundColor: "transparent",
                                border: "none",
                                color: "#1a9fff",
                                cursor: "pointer",
                            } },
                            React.createElement(FaEdit, null)),
                        React.createElement("button", { onClick: () => handleExportSingle(preset), style: {
                                padding: "8px",
                                backgroundColor: "transparent",
                                border: "none",
                                color: "#8b929a",
                                cursor: "pointer",
                            } },
                            React.createElement(FaDownload, null)),
                        React.createElement("button", { onClick: () => handleDelete(preset.app_id), style: {
                                padding: "8px",
                                backgroundColor: "transparent",
                                border: "none",
                                color: "#f44336",
                                cursor: "pointer",
                            } },
                            React.createElement(FaTrash, null)))))))))));
};
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
    return (React.createElement(React.Fragment, null,
        hasMissing && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                    padding: "12px",
                    backgroundColor: "#5c4813",
                    borderRadius: "8px",
                    marginBottom: "12px",
                    border: "1px solid #ff9800",
                } },
                React.createElement(FaExclamationCircle, { style: { color: "#ff9800", fontSize: "18px", flexShrink: 0, marginTop: "2px" } }),
                React.createElement("div", null,
                    React.createElement("div", { style: { fontWeight: "bold", color: "#ffb74d", marginBottom: "4px" } }, "Missing Components"),
                    React.createElement("div", { style: { fontSize: "12px", color: "#ffe0b2" } },
                        "Required tools not found: ",
                        React.createElement("strong", null, missingBinaries.join(", "))),
                    React.createElement("div", { style: { fontSize: "11px", color: "#ffcc80", marginTop: "4px" } }, "Stress tests are unavailable until binaries are installed."))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "Run Stress Test")),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.DropdownItem, { label: "Select Test", menuLabel: "Select Test", rgOptions: TEST_OPTIONS.map((t) => ({
                    data: t.value,
                    label: t.label,
                })), selectedOption: selectedTest, onChange: (option) => setSelectedTest(option.data), disabled: hasMissing })),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleRunTest, disabled: isRunning || hasMissing },
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", opacity: hasMissing ? 0.5 : 1 } }, isRunning ? (React.createElement(React.Fragment, null,
                    React.createElement(FaSpinner, { className: "spin" }),
                    React.createElement("span", null,
                        "Running ",
                        getTestLabel(currentTest || selectedTest),
                        "..."))) : (React.createElement(React.Fragment, null,
                    React.createElement(FaPlay, null),
                    React.createElement("span", null, "Run Test")))))),
        isRunning && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#1a3a5c",
                    borderRadius: "8px",
                    marginTop: "8px",
                } },
                React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" } },
                    React.createElement(FaSpinner, { className: "spin", style: { color: "#1a9fff" } }),
                    React.createElement("span", null, "Test in progress...")),
                React.createElement("div", { style: { fontSize: "12px", color: "#8b929a" } },
                    "Running: ",
                    getTestLabel(currentTest || selectedTest))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Test History (Last 10)")),
        history.length === 0 ? (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { color: "#8b929a", textAlign: "center", padding: "16px" } }, "No tests run yet."))) : (history.slice(0, 10).map((entry, index) => (React.createElement(DFL.PanelSectionRow, { key: index },
            React.createElement("div", { style: {
                    padding: "10px",
                    backgroundColor: "#23262e",
                    borderRadius: "6px",
                    marginBottom: "6px",
                    borderLeft: `3px solid ${entry.passed ? "#4caf50" : "#f44336"}`,
                } },
                React.createElement("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" } },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
                        entry.passed ? (React.createElement(FaCheck, { style: { color: "#4caf50" } })) : (React.createElement(FaTimes, { style: { color: "#f44336" } })),
                        React.createElement("span", { style: { fontWeight: "bold", fontSize: "13px" } }, getTestLabel(entry.test_name))),
                    React.createElement("span", { style: { fontSize: "11px", color: "#8b929a" } }, formatDuration(entry.duration))),
                React.createElement("div", { style: { fontSize: "11px", color: "#8b929a", marginTop: "4px" } }, formatTimestamp(entry.timestamp)),
                React.createElement("div", { style: { fontSize: "10px", color: "#8b929a", marginTop: "2px" } },
                    "Cores: [",
                    entry.cores_tested.join(", "),
                    "]")))))),
        React.createElement("style", null, `
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
    return (React.createElement(React.Fragment, null,
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginBottom: "8px" } }, "System Information")),
        isLoading ? (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { display: "flex", alignItems: "center", gap: "8px", color: "#8b929a" } },
                React.createElement(FaSpinner, { className: "spin" }),
                React.createElement("span", null, "Loading system info...")))) : (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                } },
                React.createElement(InfoRow, { label: "Platform", value: platformInfo ? `${platformInfo.variant} (${platformInfo.model})` : "Unknown" }),
                React.createElement(InfoRow, { label: "Safe Limit", value: platformInfo ? `${platformInfo.safe_limit} mV` : "Unknown" }),
                React.createElement(InfoRow, { label: "Detection", value: platformInfo?.detected ? "Successful" : "Failed" }),
                systemInfo && (React.createElement(React.Fragment, null,
                    React.createElement("div", { style: { borderTop: "1px solid #3d4450", margin: "8px 0" } }),
                    React.createElement(InfoRow, { label: "SteamOS Version", value: systemInfo.steamos_version || "Unknown" }),
                    React.createElement(InfoRow, { label: "Kernel", value: systemInfo.kernel || "Unknown" }),
                    React.createElement(InfoRow, { label: "Hostname", value: systemInfo.hostname || "Unknown" }),
                    systemInfo.uptime && (React.createElement(InfoRow, { label: "Uptime", value: formatUptime(systemInfo.uptime) }))))))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Current Configuration")),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: "#23262e",
                    borderRadius: "8px",
                } }, systemInfo?.config ? (React.createElement(React.Fragment, null,
                React.createElement(InfoRow, { label: "Active Cores", value: `[${systemInfo.config.cores?.join(", ") || "0, 0, 0, 0"}]` }),
                React.createElement(InfoRow, { label: "LKG Cores", value: `[${systemInfo.config.lkg_cores?.join(", ") || "0, 0, 0, 0"}]` }),
                React.createElement(InfoRow, { label: "Status", value: systemInfo.config.status || "Unknown" }),
                React.createElement(InfoRow, { label: "Presets Count", value: String(systemInfo.config.presets_count || 0) }))) : (React.createElement("div", { style: { color: "#8b929a" } }, "Configuration not available")))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: { fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" } }, "Recent Logs")),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "8px",
                    backgroundColor: "#1a1d23",
                    borderRadius: "8px",
                    maxHeight: "150px",
                    overflowY: "auto",
                    fontFamily: "monospace",
                    fontSize: "10px",
                    color: "#8b929a",
                } }, systemInfo?.logs ? (systemInfo.logs.split("\n").slice(-20).map((line, index) => (React.createElement("div", { key: index, style: { marginBottom: "2px" } }, line)))) : (React.createElement("div", null, "No logs available")))),
        React.createElement(DFL.PanelSectionRow, null,
            React.createElement(DFL.ButtonItem, { layout: "below", onClick: handleExportDiagnostics, disabled: isExporting, style: { marginTop: "16px" } },
                React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" } }, isExporting ? (React.createElement(React.Fragment, null,
                    React.createElement(FaSpinner, { className: "spin" }),
                    React.createElement("span", null, "Exporting..."))) : (React.createElement(React.Fragment, null,
                    React.createElement(FaDownload, null),
                    React.createElement("span", null, "Export Diagnostics")))))),
        exportResult && (React.createElement(DFL.PanelSectionRow, null,
            React.createElement("div", { style: {
                    padding: "12px",
                    backgroundColor: exportResult.success ? "#1b5e20" : "#b71c1c",
                    borderRadius: "8px",
                    marginTop: "8px",
                } }, exportResult.success ? (React.createElement(React.Fragment, null,
                React.createElement("div", { style: { fontWeight: "bold", marginBottom: "4px" } },
                    React.createElement(FaCheck, { style: { marginRight: "8px" } }),
                    "Export Successful"),
                React.createElement("div", { style: { fontSize: "12px", wordBreak: "break-all" } },
                    "Saved to: ",
                    exportResult.path))) : (React.createElement(React.Fragment, null,
                React.createElement("div", { style: { fontWeight: "bold" } },
                    React.createElement(FaTimes, { style: { marginRight: "8px" } }),
                    "Export Failed"),
                React.createElement("div", { style: { fontSize: "12px" } }, exportResult.error)))))),
        React.createElement("style", null, `
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `)));
};
const InfoRow = ({ label, value }) => (React.createElement("div", { style: {
        display: "flex",
        justifyContent: "space-between",
        marginBottom: "6px",
        fontSize: "12px",
    } },
    React.createElement("span", { style: { color: "#8b929a" } },
        label,
        ":"),
    React.createElement("span", { style: { color: "#fff" } }, value)));
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
 * DeckTune - Main plugin entry point for Decky Loader.
 *
 * This file registers the plugin with Decky Loader and provides
 * the main UI component that appears in the Quick Access Menu.
 */

/**
 * Main content component with mode switching.
 */
const DeckTuneContent = () => {
    const [mode, setMode] = SP_REACT.useState("wizard");
    const { state } = useDeckTune();
    return (React.createElement(React.Fragment, null,
        React.createElement(DFL.PanelSection, null,
            React.createElement(DFL.PanelSectionRow, null,
                React.createElement("div", { style: {
                        display: "flex",
                        justifyContent: "center",
                        gap: "8px",
                        marginBottom: "8px",
                    } },
                    React.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setMode("wizard"), style: {
                            flex: 1,
                            backgroundColor: mode === "wizard" ? "#1a9fff" : "#23262e",
                            borderRadius: "6px",
                        } },
                        React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" } },
                            React.createElement(FaMagic, null),
                            React.createElement("span", null, "Wizard"))),
                    React.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setMode("expert"), style: {
                            flex: 1,
                            backgroundColor: mode === "expert" ? "#1a9fff" : "#23262e",
                            borderRadius: "6px",
                        } },
                        React.createElement("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" } },
                            React.createElement(FaCog, null),
                            React.createElement("span", null, "Expert"))))),
            React.createElement(DFL.PanelSectionRow, null,
                React.createElement("div", { style: {
                        textAlign: "center",
                        fontSize: "12px",
                        color: "#8b929a",
                        padding: "4px 8px",
                        backgroundColor: "#23262e",
                        borderRadius: "4px",
                    } },
                    "Status: ",
                    React.createElement("span", { style: {
                            color: state.status === "enabled" || state.status === "DYNAMIC RUNNING"
                                ? "#4caf50"
                                : state.status === "error"
                                    ? "#f44336"
                                    : "#8b929a"
                        } }, state.status)))),
        mode === "wizard" ? React.createElement(WizardMode, null) : React.createElement(ExpertMode, null)));
};
/**
 * Main plugin component wrapped with context provider.
 */
const DeckTunePlugin = () => {
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
        // Register server event listener
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
        return (React.createElement(DFL.PanelSection, { title: "DeckTune" },
            React.createElement(DFL.PanelSectionRow, null,
                React.createElement("div", { style: { color: "#f44336", textAlign: "center", padding: "16px" } },
                    "Failed to initialize: ",
                    error))));
    }
    if (!initialized) {
        return (React.createElement(DFL.PanelSection, { title: "DeckTune" },
            React.createElement(DFL.PanelSectionRow, null,
                React.createElement("div", { style: { textAlign: "center", padding: "16px", color: "#8b929a" } }, "Loading..."))));
    }
    return (React.createElement(DeckTuneProvider, null,
        React.createElement(DeckTuneContent, null)));
};
/**
 * Plugin definition for Decky Loader.
 */
var index = DFL.definePlugin(() => {
    console.log("DeckTune plugin loaded");
    return {
        // Plugin title shown in Decky menu
        title: React.createElement("div", { className: DFL.staticClasses.Title }, "DeckTune"),
        // Main plugin content
        content: React.createElement(DeckTunePlugin, null),
        // Plugin icon (shown in Quick Access Menu)
        icon: React.createElement(FaMagic, null),
        // Called when plugin is unloaded
        onDismount() {
            console.log("DeckTune plugin unloaded");
        },
    };
});

export { index as default };
//# sourceMappingURL=index.js.map
