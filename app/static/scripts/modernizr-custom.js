/*! modernizr 3.6.0 (Custom Build) | MIT *
 * https://modernizr.com/download/?-audio-cookies-cssvhunit-eventlistener-fullscreen-inlinesvg-inputtypes-json-ligatures-postmessage-setclasses !*/
! function(e, t, n) {
  function r(e, t) {
    return typeof e === t
  }

  function i() {
    var e, t, n, i, o, s, a;
    for (var l in w)
      if (w.hasOwnProperty(l)) {
        if (e = [], t = w[l], t.name && (e.push(t.name.toLowerCase()), t.options && t.options.aliases && t.options.aliases.length))
          for (n = 0; n < t.options.aliases.length; n++) e.push(t.options.aliases[n].toLowerCase());
        for (i = r(t.fn, "function") ? t.fn() : t.fn, o = 0; o < e.length; o++) s = e[o], a = s.split("."), 1 === a.length ? Modernizr[a[0]] = i : (!Modernizr[a[0]] || Modernizr[a[0]] instanceof Boolean || (Modernizr[a[0]] = new Boolean(Modernizr[a[0]])), Modernizr[a[0]][a[1]] = i), S.push((i ? "" : "no-") + a.join("-"))
      }
  }

  function o(e) {
    var t = x.className,
      n = Modernizr._config.classPrefix || "";
    if (b && (t = t.baseVal), Modernizr._config.enableJSClass) {
      var r = new RegExp("(^|\\s)" + n + "no-js(\\s|$)");
      t = t.replace(r, "$1" + n + "js$2")
    }
    Modernizr._config.enableClasses && (t += " " + n + e.join(" " + n), b ? x.className.baseVal = t : x.className = t)
  }

  function s() {
    return "function" != typeof t.createElement ? t.createElement(arguments[0]) : b ? t.createElementNS.call(t, "http://www.w3.org/2000/svg", arguments[0]) : t.createElement.apply(t, arguments)
  }

  function a(e) {
    return e.replace(/([a-z])-([a-z])/g, function(e, t, n) {
      return t + n.toUpperCase()
    }).replace(/^-/, "")
  }

  function l(e, t) {
    return !!~("" + e).indexOf(t)
  }

  function u(e, t) {
    return function() {
      return e.apply(t, arguments)
    }
  }

  function c(e, t, n) {
    var i;
    for (var o in e)
      if (e[o] in t) return n === !1 ? e[o] : (i = t[e[o]], r(i, "function") ? u(i, n || t) : i);
    return !1
  }

  function f(e) {
    return e.replace(/([A-Z])/g, function(e, t) {
      return "-" + t.toLowerCase()
    }).replace(/^ms-/, "-ms-")
  }

  function d(t, n, r) {
    var i;
    if ("getComputedStyle" in e) {
      i = getComputedStyle.call(e, t, n);
      var o = e.console;
      if (null !== i) r && (i = i.getPropertyValue(r));
      else if (o) {
        var s = o.error ? "error" : "log";
        o[s].call(o, "getComputedStyle returning null, its possible modernizr test results are inaccurate")
      }
    } else i = !n && t.currentStyle && t.currentStyle[r];
    return i
  }

  function p() {
    var e = t.body;
    return e || (e = s(b ? "svg" : "body"), e.fake = !0), e
  }

  function y(e, n, r, i) {
    var o, a, l, u, c = "modernizr",
      f = s("div"),
      d = p();
    if (parseInt(r, 10))
      for (; r--;) l = s("div"), l.id = i ? i[r] : c + (r + 1), f.appendChild(l);
    return o = s("style"), o.type = "text/css", o.id = "s" + c, (d.fake ? d : f).appendChild(o), d.appendChild(f), o.styleSheet ? o.styleSheet.cssText = e : o.appendChild(t.createTextNode(e)), f.id = c, d.fake && (d.style.background = "", d.style.overflow = "hidden", u = x.style.overflow, x.style.overflow = "hidden", x.appendChild(d)), a = n(f, e), d.fake ? (d.parentNode.removeChild(d), x.style.overflow = u, x.offsetHeight) : f.parentNode.removeChild(f), !!a
  }

  function m(t, r) {
    var i = t.length;
    if ("CSS" in e && "supports" in e.CSS) {
      for (; i--;)
        if (e.CSS.supports(f(t[i]), r)) return !0;
      return !1
    }
    if ("CSSSupportsRule" in e) {
      for (var o = []; i--;) o.push("(" + f(t[i]) + ":" + r + ")");
      return o = o.join(" or "), y("@supports (" + o + ") { #modernizr { position: absolute; } }", function(e) {
        return "absolute" == d(e, null, "position")
      })
    }
    return n
  }

  function v(e, t, i, o) {
    function u() {
      f && (delete A.style, delete A.modElem)
    }
    if (o = r(o, "undefined") ? !1 : o, !r(i, "undefined")) {
      var c = m(e, i);
      if (!r(c, "undefined")) return c
    }
    for (var f, d, p, y, v, g = ["modernizr", "tspan", "samp"]; !A.style && g.length;) f = !0, A.modElem = s(g.shift()), A.style = A.modElem.style;
    for (p = e.length, d = 0; p > d; d++)
      if (y = e[d], v = A.style[y], l(y, "-") && (y = a(y)), A.style[y] !== n) {
        if (o || r(i, "undefined")) return u(), "pfx" == t ? y : !0;
        try {
          A.style[y] = i
        } catch (h) {}
        if (A.style[y] != v) return u(), "pfx" == t ? y : !0
      }
    return u(), !1
  }

  function g(e, t, n, i, o) {
    var s = e.charAt(0).toUpperCase() + e.slice(1),
      a = (e + " " + N.join(s + " ") + s).split(" ");
    return r(t, "string") || r(t, "undefined") ? v(a, t, i, o) : (a = (e + " " + $.join(s + " ") + s).split(" "), c(a, t, n))
  }

  function h(e, t, r) {
    return g(e, n, n, t, r)
  }

  function C(e, t) {
    return e - 1 === t || e === t || e + 1 === t
  }
  var S = [],
    w = [],
    T = {
      _version: "3.6.0",
      _config: {
        classPrefix: "",
        enableClasses: !0,
        enableJSClass: !0,
        usePrefixes: !0
      },
      _q: [],
      on: function(e, t) {
        var n = this;
        setTimeout(function() {
          t(n[e])
        }, 0)
      },
      addTest: function(e, t, n) {
        w.push({
          name: e,
          fn: t,
          options: n
        })
      },
      addAsyncTest: function(e) {
        w.push({
          name: null,
          fn: e
        })
      }
    },
    Modernizr = function() {};
  Modernizr.prototype = T, Modernizr = new Modernizr, Modernizr.addTest("cookies", function() {
    try {
      t.cookie = "cookietest=1";
      var e = -1 != t.cookie.indexOf("cookietest=");
      return t.cookie = "cookietest=1; expires=Thu, 01-Jan-1970 00:00:01 GMT", e
    } catch (n) {
      return !1
    }
  }), Modernizr.addTest("eventlistener", "addEventListener" in e), Modernizr.addTest("json", "JSON" in e && "parse" in JSON && "stringify" in JSON), Modernizr.addTest("postmessage", "postMessage" in e);
  var x = t.documentElement,
    b = "svg" === x.nodeName.toLowerCase();
  Modernizr.addTest("audio", function() {
    var e = s("audio"),
      t = !1;
    try {
      t = !!e.canPlayType, t && (t = new Boolean(t), t.ogg = e.canPlayType('audio/ogg; codecs="vorbis"').replace(/^no$/, ""), t.mp3 = e.canPlayType('audio/mpeg; codecs="mp3"').replace(/^no$/, ""), t.opus = e.canPlayType('audio/ogg; codecs="opus"') || e.canPlayType('audio/webm; codecs="opus"').replace(/^no$/, ""), t.wav = e.canPlayType('audio/wav; codecs="1"').replace(/^no$/, ""), t.m4a = (e.canPlayType("audio/x-m4a;") || e.canPlayType("audio/aac;")).replace(/^no$/, ""))
    } catch (n) {}
    return t
  }), Modernizr.addTest("inlinesvg", function() {
    var e = s("div");
    return e.innerHTML = "<svg/>", "http://www.w3.org/2000/svg" == ("undefined" != typeof SVGRect && e.firstChild && e.firstChild.namespaceURI)
  });
  var _ = s("input"),
    P = "search tel url email datetime date month week time datetime-local number range color".split(" "),
    k = {};
  Modernizr.inputtypes = function(e) {
    for (var r, i, o, s = e.length, a = "1)", l = 0; s > l; l++) _.setAttribute("type", r = e[l]), o = "text" !== _.type && "style" in _, o && (_.value = a, _.style.cssText = "position:absolute;visibility:hidden;", /^range$/.test(r) && _.style.WebkitAppearance !== n ? (x.appendChild(_), i = t.defaultView, o = i.getComputedStyle && "textfield" !== i.getComputedStyle(_, null).WebkitAppearance && 0 !== _.offsetHeight, x.removeChild(_)) : /^(search|tel)$/.test(r) || (o = /^(url|email)$/.test(r) ? _.checkValidity && _.checkValidity() === !1 : _.value != a)), k[e[l]] = !!o;
    return k
  }(P);
  var E = "Moz O ms Webkit",
    N = T._config.usePrefixes ? E.split(" ") : [];
  T._cssomPrefixes = N;
  var z = function(t) {
    var r, i = prefixes.length,
      o = e.CSSRule;
    if ("undefined" == typeof o) return n;
    if (!t) return !1;
    if (t = t.replace(/^@/, ""), r = t.replace(/-/g, "_").toUpperCase() + "_RULE", r in o) return "@" + t;
    for (var s = 0; i > s; s++) {
      var a = prefixes[s],
        l = a.toUpperCase() + "_" + r;
      if (l in o) return "@-" + a.toLowerCase() + "-" + t
    }
    return !1
  };
  T.atRule = z;
  var $ = T._config.usePrefixes ? E.toLowerCase().split(" ") : [];
  T._domPrefixes = $;
  var O = {
    elem: s("modernizr")
  };
  Modernizr._q.push(function() {
    delete O.elem
  });
  var A = {
    style: O.elem.style
  };
  Modernizr._q.unshift(function() {
    delete A.style
  }), T.testAllProps = g;
  var L = T.prefixed = function(e, t, n) {
    return 0 === e.indexOf("@") ? z(e) : (-1 != e.indexOf("-") && (e = a(e)), t ? g(e, t, n) : g(e, "pfx"))
  };
  Modernizr.addTest("fullscreen", !(!L("exitFullscreen", t, !1) && !L("cancelFullScreen", t, !1))), T.testAllProps = h, Modernizr.addTest("ligatures", h("fontFeatureSettings", '"liga" 1'));
  var j = T.testStyles = y;
  j("#modernizr { height: 50vh; }", function(t) {
    var n = parseInt(e.innerHeight / 2, 10),
      r = parseInt(d(t, null, "height"), 10);
    Modernizr.addTest("cssvhunit", C(r, n))
  }), i(), o(S), delete T.addTest, delete T.addAsyncTest;
  for (var R = 0; R < Modernizr._q.length; R++) Modernizr._q[R]();
  e.Modernizr = Modernizr
}(window, document);
