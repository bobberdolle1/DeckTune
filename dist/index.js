// Decky Loader will pass this api in, it's versioned to allow for backwards compatibility.
// @ts-ignore

// Prevents it from being duplicated in output.
const manifest = {"name":"Decky-Undervolt","author":"BakaDestroyer","api_version":1,"flags":["root"],"publish":{"tags":["root","undervolt","performance","temperature","ryzenadj","curve optimizer","battery-saving"],"description":"A simple plugin that is using ryzenadj to apply Curve Optimizer to CPU.","image":"https://raw.githubusercontent.com/totallynotbakadestroyer/Decky-Undervolt/master/assets/preview.jpg"}};
const API_VERSION = 2;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
// Initialize
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
// Version 1 throws on version mismatch so we have to account for that here.
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
// TODO these could use a lot of JSDoc
const call = api.call;
const addEventListener = api.addEventListener;
const removeEventListener = api.removeEventListener;
const routerHook = api.routerHook;

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
function FaCog (props) {
  return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M487.4 315.7l-42.6-24.6c4.3-23.2 4.3-47 0-70.2l42.6-24.6c4.9-2.8 7.1-8.6 5.5-14-11.1-35.6-30-67.8-54.7-94.6-3.8-4.1-10-5.1-14.8-2.3L380.8 110c-17.9-15.4-38.5-27.3-60.8-35.1V25.8c0-5.6-3.9-10.5-9.4-11.7-36.7-8.2-74.3-7.8-109.2 0-5.5 1.2-9.4 6.1-9.4 11.7V75c-22.2 7.9-42.8 19.8-60.8 35.1L88.7 85.5c-4.9-2.8-11-1.9-14.8 2.3-24.7 26.7-43.6 58.9-54.7 94.6-1.7 5.4.6 11.2 5.5 14L67.3 221c-4.3 23.2-4.3 47 0 70.2l-42.6 24.6c-4.9 2.8-7.1 8.6-5.5 14 11.1 35.6 30 67.8 54.7 94.6 3.8 4.1 10 5.1 14.8 2.3l42.6-24.6c17.9 15.4 38.5 27.3 60.8 35.1v49.2c0 5.6 3.9 10.5 9.4 11.7 36.7 8.2 74.3 7.8 109.2 0 5.5-1.2 9.4-6.1 9.4-11.7v-49.2c22.2-7.9 42.8-19.8 60.8-35.1l42.6 24.6c4.9 2.8 11 1.9 14.8-2.3 24.7-26.7 43.6-58.9 54.7-94.6 1.5-5.5-.7-11.3-5.6-14.1zM256 336c-44.1 0-80-35.9-80-80s35.9-80 80-80 80 35.9 80 80-35.9 80-80 80z"}}]})(props);
}function FaFire (props) {
  return GenIcon({"tag":"svg","attr":{"viewBox":"0 0 384 512"},"child":[{"tag":"path","attr":{"d":"M216 23.86c0-23.8-30.65-32.77-44.15-13.04C48 191.85 224 200 224 288c0 35.63-29.11 64.46-64.85 63.99-35.17-.45-63.15-29.77-63.15-64.94v-85.51c0-21.7-26.47-32.23-41.43-16.5C27.8 213.16 0 261.33 0 320c0 105.87 86.13 192 192 192s192-86.13 192-192c0-170.29-168-193-168-296.14z"}}]})(props);
}

function getDefaultExportFromCjs (x) {
	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
}

const warn = (...args) => {
  if (console?.warn) {
    if (isString$1(args[0])) args[0] = `react-i18next:: ${args[0]}`;
    console.warn(...args);
  }
};
const alreadyWarned = {};
const warnOnce = (...args) => {
  if (isString$1(args[0]) && alreadyWarned[args[0]]) return;
  if (isString$1(args[0])) alreadyWarned[args[0]] = new Date();
  warn(...args);
};
const loadedClb = (i18n, cb) => () => {
  if (i18n.isInitialized) {
    cb();
  } else {
    const initialized = () => {
      setTimeout(() => {
        i18n.off('initialized', initialized);
      }, 0);
      cb();
    };
    i18n.on('initialized', initialized);
  }
};
const loadNamespaces = (i18n, ns, cb) => {
  i18n.loadNamespaces(ns, loadedClb(i18n, cb));
};
const loadLanguages = (i18n, lng, ns, cb) => {
  if (isString$1(ns)) ns = [ns];
  if (i18n.options.preload && i18n.options.preload.indexOf(lng) > -1) return loadNamespaces(i18n, ns, cb);
  ns.forEach(n => {
    if (i18n.options.ns.indexOf(n) < 0) i18n.options.ns.push(n);
  });
  i18n.loadLanguages(lng, loadedClb(i18n, cb));
};
const hasLoadedNamespace = (ns, i18n, options = {}) => {
  if (!i18n.languages || !i18n.languages.length) {
    warnOnce('i18n.languages were undefined or empty', i18n.languages);
    return true;
  }
  return i18n.hasLoadedNamespace(ns, {
    lng: options.lng,
    precheck: (i18nInstance, loadNotPending) => {
      if (options.bindI18n?.indexOf('languageChanging') > -1 && i18nInstance.services.backendConnector.backend && i18nInstance.isLanguageChangingTo && !loadNotPending(i18nInstance.isLanguageChangingTo, ns)) return false;
    }
  });
};
const isString$1 = obj => typeof obj === 'string';
const isObject = obj => typeof obj === 'object' && obj !== null;

const matchHtmlEntity = /&(?:amp|#38|lt|#60|gt|#62|apos|#39|quot|#34|nbsp|#160|copy|#169|reg|#174|hellip|#8230|#x2F|#47);/g;
const htmlEntities = {
  '&amp;': '&',
  '&#38;': '&',
  '&lt;': '<',
  '&#60;': '<',
  '&gt;': '>',
  '&#62;': '>',
  '&apos;': "'",
  '&#39;': "'",
  '&quot;': '"',
  '&#34;': '"',
  '&nbsp;': ' ',
  '&#160;': ' ',
  '&copy;': '©',
  '&#169;': '©',
  '&reg;': '®',
  '&#174;': '®',
  '&hellip;': '…',
  '&#8230;': '…',
  '&#x2F;': '/',
  '&#47;': '/'
};
const unescapeHtmlEntity = m => htmlEntities[m];
const unescape = text => text.replace(matchHtmlEntity, unescapeHtmlEntity);

let defaultOptions = {
  bindI18n: 'languageChanged',
  bindI18nStore: '',
  transEmptyNodeValue: '',
  transSupportBasicHtmlNodes: true,
  transWrapTextNodes: '',
  transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'p'],
  useSuspense: true,
  unescape
};
const setDefaults = (options = {}) => {
  defaultOptions = {
    ...defaultOptions,
    ...options
  };
};
const getDefaults = () => defaultOptions;

let i18nInstance;
const setI18n = instance => {
  i18nInstance = instance;
};
const getI18n = () => i18nInstance;

const initReactI18next = {
  type: '3rdParty',
  init(instance) {
    setDefaults(instance.options.react);
    setI18n(instance);
  }
};

const I18nContext = SP_REACT.createContext();
class ReportNamespaces {
  constructor() {
    this.usedNamespaces = {};
  }
  addUsedNamespaces(namespaces) {
    namespaces.forEach(ns => {
      if (!this.usedNamespaces[ns]) this.usedNamespaces[ns] = true;
    });
  }
  getUsedNamespaces() {
    return Object.keys(this.usedNamespaces);
  }
}

const usePrevious = (value, ignore) => {
  const ref = SP_REACT.useRef();
  SP_REACT.useEffect(() => {
    ref.current = value;
  }, [value, ignore]);
  return ref.current;
};
const alwaysNewT = (i18n, language, namespace, keyPrefix) => i18n.getFixedT(language, namespace, keyPrefix);
const useMemoizedT = (i18n, language, namespace, keyPrefix) => SP_REACT.useCallback(alwaysNewT(i18n, language, namespace, keyPrefix), [i18n, language, namespace, keyPrefix]);
const useTranslation = (ns, props = {}) => {
  const {
    i18n: i18nFromProps
  } = props;
  const {
    i18n: i18nFromContext,
    defaultNS: defaultNSFromContext
  } = SP_REACT.useContext(I18nContext) || {};
  const i18n = i18nFromProps || i18nFromContext || getI18n();
  if (i18n && !i18n.reportNamespaces) i18n.reportNamespaces = new ReportNamespaces();
  if (!i18n) {
    warnOnce('You will need to pass in an i18next instance by using initReactI18next');
    const notReadyT = (k, optsOrDefaultValue) => {
      if (isString$1(optsOrDefaultValue)) return optsOrDefaultValue;
      if (isObject(optsOrDefaultValue) && isString$1(optsOrDefaultValue.defaultValue)) return optsOrDefaultValue.defaultValue;
      return Array.isArray(k) ? k[k.length - 1] : k;
    };
    const retNotReady = [notReadyT, {}, false];
    retNotReady.t = notReadyT;
    retNotReady.i18n = {};
    retNotReady.ready = false;
    return retNotReady;
  }
  if (i18n.options.react?.wait) warnOnce('It seems you are still using the old wait option, you may migrate to the new useSuspense behaviour.');
  const i18nOptions = {
    ...getDefaults(),
    ...i18n.options.react,
    ...props
  };
  const {
    useSuspense,
    keyPrefix
  } = i18nOptions;
  let namespaces = defaultNSFromContext || i18n.options?.defaultNS;
  namespaces = isString$1(namespaces) ? [namespaces] : namespaces || ['translation'];
  i18n.reportNamespaces.addUsedNamespaces?.(namespaces);
  const ready = (i18n.isInitialized || i18n.initializedStoreOnce) && namespaces.every(n => hasLoadedNamespace(n, i18n, i18nOptions));
  const memoGetT = useMemoizedT(i18n, props.lng || null, i18nOptions.nsMode === 'fallback' ? namespaces : namespaces[0], keyPrefix);
  const getT = () => memoGetT;
  const getNewT = () => alwaysNewT(i18n, props.lng || null, i18nOptions.nsMode === 'fallback' ? namespaces : namespaces[0], keyPrefix);
  const [t, setT] = SP_REACT.useState(getT);
  let joinedNS = namespaces.join();
  if (props.lng) joinedNS = `${props.lng}${joinedNS}`;
  const previousJoinedNS = usePrevious(joinedNS);
  const isMounted = SP_REACT.useRef(true);
  SP_REACT.useEffect(() => {
    const {
      bindI18n,
      bindI18nStore
    } = i18nOptions;
    isMounted.current = true;
    if (!ready && !useSuspense) {
      if (props.lng) {
        loadLanguages(i18n, props.lng, namespaces, () => {
          if (isMounted.current) setT(getNewT);
        });
      } else {
        loadNamespaces(i18n, namespaces, () => {
          if (isMounted.current) setT(getNewT);
        });
      }
    }
    if (ready && previousJoinedNS && previousJoinedNS !== joinedNS && isMounted.current) {
      setT(getNewT);
    }
    const boundReset = () => {
      if (isMounted.current) setT(getNewT);
    };
    if (bindI18n) i18n?.on(bindI18n, boundReset);
    if (bindI18nStore) i18n?.store.on(bindI18nStore, boundReset);
    return () => {
      isMounted.current = false;
      if (i18n) bindI18n?.split(' ').forEach(e => i18n.off(e, boundReset));
      if (bindI18nStore && i18n) bindI18nStore.split(' ').forEach(e => i18n.store.off(e, boundReset));
    };
  }, [i18n, joinedNS]);
  SP_REACT.useEffect(() => {
    if (isMounted.current && ready) {
      setT(getT);
    }
  }, [i18n, keyPrefix, ready]);
  const ret = [t, i18n, ready];
  ret.t = t;
  ret.i18n = i18n;
  ret.ready = ready;
  if (ready) return ret;
  if (!ready && !useSuspense) return ret;
  throw new Promise(resolve => {
    if (props.lng) {
      loadLanguages(i18n, props.lng, namespaces, () => resolve());
    } else {
      loadNamespaces(i18n, namespaces, () => resolve());
    }
  });
};

const PresetSelector = ({ presets, selectedPreset, handleSetSelectedPreset, }) => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement(DFL.DropdownItem, { rgOptions: [
                { label: t("presetManager.presetSelector.none"), data: null },
                ...presets.map((x) => ({ label: x.label, data: x })),
            ], selectedOption: selectedPreset, onChange: handleSetSelectedPreset, label: t("presetManager.presetSelector.label") })));
};

const PresetControls$1 = ({ editablePreset, setEditablePreset, }) => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { checked: editablePreset.use_timeout, onChange: (value) => setEditablePreset({ ...editablePreset, use_timeout: value }), label: t("presetControls.useTimeout"), description: t("presetControls.timeoutDescription", {
                    label: editablePreset.label,
                }) })),
        editablePreset.use_timeout && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { bottomSeparator: "standard", min: 0, showValue: true, max: 1000, step: 1, label: t("presetControls.timeoutLabel"), value: editablePreset.timeout, onChange: (value) => setEditablePreset({ ...editablePreset, timeout: value }) })))));
};

const CoreSlider = ({ coreNumber, coreValue, setCoreValue, }) => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement(DFL.SliderField, { label: t("coreSlider", { coreNumber }), showValue: true, min: 0, max: 60, step: 1, value: coreValue, onChange: setCoreValue })));
};

const CoreSliders = ({ cores, updateCore, }) => (window.SP_REACT.createElement(SP_REACT.Fragment, null, cores.map((core, index) => (window.SP_REACT.createElement(CoreSlider, { key: index, coreValue: core, coreNumber: index, setCoreValue: (value) => updateCore(index, value) })))));

const ActionButtons$2 = ({ loading, doubleCheckDelete, handleUpdatePreset, handleDeletePreset, }) => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleUpdatePreset }, loading
                ? t("presetManager.actionButtons.saving")
                : t("presetManager.actionButtons.savePreset"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { disabled: loading, layout: "below", onClick: handleDeletePreset }, doubleCheckDelete
                ? t("presetManager.actionButtons.deleteConfirm")
                : t("presetManager.actionButtons.delete")))));
};

var eventemitter3 = {exports: {}};

(function (module) {

	var has = Object.prototype.hasOwnProperty
	  , prefix = '~';

	/**
	 * Constructor to create a storage for our `EE` objects.
	 * An `Events` instance is a plain object whose properties are event names.
	 *
	 * @constructor
	 * @private
	 */
	function Events() {}

	//
	// We try to not inherit from `Object.prototype`. In some engines creating an
	// instance in this way is faster than calling `Object.create(null)` directly.
	// If `Object.create(null)` is not supported we prefix the event names with a
	// character to make sure that the built-in object properties are not
	// overridden or used as an attack vector.
	//
	if (Object.create) {
	  Events.prototype = Object.create(null);

	  //
	  // This hack is needed because the `__proto__` property is still inherited in
	  // some old browsers like Android 4, iPhone 5.1, Opera 11 and Safari 5.
	  //
	  if (!new Events().__proto__) prefix = false;
	}

	/**
	 * Representation of a single event listener.
	 *
	 * @param {Function} fn The listener function.
	 * @param {*} context The context to invoke the listener with.
	 * @param {Boolean} [once=false] Specify if the listener is a one-time listener.
	 * @constructor
	 * @private
	 */
	function EE(fn, context, once) {
	  this.fn = fn;
	  this.context = context;
	  this.once = once || false;
	}

	/**
	 * Add a listener for a given event.
	 *
	 * @param {EventEmitter} emitter Reference to the `EventEmitter` instance.
	 * @param {(String|Symbol)} event The event name.
	 * @param {Function} fn The listener function.
	 * @param {*} context The context to invoke the listener with.
	 * @param {Boolean} once Specify if the listener is a one-time listener.
	 * @returns {EventEmitter}
	 * @private
	 */
	function addListener(emitter, event, fn, context, once) {
	  if (typeof fn !== 'function') {
	    throw new TypeError('The listener must be a function');
	  }

	  var listener = new EE(fn, context || emitter, once)
	    , evt = prefix ? prefix + event : event;

	  if (!emitter._events[evt]) emitter._events[evt] = listener, emitter._eventsCount++;
	  else if (!emitter._events[evt].fn) emitter._events[evt].push(listener);
	  else emitter._events[evt] = [emitter._events[evt], listener];

	  return emitter;
	}

	/**
	 * Clear event by name.
	 *
	 * @param {EventEmitter} emitter Reference to the `EventEmitter` instance.
	 * @param {(String|Symbol)} evt The Event name.
	 * @private
	 */
	function clearEvent(emitter, evt) {
	  if (--emitter._eventsCount === 0) emitter._events = new Events();
	  else delete emitter._events[evt];
	}

	/**
	 * Minimal `EventEmitter` interface that is molded against the Node.js
	 * `EventEmitter` interface.
	 *
	 * @constructor
	 * @public
	 */
	function EventEmitter() {
	  this._events = new Events();
	  this._eventsCount = 0;
	}

	/**
	 * Return an array listing the events for which the emitter has registered
	 * listeners.
	 *
	 * @returns {Array}
	 * @public
	 */
	EventEmitter.prototype.eventNames = function eventNames() {
	  var names = []
	    , events
	    , name;

	  if (this._eventsCount === 0) return names;

	  for (name in (events = this._events)) {
	    if (has.call(events, name)) names.push(prefix ? name.slice(1) : name);
	  }

	  if (Object.getOwnPropertySymbols) {
	    return names.concat(Object.getOwnPropertySymbols(events));
	  }

	  return names;
	};

	/**
	 * Return the listeners registered for a given event.
	 *
	 * @param {(String|Symbol)} event The event name.
	 * @returns {Array} The registered listeners.
	 * @public
	 */
	EventEmitter.prototype.listeners = function listeners(event) {
	  var evt = prefix ? prefix + event : event
	    , handlers = this._events[evt];

	  if (!handlers) return [];
	  if (handlers.fn) return [handlers.fn];

	  for (var i = 0, l = handlers.length, ee = new Array(l); i < l; i++) {
	    ee[i] = handlers[i].fn;
	  }

	  return ee;
	};

	/**
	 * Return the number of listeners listening to a given event.
	 *
	 * @param {(String|Symbol)} event The event name.
	 * @returns {Number} The number of listeners.
	 * @public
	 */
	EventEmitter.prototype.listenerCount = function listenerCount(event) {
	  var evt = prefix ? prefix + event : event
	    , listeners = this._events[evt];

	  if (!listeners) return 0;
	  if (listeners.fn) return 1;
	  return listeners.length;
	};

	/**
	 * Calls each of the listeners registered for a given event.
	 *
	 * @param {(String|Symbol)} event The event name.
	 * @returns {Boolean} `true` if the event had listeners, else `false`.
	 * @public
	 */
	EventEmitter.prototype.emit = function emit(event, a1, a2, a3, a4, a5) {
	  var evt = prefix ? prefix + event : event;

	  if (!this._events[evt]) return false;

	  var listeners = this._events[evt]
	    , len = arguments.length
	    , args
	    , i;

	  if (listeners.fn) {
	    if (listeners.once) this.removeListener(event, listeners.fn, undefined, true);

	    switch (len) {
	      case 1: return listeners.fn.call(listeners.context), true;
	      case 2: return listeners.fn.call(listeners.context, a1), true;
	      case 3: return listeners.fn.call(listeners.context, a1, a2), true;
	      case 4: return listeners.fn.call(listeners.context, a1, a2, a3), true;
	      case 5: return listeners.fn.call(listeners.context, a1, a2, a3, a4), true;
	      case 6: return listeners.fn.call(listeners.context, a1, a2, a3, a4, a5), true;
	    }

	    for (i = 1, args = new Array(len -1); i < len; i++) {
	      args[i - 1] = arguments[i];
	    }

	    listeners.fn.apply(listeners.context, args);
	  } else {
	    var length = listeners.length
	      , j;

	    for (i = 0; i < length; i++) {
	      if (listeners[i].once) this.removeListener(event, listeners[i].fn, undefined, true);

	      switch (len) {
	        case 1: listeners[i].fn.call(listeners[i].context); break;
	        case 2: listeners[i].fn.call(listeners[i].context, a1); break;
	        case 3: listeners[i].fn.call(listeners[i].context, a1, a2); break;
	        case 4: listeners[i].fn.call(listeners[i].context, a1, a2, a3); break;
	        default:
	          if (!args) for (j = 1, args = new Array(len -1); j < len; j++) {
	            args[j - 1] = arguments[j];
	          }

	          listeners[i].fn.apply(listeners[i].context, args);
	      }
	    }
	  }

	  return true;
	};

	/**
	 * Add a listener for a given event.
	 *
	 * @param {(String|Symbol)} event The event name.
	 * @param {Function} fn The listener function.
	 * @param {*} [context=this] The context to invoke the listener with.
	 * @returns {EventEmitter} `this`.
	 * @public
	 */
	EventEmitter.prototype.on = function on(event, fn, context) {
	  return addListener(this, event, fn, context, false);
	};

	/**
	 * Add a one-time listener for a given event.
	 *
	 * @param {(String|Symbol)} event The event name.
	 * @param {Function} fn The listener function.
	 * @param {*} [context=this] The context to invoke the listener with.
	 * @returns {EventEmitter} `this`.
	 * @public
	 */
	EventEmitter.prototype.once = function once(event, fn, context) {
	  return addListener(this, event, fn, context, true);
	};

	/**
	 * Remove the listeners of a given event.
	 *
	 * @param {(String|Symbol)} event The event name.
	 * @param {Function} fn Only remove the listeners that match this function.
	 * @param {*} context Only remove the listeners that have this context.
	 * @param {Boolean} once Only remove one-time listeners.
	 * @returns {EventEmitter} `this`.
	 * @public
	 */
	EventEmitter.prototype.removeListener = function removeListener(event, fn, context, once) {
	  var evt = prefix ? prefix + event : event;

	  if (!this._events[evt]) return this;
	  if (!fn) {
	    clearEvent(this, evt);
	    return this;
	  }

	  var listeners = this._events[evt];

	  if (listeners.fn) {
	    if (
	      listeners.fn === fn &&
	      (!once || listeners.once) &&
	      (!context || listeners.context === context)
	    ) {
	      clearEvent(this, evt);
	    }
	  } else {
	    for (var i = 0, events = [], length = listeners.length; i < length; i++) {
	      if (
	        listeners[i].fn !== fn ||
	        (once && !listeners[i].once) ||
	        (context && listeners[i].context !== context)
	      ) {
	        events.push(listeners[i]);
	      }
	    }

	    //
	    // Reset the array, or remove it completely if we have no more listeners.
	    //
	    if (events.length) this._events[evt] = events.length === 1 ? events[0] : events;
	    else clearEvent(this, evt);
	  }

	  return this;
	};

	/**
	 * Remove all listeners, or those of the specified event.
	 *
	 * @param {(String|Symbol)} [event] The event name.
	 * @returns {EventEmitter} `this`.
	 * @public
	 */
	EventEmitter.prototype.removeAllListeners = function removeAllListeners(event) {
	  var evt;

	  if (event) {
	    evt = prefix ? prefix + event : event;
	    if (this._events[evt]) clearEvent(this, evt);
	  } else {
	    this._events = new Events();
	    this._eventsCount = 0;
	  }

	  return this;
	};

	//
	// Alias methods names because people roll like that.
	//
	EventEmitter.prototype.off = EventEmitter.prototype.removeListener;
	EventEmitter.prototype.addListener = EventEmitter.prototype.on;

	//
	// Expose the prefix.
	//
	EventEmitter.prefixed = prefix;

	//
	// Allow `EventEmitter` to be imported as module namespace.
	//
	EventEmitter.EventEmitter = EventEmitter;

	//
	// Expose the module.
	//
	{
	  module.exports = EventEmitter;
	} 
} (eventemitter3));

var eventemitter3Exports = eventemitter3.exports;
var EventEmitter$1 = /*@__PURE__*/getDefaultExportFromCjs(eventemitter3Exports);

let apiInstance = null;
const getApiInstance = (initialState) => {
    if (!apiInstance) {
        apiInstance = new Api(initialState);
    }
    return apiInstance;
};
class Api extends EventEmitter$1 {
    constructor(initialState) {
        super();
        this.registeredListeners = [];
        this.state = initialState;
    }
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.emit("state_change", this.state);
    }
    getState() {
        return this.state;
    }
    async init() {
        await call("init");
        await this.fetchConfig();
        this.registeredListeners.push(SteamClient.GameSessions.RegisterForAppLifetimeNotifications(this.onAppLifetimeNotification.bind(this)));
        this.registeredListeners.push(SteamClient.System.RegisterForOnResumeFromSuspend(this.onResumeFromSuspend.bind(this)));
        if (this.state.settings.isRunAutomatically && DFL.Router.MainRunningApp) {
            return await this.handleMainRunningApp();
        }
        if (this.state.settings.runAtStartup) {
            return await this.applyUndervolt(this.state.cores, this.state.settings.timeoutApply);
        }
        await this.disableUndervolt();
    }
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
    async handleMainRunningApp(id, label) {
        if (DFL.Router.MainRunningApp || (id && label)) {
            this.setState({
                runningAppName: label || DFL.Router.MainRunningApp?.display_name || null,
                runningAppId: id || Number(DFL.Router.MainRunningApp?.appid) || null,
            });
            await this.applyUndervoltBasedOnPreset();
        }
        else {
            this.setState({ cores: this.state.globalCores });
        }
    }
    async applyUndervoltBasedOnPreset() {
        const preset = this.state.presets.find((p) => p.app_id === this.state.runningAppId);
        if (preset) {
            this.setState({ cores: preset.value, currentPreset: preset });
            await this.applyUndervolt(preset.value, preset.use_timeout ? preset.timeout : 0);
        }
        else {
            await this.applyUndervolt(this.state.globalCores);
        }
    }
    async onAppLifetimeNotification(app) {
        const gameId = app.unAppID;
        const gameInfo = appStore.GetAppOverviewByGameID(gameId);
        if (app.bRunning) {
            if (!this.state.settings.isRunAutomatically)
                return;
            await this.handleMainRunningApp(gameId, gameInfo.display_name);
        }
        else {
            this.setState({ runningAppName: null, cores: this.state.globalCores });
            if (this.state.settings.isGlobal && this.state.status === "enabled") {
                await this.applyUndervolt(this.state.globalCores);
            }
            else {
                await this.disableUndervolt();
            }
        }
    }
    async onResumeFromSuspend() {
        if (this.state.status === "enabled") {
            await this.applyUndervolt(this.state.cores, 5);
        }
    }
    async enableGymdeck() {
        await call("start_gymdeck", this.state.dynamicSettings);
    }
    async disableGymdeck() {
        await call('stop_gymdeck');
    }
    async applyUndervolt(core_values, timeout = 0) {
        this.setState({ cores: core_values });
        await call("apply_undervolt", core_values, timeout);
    }
    async disableUndervolt() {
        await call("disable_undervolt");
    }
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
                    label: this.state.runningAppName,
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
    async saveSettings(settings) {
        await call("save_settings", settings);
        this.setState({ settings });
    }
    async resetConfig() {
        const result = (await call("reset_config"));
        this.setState({
            globalCores: result.cores,
            cores: result.cores,
            settings: result.settings,
            status: "Disabled",
            currentPreset: null,
        });
        await this.disableUndervolt();
    }
    destroy() {
        this.registeredListeners.forEach((call) => {
            call.unregister();
        });
    }
    async deletePreset(app_id) {
        const presets = [...this.state.presets];
        const presetIndex = presets.findIndex((p) => p.app_id === app_id);
        if (presetIndex !== -1) {
            presets.splice(presetIndex, 1);
        }
        this.setState({ presets });
        await call("delete_preset", app_id);
    }
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
    handleServerEvent({ type, data, }) {
        switch (type) {
            case "update_status":
                this.setState({ status: data });
                break;
        }
    }
}

// @ts-ignore
const Context = SP_REACT.createContext(null);
const Provider = ({ children }) => {
    const initialState = {
        gymdeckRunning: false,
        isDynamic: false,
        dynamicSettings: {
            cores: [
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
            ],
            sampleInterval: 50000,
            strategy: "DEFAULT",
        },
        runningAppName: null,
        runningAppId: null,
        status: "Disabled",
        cores: [5, 5, 5, 5],
        currentPreset: null,
        presets: [],
        settings: {
            isGlobal: false,
            runAtStartup: false,
            isRunAutomatically: false,
            timeoutApply: 15,
        },
        globalCores: [],
    };
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
    return window.SP_REACT.createElement(Context.Provider, { value: { state, api } }, children);
};

const PresetManager = ({ setCurrentPage, }) => {
    const { t } = useTranslation();
    const [selectedPreset, setSelectedPreset] = SP_REACT.useState(null);
    const [editablePreset, setEditablePreset] = SP_REACT.useState(null);
    const [doubleCheckDelete, setDoubleCheckDelete] = SP_REACT.useState(false);
    const [loading, setLoading] = SP_REACT.useState(false);
    const { state, api } = SP_REACT.useContext(Context);
    const handleSetSelectedPreset = (preset) => {
        setDoubleCheckDelete(false);
        setSelectedPreset(preset?.data || null);
        setEditablePreset(preset?.data || null);
    };
    const updateCore = (index, value) => {
        const newCores = [...editablePreset.value];
        newCores[index] = value;
        setEditablePreset({ ...editablePreset, value: newCores });
    };
    const handleUpdatePreset = async () => {
        setSelectedPreset(editablePreset);
        setDoubleCheckDelete(false);
        setLoading(true);
        if (!editablePreset)
            return;
        await api.updatePreset(editablePreset);
        setTimeout(() => setLoading(false), 1000);
    };
    const handleDeletePreset = async () => {
        if (!doubleCheckDelete) {
            setDoubleCheckDelete(true);
            return;
        }
        if (!editablePreset)
            return;
        setDoubleCheckDelete(false);
        await api.deletePreset(editablePreset.app_id);
        setSelectedPreset(null);
        setEditablePreset(null);
    };
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setCurrentPage("main") }, t("presetManager.backButton"))),
        window.SP_REACT.createElement(PresetSelector, { presets: state.presets, selectedPreset: selectedPreset, handleSetSelectedPreset: handleSetSelectedPreset }),
        editablePreset && (window.SP_REACT.createElement(SP_REACT.Fragment, null,
            state.settings.isRunAutomatically && (window.SP_REACT.createElement(PresetControls$1, { editablePreset: editablePreset, setEditablePreset: setEditablePreset })),
            window.SP_REACT.createElement(CoreSliders, { cores: editablePreset.value, updateCore: updateCore }),
            window.SP_REACT.createElement(ActionButtons$2, { loading: loading, doubleCheckDelete: doubleCheckDelete, handleUpdatePreset: handleUpdatePreset, handleDeletePreset: handleDeletePreset })))));
};

const UndervoltStatus = () => {
    const { state } = SP_REACT.useContext(Context);
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        t("undervoltStatus.status"),
        " ",
        t("undervoltStatus." + state.status || "disabled")));
};

const PresetControls = ({ useAsPreset, setUseAsPreset, usePresetTimeout, setUsePresetTimeout, presetTimeout, setPresetTimeout, }) => {
    const { state } = SP_REACT.useContext(Context);
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { checked: useAsPreset, onChange: (value) => setUseAsPreset(value), label: t("staticUndervolt.useForCurrentGame", {
                    appName: state.runningAppName ||
                        t("staticUndervolt.currentGamePlaceholder"),
                }), disabled: !state.runningAppName, description: state.runningAppName
                    ? t("staticUndervolt.descriptionRunningGame", {
                        appName: state.runningAppName,
                    })
                    : t("staticUndervolt.noGameRunning") })),
        state.settings.isRunAutomatically && useAsPreset && (window.SP_REACT.createElement(SP_REACT.Fragment, null,
            window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.ToggleField, { checked: usePresetTimeout, onChange: (value) => setUsePresetTimeout(value), label: t("presetControls.useTimeout"), description: t("presetControls.timeoutDescription", {
                        label: state.runningAppName,
                    }) })),
            usePresetTimeout && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
                window.SP_REACT.createElement(DFL.SliderField, { bottomSeparator: "standard", min: 0, showValue: true, max: 1000, step: 1, label: t("presetControls.timeoutLabel"), value: presetTimeout, onChange: setPresetTimeout })))))));
};

const ActionButtons$1 = ({ loading, updateCoreValues, handleReset, handleDisableUndervolt, }) => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { disabled: loading, layout: "below", onClick: updateCoreValues }, loading
                ? t("staticUndervolt.actionButtons.applying")
                : t("staticUndervolt.actionButtons.saveAndApply"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { disabled: loading, layout: "below", onClick: handleReset }, t("staticUndervolt.actionButtons.reset"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { disabled: loading, layout: "below", onClick: handleDisableUndervolt }, t("staticUndervolt.actionButtons.disable")))));
};

const StaticUndervolt = ({ setCurrentPage, }) => {
    const [cores, setCores] = SP_REACT.useState([5, 5, 5, 5]);
    const [useAsPreset, setUseAsPreset] = SP_REACT.useState(false);
    const [usePresetTimeout, setUsePresetTimeout] = SP_REACT.useState(false);
    const [presetTimeout, setPresetTimeout] = SP_REACT.useState(0);
    const { api, state } = SP_REACT.useContext(Context);
    const [loading, setLoading] = SP_REACT.useState(false);
    const { t } = useTranslation();
    SP_REACT.useEffect(() => {
        setCores(state.cores);
        setUseAsPreset(!!state.currentPreset && !!state.runningAppName);
        setUsePresetTimeout(state?.currentPreset?.use_timeout || false);
        setPresetTimeout(state?.currentPreset?.timeout || 0);
    }, [state]);
    const setDynamicUndervolt = (value) => {
        api.setState({ isDynamic: value });
    };
    const updateCore = (index, value) => {
        const newCores = [...cores];
        newCores[index] = value;
        setCores(newCores);
    };
    const updateCoreValues = async () => {
        setLoading(true);
        try {
            await api.saveAndApply(cores, useAsPreset, {
                use_timeout: usePresetTimeout,
                timeout: presetTimeout,
            });
        }
        catch (e) {
            console.error(e);
        }
        finally {
            setTimeout(() => setLoading(false), 1000);
        }
    };
    const handleReset = () => setCores([5, 5, 5, 5]);
    const handleDisableUndervolt = async () => {
        await api.disableUndervolt();
    };
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(UndervoltStatus, null),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { checked: state.isDynamic, label: 'Use Dynamic Undervolting', onChange: setDynamicUndervolt })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: () => setCurrentPage("preset-manager") }, t("staticUndervolt.presetManagerButton"))),
        window.SP_REACT.createElement(PresetControls, { useAsPreset: useAsPreset, setUseAsPreset: setUseAsPreset, usePresetTimeout: usePresetTimeout, setUsePresetTimeout: setUsePresetTimeout, presetTimeout: presetTimeout, setPresetTimeout: setPresetTimeout }),
        window.SP_REACT.createElement(CoreSliders, { cores: cores, updateCore: updateCore }),
        window.SP_REACT.createElement(ActionButtons$1, { loading: loading, updateCoreValues: updateCoreValues, handleReset: handleReset, handleDisableUndervolt: handleDisableUndervolt })));
};

const ActionButtons = ({ handleSave, loading, }) => {
    const { api } = SP_REACT.useContext(Context);
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: handleSave, disabled: loading }, "Save and Enable Dynamic"),
        window.SP_REACT.createElement(DFL.ButtonItem, { layout: "below", onClick: api.disableGymdeck, disabled: loading }, "Disable")));
};

const StrategySelector = ({ handleChangeStrategy, selectedStrategy, }) => {
    return (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
        window.SP_REACT.createElement(DFL.DropdownItem, { rgOptions: [
                { label: "Manual", data: "MANUAL" },
                { label: "Aggressive", data: "AGGRESSIVE" },
                { label: "Default", data: "DEFAULT" },
            ], selectedOption: selectedStrategy, onChange: handleChangeStrategy, label: "Strategy Selector" })));
};

// A helper to create a smooth path with quadratic Bézier curves
function getSmoothPath(points) {
    if (points.length < 2)
        return "";
    let d = `M ${points[0].x},${points[0].y}`;
    for (let i = 0; i < points.length - 1; i++) {
        const p0 = points[i];
        const p1 = points[i + 1];
        const midX = (p0.x + p1.x) / 2;
        const midY = (p0.y + p1.y) / 2;
        // Quadratic curve from p0 to mid‐point
        d += ` Q ${p0.x},${p0.y} ${midX},${midY}`;
    }
    // "T" continues the smooth curve to the final point
    const last = points[points.length - 1];
    d += ` T ${last.x},${last.y}`;
    return d;
}
const UndervoltingPreview = ({ data }) => {
    // We reserve a 10% margin at each edge
    const MARGIN = 10;
    const CHART_MIN = MARGIN;
    const CHART_MAX = 100 - MARGIN;
    const CHART_SIZE = CHART_MAX - CHART_MIN; // 80
    // Map data [0..100] → [MARGIN..(100 - MARGIN)]
    const normalizedData = data.map((pt) => ({
        x: CHART_MIN + (pt.point / 100) * CHART_SIZE,
        // invert Y so 100 is at bottom
        y: CHART_MAX - (pt.value / 100) * CHART_SIZE,
    }));
    const smoothPath = getSmoothPath(normalizedData);
    return (window.SP_REACT.createElement("div", { style: { width: "100%", height: "250px", position: "relative" } },
        window.SP_REACT.createElement("svg", { viewBox: "0 0 100 100", preserveAspectRatio: "xMidYMid meet", style: {
                width: "100%",
                height: "100%",
                backgroundColor: "black",
                border: "1px solid #1e90ff",
                display: "block",
            } },
            [...Array(11)].map((_, i) => {
                // e.g. i=0 => val=0, i=10 => val=100
                const val = (i * 100) / 10; // 0,10,20,...,100
                // Convert val to chart coords
                const xPos = CHART_MIN + (val / 100) * CHART_SIZE;
                const yPos = CHART_MAX - (val / 100) * CHART_SIZE;
                return (window.SP_REACT.createElement(SP_REACT.Fragment, { key: i },
                    window.SP_REACT.createElement("line", { x1: CHART_MIN, y1: yPos, x2: CHART_MAX, y2: yPos, stroke: "#1e90ff", strokeWidth: "0.2" }),
                    window.SP_REACT.createElement("line", { x1: xPos, y1: CHART_MIN, x2: xPos, y2: CHART_MAX, stroke: "#1e90ff", strokeWidth: "0.2" })));
            }),
            [...Array(11)].map((_, i) => {
                const val = i * 10; // 0..100
                const xPos = CHART_MIN + (val / 100) * CHART_SIZE;
                return (window.SP_REACT.createElement("text", { key: `x-label-${val}`, x: xPos, y: CHART_MAX + 5, fontSize: "2", fill: "#ccc", textAnchor: "middle", style: { fontFamily: "sans-serif" } },
                    val,
                    "%"));
            }),
            [...Array(11)].map((_, i) => {
                const val = i * 10; // 0..100
                const yPos = CHART_MAX - (val / 100) * CHART_SIZE;
                return (window.SP_REACT.createElement("text", { key: `y-label-${val}`, x: CHART_MIN - 2, y: yPos, fontSize: "2", fill: "#ccc", textAnchor: "end", alignmentBaseline: "middle", style: { fontFamily: "sans-serif" } }, val));
            }),
            window.SP_REACT.createElement("text", { x: (CHART_MIN + CHART_MAX) / 2, y: CHART_MAX + 9, fontSize: "4", fill: "white", textAnchor: "middle", style: { fontFamily: "sans-serif" } }, "CPU Load %"),
            window.SP_REACT.createElement("text", { x: CHART_MIN - 9, y: (CHART_MIN + CHART_MAX) / 2, fontSize: "4", fill: "white", textAnchor: "middle", style: { fontFamily: "sans-serif" }, transform: `
            rotate(-90, 
              ${CHART_MIN - 9}, 
              ${(CHART_MIN + CHART_MAX) / 2}
            )
          ` }, "CO Step"),
            window.SP_REACT.createElement("path", { d: smoothPath, stroke: "#1e90ff", strokeWidth: "0.7", fill: "none" }))));
};

function debounce(func, ms) {
    let timeout;
    return function () {
        clearTimeout(timeout);
        // @ts-ignore
        timeout = setTimeout(() => func.apply(this, arguments), ms);
    };
}

const DynamicCoreSettings = ({ label, coreSettings, handleChange, strategy, }) => {
    const [graphData, setGraphData] = SP_REACT.useState([]);
    const generateGraphData = () => {
        const data = [];
        const threshold = coreSettings.threshold;
        const minValue = coreSettings.minimumValue;
        const maxValue = coreSettings.maximumValue;
        for (let i = 0; i < 100; i++) {
            const point = i; // Temperature from 0 to 100
            let value = minValue; // Default curve optimizer step value
            if (strategy === "AGGRESSIVE") {
                if (point > threshold) {
                    const loadAboveThreshold = point - threshold;
                    const loadRange = 100 - threshold;
                    const normalizedLoad = loadAboveThreshold / loadRange;
                    value = minValue + Math.round(normalizedLoad * (maxValue - minValue));
                }
            }
            else if (strategy === "DEFAULT") {
                if (point > threshold) {
                    value = Math.round((point / 100) * maxValue);
                }
                else {
                    value = Math.round((point / 100) * minValue);
                }
                value = Math.max(minValue, Math.min(value, maxValue));
            }
            else if (strategy === "MANUAL") {
                // Manual logic can be implemented if specific points and values are provided
                // For now, we assume linear mapping between minValue and maxValue
                value = Math.round((point / 100) * (maxValue - minValue) + minValue);
            }
            data.push({ point, value });
        }
        console.log(data);
        setGraphData(data);
    };
    const debouncedGenerateGraphData = debounce(generateGraphData, 200);
    const handleSliderChange = (key, value) => {
        handleChange({ ...coreSettings, [key]: value });
        debouncedGenerateGraphData();
    };
    SP_REACT.useEffect(() => {
        debouncedGenerateGraphData();
    }, []);
    SP_REACT.useEffect(() => {
        debouncedGenerateGraphData();
    }, [strategy]);
    return (window.SP_REACT.createElement("div", { style: { marginBottom: 10 } },
        label,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { showValue: true, label: "Minimal Value", min: 0, max: 100, value: coreSettings.minimumValue, onChange: (value) => handleSliderChange("minimumValue", value) })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { label: "Maximum Value", min: 0, showValue: true, max: 100, value: coreSettings.maximumValue, onChange: (value) => handleSliderChange("maximumValue", value) })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { label: "Threshold", min: 0, showValue: true, max: 100, value: coreSettings.threshold, onChange: (value) => handleSliderChange("threshold", value) })),
        window.SP_REACT.createElement(UndervoltingPreview, { data: graphData })));
};

const DynamicUndervolt = () => {
    const { api, state } = SP_REACT.useContext(Context);
    const [loading, setLoading] = SP_REACT.useState(false);
    const [dynamicSettings, setDynamicSettings] = SP_REACT.useState({
        ...state.dynamicSettings,
    });
    const setDynamicUndervolt = (checked) => {
        api.setState({ isDynamic: checked });
    };
    const handleUpdateStrategy = (strategy) => {
        setDynamicSettings((prevState) => ({
            ...prevState,
            strategy: strategy.data,
        }));
    };
    const handleUpdateSampleInterval = (value) => {
        setDynamicSettings((prevState) => ({
            ...prevState,
            sampleInterval: value,
        }));
    };
    const handleUpdateCoreSettings = (coreIndex, value) => {
        setDynamicSettings((prevState) => ({
            ...prevState,
            cores: prevState.cores.map((core, index) => {
                if (index === coreIndex) {
                    return {
                        ...core,
                        ...value,
                    };
                }
                return core;
            }),
        }));
    };
    const handleSave = async () => {
        api.setState({ dynamicSettings });
        setLoading(true);
        await api.enableGymdeck();
        setLoading(false);
    };
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(UndervoltStatus, null),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { checked: state.isDynamic, label: "Use Dynamic Undervolting", onChange: setDynamicUndervolt })),
        window.SP_REACT.createElement(StrategySelector, { handleChangeStrategy: handleUpdateStrategy, selectedStrategy: dynamicSettings.strategy }),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.SliderField, { label: "Sample Interval", min: 10000, showValue: true, max: 100000, value: dynamicSettings.sampleInterval, onChange: handleUpdateSampleInterval })),
        state.dynamicSettings.cores.map((_core, index) => (window.SP_REACT.createElement(DynamicCoreSettings, { coreSettings: dynamicSettings.cores[index], handleChange: (data) => handleUpdateCoreSettings(index, data), key: index, label: `Core ${index}`, strategy: dynamicSettings.strategy }))),
        window.SP_REACT.createElement(ActionButtons, { handleSave: handleSave, loading: loading })));
};

const UndervoltSection = () => {
    const [currentPage, setCurrentPage] = SP_REACT.useState("main");
    const { state } = SP_REACT.useContext(Context);
    if (state.isDynamic)
        return window.SP_REACT.createElement(DynamicUndervolt, null);
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        currentPage === "main" && (window.SP_REACT.createElement(StaticUndervolt, { setCurrentPage: setCurrentPage })),
        currentPage === "preset-manager" && (window.SP_REACT.createElement(PresetManager, { setCurrentPage: setCurrentPage }))));
};

const Settings = () => {
    const { t } = useTranslation();
    const [settings, setSettings] = SP_REACT.useState({
        isGlobal: false,
        runAtStartup: false,
        isRunAutomatically: false,
        timeoutApply: 0,
    });
    const { api, state } = SP_REACT.useContext(Context);
    SP_REACT.useEffect(() => {
        setSettings({ ...state.settings });
    }, [state]);
    const [loadingSave, setLoadingSave] = SP_REACT.useState(false);
    const [loadingReset, setLoadingReset] = SP_REACT.useState(false);
    const handleSaveSettings = async () => {
        setLoadingSave(true);
        try {
            await api.saveSettings(settings);
        }
        catch (error) {
            console.error(error);
        }
        finally {
            setTimeout(() => setLoadingSave(false), 1000);
        }
    };
    const handleTimeoutApplyChange = ($event) => {
        const value = Number($event?.target?.value);
        if (!isNaN(Number(value))) {
            setSettings({ ...settings, timeoutApply: Number(value) });
        }
    };
    const handleResetConfig = async () => {
        setLoadingReset(true);
        try {
            await api.resetConfig();
            setSettings({ ...state.settings });
        }
        catch (error) {
            console.error(error);
        }
        finally {
            setTimeout(() => setLoadingReset(false), 1000);
        }
    };
    const { isGlobal, runAtStartup, isRunAutomatically, timeoutApply } = settings;
    return (window.SP_REACT.createElement(SP_REACT.Fragment, null,
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { label: t("settings.useGlobally"), checked: isGlobal, onChange: (checked) => setSettings({ ...settings, isGlobal: checked }), description: t("settings.useGloballyDescription") })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { label: t("settings.runWithGame"), checked: isRunAutomatically, onChange: (checked) => setSettings({ ...settings, isRunAutomatically: checked }), description: t("settings.runWithGameDescription") })),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ToggleField, { label: t("settings.runAtStartup"), checked: runAtStartup, onChange: (checked) => setSettings({ ...settings, runAtStartup: checked }), description: t("settings.runAtStartupDescription") })),
        runAtStartup && (window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.TextField, { label: t("settings.timeoutApply"), mustBeNumeric: true, value: String(timeoutApply), onChange: handleTimeoutApplyChange, description: t("settings.timeoutApplyDescription") }))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { disabled: loadingReset, onClick: handleResetConfig, layout: "inline" }, loadingReset
                ? t("settings.resettingConfig")
                : t("settings.resetConfig"))),
        window.SP_REACT.createElement(DFL.PanelSectionRow, null,
            window.SP_REACT.createElement(DFL.ButtonItem, { disabled: loadingSave, onClick: handleSaveSettings, layout: "inline" }, loadingSave
                ? t("settings.savingSettings")
                : t("settings.saveSettings")))));
};

const AboutPage = () => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement("div", { style: { fontSize: "12px" } },
        window.SP_REACT.createElement("p", null, t("about.header")),
        window.SP_REACT.createElement("ul", null,
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.tools.ryzenadj"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.tools.steamDeck")))),
        window.SP_REACT.createElement("p", null, t("about.supportHeader")),
        window.SP_REACT.createElement("ul", null,
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.kigs"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.pososaku"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.deadwenk"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.foxn"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.robert"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.ngnius"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.notBullseye"))),
            window.SP_REACT.createElement("li", null,
                window.SP_REACT.createElement("b", null, t("about.supporters.community")))),
        window.SP_REACT.createElement("div", { style: { textAlign: "center" } },
            window.SP_REACT.createElement("p", null, t("about.footer.thankYou")),
            window.SP_REACT.createElement("div", null, t("about.footer.madeBy")))));
};

const Pages = () => {
    const { t } = useTranslation();
    return (window.SP_REACT.createElement(DFL.SidebarNavigation, { title: t("sidebar.title"), showTitle: false, pages: [
            {
                title: t("sidebar.settings"),
                content: window.SP_REACT.createElement(Settings, null),
            },
            {
                title: t("sidebar.about"),
                content: window.SP_REACT.createElement(AboutPage, null),
            },
        ] }));
};

const isString = obj => typeof obj === 'string';
const defer = () => {
  let res;
  let rej;
  const promise = new Promise((resolve, reject) => {
    res = resolve;
    rej = reject;
  });
  promise.resolve = res;
  promise.reject = rej;
  return promise;
};
const makeString = object => {
  if (object == null) return '';
  return '' + object;
};
const copy = (a, s, t) => {
  a.forEach(m => {
    if (s[m]) t[m] = s[m];
  });
};
const lastOfPathSeparatorRegExp = /###/g;
const cleanKey = key => key && key.indexOf('###') > -1 ? key.replace(lastOfPathSeparatorRegExp, '.') : key;
const canNotTraverseDeeper = object => !object || isString(object);
const getLastOfPath = (object, path, Empty) => {
  const stack = !isString(path) ? path : path.split('.');
  let stackIndex = 0;
  while (stackIndex < stack.length - 1) {
    if (canNotTraverseDeeper(object)) return {};
    const key = cleanKey(stack[stackIndex]);
    if (!object[key] && Empty) object[key] = new Empty();
    if (Object.prototype.hasOwnProperty.call(object, key)) {
      object = object[key];
    } else {
      object = {};
    }
    ++stackIndex;
  }
  if (canNotTraverseDeeper(object)) return {};
  return {
    obj: object,
    k: cleanKey(stack[stackIndex])
  };
};
const setPath = (object, path, newValue) => {
  const {
    obj,
    k
  } = getLastOfPath(object, path, Object);
  if (obj !== undefined || path.length === 1) {
    obj[k] = newValue;
    return;
  }
  let e = path[path.length - 1];
  let p = path.slice(0, path.length - 1);
  let last = getLastOfPath(object, p, Object);
  while (last.obj === undefined && p.length) {
    e = `${p[p.length - 1]}.${e}`;
    p = p.slice(0, p.length - 1);
    last = getLastOfPath(object, p, Object);
    if (last && last.obj && typeof last.obj[`${last.k}.${e}`] !== 'undefined') {
      last.obj = undefined;
    }
  }
  last.obj[`${last.k}.${e}`] = newValue;
};
const pushPath = (object, path, newValue, concat) => {
  const {
    obj,
    k
  } = getLastOfPath(object, path, Object);
  obj[k] = obj[k] || [];
  obj[k].push(newValue);
};
const getPath = (object, path) => {
  const {
    obj,
    k
  } = getLastOfPath(object, path);
  if (!obj) return undefined;
  return obj[k];
};
const getPathWithDefaults = (data, defaultData, key) => {
  const value = getPath(data, key);
  if (value !== undefined) {
    return value;
  }
  return getPath(defaultData, key);
};
const deepExtend = (target, source, overwrite) => {
  for (const prop in source) {
    if (prop !== '__proto__' && prop !== 'constructor') {
      if (prop in target) {
        if (isString(target[prop]) || target[prop] instanceof String || isString(source[prop]) || source[prop] instanceof String) {
          if (overwrite) target[prop] = source[prop];
        } else {
          deepExtend(target[prop], source[prop], overwrite);
        }
      } else {
        target[prop] = source[prop];
      }
    }
  }
  return target;
};
const regexEscape = str => str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&');
var _entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;'
};
const escape = data => {
  if (isString(data)) {
    return data.replace(/[&<>"'\/]/g, s => _entityMap[s]);
  }
  return data;
};
class RegExpCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.regExpMap = new Map();
    this.regExpQueue = [];
  }
  getRegExp(pattern) {
    const regExpFromCache = this.regExpMap.get(pattern);
    if (regExpFromCache !== undefined) {
      return regExpFromCache;
    }
    const regExpNew = new RegExp(pattern);
    if (this.regExpQueue.length === this.capacity) {
      this.regExpMap.delete(this.regExpQueue.shift());
    }
    this.regExpMap.set(pattern, regExpNew);
    this.regExpQueue.push(pattern);
    return regExpNew;
  }
}
const chars = [' ', ',', '?', '!', ';'];
const looksLikeObjectPathRegExpCache = new RegExpCache(20);
const looksLikeObjectPath = (key, nsSeparator, keySeparator) => {
  nsSeparator = nsSeparator || '';
  keySeparator = keySeparator || '';
  const possibleChars = chars.filter(c => nsSeparator.indexOf(c) < 0 && keySeparator.indexOf(c) < 0);
  if (possibleChars.length === 0) return true;
  const r = looksLikeObjectPathRegExpCache.getRegExp(`(${possibleChars.map(c => c === '?' ? '\\?' : c).join('|')})`);
  let matched = !r.test(key);
  if (!matched) {
    const ki = key.indexOf(keySeparator);
    if (ki > 0 && !r.test(key.substring(0, ki))) {
      matched = true;
    }
  }
  return matched;
};
const deepFind = function (obj, path) {
  let keySeparator = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '.';
  if (!obj) return undefined;
  if (obj[path]) return obj[path];
  const tokens = path.split(keySeparator);
  let current = obj;
  for (let i = 0; i < tokens.length;) {
    if (!current || typeof current !== 'object') {
      return undefined;
    }
    let next;
    let nextPath = '';
    for (let j = i; j < tokens.length; ++j) {
      if (j !== i) {
        nextPath += keySeparator;
      }
      nextPath += tokens[j];
      next = current[nextPath];
      if (next !== undefined) {
        if (['string', 'number', 'boolean'].indexOf(typeof next) > -1 && j < tokens.length - 1) {
          continue;
        }
        i += j - i + 1;
        break;
      }
    }
    current = next;
  }
  return current;
};
const getCleanedCode = code => code && code.replace('_', '-');

const consoleLogger = {
  type: 'logger',
  log(args) {
    this.output('log', args);
  },
  warn(args) {
    this.output('warn', args);
  },
  error(args) {
    this.output('error', args);
  },
  output(type, args) {
    if (console && console[type]) console[type].apply(console, args);
  }
};
class Logger {
  constructor(concreteLogger) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    this.init(concreteLogger, options);
  }
  init(concreteLogger) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    this.prefix = options.prefix || 'i18next:';
    this.logger = concreteLogger || consoleLogger;
    this.options = options;
    this.debug = options.debug;
  }
  log() {
    for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }
    return this.forward(args, 'log', '', true);
  }
  warn() {
    for (var _len2 = arguments.length, args = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
      args[_key2] = arguments[_key2];
    }
    return this.forward(args, 'warn', '', true);
  }
  error() {
    for (var _len3 = arguments.length, args = new Array(_len3), _key3 = 0; _key3 < _len3; _key3++) {
      args[_key3] = arguments[_key3];
    }
    return this.forward(args, 'error', '');
  }
  deprecate() {
    for (var _len4 = arguments.length, args = new Array(_len4), _key4 = 0; _key4 < _len4; _key4++) {
      args[_key4] = arguments[_key4];
    }
    return this.forward(args, 'warn', 'WARNING DEPRECATED: ', true);
  }
  forward(args, lvl, prefix, debugOnly) {
    if (debugOnly && !this.debug) return null;
    if (isString(args[0])) args[0] = `${prefix}${this.prefix} ${args[0]}`;
    return this.logger[lvl](args);
  }
  create(moduleName) {
    return new Logger(this.logger, {
      ...{
        prefix: `${this.prefix}:${moduleName}:`
      },
      ...this.options
    });
  }
  clone(options) {
    options = options || this.options;
    options.prefix = options.prefix || this.prefix;
    return new Logger(this.logger, options);
  }
}
var baseLogger = new Logger();

class EventEmitter {
  constructor() {
    this.observers = {};
  }
  on(events, listener) {
    events.split(' ').forEach(event => {
      if (!this.observers[event]) this.observers[event] = new Map();
      const numListeners = this.observers[event].get(listener) || 0;
      this.observers[event].set(listener, numListeners + 1);
    });
    return this;
  }
  off(event, listener) {
    if (!this.observers[event]) return;
    if (!listener) {
      delete this.observers[event];
      return;
    }
    this.observers[event].delete(listener);
  }
  emit(event) {
    for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
      args[_key - 1] = arguments[_key];
    }
    if (this.observers[event]) {
      const cloned = Array.from(this.observers[event].entries());
      cloned.forEach(_ref => {
        let [observer, numTimesAdded] = _ref;
        for (let i = 0; i < numTimesAdded; i++) {
          observer(...args);
        }
      });
    }
    if (this.observers['*']) {
      const cloned = Array.from(this.observers['*'].entries());
      cloned.forEach(_ref2 => {
        let [observer, numTimesAdded] = _ref2;
        for (let i = 0; i < numTimesAdded; i++) {
          observer.apply(observer, [event, ...args]);
        }
      });
    }
  }
}

class ResourceStore extends EventEmitter {
  constructor(data) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {
      ns: ['translation'],
      defaultNS: 'translation'
    };
    super();
    this.data = data || {};
    this.options = options;
    if (this.options.keySeparator === undefined) {
      this.options.keySeparator = '.';
    }
    if (this.options.ignoreJSONStructure === undefined) {
      this.options.ignoreJSONStructure = true;
    }
  }
  addNamespaces(ns) {
    if (this.options.ns.indexOf(ns) < 0) {
      this.options.ns.push(ns);
    }
  }
  removeNamespaces(ns) {
    const index = this.options.ns.indexOf(ns);
    if (index > -1) {
      this.options.ns.splice(index, 1);
    }
  }
  getResource(lng, ns, key) {
    let options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
    const keySeparator = options.keySeparator !== undefined ? options.keySeparator : this.options.keySeparator;
    const ignoreJSONStructure = options.ignoreJSONStructure !== undefined ? options.ignoreJSONStructure : this.options.ignoreJSONStructure;
    let path;
    if (lng.indexOf('.') > -1) {
      path = lng.split('.');
    } else {
      path = [lng, ns];
      if (key) {
        if (Array.isArray(key)) {
          path.push(...key);
        } else if (isString(key) && keySeparator) {
          path.push(...key.split(keySeparator));
        } else {
          path.push(key);
        }
      }
    }
    const result = getPath(this.data, path);
    if (!result && !ns && !key && lng.indexOf('.') > -1) {
      lng = path[0];
      ns = path[1];
      key = path.slice(2).join('.');
    }
    if (result || !ignoreJSONStructure || !isString(key)) return result;
    return deepFind(this.data && this.data[lng] && this.data[lng][ns], key, keySeparator);
  }
  addResource(lng, ns, key, value) {
    let options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {
      silent: false
    };
    const keySeparator = options.keySeparator !== undefined ? options.keySeparator : this.options.keySeparator;
    let path = [lng, ns];
    if (key) path = path.concat(keySeparator ? key.split(keySeparator) : key);
    if (lng.indexOf('.') > -1) {
      path = lng.split('.');
      value = ns;
      ns = path[1];
    }
    this.addNamespaces(ns);
    setPath(this.data, path, value);
    if (!options.silent) this.emit('added', lng, ns, key, value);
  }
  addResources(lng, ns, resources) {
    let options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {
      silent: false
    };
    for (const m in resources) {
      if (isString(resources[m]) || Array.isArray(resources[m])) this.addResource(lng, ns, m, resources[m], {
        silent: true
      });
    }
    if (!options.silent) this.emit('added', lng, ns, resources);
  }
  addResourceBundle(lng, ns, resources, deep, overwrite) {
    let options = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : {
      silent: false,
      skipCopy: false
    };
    let path = [lng, ns];
    if (lng.indexOf('.') > -1) {
      path = lng.split('.');
      deep = resources;
      resources = ns;
      ns = path[1];
    }
    this.addNamespaces(ns);
    let pack = getPath(this.data, path) || {};
    if (!options.skipCopy) resources = JSON.parse(JSON.stringify(resources));
    if (deep) {
      deepExtend(pack, resources, overwrite);
    } else {
      pack = {
        ...pack,
        ...resources
      };
    }
    setPath(this.data, path, pack);
    if (!options.silent) this.emit('added', lng, ns, resources);
  }
  removeResourceBundle(lng, ns) {
    if (this.hasResourceBundle(lng, ns)) {
      delete this.data[lng][ns];
    }
    this.removeNamespaces(ns);
    this.emit('removed', lng, ns);
  }
  hasResourceBundle(lng, ns) {
    return this.getResource(lng, ns) !== undefined;
  }
  getResourceBundle(lng, ns) {
    if (!ns) ns = this.options.defaultNS;
    if (this.options.compatibilityAPI === 'v1') return {
      ...{},
      ...this.getResource(lng, ns)
    };
    return this.getResource(lng, ns);
  }
  getDataByLanguage(lng) {
    return this.data[lng];
  }
  hasLanguageSomeTranslations(lng) {
    const data = this.getDataByLanguage(lng);
    const n = data && Object.keys(data) || [];
    return !!n.find(v => data[v] && Object.keys(data[v]).length > 0);
  }
  toJSON() {
    return this.data;
  }
}

var postProcessor = {
  processors: {},
  addPostProcessor(module) {
    this.processors[module.name] = module;
  },
  handle(processors, value, key, options, translator) {
    processors.forEach(processor => {
      if (this.processors[processor]) value = this.processors[processor].process(value, key, options, translator);
    });
    return value;
  }
};

const checkedLoadedFor = {};
class Translator extends EventEmitter {
  constructor(services) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    super();
    copy(['resourceStore', 'languageUtils', 'pluralResolver', 'interpolator', 'backendConnector', 'i18nFormat', 'utils'], services, this);
    this.options = options;
    if (this.options.keySeparator === undefined) {
      this.options.keySeparator = '.';
    }
    this.logger = baseLogger.create('translator');
  }
  changeLanguage(lng) {
    if (lng) this.language = lng;
  }
  exists(key) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {
      interpolation: {}
    };
    if (key === undefined || key === null) {
      return false;
    }
    const resolved = this.resolve(key, options);
    return resolved && resolved.res !== undefined;
  }
  extractFromKey(key, options) {
    let nsSeparator = options.nsSeparator !== undefined ? options.nsSeparator : this.options.nsSeparator;
    if (nsSeparator === undefined) nsSeparator = ':';
    const keySeparator = options.keySeparator !== undefined ? options.keySeparator : this.options.keySeparator;
    let namespaces = options.ns || this.options.defaultNS || [];
    const wouldCheckForNsInKey = nsSeparator && key.indexOf(nsSeparator) > -1;
    const seemsNaturalLanguage = !this.options.userDefinedKeySeparator && !options.keySeparator && !this.options.userDefinedNsSeparator && !options.nsSeparator && !looksLikeObjectPath(key, nsSeparator, keySeparator);
    if (wouldCheckForNsInKey && !seemsNaturalLanguage) {
      const m = key.match(this.interpolator.nestingRegexp);
      if (m && m.length > 0) {
        return {
          key,
          namespaces: isString(namespaces) ? [namespaces] : namespaces
        };
      }
      const parts = key.split(nsSeparator);
      if (nsSeparator !== keySeparator || nsSeparator === keySeparator && this.options.ns.indexOf(parts[0]) > -1) namespaces = parts.shift();
      key = parts.join(keySeparator);
    }
    return {
      key,
      namespaces: isString(namespaces) ? [namespaces] : namespaces
    };
  }
  translate(keys, options, lastKey) {
    if (typeof options !== 'object' && this.options.overloadTranslationOptionHandler) {
      options = this.options.overloadTranslationOptionHandler(arguments);
    }
    if (typeof options === 'object') options = {
      ...options
    };
    if (!options) options = {};
    if (keys === undefined || keys === null) return '';
    if (!Array.isArray(keys)) keys = [String(keys)];
    const returnDetails = options.returnDetails !== undefined ? options.returnDetails : this.options.returnDetails;
    const keySeparator = options.keySeparator !== undefined ? options.keySeparator : this.options.keySeparator;
    const {
      key,
      namespaces
    } = this.extractFromKey(keys[keys.length - 1], options);
    const namespace = namespaces[namespaces.length - 1];
    const lng = options.lng || this.language;
    const appendNamespaceToCIMode = options.appendNamespaceToCIMode || this.options.appendNamespaceToCIMode;
    if (lng && lng.toLowerCase() === 'cimode') {
      if (appendNamespaceToCIMode) {
        const nsSeparator = options.nsSeparator || this.options.nsSeparator;
        if (returnDetails) {
          return {
            res: `${namespace}${nsSeparator}${key}`,
            usedKey: key,
            exactUsedKey: key,
            usedLng: lng,
            usedNS: namespace,
            usedParams: this.getUsedParamsDetails(options)
          };
        }
        return `${namespace}${nsSeparator}${key}`;
      }
      if (returnDetails) {
        return {
          res: key,
          usedKey: key,
          exactUsedKey: key,
          usedLng: lng,
          usedNS: namespace,
          usedParams: this.getUsedParamsDetails(options)
        };
      }
      return key;
    }
    const resolved = this.resolve(keys, options);
    let res = resolved && resolved.res;
    const resUsedKey = resolved && resolved.usedKey || key;
    const resExactUsedKey = resolved && resolved.exactUsedKey || key;
    const resType = Object.prototype.toString.apply(res);
    const noObject = ['[object Number]', '[object Function]', '[object RegExp]'];
    const joinArrays = options.joinArrays !== undefined ? options.joinArrays : this.options.joinArrays;
    const handleAsObjectInI18nFormat = !this.i18nFormat || this.i18nFormat.handleAsObject;
    const handleAsObject = !isString(res) && typeof res !== 'boolean' && typeof res !== 'number';
    if (handleAsObjectInI18nFormat && res && handleAsObject && noObject.indexOf(resType) < 0 && !(isString(joinArrays) && Array.isArray(res))) {
      if (!options.returnObjects && !this.options.returnObjects) {
        if (!this.options.returnedObjectHandler) {
          this.logger.warn('accessing an object - but returnObjects options is not enabled!');
        }
        const r = this.options.returnedObjectHandler ? this.options.returnedObjectHandler(resUsedKey, res, {
          ...options,
          ns: namespaces
        }) : `key '${key} (${this.language})' returned an object instead of string.`;
        if (returnDetails) {
          resolved.res = r;
          resolved.usedParams = this.getUsedParamsDetails(options);
          return resolved;
        }
        return r;
      }
      if (keySeparator) {
        const resTypeIsArray = Array.isArray(res);
        const copy = resTypeIsArray ? [] : {};
        const newKeyToUse = resTypeIsArray ? resExactUsedKey : resUsedKey;
        for (const m in res) {
          if (Object.prototype.hasOwnProperty.call(res, m)) {
            const deepKey = `${newKeyToUse}${keySeparator}${m}`;
            copy[m] = this.translate(deepKey, {
              ...options,
              ...{
                joinArrays: false,
                ns: namespaces
              }
            });
            if (copy[m] === deepKey) copy[m] = res[m];
          }
        }
        res = copy;
      }
    } else if (handleAsObjectInI18nFormat && isString(joinArrays) && Array.isArray(res)) {
      res = res.join(joinArrays);
      if (res) res = this.extendTranslation(res, keys, options, lastKey);
    } else {
      let usedDefault = false;
      let usedKey = false;
      const needsPluralHandling = options.count !== undefined && !isString(options.count);
      const hasDefaultValue = Translator.hasDefaultValue(options);
      const defaultValueSuffix = needsPluralHandling ? this.pluralResolver.getSuffix(lng, options.count, options) : '';
      const defaultValueSuffixOrdinalFallback = options.ordinal && needsPluralHandling ? this.pluralResolver.getSuffix(lng, options.count, {
        ordinal: false
      }) : '';
      const needsZeroSuffixLookup = needsPluralHandling && !options.ordinal && options.count === 0 && this.pluralResolver.shouldUseIntlApi();
      const defaultValue = needsZeroSuffixLookup && options[`defaultValue${this.options.pluralSeparator}zero`] || options[`defaultValue${defaultValueSuffix}`] || options[`defaultValue${defaultValueSuffixOrdinalFallback}`] || options.defaultValue;
      if (!this.isValidLookup(res) && hasDefaultValue) {
        usedDefault = true;
        res = defaultValue;
      }
      if (!this.isValidLookup(res)) {
        usedKey = true;
        res = key;
      }
      const missingKeyNoValueFallbackToKey = options.missingKeyNoValueFallbackToKey || this.options.missingKeyNoValueFallbackToKey;
      const resForMissing = missingKeyNoValueFallbackToKey && usedKey ? undefined : res;
      const updateMissing = hasDefaultValue && defaultValue !== res && this.options.updateMissing;
      if (usedKey || usedDefault || updateMissing) {
        this.logger.log(updateMissing ? 'updateKey' : 'missingKey', lng, namespace, key, updateMissing ? defaultValue : res);
        if (keySeparator) {
          const fk = this.resolve(key, {
            ...options,
            keySeparator: false
          });
          if (fk && fk.res) this.logger.warn('Seems the loaded translations were in flat JSON format instead of nested. Either set keySeparator: false on init or make sure your translations are published in nested format.');
        }
        let lngs = [];
        const fallbackLngs = this.languageUtils.getFallbackCodes(this.options.fallbackLng, options.lng || this.language);
        if (this.options.saveMissingTo === 'fallback' && fallbackLngs && fallbackLngs[0]) {
          for (let i = 0; i < fallbackLngs.length; i++) {
            lngs.push(fallbackLngs[i]);
          }
        } else if (this.options.saveMissingTo === 'all') {
          lngs = this.languageUtils.toResolveHierarchy(options.lng || this.language);
        } else {
          lngs.push(options.lng || this.language);
        }
        const send = (l, k, specificDefaultValue) => {
          const defaultForMissing = hasDefaultValue && specificDefaultValue !== res ? specificDefaultValue : resForMissing;
          if (this.options.missingKeyHandler) {
            this.options.missingKeyHandler(l, namespace, k, defaultForMissing, updateMissing, options);
          } else if (this.backendConnector && this.backendConnector.saveMissing) {
            this.backendConnector.saveMissing(l, namespace, k, defaultForMissing, updateMissing, options);
          }
          this.emit('missingKey', l, namespace, k, res);
        };
        if (this.options.saveMissing) {
          if (this.options.saveMissingPlurals && needsPluralHandling) {
            lngs.forEach(language => {
              const suffixes = this.pluralResolver.getSuffixes(language, options);
              if (needsZeroSuffixLookup && options[`defaultValue${this.options.pluralSeparator}zero`] && suffixes.indexOf(`${this.options.pluralSeparator}zero`) < 0) {
                suffixes.push(`${this.options.pluralSeparator}zero`);
              }
              suffixes.forEach(suffix => {
                send([language], key + suffix, options[`defaultValue${suffix}`] || defaultValue);
              });
            });
          } else {
            send(lngs, key, defaultValue);
          }
        }
      }
      res = this.extendTranslation(res, keys, options, resolved, lastKey);
      if (usedKey && res === key && this.options.appendNamespaceToMissingKey) res = `${namespace}:${key}`;
      if ((usedKey || usedDefault) && this.options.parseMissingKeyHandler) {
        if (this.options.compatibilityAPI !== 'v1') {
          res = this.options.parseMissingKeyHandler(this.options.appendNamespaceToMissingKey ? `${namespace}:${key}` : key, usedDefault ? res : undefined);
        } else {
          res = this.options.parseMissingKeyHandler(res);
        }
      }
    }
    if (returnDetails) {
      resolved.res = res;
      resolved.usedParams = this.getUsedParamsDetails(options);
      return resolved;
    }
    return res;
  }
  extendTranslation(res, key, options, resolved, lastKey) {
    var _this = this;
    if (this.i18nFormat && this.i18nFormat.parse) {
      res = this.i18nFormat.parse(res, {
        ...this.options.interpolation.defaultVariables,
        ...options
      }, options.lng || this.language || resolved.usedLng, resolved.usedNS, resolved.usedKey, {
        resolved
      });
    } else if (!options.skipInterpolation) {
      if (options.interpolation) this.interpolator.init({
        ...options,
        ...{
          interpolation: {
            ...this.options.interpolation,
            ...options.interpolation
          }
        }
      });
      const skipOnVariables = isString(res) && (options && options.interpolation && options.interpolation.skipOnVariables !== undefined ? options.interpolation.skipOnVariables : this.options.interpolation.skipOnVariables);
      let nestBef;
      if (skipOnVariables) {
        const nb = res.match(this.interpolator.nestingRegexp);
        nestBef = nb && nb.length;
      }
      let data = options.replace && !isString(options.replace) ? options.replace : options;
      if (this.options.interpolation.defaultVariables) data = {
        ...this.options.interpolation.defaultVariables,
        ...data
      };
      res = this.interpolator.interpolate(res, data, options.lng || this.language || resolved.usedLng, options);
      if (skipOnVariables) {
        const na = res.match(this.interpolator.nestingRegexp);
        const nestAft = na && na.length;
        if (nestBef < nestAft) options.nest = false;
      }
      if (!options.lng && this.options.compatibilityAPI !== 'v1' && resolved && resolved.res) options.lng = this.language || resolved.usedLng;
      if (options.nest !== false) res = this.interpolator.nest(res, function () {
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        if (lastKey && lastKey[0] === args[0] && !options.context) {
          _this.logger.warn(`It seems you are nesting recursively key: ${args[0]} in key: ${key[0]}`);
          return null;
        }
        return _this.translate(...args, key);
      }, options);
      if (options.interpolation) this.interpolator.reset();
    }
    const postProcess = options.postProcess || this.options.postProcess;
    const postProcessorNames = isString(postProcess) ? [postProcess] : postProcess;
    if (res !== undefined && res !== null && postProcessorNames && postProcessorNames.length && options.applyPostProcessor !== false) {
      res = postProcessor.handle(postProcessorNames, res, key, this.options && this.options.postProcessPassResolved ? {
        i18nResolved: {
          ...resolved,
          usedParams: this.getUsedParamsDetails(options)
        },
        ...options
      } : options, this);
    }
    return res;
  }
  resolve(keys) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    let found;
    let usedKey;
    let exactUsedKey;
    let usedLng;
    let usedNS;
    if (isString(keys)) keys = [keys];
    keys.forEach(k => {
      if (this.isValidLookup(found)) return;
      const extracted = this.extractFromKey(k, options);
      const key = extracted.key;
      usedKey = key;
      let namespaces = extracted.namespaces;
      if (this.options.fallbackNS) namespaces = namespaces.concat(this.options.fallbackNS);
      const needsPluralHandling = options.count !== undefined && !isString(options.count);
      const needsZeroSuffixLookup = needsPluralHandling && !options.ordinal && options.count === 0 && this.pluralResolver.shouldUseIntlApi();
      const needsContextHandling = options.context !== undefined && (isString(options.context) || typeof options.context === 'number') && options.context !== '';
      const codes = options.lngs ? options.lngs : this.languageUtils.toResolveHierarchy(options.lng || this.language, options.fallbackLng);
      namespaces.forEach(ns => {
        if (this.isValidLookup(found)) return;
        usedNS = ns;
        if (!checkedLoadedFor[`${codes[0]}-${ns}`] && this.utils && this.utils.hasLoadedNamespace && !this.utils.hasLoadedNamespace(usedNS)) {
          checkedLoadedFor[`${codes[0]}-${ns}`] = true;
          this.logger.warn(`key "${usedKey}" for languages "${codes.join(', ')}" won't get resolved as namespace "${usedNS}" was not yet loaded`, 'This means something IS WRONG in your setup. You access the t function before i18next.init / i18next.loadNamespace / i18next.changeLanguage was done. Wait for the callback or Promise to resolve before accessing it!!!');
        }
        codes.forEach(code => {
          if (this.isValidLookup(found)) return;
          usedLng = code;
          const finalKeys = [key];
          if (this.i18nFormat && this.i18nFormat.addLookupKeys) {
            this.i18nFormat.addLookupKeys(finalKeys, key, code, ns, options);
          } else {
            let pluralSuffix;
            if (needsPluralHandling) pluralSuffix = this.pluralResolver.getSuffix(code, options.count, options);
            const zeroSuffix = `${this.options.pluralSeparator}zero`;
            const ordinalPrefix = `${this.options.pluralSeparator}ordinal${this.options.pluralSeparator}`;
            if (needsPluralHandling) {
              finalKeys.push(key + pluralSuffix);
              if (options.ordinal && pluralSuffix.indexOf(ordinalPrefix) === 0) {
                finalKeys.push(key + pluralSuffix.replace(ordinalPrefix, this.options.pluralSeparator));
              }
              if (needsZeroSuffixLookup) {
                finalKeys.push(key + zeroSuffix);
              }
            }
            if (needsContextHandling) {
              const contextKey = `${key}${this.options.contextSeparator}${options.context}`;
              finalKeys.push(contextKey);
              if (needsPluralHandling) {
                finalKeys.push(contextKey + pluralSuffix);
                if (options.ordinal && pluralSuffix.indexOf(ordinalPrefix) === 0) {
                  finalKeys.push(contextKey + pluralSuffix.replace(ordinalPrefix, this.options.pluralSeparator));
                }
                if (needsZeroSuffixLookup) {
                  finalKeys.push(contextKey + zeroSuffix);
                }
              }
            }
          }
          let possibleKey;
          while (possibleKey = finalKeys.pop()) {
            if (!this.isValidLookup(found)) {
              exactUsedKey = possibleKey;
              found = this.getResource(code, ns, possibleKey, options);
            }
          }
        });
      });
    });
    return {
      res: found,
      usedKey,
      exactUsedKey,
      usedLng,
      usedNS
    };
  }
  isValidLookup(res) {
    return res !== undefined && !(!this.options.returnNull && res === null) && !(!this.options.returnEmptyString && res === '');
  }
  getResource(code, ns, key) {
    let options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
    if (this.i18nFormat && this.i18nFormat.getResource) return this.i18nFormat.getResource(code, ns, key, options);
    return this.resourceStore.getResource(code, ns, key, options);
  }
  getUsedParamsDetails() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    const optionsKeys = ['defaultValue', 'ordinal', 'context', 'replace', 'lng', 'lngs', 'fallbackLng', 'ns', 'keySeparator', 'nsSeparator', 'returnObjects', 'returnDetails', 'joinArrays', 'postProcess', 'interpolation'];
    const useOptionsReplaceForData = options.replace && !isString(options.replace);
    let data = useOptionsReplaceForData ? options.replace : options;
    if (useOptionsReplaceForData && typeof options.count !== 'undefined') {
      data.count = options.count;
    }
    if (this.options.interpolation.defaultVariables) {
      data = {
        ...this.options.interpolation.defaultVariables,
        ...data
      };
    }
    if (!useOptionsReplaceForData) {
      data = {
        ...data
      };
      for (const key of optionsKeys) {
        delete data[key];
      }
    }
    return data;
  }
  static hasDefaultValue(options) {
    const prefix = 'defaultValue';
    for (const option in options) {
      if (Object.prototype.hasOwnProperty.call(options, option) && prefix === option.substring(0, prefix.length) && undefined !== options[option]) {
        return true;
      }
    }
    return false;
  }
}

const capitalize = string => string.charAt(0).toUpperCase() + string.slice(1);
class LanguageUtil {
  constructor(options) {
    this.options = options;
    this.supportedLngs = this.options.supportedLngs || false;
    this.logger = baseLogger.create('languageUtils');
  }
  getScriptPartFromCode(code) {
    code = getCleanedCode(code);
    if (!code || code.indexOf('-') < 0) return null;
    const p = code.split('-');
    if (p.length === 2) return null;
    p.pop();
    if (p[p.length - 1].toLowerCase() === 'x') return null;
    return this.formatLanguageCode(p.join('-'));
  }
  getLanguagePartFromCode(code) {
    code = getCleanedCode(code);
    if (!code || code.indexOf('-') < 0) return code;
    const p = code.split('-');
    return this.formatLanguageCode(p[0]);
  }
  formatLanguageCode(code) {
    if (isString(code) && code.indexOf('-') > -1) {
      if (typeof Intl !== 'undefined' && typeof Intl.getCanonicalLocales !== 'undefined') {
        try {
          let formattedCode = Intl.getCanonicalLocales(code)[0];
          if (formattedCode && this.options.lowerCaseLng) {
            formattedCode = formattedCode.toLowerCase();
          }
          if (formattedCode) return formattedCode;
        } catch (e) {}
      }
      const specialCases = ['hans', 'hant', 'latn', 'cyrl', 'cans', 'mong', 'arab'];
      let p = code.split('-');
      if (this.options.lowerCaseLng) {
        p = p.map(part => part.toLowerCase());
      } else if (p.length === 2) {
        p[0] = p[0].toLowerCase();
        p[1] = p[1].toUpperCase();
        if (specialCases.indexOf(p[1].toLowerCase()) > -1) p[1] = capitalize(p[1].toLowerCase());
      } else if (p.length === 3) {
        p[0] = p[0].toLowerCase();
        if (p[1].length === 2) p[1] = p[1].toUpperCase();
        if (p[0] !== 'sgn' && p[2].length === 2) p[2] = p[2].toUpperCase();
        if (specialCases.indexOf(p[1].toLowerCase()) > -1) p[1] = capitalize(p[1].toLowerCase());
        if (specialCases.indexOf(p[2].toLowerCase()) > -1) p[2] = capitalize(p[2].toLowerCase());
      }
      return p.join('-');
    }
    return this.options.cleanCode || this.options.lowerCaseLng ? code.toLowerCase() : code;
  }
  isSupportedCode(code) {
    if (this.options.load === 'languageOnly' || this.options.nonExplicitSupportedLngs) {
      code = this.getLanguagePartFromCode(code);
    }
    return !this.supportedLngs || !this.supportedLngs.length || this.supportedLngs.indexOf(code) > -1;
  }
  getBestMatchFromCodes(codes) {
    if (!codes) return null;
    let found;
    codes.forEach(code => {
      if (found) return;
      const cleanedLng = this.formatLanguageCode(code);
      if (!this.options.supportedLngs || this.isSupportedCode(cleanedLng)) found = cleanedLng;
    });
    if (!found && this.options.supportedLngs) {
      codes.forEach(code => {
        if (found) return;
        const lngOnly = this.getLanguagePartFromCode(code);
        if (this.isSupportedCode(lngOnly)) return found = lngOnly;
        found = this.options.supportedLngs.find(supportedLng => {
          if (supportedLng === lngOnly) return supportedLng;
          if (supportedLng.indexOf('-') < 0 && lngOnly.indexOf('-') < 0) return;
          if (supportedLng.indexOf('-') > 0 && lngOnly.indexOf('-') < 0 && supportedLng.substring(0, supportedLng.indexOf('-')) === lngOnly) return supportedLng;
          if (supportedLng.indexOf(lngOnly) === 0 && lngOnly.length > 1) return supportedLng;
        });
      });
    }
    if (!found) found = this.getFallbackCodes(this.options.fallbackLng)[0];
    return found;
  }
  getFallbackCodes(fallbacks, code) {
    if (!fallbacks) return [];
    if (typeof fallbacks === 'function') fallbacks = fallbacks(code);
    if (isString(fallbacks)) fallbacks = [fallbacks];
    if (Array.isArray(fallbacks)) return fallbacks;
    if (!code) return fallbacks.default || [];
    let found = fallbacks[code];
    if (!found) found = fallbacks[this.getScriptPartFromCode(code)];
    if (!found) found = fallbacks[this.formatLanguageCode(code)];
    if (!found) found = fallbacks[this.getLanguagePartFromCode(code)];
    if (!found) found = fallbacks.default;
    return found || [];
  }
  toResolveHierarchy(code, fallbackCode) {
    const fallbackCodes = this.getFallbackCodes(fallbackCode || this.options.fallbackLng || [], code);
    const codes = [];
    const addCode = c => {
      if (!c) return;
      if (this.isSupportedCode(c)) {
        codes.push(c);
      } else {
        this.logger.warn(`rejecting language code not found in supportedLngs: ${c}`);
      }
    };
    if (isString(code) && (code.indexOf('-') > -1 || code.indexOf('_') > -1)) {
      if (this.options.load !== 'languageOnly') addCode(this.formatLanguageCode(code));
      if (this.options.load !== 'languageOnly' && this.options.load !== 'currentOnly') addCode(this.getScriptPartFromCode(code));
      if (this.options.load !== 'currentOnly') addCode(this.getLanguagePartFromCode(code));
    } else if (isString(code)) {
      addCode(this.formatLanguageCode(code));
    }
    fallbackCodes.forEach(fc => {
      if (codes.indexOf(fc) < 0) addCode(this.formatLanguageCode(fc));
    });
    return codes;
  }
}

let sets = [{
  lngs: ['ach', 'ak', 'am', 'arn', 'br', 'fil', 'gun', 'ln', 'mfe', 'mg', 'mi', 'oc', 'pt', 'pt-BR', 'tg', 'tl', 'ti', 'tr', 'uz', 'wa'],
  nr: [1, 2],
  fc: 1
}, {
  lngs: ['af', 'an', 'ast', 'az', 'bg', 'bn', 'ca', 'da', 'de', 'dev', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fi', 'fo', 'fur', 'fy', 'gl', 'gu', 'ha', 'hi', 'hu', 'hy', 'ia', 'it', 'kk', 'kn', 'ku', 'lb', 'mai', 'ml', 'mn', 'mr', 'nah', 'nap', 'nb', 'ne', 'nl', 'nn', 'no', 'nso', 'pa', 'pap', 'pms', 'ps', 'pt-PT', 'rm', 'sco', 'se', 'si', 'so', 'son', 'sq', 'sv', 'sw', 'ta', 'te', 'tk', 'ur', 'yo'],
  nr: [1, 2],
  fc: 2
}, {
  lngs: ['ay', 'bo', 'cgg', 'fa', 'ht', 'id', 'ja', 'jbo', 'ka', 'km', 'ko', 'ky', 'lo', 'ms', 'sah', 'su', 'th', 'tt', 'ug', 'vi', 'wo', 'zh'],
  nr: [1],
  fc: 3
}, {
  lngs: ['be', 'bs', 'cnr', 'dz', 'hr', 'ru', 'sr', 'uk'],
  nr: [1, 2, 5],
  fc: 4
}, {
  lngs: ['ar'],
  nr: [0, 1, 2, 3, 11, 100],
  fc: 5
}, {
  lngs: ['cs', 'sk'],
  nr: [1, 2, 5],
  fc: 6
}, {
  lngs: ['csb', 'pl'],
  nr: [1, 2, 5],
  fc: 7
}, {
  lngs: ['cy'],
  nr: [1, 2, 3, 8],
  fc: 8
}, {
  lngs: ['fr'],
  nr: [1, 2],
  fc: 9
}, {
  lngs: ['ga'],
  nr: [1, 2, 3, 7, 11],
  fc: 10
}, {
  lngs: ['gd'],
  nr: [1, 2, 3, 20],
  fc: 11
}, {
  lngs: ['is'],
  nr: [1, 2],
  fc: 12
}, {
  lngs: ['jv'],
  nr: [0, 1],
  fc: 13
}, {
  lngs: ['kw'],
  nr: [1, 2, 3, 4],
  fc: 14
}, {
  lngs: ['lt'],
  nr: [1, 2, 10],
  fc: 15
}, {
  lngs: ['lv'],
  nr: [1, 2, 0],
  fc: 16
}, {
  lngs: ['mk'],
  nr: [1, 2],
  fc: 17
}, {
  lngs: ['mnk'],
  nr: [0, 1, 2],
  fc: 18
}, {
  lngs: ['mt'],
  nr: [1, 2, 11, 20],
  fc: 19
}, {
  lngs: ['or'],
  nr: [2, 1],
  fc: 2
}, {
  lngs: ['ro'],
  nr: [1, 2, 20],
  fc: 20
}, {
  lngs: ['sl'],
  nr: [5, 1, 2, 3],
  fc: 21
}, {
  lngs: ['he', 'iw'],
  nr: [1, 2, 20, 21],
  fc: 22
}];
let _rulesPluralsTypes = {
  1: n => Number(n > 1),
  2: n => Number(n != 1),
  3: n => 0,
  4: n => Number(n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? 1 : 2),
  5: n => Number(n == 0 ? 0 : n == 1 ? 1 : n == 2 ? 2 : n % 100 >= 3 && n % 100 <= 10 ? 3 : n % 100 >= 11 ? 4 : 5),
  6: n => Number(n == 1 ? 0 : n >= 2 && n <= 4 ? 1 : 2),
  7: n => Number(n == 1 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? 1 : 2),
  8: n => Number(n == 1 ? 0 : n == 2 ? 1 : n != 8 && n != 11 ? 2 : 3),
  9: n => Number(n >= 2),
  10: n => Number(n == 1 ? 0 : n == 2 ? 1 : n < 7 ? 2 : n < 11 ? 3 : 4),
  11: n => Number(n == 1 || n == 11 ? 0 : n == 2 || n == 12 ? 1 : n > 2 && n < 20 ? 2 : 3),
  12: n => Number(n % 10 != 1 || n % 100 == 11),
  13: n => Number(n !== 0),
  14: n => Number(n == 1 ? 0 : n == 2 ? 1 : n == 3 ? 2 : 3),
  15: n => Number(n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && (n % 100 < 10 || n % 100 >= 20) ? 1 : 2),
  16: n => Number(n % 10 == 1 && n % 100 != 11 ? 0 : n !== 0 ? 1 : 2),
  17: n => Number(n == 1 || n % 10 == 1 && n % 100 != 11 ? 0 : 1),
  18: n => Number(n == 0 ? 0 : n == 1 ? 1 : 2),
  19: n => Number(n == 1 ? 0 : n == 0 || n % 100 > 1 && n % 100 < 11 ? 1 : n % 100 > 10 && n % 100 < 20 ? 2 : 3),
  20: n => Number(n == 1 ? 0 : n == 0 || n % 100 > 0 && n % 100 < 20 ? 1 : 2),
  21: n => Number(n % 100 == 1 ? 1 : n % 100 == 2 ? 2 : n % 100 == 3 || n % 100 == 4 ? 3 : 0),
  22: n => Number(n == 1 ? 0 : n == 2 ? 1 : (n < 0 || n > 10) && n % 10 == 0 ? 2 : 3)
};
const nonIntlVersions = ['v1', 'v2', 'v3'];
const intlVersions = ['v4'];
const suffixesOrder = {
  zero: 0,
  one: 1,
  two: 2,
  few: 3,
  many: 4,
  other: 5
};
const createRules = () => {
  const rules = {};
  sets.forEach(set => {
    set.lngs.forEach(l => {
      rules[l] = {
        numbers: set.nr,
        plurals: _rulesPluralsTypes[set.fc]
      };
    });
  });
  return rules;
};
class PluralResolver {
  constructor(languageUtils) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    this.languageUtils = languageUtils;
    this.options = options;
    this.logger = baseLogger.create('pluralResolver');
    if ((!this.options.compatibilityJSON || intlVersions.includes(this.options.compatibilityJSON)) && (typeof Intl === 'undefined' || !Intl.PluralRules)) {
      this.options.compatibilityJSON = 'v3';
      this.logger.error('Your environment seems not to be Intl API compatible, use an Intl.PluralRules polyfill. Will fallback to the compatibilityJSON v3 format handling.');
    }
    this.rules = createRules();
    this.pluralRulesCache = {};
  }
  addRule(lng, obj) {
    this.rules[lng] = obj;
  }
  clearCache() {
    this.pluralRulesCache = {};
  }
  getRule(code) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    if (this.shouldUseIntlApi()) {
      const cleanedCode = getCleanedCode(code === 'dev' ? 'en' : code);
      const type = options.ordinal ? 'ordinal' : 'cardinal';
      const cacheKey = JSON.stringify({
        cleanedCode,
        type
      });
      if (cacheKey in this.pluralRulesCache) {
        return this.pluralRulesCache[cacheKey];
      }
      let rule;
      try {
        rule = new Intl.PluralRules(cleanedCode, {
          type
        });
      } catch (err) {
        if (!code.match(/-|_/)) return;
        const lngPart = this.languageUtils.getLanguagePartFromCode(code);
        rule = this.getRule(lngPart, options);
      }
      this.pluralRulesCache[cacheKey] = rule;
      return rule;
    }
    return this.rules[code] || this.rules[this.languageUtils.getLanguagePartFromCode(code)];
  }
  needsPlural(code) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    const rule = this.getRule(code, options);
    if (this.shouldUseIntlApi()) {
      return rule && rule.resolvedOptions().pluralCategories.length > 1;
    }
    return rule && rule.numbers.length > 1;
  }
  getPluralFormsOfKey(code, key) {
    let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
    return this.getSuffixes(code, options).map(suffix => `${key}${suffix}`);
  }
  getSuffixes(code) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    const rule = this.getRule(code, options);
    if (!rule) {
      return [];
    }
    if (this.shouldUseIntlApi()) {
      return rule.resolvedOptions().pluralCategories.sort((pluralCategory1, pluralCategory2) => suffixesOrder[pluralCategory1] - suffixesOrder[pluralCategory2]).map(pluralCategory => `${this.options.prepend}${options.ordinal ? `ordinal${this.options.prepend}` : ''}${pluralCategory}`);
    }
    return rule.numbers.map(number => this.getSuffix(code, number, options));
  }
  getSuffix(code, count) {
    let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
    const rule = this.getRule(code, options);
    if (rule) {
      if (this.shouldUseIntlApi()) {
        return `${this.options.prepend}${options.ordinal ? `ordinal${this.options.prepend}` : ''}${rule.select(count)}`;
      }
      return this.getSuffixRetroCompatible(rule, count);
    }
    this.logger.warn(`no plural rule found for: ${code}`);
    return '';
  }
  getSuffixRetroCompatible(rule, count) {
    const idx = rule.noAbs ? rule.plurals(count) : rule.plurals(Math.abs(count));
    let suffix = rule.numbers[idx];
    if (this.options.simplifyPluralSuffix && rule.numbers.length === 2 && rule.numbers[0] === 1) {
      if (suffix === 2) {
        suffix = 'plural';
      } else if (suffix === 1) {
        suffix = '';
      }
    }
    const returnSuffix = () => this.options.prepend && suffix.toString() ? this.options.prepend + suffix.toString() : suffix.toString();
    if (this.options.compatibilityJSON === 'v1') {
      if (suffix === 1) return '';
      if (typeof suffix === 'number') return `_plural_${suffix.toString()}`;
      return returnSuffix();
    } else if (this.options.compatibilityJSON === 'v2') {
      return returnSuffix();
    } else if (this.options.simplifyPluralSuffix && rule.numbers.length === 2 && rule.numbers[0] === 1) {
      return returnSuffix();
    }
    return this.options.prepend && idx.toString() ? this.options.prepend + idx.toString() : idx.toString();
  }
  shouldUseIntlApi() {
    return !nonIntlVersions.includes(this.options.compatibilityJSON);
  }
}

const deepFindWithDefaults = function (data, defaultData, key) {
  let keySeparator = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : '.';
  let ignoreJSONStructure = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : true;
  let path = getPathWithDefaults(data, defaultData, key);
  if (!path && ignoreJSONStructure && isString(key)) {
    path = deepFind(data, key, keySeparator);
    if (path === undefined) path = deepFind(defaultData, key, keySeparator);
  }
  return path;
};
const regexSafe = val => val.replace(/\$/g, '$$$$');
class Interpolator {
  constructor() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    this.logger = baseLogger.create('interpolator');
    this.options = options;
    this.format = options.interpolation && options.interpolation.format || (value => value);
    this.init(options);
  }
  init() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    if (!options.interpolation) options.interpolation = {
      escapeValue: true
    };
    const {
      escape: escape$1,
      escapeValue,
      useRawValueToEscape,
      prefix,
      prefixEscaped,
      suffix,
      suffixEscaped,
      formatSeparator,
      unescapeSuffix,
      unescapePrefix,
      nestingPrefix,
      nestingPrefixEscaped,
      nestingSuffix,
      nestingSuffixEscaped,
      nestingOptionsSeparator,
      maxReplaces,
      alwaysFormat
    } = options.interpolation;
    this.escape = escape$1 !== undefined ? escape$1 : escape;
    this.escapeValue = escapeValue !== undefined ? escapeValue : true;
    this.useRawValueToEscape = useRawValueToEscape !== undefined ? useRawValueToEscape : false;
    this.prefix = prefix ? regexEscape(prefix) : prefixEscaped || '{{';
    this.suffix = suffix ? regexEscape(suffix) : suffixEscaped || '}}';
    this.formatSeparator = formatSeparator || ',';
    this.unescapePrefix = unescapeSuffix ? '' : unescapePrefix || '-';
    this.unescapeSuffix = this.unescapePrefix ? '' : unescapeSuffix || '';
    this.nestingPrefix = nestingPrefix ? regexEscape(nestingPrefix) : nestingPrefixEscaped || regexEscape('$t(');
    this.nestingSuffix = nestingSuffix ? regexEscape(nestingSuffix) : nestingSuffixEscaped || regexEscape(')');
    this.nestingOptionsSeparator = nestingOptionsSeparator || ',';
    this.maxReplaces = maxReplaces || 1000;
    this.alwaysFormat = alwaysFormat !== undefined ? alwaysFormat : false;
    this.resetRegExp();
  }
  reset() {
    if (this.options) this.init(this.options);
  }
  resetRegExp() {
    const getOrResetRegExp = (existingRegExp, pattern) => {
      if (existingRegExp && existingRegExp.source === pattern) {
        existingRegExp.lastIndex = 0;
        return existingRegExp;
      }
      return new RegExp(pattern, 'g');
    };
    this.regexp = getOrResetRegExp(this.regexp, `${this.prefix}(.+?)${this.suffix}`);
    this.regexpUnescape = getOrResetRegExp(this.regexpUnescape, `${this.prefix}${this.unescapePrefix}(.+?)${this.unescapeSuffix}${this.suffix}`);
    this.nestingRegexp = getOrResetRegExp(this.nestingRegexp, `${this.nestingPrefix}(.+?)${this.nestingSuffix}`);
  }
  interpolate(str, data, lng, options) {
    let match;
    let value;
    let replaces;
    const defaultData = this.options && this.options.interpolation && this.options.interpolation.defaultVariables || {};
    const handleFormat = key => {
      if (key.indexOf(this.formatSeparator) < 0) {
        const path = deepFindWithDefaults(data, defaultData, key, this.options.keySeparator, this.options.ignoreJSONStructure);
        return this.alwaysFormat ? this.format(path, undefined, lng, {
          ...options,
          ...data,
          interpolationkey: key
        }) : path;
      }
      const p = key.split(this.formatSeparator);
      const k = p.shift().trim();
      const f = p.join(this.formatSeparator).trim();
      return this.format(deepFindWithDefaults(data, defaultData, k, this.options.keySeparator, this.options.ignoreJSONStructure), f, lng, {
        ...options,
        ...data,
        interpolationkey: k
      });
    };
    this.resetRegExp();
    const missingInterpolationHandler = options && options.missingInterpolationHandler || this.options.missingInterpolationHandler;
    const skipOnVariables = options && options.interpolation && options.interpolation.skipOnVariables !== undefined ? options.interpolation.skipOnVariables : this.options.interpolation.skipOnVariables;
    const todos = [{
      regex: this.regexpUnescape,
      safeValue: val => regexSafe(val)
    }, {
      regex: this.regexp,
      safeValue: val => this.escapeValue ? regexSafe(this.escape(val)) : regexSafe(val)
    }];
    todos.forEach(todo => {
      replaces = 0;
      while (match = todo.regex.exec(str)) {
        const matchedVar = match[1].trim();
        value = handleFormat(matchedVar);
        if (value === undefined) {
          if (typeof missingInterpolationHandler === 'function') {
            const temp = missingInterpolationHandler(str, match, options);
            value = isString(temp) ? temp : '';
          } else if (options && Object.prototype.hasOwnProperty.call(options, matchedVar)) {
            value = '';
          } else if (skipOnVariables) {
            value = match[0];
            continue;
          } else {
            this.logger.warn(`missed to pass in variable ${matchedVar} for interpolating ${str}`);
            value = '';
          }
        } else if (!isString(value) && !this.useRawValueToEscape) {
          value = makeString(value);
        }
        const safeValue = todo.safeValue(value);
        str = str.replace(match[0], safeValue);
        if (skipOnVariables) {
          todo.regex.lastIndex += value.length;
          todo.regex.lastIndex -= match[0].length;
        } else {
          todo.regex.lastIndex = 0;
        }
        replaces++;
        if (replaces >= this.maxReplaces) {
          break;
        }
      }
    });
    return str;
  }
  nest(str, fc) {
    let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
    let match;
    let value;
    let clonedOptions;
    const handleHasOptions = (key, inheritedOptions) => {
      const sep = this.nestingOptionsSeparator;
      if (key.indexOf(sep) < 0) return key;
      const c = key.split(new RegExp(`${sep}[ ]*{`));
      let optionsString = `{${c[1]}`;
      key = c[0];
      optionsString = this.interpolate(optionsString, clonedOptions);
      const matchedSingleQuotes = optionsString.match(/'/g);
      const matchedDoubleQuotes = optionsString.match(/"/g);
      if (matchedSingleQuotes && matchedSingleQuotes.length % 2 === 0 && !matchedDoubleQuotes || matchedDoubleQuotes.length % 2 !== 0) {
        optionsString = optionsString.replace(/'/g, '"');
      }
      try {
        clonedOptions = JSON.parse(optionsString);
        if (inheritedOptions) clonedOptions = {
          ...inheritedOptions,
          ...clonedOptions
        };
      } catch (e) {
        this.logger.warn(`failed parsing options string in nesting for key ${key}`, e);
        return `${key}${sep}${optionsString}`;
      }
      if (clonedOptions.defaultValue && clonedOptions.defaultValue.indexOf(this.prefix) > -1) delete clonedOptions.defaultValue;
      return key;
    };
    while (match = this.nestingRegexp.exec(str)) {
      let formatters = [];
      clonedOptions = {
        ...options
      };
      clonedOptions = clonedOptions.replace && !isString(clonedOptions.replace) ? clonedOptions.replace : clonedOptions;
      clonedOptions.applyPostProcessor = false;
      delete clonedOptions.defaultValue;
      let doReduce = false;
      if (match[0].indexOf(this.formatSeparator) !== -1 && !/{.*}/.test(match[1])) {
        const r = match[1].split(this.formatSeparator).map(elem => elem.trim());
        match[1] = r.shift();
        formatters = r;
        doReduce = true;
      }
      value = fc(handleHasOptions.call(this, match[1].trim(), clonedOptions), clonedOptions);
      if (value && match[0] === str && !isString(value)) return value;
      if (!isString(value)) value = makeString(value);
      if (!value) {
        this.logger.warn(`missed to resolve ${match[1]} for nesting ${str}`);
        value = '';
      }
      if (doReduce) {
        value = formatters.reduce((v, f) => this.format(v, f, options.lng, {
          ...options,
          interpolationkey: match[1].trim()
        }), value.trim());
      }
      str = str.replace(match[0], value);
      this.regexp.lastIndex = 0;
    }
    return str;
  }
}

const parseFormatStr = formatStr => {
  let formatName = formatStr.toLowerCase().trim();
  const formatOptions = {};
  if (formatStr.indexOf('(') > -1) {
    const p = formatStr.split('(');
    formatName = p[0].toLowerCase().trim();
    const optStr = p[1].substring(0, p[1].length - 1);
    if (formatName === 'currency' && optStr.indexOf(':') < 0) {
      if (!formatOptions.currency) formatOptions.currency = optStr.trim();
    } else if (formatName === 'relativetime' && optStr.indexOf(':') < 0) {
      if (!formatOptions.range) formatOptions.range = optStr.trim();
    } else {
      const opts = optStr.split(';');
      opts.forEach(opt => {
        if (opt) {
          const [key, ...rest] = opt.split(':');
          const val = rest.join(':').trim().replace(/^'+|'+$/g, '');
          const trimmedKey = key.trim();
          if (!formatOptions[trimmedKey]) formatOptions[trimmedKey] = val;
          if (val === 'false') formatOptions[trimmedKey] = false;
          if (val === 'true') formatOptions[trimmedKey] = true;
          if (!isNaN(val)) formatOptions[trimmedKey] = parseInt(val, 10);
        }
      });
    }
  }
  return {
    formatName,
    formatOptions
  };
};
const createCachedFormatter = fn => {
  const cache = {};
  return (val, lng, options) => {
    let optForCache = options;
    if (options && options.interpolationkey && options.formatParams && options.formatParams[options.interpolationkey] && options[options.interpolationkey]) {
      optForCache = {
        ...optForCache,
        [options.interpolationkey]: undefined
      };
    }
    const key = lng + JSON.stringify(optForCache);
    let formatter = cache[key];
    if (!formatter) {
      formatter = fn(getCleanedCode(lng), options);
      cache[key] = formatter;
    }
    return formatter(val);
  };
};
class Formatter {
  constructor() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    this.logger = baseLogger.create('formatter');
    this.options = options;
    this.formats = {
      number: createCachedFormatter((lng, opt) => {
        const formatter = new Intl.NumberFormat(lng, {
          ...opt
        });
        return val => formatter.format(val);
      }),
      currency: createCachedFormatter((lng, opt) => {
        const formatter = new Intl.NumberFormat(lng, {
          ...opt,
          style: 'currency'
        });
        return val => formatter.format(val);
      }),
      datetime: createCachedFormatter((lng, opt) => {
        const formatter = new Intl.DateTimeFormat(lng, {
          ...opt
        });
        return val => formatter.format(val);
      }),
      relativetime: createCachedFormatter((lng, opt) => {
        const formatter = new Intl.RelativeTimeFormat(lng, {
          ...opt
        });
        return val => formatter.format(val, opt.range || 'day');
      }),
      list: createCachedFormatter((lng, opt) => {
        const formatter = new Intl.ListFormat(lng, {
          ...opt
        });
        return val => formatter.format(val);
      })
    };
    this.init(options);
  }
  init(services) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {
      interpolation: {}
    };
    this.formatSeparator = options.interpolation.formatSeparator || ',';
  }
  add(name, fc) {
    this.formats[name.toLowerCase().trim()] = fc;
  }
  addCached(name, fc) {
    this.formats[name.toLowerCase().trim()] = createCachedFormatter(fc);
  }
  format(value, format, lng) {
    let options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
    const formats = format.split(this.formatSeparator);
    if (formats.length > 1 && formats[0].indexOf('(') > 1 && formats[0].indexOf(')') < 0 && formats.find(f => f.indexOf(')') > -1)) {
      const lastIndex = formats.findIndex(f => f.indexOf(')') > -1);
      formats[0] = [formats[0], ...formats.splice(1, lastIndex)].join(this.formatSeparator);
    }
    const result = formats.reduce((mem, f) => {
      const {
        formatName,
        formatOptions
      } = parseFormatStr(f);
      if (this.formats[formatName]) {
        let formatted = mem;
        try {
          const valOptions = options && options.formatParams && options.formatParams[options.interpolationkey] || {};
          const l = valOptions.locale || valOptions.lng || options.locale || options.lng || lng;
          formatted = this.formats[formatName](mem, l, {
            ...formatOptions,
            ...options,
            ...valOptions
          });
        } catch (error) {
          this.logger.warn(error);
        }
        return formatted;
      } else {
        this.logger.warn(`there was no format function for ${formatName}`);
      }
      return mem;
    }, value);
    return result;
  }
}

const removePending = (q, name) => {
  if (q.pending[name] !== undefined) {
    delete q.pending[name];
    q.pendingCount--;
  }
};
class Connector extends EventEmitter {
  constructor(backend, store, services) {
    let options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
    super();
    this.backend = backend;
    this.store = store;
    this.services = services;
    this.languageUtils = services.languageUtils;
    this.options = options;
    this.logger = baseLogger.create('backendConnector');
    this.waitingReads = [];
    this.maxParallelReads = options.maxParallelReads || 10;
    this.readingCalls = 0;
    this.maxRetries = options.maxRetries >= 0 ? options.maxRetries : 5;
    this.retryTimeout = options.retryTimeout >= 1 ? options.retryTimeout : 350;
    this.state = {};
    this.queue = [];
    if (this.backend && this.backend.init) {
      this.backend.init(services, options.backend, options);
    }
  }
  queueLoad(languages, namespaces, options, callback) {
    const toLoad = {};
    const pending = {};
    const toLoadLanguages = {};
    const toLoadNamespaces = {};
    languages.forEach(lng => {
      let hasAllNamespaces = true;
      namespaces.forEach(ns => {
        const name = `${lng}|${ns}`;
        if (!options.reload && this.store.hasResourceBundle(lng, ns)) {
          this.state[name] = 2;
        } else if (this.state[name] < 0) ; else if (this.state[name] === 1) {
          if (pending[name] === undefined) pending[name] = true;
        } else {
          this.state[name] = 1;
          hasAllNamespaces = false;
          if (pending[name] === undefined) pending[name] = true;
          if (toLoad[name] === undefined) toLoad[name] = true;
          if (toLoadNamespaces[ns] === undefined) toLoadNamespaces[ns] = true;
        }
      });
      if (!hasAllNamespaces) toLoadLanguages[lng] = true;
    });
    if (Object.keys(toLoad).length || Object.keys(pending).length) {
      this.queue.push({
        pending,
        pendingCount: Object.keys(pending).length,
        loaded: {},
        errors: [],
        callback
      });
    }
    return {
      toLoad: Object.keys(toLoad),
      pending: Object.keys(pending),
      toLoadLanguages: Object.keys(toLoadLanguages),
      toLoadNamespaces: Object.keys(toLoadNamespaces)
    };
  }
  loaded(name, err, data) {
    const s = name.split('|');
    const lng = s[0];
    const ns = s[1];
    if (err) this.emit('failedLoading', lng, ns, err);
    if (!err && data) {
      this.store.addResourceBundle(lng, ns, data, undefined, undefined, {
        skipCopy: true
      });
    }
    this.state[name] = err ? -1 : 2;
    if (err && data) this.state[name] = 0;
    const loaded = {};
    this.queue.forEach(q => {
      pushPath(q.loaded, [lng], ns);
      removePending(q, name);
      if (err) q.errors.push(err);
      if (q.pendingCount === 0 && !q.done) {
        Object.keys(q.loaded).forEach(l => {
          if (!loaded[l]) loaded[l] = {};
          const loadedKeys = q.loaded[l];
          if (loadedKeys.length) {
            loadedKeys.forEach(n => {
              if (loaded[l][n] === undefined) loaded[l][n] = true;
            });
          }
        });
        q.done = true;
        if (q.errors.length) {
          q.callback(q.errors);
        } else {
          q.callback();
        }
      }
    });
    this.emit('loaded', loaded);
    this.queue = this.queue.filter(q => !q.done);
  }
  read(lng, ns, fcName) {
    let tried = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 0;
    let wait = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : this.retryTimeout;
    let callback = arguments.length > 5 ? arguments[5] : undefined;
    if (!lng.length) return callback(null, {});
    if (this.readingCalls >= this.maxParallelReads) {
      this.waitingReads.push({
        lng,
        ns,
        fcName,
        tried,
        wait,
        callback
      });
      return;
    }
    this.readingCalls++;
    const resolver = (err, data) => {
      this.readingCalls--;
      if (this.waitingReads.length > 0) {
        const next = this.waitingReads.shift();
        this.read(next.lng, next.ns, next.fcName, next.tried, next.wait, next.callback);
      }
      if (err && data && tried < this.maxRetries) {
        setTimeout(() => {
          this.read.call(this, lng, ns, fcName, tried + 1, wait * 2, callback);
        }, wait);
        return;
      }
      callback(err, data);
    };
    const fc = this.backend[fcName].bind(this.backend);
    if (fc.length === 2) {
      try {
        const r = fc(lng, ns);
        if (r && typeof r.then === 'function') {
          r.then(data => resolver(null, data)).catch(resolver);
        } else {
          resolver(null, r);
        }
      } catch (err) {
        resolver(err);
      }
      return;
    }
    return fc(lng, ns, resolver);
  }
  prepareLoading(languages, namespaces) {
    let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
    let callback = arguments.length > 3 ? arguments[3] : undefined;
    if (!this.backend) {
      this.logger.warn('No backend was added via i18next.use. Will not load resources.');
      return callback && callback();
    }
    if (isString(languages)) languages = this.languageUtils.toResolveHierarchy(languages);
    if (isString(namespaces)) namespaces = [namespaces];
    const toLoad = this.queueLoad(languages, namespaces, options, callback);
    if (!toLoad.toLoad.length) {
      if (!toLoad.pending.length) callback();
      return null;
    }
    toLoad.toLoad.forEach(name => {
      this.loadOne(name);
    });
  }
  load(languages, namespaces, callback) {
    this.prepareLoading(languages, namespaces, {}, callback);
  }
  reload(languages, namespaces, callback) {
    this.prepareLoading(languages, namespaces, {
      reload: true
    }, callback);
  }
  loadOne(name) {
    let prefix = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : '';
    const s = name.split('|');
    const lng = s[0];
    const ns = s[1];
    this.read(lng, ns, 'read', undefined, undefined, (err, data) => {
      if (err) this.logger.warn(`${prefix}loading namespace ${ns} for language ${lng} failed`, err);
      if (!err && data) this.logger.log(`${prefix}loaded namespace ${ns} for language ${lng}`, data);
      this.loaded(name, err, data);
    });
  }
  saveMissing(languages, namespace, key, fallbackValue, isUpdate) {
    let options = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : {};
    let clb = arguments.length > 6 && arguments[6] !== undefined ? arguments[6] : () => {};
    if (this.services.utils && this.services.utils.hasLoadedNamespace && !this.services.utils.hasLoadedNamespace(namespace)) {
      this.logger.warn(`did not save key "${key}" as the namespace "${namespace}" was not yet loaded`, 'This means something IS WRONG in your setup. You access the t function before i18next.init / i18next.loadNamespace / i18next.changeLanguage was done. Wait for the callback or Promise to resolve before accessing it!!!');
      return;
    }
    if (key === undefined || key === null || key === '') return;
    if (this.backend && this.backend.create) {
      const opts = {
        ...options,
        isUpdate
      };
      const fc = this.backend.create.bind(this.backend);
      if (fc.length < 6) {
        try {
          let r;
          if (fc.length === 5) {
            r = fc(languages, namespace, key, fallbackValue, opts);
          } else {
            r = fc(languages, namespace, key, fallbackValue);
          }
          if (r && typeof r.then === 'function') {
            r.then(data => clb(null, data)).catch(clb);
          } else {
            clb(null, r);
          }
        } catch (err) {
          clb(err);
        }
      } else {
        fc(languages, namespace, key, fallbackValue, clb, opts);
      }
    }
    if (!languages || !languages[0]) return;
    this.store.addResource(languages[0], namespace, key, fallbackValue);
  }
}

const get = () => ({
  debug: false,
  initImmediate: true,
  ns: ['translation'],
  defaultNS: ['translation'],
  fallbackLng: ['dev'],
  fallbackNS: false,
  supportedLngs: false,
  nonExplicitSupportedLngs: false,
  load: 'all',
  preload: false,
  simplifyPluralSuffix: true,
  keySeparator: '.',
  nsSeparator: ':',
  pluralSeparator: '_',
  contextSeparator: '_',
  partialBundledLanguages: false,
  saveMissing: false,
  updateMissing: false,
  saveMissingTo: 'fallback',
  saveMissingPlurals: true,
  missingKeyHandler: false,
  missingInterpolationHandler: false,
  postProcess: false,
  postProcessPassResolved: false,
  returnNull: false,
  returnEmptyString: true,
  returnObjects: false,
  joinArrays: false,
  returnedObjectHandler: false,
  parseMissingKeyHandler: false,
  appendNamespaceToMissingKey: false,
  appendNamespaceToCIMode: false,
  overloadTranslationOptionHandler: args => {
    let ret = {};
    if (typeof args[1] === 'object') ret = args[1];
    if (isString(args[1])) ret.defaultValue = args[1];
    if (isString(args[2])) ret.tDescription = args[2];
    if (typeof args[2] === 'object' || typeof args[3] === 'object') {
      const options = args[3] || args[2];
      Object.keys(options).forEach(key => {
        ret[key] = options[key];
      });
    }
    return ret;
  },
  interpolation: {
    escapeValue: true,
    format: value => value,
    prefix: '{{',
    suffix: '}}',
    formatSeparator: ',',
    unescapePrefix: '-',
    nestingPrefix: '$t(',
    nestingSuffix: ')',
    nestingOptionsSeparator: ',',
    maxReplaces: 1000,
    skipOnVariables: true
  }
});
const transformOptions = options => {
  if (isString(options.ns)) options.ns = [options.ns];
  if (isString(options.fallbackLng)) options.fallbackLng = [options.fallbackLng];
  if (isString(options.fallbackNS)) options.fallbackNS = [options.fallbackNS];
  if (options.supportedLngs && options.supportedLngs.indexOf('cimode') < 0) {
    options.supportedLngs = options.supportedLngs.concat(['cimode']);
  }
  return options;
};

const noop = () => {};
const bindMemberFunctions = inst => {
  const mems = Object.getOwnPropertyNames(Object.getPrototypeOf(inst));
  mems.forEach(mem => {
    if (typeof inst[mem] === 'function') {
      inst[mem] = inst[mem].bind(inst);
    }
  });
};
class I18n extends EventEmitter {
  constructor() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    let callback = arguments.length > 1 ? arguments[1] : undefined;
    super();
    this.options = transformOptions(options);
    this.services = {};
    this.logger = baseLogger;
    this.modules = {
      external: []
    };
    bindMemberFunctions(this);
    if (callback && !this.isInitialized && !options.isClone) {
      if (!this.options.initImmediate) {
        this.init(options, callback);
        return this;
      }
      setTimeout(() => {
        this.init(options, callback);
      }, 0);
    }
  }
  init() {
    var _this = this;
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    let callback = arguments.length > 1 ? arguments[1] : undefined;
    this.isInitializing = true;
    if (typeof options === 'function') {
      callback = options;
      options = {};
    }
    if (!options.defaultNS && options.defaultNS !== false && options.ns) {
      if (isString(options.ns)) {
        options.defaultNS = options.ns;
      } else if (options.ns.indexOf('translation') < 0) {
        options.defaultNS = options.ns[0];
      }
    }
    const defOpts = get();
    this.options = {
      ...defOpts,
      ...this.options,
      ...transformOptions(options)
    };
    if (this.options.compatibilityAPI !== 'v1') {
      this.options.interpolation = {
        ...defOpts.interpolation,
        ...this.options.interpolation
      };
    }
    if (options.keySeparator !== undefined) {
      this.options.userDefinedKeySeparator = options.keySeparator;
    }
    if (options.nsSeparator !== undefined) {
      this.options.userDefinedNsSeparator = options.nsSeparator;
    }
    const createClassOnDemand = ClassOrObject => {
      if (!ClassOrObject) return null;
      if (typeof ClassOrObject === 'function') return new ClassOrObject();
      return ClassOrObject;
    };
    if (!this.options.isClone) {
      if (this.modules.logger) {
        baseLogger.init(createClassOnDemand(this.modules.logger), this.options);
      } else {
        baseLogger.init(null, this.options);
      }
      let formatter;
      if (this.modules.formatter) {
        formatter = this.modules.formatter;
      } else if (typeof Intl !== 'undefined') {
        formatter = Formatter;
      }
      const lu = new LanguageUtil(this.options);
      this.store = new ResourceStore(this.options.resources, this.options);
      const s = this.services;
      s.logger = baseLogger;
      s.resourceStore = this.store;
      s.languageUtils = lu;
      s.pluralResolver = new PluralResolver(lu, {
        prepend: this.options.pluralSeparator,
        compatibilityJSON: this.options.compatibilityJSON,
        simplifyPluralSuffix: this.options.simplifyPluralSuffix
      });
      if (formatter && (!this.options.interpolation.format || this.options.interpolation.format === defOpts.interpolation.format)) {
        s.formatter = createClassOnDemand(formatter);
        s.formatter.init(s, this.options);
        this.options.interpolation.format = s.formatter.format.bind(s.formatter);
      }
      s.interpolator = new Interpolator(this.options);
      s.utils = {
        hasLoadedNamespace: this.hasLoadedNamespace.bind(this)
      };
      s.backendConnector = new Connector(createClassOnDemand(this.modules.backend), s.resourceStore, s, this.options);
      s.backendConnector.on('*', function (event) {
        for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
          args[_key - 1] = arguments[_key];
        }
        _this.emit(event, ...args);
      });
      if (this.modules.languageDetector) {
        s.languageDetector = createClassOnDemand(this.modules.languageDetector);
        if (s.languageDetector.init) s.languageDetector.init(s, this.options.detection, this.options);
      }
      if (this.modules.i18nFormat) {
        s.i18nFormat = createClassOnDemand(this.modules.i18nFormat);
        if (s.i18nFormat.init) s.i18nFormat.init(this);
      }
      this.translator = new Translator(this.services, this.options);
      this.translator.on('*', function (event) {
        for (var _len2 = arguments.length, args = new Array(_len2 > 1 ? _len2 - 1 : 0), _key2 = 1; _key2 < _len2; _key2++) {
          args[_key2 - 1] = arguments[_key2];
        }
        _this.emit(event, ...args);
      });
      this.modules.external.forEach(m => {
        if (m.init) m.init(this);
      });
    }
    this.format = this.options.interpolation.format;
    if (!callback) callback = noop;
    if (this.options.fallbackLng && !this.services.languageDetector && !this.options.lng) {
      const codes = this.services.languageUtils.getFallbackCodes(this.options.fallbackLng);
      if (codes.length > 0 && codes[0] !== 'dev') this.options.lng = codes[0];
    }
    if (!this.services.languageDetector && !this.options.lng) {
      this.logger.warn('init: no languageDetector is used and no lng is defined');
    }
    const storeApi = ['getResource', 'hasResourceBundle', 'getResourceBundle', 'getDataByLanguage'];
    storeApi.forEach(fcName => {
      this[fcName] = function () {
        return _this.store[fcName](...arguments);
      };
    });
    const storeApiChained = ['addResource', 'addResources', 'addResourceBundle', 'removeResourceBundle'];
    storeApiChained.forEach(fcName => {
      this[fcName] = function () {
        _this.store[fcName](...arguments);
        return _this;
      };
    });
    const deferred = defer();
    const load = () => {
      const finish = (err, t) => {
        this.isInitializing = false;
        if (this.isInitialized && !this.initializedStoreOnce) this.logger.warn('init: i18next is already initialized. You should call init just once!');
        this.isInitialized = true;
        if (!this.options.isClone) this.logger.log('initialized', this.options);
        this.emit('initialized', this.options);
        deferred.resolve(t);
        callback(err, t);
      };
      if (this.languages && this.options.compatibilityAPI !== 'v1' && !this.isInitialized) return finish(null, this.t.bind(this));
      this.changeLanguage(this.options.lng, finish);
    };
    if (this.options.resources || !this.options.initImmediate) {
      load();
    } else {
      setTimeout(load, 0);
    }
    return deferred;
  }
  loadResources(language) {
    let callback = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : noop;
    let usedCallback = callback;
    const usedLng = isString(language) ? language : this.language;
    if (typeof language === 'function') usedCallback = language;
    if (!this.options.resources || this.options.partialBundledLanguages) {
      if (usedLng && usedLng.toLowerCase() === 'cimode' && (!this.options.preload || this.options.preload.length === 0)) return usedCallback();
      const toLoad = [];
      const append = lng => {
        if (!lng) return;
        if (lng === 'cimode') return;
        const lngs = this.services.languageUtils.toResolveHierarchy(lng);
        lngs.forEach(l => {
          if (l === 'cimode') return;
          if (toLoad.indexOf(l) < 0) toLoad.push(l);
        });
      };
      if (!usedLng) {
        const fallbacks = this.services.languageUtils.getFallbackCodes(this.options.fallbackLng);
        fallbacks.forEach(l => append(l));
      } else {
        append(usedLng);
      }
      if (this.options.preload) {
        this.options.preload.forEach(l => append(l));
      }
      this.services.backendConnector.load(toLoad, this.options.ns, e => {
        if (!e && !this.resolvedLanguage && this.language) this.setResolvedLanguage(this.language);
        usedCallback(e);
      });
    } else {
      usedCallback(null);
    }
  }
  reloadResources(lngs, ns, callback) {
    const deferred = defer();
    if (typeof lngs === 'function') {
      callback = lngs;
      lngs = undefined;
    }
    if (typeof ns === 'function') {
      callback = ns;
      ns = undefined;
    }
    if (!lngs) lngs = this.languages;
    if (!ns) ns = this.options.ns;
    if (!callback) callback = noop;
    this.services.backendConnector.reload(lngs, ns, err => {
      deferred.resolve();
      callback(err);
    });
    return deferred;
  }
  use(module) {
    if (!module) throw new Error('You are passing an undefined module! Please check the object you are passing to i18next.use()');
    if (!module.type) throw new Error('You are passing a wrong module! Please check the object you are passing to i18next.use()');
    if (module.type === 'backend') {
      this.modules.backend = module;
    }
    if (module.type === 'logger' || module.log && module.warn && module.error) {
      this.modules.logger = module;
    }
    if (module.type === 'languageDetector') {
      this.modules.languageDetector = module;
    }
    if (module.type === 'i18nFormat') {
      this.modules.i18nFormat = module;
    }
    if (module.type === 'postProcessor') {
      postProcessor.addPostProcessor(module);
    }
    if (module.type === 'formatter') {
      this.modules.formatter = module;
    }
    if (module.type === '3rdParty') {
      this.modules.external.push(module);
    }
    return this;
  }
  setResolvedLanguage(l) {
    if (!l || !this.languages) return;
    if (['cimode', 'dev'].indexOf(l) > -1) return;
    for (let li = 0; li < this.languages.length; li++) {
      const lngInLngs = this.languages[li];
      if (['cimode', 'dev'].indexOf(lngInLngs) > -1) continue;
      if (this.store.hasLanguageSomeTranslations(lngInLngs)) {
        this.resolvedLanguage = lngInLngs;
        break;
      }
    }
  }
  changeLanguage(lng, callback) {
    var _this2 = this;
    this.isLanguageChangingTo = lng;
    const deferred = defer();
    this.emit('languageChanging', lng);
    const setLngProps = l => {
      this.language = l;
      this.languages = this.services.languageUtils.toResolveHierarchy(l);
      this.resolvedLanguage = undefined;
      this.setResolvedLanguage(l);
    };
    const done = (err, l) => {
      if (l) {
        setLngProps(l);
        this.translator.changeLanguage(l);
        this.isLanguageChangingTo = undefined;
        this.emit('languageChanged', l);
        this.logger.log('languageChanged', l);
      } else {
        this.isLanguageChangingTo = undefined;
      }
      deferred.resolve(function () {
        return _this2.t(...arguments);
      });
      if (callback) callback(err, function () {
        return _this2.t(...arguments);
      });
    };
    const setLng = lngs => {
      if (!lng && !lngs && this.services.languageDetector) lngs = [];
      const l = isString(lngs) ? lngs : this.services.languageUtils.getBestMatchFromCodes(lngs);
      if (l) {
        if (!this.language) {
          setLngProps(l);
        }
        if (!this.translator.language) this.translator.changeLanguage(l);
        if (this.services.languageDetector && this.services.languageDetector.cacheUserLanguage) this.services.languageDetector.cacheUserLanguage(l);
      }
      this.loadResources(l, err => {
        done(err, l);
      });
    };
    if (!lng && this.services.languageDetector && !this.services.languageDetector.async) {
      setLng(this.services.languageDetector.detect());
    } else if (!lng && this.services.languageDetector && this.services.languageDetector.async) {
      if (this.services.languageDetector.detect.length === 0) {
        this.services.languageDetector.detect().then(setLng);
      } else {
        this.services.languageDetector.detect(setLng);
      }
    } else {
      setLng(lng);
    }
    return deferred;
  }
  getFixedT(lng, ns, keyPrefix) {
    var _this3 = this;
    const fixedT = function (key, opts) {
      let options;
      if (typeof opts !== 'object') {
        for (var _len3 = arguments.length, rest = new Array(_len3 > 2 ? _len3 - 2 : 0), _key3 = 2; _key3 < _len3; _key3++) {
          rest[_key3 - 2] = arguments[_key3];
        }
        options = _this3.options.overloadTranslationOptionHandler([key, opts].concat(rest));
      } else {
        options = {
          ...opts
        };
      }
      options.lng = options.lng || fixedT.lng;
      options.lngs = options.lngs || fixedT.lngs;
      options.ns = options.ns || fixedT.ns;
      if (options.keyPrefix !== '') options.keyPrefix = options.keyPrefix || keyPrefix || fixedT.keyPrefix;
      const keySeparator = _this3.options.keySeparator || '.';
      let resultKey;
      if (options.keyPrefix && Array.isArray(key)) {
        resultKey = key.map(k => `${options.keyPrefix}${keySeparator}${k}`);
      } else {
        resultKey = options.keyPrefix ? `${options.keyPrefix}${keySeparator}${key}` : key;
      }
      return _this3.t(resultKey, options);
    };
    if (isString(lng)) {
      fixedT.lng = lng;
    } else {
      fixedT.lngs = lng;
    }
    fixedT.ns = ns;
    fixedT.keyPrefix = keyPrefix;
    return fixedT;
  }
  t() {
    return this.translator && this.translator.translate(...arguments);
  }
  exists() {
    return this.translator && this.translator.exists(...arguments);
  }
  setDefaultNamespace(ns) {
    this.options.defaultNS = ns;
  }
  hasLoadedNamespace(ns) {
    let options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    if (!this.isInitialized) {
      this.logger.warn('hasLoadedNamespace: i18next was not initialized', this.languages);
      return false;
    }
    if (!this.languages || !this.languages.length) {
      this.logger.warn('hasLoadedNamespace: i18n.languages were undefined or empty', this.languages);
      return false;
    }
    const lng = options.lng || this.resolvedLanguage || this.languages[0];
    const fallbackLng = this.options ? this.options.fallbackLng : false;
    const lastLng = this.languages[this.languages.length - 1];
    if (lng.toLowerCase() === 'cimode') return true;
    const loadNotPending = (l, n) => {
      const loadState = this.services.backendConnector.state[`${l}|${n}`];
      return loadState === -1 || loadState === 0 || loadState === 2;
    };
    if (options.precheck) {
      const preResult = options.precheck(this, loadNotPending);
      if (preResult !== undefined) return preResult;
    }
    if (this.hasResourceBundle(lng, ns)) return true;
    if (!this.services.backendConnector.backend || this.options.resources && !this.options.partialBundledLanguages) return true;
    if (loadNotPending(lng, ns) && (!fallbackLng || loadNotPending(lastLng, ns))) return true;
    return false;
  }
  loadNamespaces(ns, callback) {
    const deferred = defer();
    if (!this.options.ns) {
      if (callback) callback();
      return Promise.resolve();
    }
    if (isString(ns)) ns = [ns];
    ns.forEach(n => {
      if (this.options.ns.indexOf(n) < 0) this.options.ns.push(n);
    });
    this.loadResources(err => {
      deferred.resolve();
      if (callback) callback(err);
    });
    return deferred;
  }
  loadLanguages(lngs, callback) {
    const deferred = defer();
    if (isString(lngs)) lngs = [lngs];
    const preloaded = this.options.preload || [];
    const newLngs = lngs.filter(lng => preloaded.indexOf(lng) < 0 && this.services.languageUtils.isSupportedCode(lng));
    if (!newLngs.length) {
      if (callback) callback();
      return Promise.resolve();
    }
    this.options.preload = preloaded.concat(newLngs);
    this.loadResources(err => {
      deferred.resolve();
      if (callback) callback(err);
    });
    return deferred;
  }
  dir(lng) {
    if (!lng) lng = this.resolvedLanguage || (this.languages && this.languages.length > 0 ? this.languages[0] : this.language);
    if (!lng) return 'rtl';
    const rtlLngs = ['ar', 'shu', 'sqr', 'ssh', 'xaa', 'yhd', 'yud', 'aao', 'abh', 'abv', 'acm', 'acq', 'acw', 'acx', 'acy', 'adf', 'ads', 'aeb', 'aec', 'afb', 'ajp', 'apc', 'apd', 'arb', 'arq', 'ars', 'ary', 'arz', 'auz', 'avl', 'ayh', 'ayl', 'ayn', 'ayp', 'bbz', 'pga', 'he', 'iw', 'ps', 'pbt', 'pbu', 'pst', 'prp', 'prd', 'ug', 'ur', 'ydd', 'yds', 'yih', 'ji', 'yi', 'hbo', 'men', 'xmn', 'fa', 'jpr', 'peo', 'pes', 'prs', 'dv', 'sam', 'ckb'];
    const languageUtils = this.services && this.services.languageUtils || new LanguageUtil(get());
    return rtlLngs.indexOf(languageUtils.getLanguagePartFromCode(lng)) > -1 || lng.toLowerCase().indexOf('-arab') > 1 ? 'rtl' : 'ltr';
  }
  static createInstance() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    let callback = arguments.length > 1 ? arguments[1] : undefined;
    return new I18n(options, callback);
  }
  cloneInstance() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    let callback = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : noop;
    const forkResourceStore = options.forkResourceStore;
    if (forkResourceStore) delete options.forkResourceStore;
    const mergedOptions = {
      ...this.options,
      ...options,
      ...{
        isClone: true
      }
    };
    const clone = new I18n(mergedOptions);
    if (options.debug !== undefined || options.prefix !== undefined) {
      clone.logger = clone.logger.clone(options);
    }
    const membersToCopy = ['store', 'services', 'language'];
    membersToCopy.forEach(m => {
      clone[m] = this[m];
    });
    clone.services = {
      ...this.services
    };
    clone.services.utils = {
      hasLoadedNamespace: clone.hasLoadedNamespace.bind(clone)
    };
    if (forkResourceStore) {
      clone.store = new ResourceStore(this.store.data, mergedOptions);
      clone.services.resourceStore = clone.store;
    }
    clone.translator = new Translator(clone.services, mergedOptions);
    clone.translator.on('*', function (event) {
      for (var _len4 = arguments.length, args = new Array(_len4 > 1 ? _len4 - 1 : 0), _key4 = 1; _key4 < _len4; _key4++) {
        args[_key4 - 1] = arguments[_key4];
      }
      clone.emit(event, ...args);
    });
    clone.init(mergedOptions, callback);
    clone.translator.options = mergedOptions;
    clone.translator.backendConnector.services.utils = {
      hasLoadedNamespace: clone.hasLoadedNamespace.bind(clone)
    };
    return clone;
  }
  toJSON() {
    return {
      options: this.options,
      store: this.store,
      language: this.language,
      languages: this.languages,
      resolvedLanguage: this.resolvedLanguage
    };
  }
}
const instance = I18n.createInstance();
instance.createInstance = I18n.createInstance;

const translations = {
    en: {
        translation: {
            about: {
                header: "Decky-Undervolt could not be made without these awesome tools:",
                tools: {
                    ryzenadj: "Ryzenadj: Power Management tool for Ryzen APUs made by FlyGoat (LGPL-3.0 license)",
                    steamDeck: "Steam-Deck-Software-Undervolt Pososaku's fork: Easy way to implement per-core undervolt, made by Pososaku (GPL-3.0 License)",
                },
                supportHeader: "But most importantly, Decky-Undervolt could not be made without the support of these amazing people:",
                supporters: {
                    pososaku: "Pososaku (Ew Meh): For making Steam Deck overclocking popular in Russian community and his awesome fork",
                    kigs: "k1gs: For contributing to the project and helping with the development",
                    deadwenk: "deadwenk (Alexey Tarasov): For contributing Steam-Deck-Software-Undervolt and making it easier to use per-core undervolting",
                    foxn: "FoxN: For finding a solution to make software undervolting possible at Steam Deck OLED",
                    robert: "Robert (biddbb): For maintaining overclocking guide",
                    ngnius: "NGnius: For resolving licensing issues",
                    notBullseye: "NotBullseye: For creating plugin logo",
                    community: "Everyone in the Steam Deck OC (@steamdeckoverclock) Telegram community: For their support and feedback",
                },
                footer: {
                    thankYou: "And of course, thank you for using Decky-Undervolt!",
                    madeBy: "Made with ❤️ by BakaDestroyer",
                },
            },
            sidebar: {
                settings: "Settings",
                about: "About",
                title: "Decky-Undervolt",
            },
            settings: {
                useGlobally: "Use Globally",
                useGloballyDescription: "Undervolt will persist even if the game is closed. By default, it turns off when the game is not running.",
                runWithGame: "Run With Game",
                runWithGameDescription: "Undervolt will be applied automatically when the game starts.",
                runAtStartup: "Run at Startup",
                runAtStartupDescription: "Undervolt will be applied automatically when the system starts.",
                timeoutApply: "Timeout Apply",
                timeoutApplyDescription: "The time in seconds to wait before applying the undervolt at startup.",
                resetConfig: "Reset Config",
                resettingConfig: "Resetting Config...",
                saveSettings: "Save Settings",
                savingSettings: "Saving Settings...",
            },
            staticUndervolt: {
                useForCurrentGame: "Use only for {{appName}}?",
                currentGamePlaceholder: "current game",
                noGameRunning: "No game is running, please start a game to use this feature. Undervolting settings will be applied globally.",
                descriptionRunningGame: "Checking this will save the undervolt settings and will apply them only when {{appName}} is running instead of applying it globally.",
                presetManagerButton: "Preset Manager",
                actionButtons: {
                    saveAndApply: "Save & Apply",
                    applying: "Applying...",
                    reset: "Reset",
                    disable: "Disable",
                },
            },
            presetManager: {
                label: "Preset Manager",
                presetSelector: {
                    none: "None",
                    label: "Preset to edit:",
                },
                actionButtons: {
                    saving: "Saving...",
                    savePreset: "Save Preset",
                    deleteConfirm: "Really delete?",
                    delete: "Delete",
                },
                backButton: "Back",
            },
            coreSlider: "Core {{coreNumber}}",
            presetControls: {
                useTimeout: "Use timeout for this preset?",
                timeoutDescription: "Checking this will apply the undervolt after some time when {{label}} is opened. Might be useful for games with launchers.",
                timeoutLabel: "Timeout in seconds",
            },
            undervoltStatus: {
                status: "Undervolt Status: ",
                enabled: "Enabled",
                disabled: "Disabled",
                error: "Error",
                scheduled: "Scheduled",
            },
        },
    },
    ru: {
        translation: {
            about: {
                header: "Decky-Undervolt не мог бы быть создан без этих замечательных инструментов:",
                tools: {
                    ryzenadj: "Ryzenadj: Инструмент управления питанием для Ryzen APU от FlyGoat (лицензия LGPL-3.0)",
                    steamDeck: "Steam-Deck-Software-Undervolt, форк Pososaku: Удобный способ реализовать поядерный андервольтинг, созданный Pososaku (лицензия GPL-3.0)",
                },
                supportHeader: "Но, самое главное, Decky-Undervolt не мог бы быть создан без поддержки этих потрясающих людей:",
                supporters: {
                    pososaku: "Pososaku (Ew Meh): За популяризацию разгона Steam Deck в российском сообществе и его замечательный форк",
                    kigs: "k1gs: За вклад в проект и помощь в разработке",
                    deadwenk: "deadwenk (Алексей Тарасов): За вклад в Steam-Deck-Software-Undervolt и упрощение настройки поядерного андервольтинга",
                    foxn: "FoxN: За решение, позволившее программный андервольтинг на Steam Deck OLED",
                    robert: "Robert (biddbb): За поддержку гайда по разгону",
                    ngnius: "NGnius: За решение вопросов лицензирования",
                    notBullseye: "NotBullseye: За создание логотипа плагина",
                    community: "Всем участникам сообщества Steam Deck OC (@steamdeckoverclock) в Telegram: За их поддержку и обратную связь",
                },
                footer: {
                    thankYou: "И, конечно же, спасибо за использование Decky-Undervolt!",
                    madeBy: "Создано с ❤️ BakaDestroyer",
                },
            },
            sidebar: {
                settings: "Настройки",
                about: "О плагине",
                title: "Decky-Undervolt",
            },
            settings: {
                useGlobally: "Использовать глобально",
                useGloballyDescription: "Андервольтинг будет сохраняться даже после закрытия игры. По умолчанию он отключается, если игра не запущена.",
                runWithGame: "Включать с игрой",
                runWithGameDescription: "Андервольтинг будет автоматически применяться при запуске игры.",
                runAtStartup: "Включать при запуске системы",
                runAtStartupDescription: "Андервольтинг будет автоматически применяться при включении системы.",
                timeoutApply: "Применение с задержкой",
                timeoutApplyDescription: "Задержка в секундах перед применением андервольтинга при старте системы.",
                resetConfig: "Сбросить настройки",
                resettingConfig: "Сброс настроек...",
                saveSettings: "Сохранить настройки",
                savingSettings: "Сохранение настроек...",
            },
            staticUndervolt: {
                useForCurrentGame: "Использовать только для {{appName}}?",
                currentGamePlaceholder: "текущей игры",
                noGameRunning: "Игра не запущена. Запустите игру, чтобы использовать эту функцию. Настройки андервольтинга будут применены глобально.",
                descriptionRunningGame: "Выбор этого параметра сохранит настройки андервольтинга и будет применять их только при запуске {{appName}}, а не глобально.",
                presetManagerButton: "Менеджер пресетов",
                actionButtons: {
                    saveAndApply: "Сохранить и применить",
                    applying: "Применение...",
                    reset: "Сбросить",
                    disable: "Отключить",
                },
            },
            presetManager: {
                label: "Менеджер пресетов",
                presetSelector: {
                    none: "Нет",
                    label: "Пресет для редактирования:",
                },
                actionButtons: {
                    saving: "Сохранение...",
                    savePreset: "Сохранить пресет",
                    deleteConfirm: "Удалить пресет?",
                    delete: "Удалить",
                },
                backButton: "Назад",
            },
            coreSlider: "Ядро {{coreNumber}}",
            presetControls: {
                useTimeout: "Использовать задержку для этого пресета?",
                timeoutDescription: "Выбор этого параметра применит андервольтинг через некоторое время после запуска {{label}}. Может быть полезно для игр с лаунчерами.",
                timeoutLabel: "Задержка (в секундах)",
            },
            undervoltStatus: {
                status: "Статус андервольтинга: ",
                enabled: "Включено",
                disabled: "Отключено",
                error: "Ошибка",
                scheduled: "Запланировано",
            },
        },
    },
    uk: {
        translation: {
            about: {
                header: "Decky-Undervolt не міг би бути створений без цих чудових інструментів:",
                tools: {
                    ryzenadj: "Ryzenadj: Інструмент керування живленням для Ryzen APU від FlyGoat (ліцензія LGPL-3.0)",
                    steamDeck: "Steam-Deck-Software-Undervolt, форк Pososaku: Зручний спосіб реалізувати поядерний андервольтинг, створений Pososaku (ліцензія GPL-3.0)",
                },
                supportHeader: "Але найважливіше, Decky-Undervolt не міг би існувати без підтримки цих дивовижних людей:",
                supporters: {
                    kigs: "k1gs: За внесок у проєкт та допомогу у розробці",
                    pososaku: "Pososaku (Ew Meh): За популяризацію розгону Steam Deck у російській спільноті та його чудовий форк",
                    deadwenk: "deadwenk (Олексій Тарасов): За вклад у Steam-Deck-Software-Undervolt та спрощення налаштування поядерного андервольтингу",
                    foxn: "FoxN: За рішення, яке дозволило програмний андервольтинг для Steam Deck OLED",
                    robert: "Robert (biddbb): За підтримку гайду з розгону",
                    ngnius: "NGnius: За вирішення питань ліцензування",
                    notBullseye: "NotBullseye: За створення логотипу плагіна",
                    community: "Усім учасникам спільноти Steam Deck OC (@steamdeckoverclock) у Telegram: За їхню підтримку та відгуки",
                },
                footer: {
                    thankYou: "І, звісно, дякуємо за використання Decky-Undervolt!",
                    madeBy: "Створено з ❤️ BakaDestroyer",
                },
            },
            sidebar: {
                settings: "Налаштування",
                about: "Про плагін",
                title: "Decky-Undervolt",
            },
            settings: {
                useGlobally: "Використовувати глобально",
                useGloballyDescription: "Андервольтинг буде зберігатися навіть після закриття гри. За замовчуванням він вимикається, якщо гра не запущена.",
                runWithGame: "Увімкнути з грою",
                runWithGameDescription: "Андервольтинг буде автоматично застосовуватися під час запуску гри.",
                runAtStartup: "Увімкнути при запуску системи",
                runAtStartupDescription: "Андервольтинг буде автоматично застосовуватися при увімкненні системи.",
                timeoutApply: "Застосувати із затримкою",
                timeoutApplyDescription: "Час у секундах, через який буде застосовано андервольтинг після запуску системи.",
                resetConfig: "Скинути налаштування",
                resettingConfig: "Скидання налаштувань...",
                saveSettings: "Зберегти налаштування",
                savingSettings: "Збереження налаштувань...",
            },
            staticUndervolt: {
                useForCurrentGame: "Використовувати лише для {{appName}}?",
                currentGamePlaceholder: "поточної гри",
                noGameRunning: "Жодна гра не запущена. Запустіть гру, щоб скористатися цією функцією. Налаштування андервольтингу будуть застосовані глобально.",
                descriptionRunningGame: "Вибір цього параметра збереже налаштування андервольтингу і застосовуватиме їх тільки під час запуску {{appName}}, а не глобально.",
                presetManagerButton: "Менеджер пресетів",
                actionButtons: {
                    saveAndApply: "Зберегти та застосувати",
                    applying: "Застосування...",
                    reset: "Скинути",
                    disable: "Вимкнути",
                },
            },
            presetManager: {
                label: "Менеджер пресетів",
                presetSelector: {
                    none: "Немає",
                    label: "Пресет для редагування:",
                },
                actionButtons: {
                    saving: "Збереження...",
                    savePreset: "Зберегти пресет",
                    deleteConfirm: "Видалити пресет?",
                    delete: "Видалити",
                },
                backButton: "Назад",
            },
            coreSlider: "Ядро {{coreNumber}}",
            presetControls: {
                useTimeout: "Використовувати затримку для цього пресета?",
                timeoutDescription: "Вибір цього параметра застосує андервольтинг через певний час після запуску {{label}}. Може бути корисно для ігор із лаунчерами.",
                timeoutLabel: "Затримка (у секундах)",
            },
            undervoltStatus: {
                status: "Стан андервольтингу: ",
                enabled: "Увімкнено",
                disabled: "Вимкнено",
                error: "Помилка",
                scheduled: "Заплановано",
            },
        },
    },
    cz: {
        translation: {
            about: {
                header: "Decky-Undervolt by nemohl vzniknout bez těchto skvělých nástrojů:",
                tools: {
                    ryzenadj: "Ryzenadj: Nástroj pro správu výkonu pro Ryzen APU od FlyGoat (licence LGPL-3.0)",
                    steamDeck: "Steam-Deck-Software-Undervolt, fork od Pososaku: Snadný způsob implementace undervoltingu na jednotlivých jádrech, vytvořeno Pososaku (licence GPL-3.0)",
                },
                supportHeader: "Ale především, Decky-Undervolt by nevznikl bez podpory těchto úžasných lidí:",
                supporters: {
                    pososaku: "Pososaku (Ew Meh): Za popularizaci přetaktování Steam Decku v ruské komunitě a jeho skvělý fork",
                    kigs: "k1gs: Za přispění do projektu a pomoc s vývojem",
                    deadwenk: "deadwenk (Alexey Tarasov): Za příspěvky do Steam-Deck-Software-Undervolt a zjednodušení konfigurace undervoltingu na jednotlivých jádrech",
                    foxn: "FoxN: Za nalezení řešení umožňujícího softwarový undervolting na Steam Deck OLED",
                    robert: "Robert (biddbb): Za udržování průvodce přetaktováním",
                    ngnius: "NGnius: Za řešení licenčních problémů",
                    notBullseye: "NotBullseye: Za vytvoření loga pluginu",
                    community: "Všem členům komunity Steam Deck OC (@steamdeckoverclock) na Telegramu: Za jejich podporu a zpětnou vazbu",
                },
                footer: {
                    thankYou: "A samozřejmě děkujeme za používání Decky-Undervolt!",
                    madeBy: "Vytvořeno s ❤️ BakaDestroyer",
                },
            },
            sidebar: {
                settings: "Nastavení",
                about: "O pluginu",
                title: "Decky-Undervolt",
            },
            settings: {
                useGlobally: "Používat globálně",
                useGloballyDescription: "Undervolting zůstane aktivní i po zavření hry. Ve výchozím nastavení se vypíná, když hra neběží.",
                runWithGame: "Spustit s hrou",
                runWithGameDescription: "Undervolting se automaticky aplikuje při spuštění hry.",
                runAtStartup: "Spustit při startu systému",
                runAtStartupDescription: "Undervolting se automaticky aplikuje při spuštění systému.",
                timeoutApply: "Aplikovat se zpožděním",
                timeoutApplyDescription: "Čas v sekundách, po kterém se undervolting aplikuje při spuštění systému.",
                resetConfig: "Obnovit nastavení",
                resettingConfig: "Obnovování nastavení...",
                saveSettings: "Uložit nastavení",
                savingSettings: "Ukládání nastavení...",
            },
            staticUndervolt: {
                useForCurrentGame: "Použít pouze pro {{appName}}?",
                currentGamePlaceholder: "aktuální hru",
                noGameRunning: "Žádná hra neběží. Spusťte hru, abyste mohli použít tuto funkci. Nastavení undervoltingu bude použito globálně.",
                descriptionRunningGame: "Zaškrtnutí tohoto políčka uloží nastavení undervoltingu a aplikuje je pouze při spuštění {{appName}}, místo aby se aplikovala globálně.",
                presetManagerButton: "Správce profilů",
                actionButtons: {
                    saveAndApply: "Uložit a aplikovat",
                    applying: "Aplikuje se...",
                    reset: "Obnovit",
                    disable: "Zakázat",
                },
            },
            presetManager: {
                label: "Správce profilů",
                presetSelector: {
                    none: "Žádný",
                    label: "Profil k úpravě:",
                },
                actionButtons: {
                    saving: "Ukládání...",
                    savePreset: "Uložit profil",
                    deleteConfirm: "Opravdu odstranit?",
                    delete: "Odstranit",
                },
                backButton: "Zpět",
            },
            coreSlider: "Jádro {{coreNumber}}",
            presetControls: {
                useTimeout: "Použít zpoždění pro tento profil?",
                timeoutDescription: "Zaškrtnutím tohoto políčka se undervolting aplikuje po určité době od spuštění {{label}}. Může být užitečné pro hry se spouštěčem.",
                timeoutLabel: "Zpoždění v sekundách",
            },
            undervoltStatus: {
                status: "Stav undervoltingu: ",
                enabled: "Povoleno",
                disabled: "Zakázáno",
                error: "Chyba",
                scheduled: "Naplánováno",
            },
        },
    },
};

instance.use(initReactI18next).init({
    resources: translations,
    lng: navigator.language.split("-")[0],
    fallbackLng: "en",
    interpolation: {
        escapeValue: false,
    },
});

instance.t("en");
function Content() {
    return (window.SP_REACT.createElement(DFL.PanelSection, null,
        window.SP_REACT.createElement(UndervoltSection, null)));
}
function TitleView() {
    const handleNavigate = () => {
        DFL.Navigation.CloseSideMenus();
        DFL.Navigation.Navigate("/decky-undervolt");
    };
    return (window.SP_REACT.createElement("div", { style: {
            display: "flex",
            justifyContent: "space-between",
            width: "100%",
        } },
        window.SP_REACT.createElement("span", { style: { fontSize: 20, flex: 1 } }, "Decky-Undervolt"),
        window.SP_REACT.createElement(DFL.DialogButton, { style: {
                height: "28px",
                width: "40px",
                minWidth: 0,
                padding: "10px 12px",
            }, onClick: () => handleNavigate() },
            window.SP_REACT.createElement(FaCog, { style: { marginTop: "-4px", display: "block" } }))));
}
var index = DFL.definePlugin(() => {
    routerHook.addRoute("/decky-undervolt", () => (window.SP_REACT.createElement(Provider, null,
        window.SP_REACT.createElement(Pages, null))));
    const initialState = {
        gymdeckRunning: false,
        isDynamic: false,
        dynamicSettings: {
            cores: [
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
                { manualPoints: [], maximumValue: 100, minimumValue: 0, threshold: 0 },
            ],
            strategy: 'DEFAULT',
            sampleInterval: 50000,
        },
        runningAppName: null,
        runningAppId: null,
        status: "Disabled",
        cores: [5, 5, 5, 5],
        currentPreset: null,
        presets: [],
        settings: {
            isGlobal: false,
            runAtStartup: false,
            isRunAutomatically: false,
            timeoutApply: 15,
        },
        globalCores: []
    };
    const api = getApiInstance(initialState);
    const handleServerEvent = (serverEvent) => {
        return api.handleServerEvent(serverEvent);
    };
    api.init();
    addEventListener("server_event", handleServerEvent);
    return {
        alwaysRender: true,
        titleView: window.SP_REACT.createElement(TitleView, null),
        title: window.SP_REACT.createElement("div", null, "Decky-Undervolt"),
        content: (window.SP_REACT.createElement(Provider, null,
            window.SP_REACT.createElement(Content, null))),
        icon: window.SP_REACT.createElement(FaFire, null),
        onDismount: () => {
            routerHook.removeRoute("/decky-undervolt");
            removeEventListener("server_event", handleServerEvent);
            api.destroy();
        },
    };
});

export { index as default };
//# sourceMappingURL=index.js.map
