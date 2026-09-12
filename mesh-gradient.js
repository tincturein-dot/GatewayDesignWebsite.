(function () {
  "use strict";

  var VERT = [
    "attribute vec2 a_pos;",
    "varying vec2 v_uv;",
    "void main(){ v_uv = a_pos * 0.5 + 0.5; gl_Position = vec4(a_pos, 0.0, 1.0); }"
  ].join("\n");

  var FRAG = [
    "precision highp float;",
    "varying vec2 v_uv;",
    "uniform float u_time;",
    "uniform vec2 u_res;",
    "uniform vec3 c1; uniform vec3 c2; uniform vec3 c3; uniform vec3 c4;",
    // Ashima simplex noise
    "vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}",
    "vec2 mod289(vec2 x){return x-floor(x*(1.0/289.0))*289.0;}",
    "vec3 permute(vec3 x){return mod289(((x*34.0)+1.0)*x);}",
    "float snoise(vec2 v){",
    "  const vec4 C=vec4(0.211324865405187,0.366025403784439,-0.577350269189626,0.024390243902439);",
    "  vec2 i=floor(v+dot(v,C.yy));",
    "  vec2 x0=v-i+dot(i,C.xx);",
    "  vec2 i1=(x0.x>x0.y)?vec2(1.0,0.0):vec2(0.0,1.0);",
    "  vec4 x12=x0.xyxy+C.xxzz; x12.xy-=i1;",
    "  i=mod289(i);",
    "  vec3 p=permute(permute(i.y+vec3(0.0,i1.y,1.0))+i.x+vec3(0.0,i1.x,1.0));",
    "  vec3 m=max(0.5-vec3(dot(x0,x0),dot(x12.xy,x12.xy),dot(x12.zw,x12.zw)),0.0);",
    "  m=m*m; m=m*m;",
    "  vec3 x=2.0*fract(p*C.www)-1.0;",
    "  vec3 h=abs(x)-0.5;",
    "  vec3 ox=floor(x+0.5);",
    "  vec3 a0=x-ox;",
    "  m*=1.79284291400159-0.85373472095314*(a0*a0+h*h);",
    "  vec3 g;",
    "  g.x=a0.x*x0.x+h.x*x0.y;",
    "  g.yz=a0.yz*x12.xz+h.yz*x12.yw;",
    "  return 130.0*dot(m,g);",
    "}",
    "float fbm(vec2 p){",
    "  float s=0.0; float a=0.55;",
    "  for(int i=0;i<3;i++){ s+=a*snoise(p); p*=1.9; a*=0.5; }",
    "  return s;",
    "}",
    "void main(){",
    "  vec2 uv=v_uv;",
    "  float asp=u_res.x/max(u_res.y,1.0);",
    "  vec2 p=vec2(uv.x*asp, uv.y)*0.62;",
    "  float t=u_time*0.035;",
    "  vec2 q=vec2(fbm(p+vec2(0.0,t)), fbm(p+vec2(4.3,-t)));",
    "  vec2 r=vec2(fbm(p+q*0.5+vec2(1.7,9.2)+t*0.5), fbm(p+q*0.5+vec2(8.3,2.8)-t*0.5));",
    "  float n1=0.5+0.5*fbm(p+r*0.6+vec2(0.0,t));",
    "  float n2=0.5+0.5*fbm(p*1.15+r*0.5+vec2(3.1,-t));",
    "  float n3=0.5+0.5*snoise(p*0.7+r*0.4+vec2(-t,t));",
    "  vec3 col=mix(c1,c2,smoothstep(0.2,0.9,n1));",
    "  col=mix(col,c3,smoothstep(0.35,0.95,n2)*0.8);",
    "  col=mix(col,c4,smoothstep(0.62,1.0,n3)*0.55);",
    "  float len=length((uv-0.5)*vec2(asp,1.0));",
    "  col*=1.0-0.4*smoothstep(0.35,1.15,len);",
    "  float grain=fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453);",
    "  col+=(grain-0.5)*0.025;",
    "  gl_FragColor=vec4(col,1.0);",
    "}"
  ].join("\n");

  function hex(h) {
    h = h.replace("#", "");
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    var n = parseInt(h, 16);
    return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
  }

  function compile(gl, type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.warn("MeshGradient shader:", gl.getShaderInfoLog(s));
      return null;
    }
    return s;
  }

  function MeshGradient() {}

  MeshGradient.prototype.init = function (selector, colors) {
    var canvas = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!canvas) return this;
    var gl = canvas.getContext("webgl", { antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" }) ||
             canvas.getContext("experimental-webgl", { preserveDrawingBuffer: true });
    if (!gl) return this;
    this.canvas = canvas; this.gl = gl;

    var prog = gl.createProgram();
    var vs = compile(gl, gl.VERTEX_SHADER, VERT);
    var fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return this;
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    gl.useProgram(prog);
    this.prog = prog;

    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, "a_pos");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    this.u_time = gl.getUniformLocation(prog, "u_time");
    this.u_res = gl.getUniformLocation(prog, "u_res");
    var cs = colors && colors.length === 4 ? colors : ["#040a1a", "#1230a8", "#1e6fd9", "#47c3ff"];
    ["c1", "c2", "c3", "c4"].forEach(function (name, i) {
      gl.uniform3fv(gl.getUniformLocation(prog, name), hex(cs[i]));
    });

    var self = this;
    this._lastW = 0; this._lastH = 0;
    // The shader is a domain-warped fBm: roughly nineteen simplex-noise
    // evaluations per pixel. At device resolution on a large screen that is
    // tens of millions of evaluations per frame, which is what made the hero
    // lag. The output has no high-frequency detail — it is a soft blob field —
    // so it is drawn into a small buffer and stretched by the browser, which
    // is visually indistinguishable and costs a fraction as much. Budgeting
    // total pixels rather than a device-pixel ratio keeps a 4K monitor from
    // costing any more than a laptop.
    var MAX_PIXELS = 900 * 560;
    this._resize = function () {
      var w = canvas.clientWidth || canvas.offsetWidth || 800;
      var h = canvas.clientHeight || canvas.offsetHeight || 600;
      // Ignore mobile URL-bar height jitter: only resize on real width change
      // or a large (>140px) height change. Prevents buffer-realloc flicker.
      if (Math.abs(w - self._lastW) < 1 && Math.abs(h - self._lastH) < 140) return;
      self._lastW = w; self._lastH = h;
      var scale = Math.min(1, Math.sqrt(MAX_PIXELS / Math.max(w * h, 1)));
      canvas.width = Math.max(1, Math.floor(w * scale));
      canvas.height = Math.max(1, Math.floor(h * scale));
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(self.u_res, canvas.width, canvas.height);
    };
    this._resize();
    this._onWinResize = function () {
      if (self._rt) return;
      self._rt = setTimeout(function () { self._rt = null; self._resize(); }, 150);
    };
    window.addEventListener("resize", this._onWinResize, { passive: true });

    // Recover cleanly from GPU context loss (common on mobile) instead of
    // freezing on a corrupted frame.
    this._onLost = function (e) { e.preventDefault(); self._running = false; if (self._raf) cancelAnimationFrame(self._raf); };
    this._onRestored = function () { self.init(canvas, cs); };
    canvas.addEventListener("webglcontextlost", this._onLost, false);
    canvas.addEventListener("webglcontextrestored", this._onRestored, false);

    this._start = performance.now();
    this._running = true;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion:reduce)").matches;

    // Hold the last frame while a scroll gesture is in flight. A full-screen
    // fragment shader is the most expensive thing on the page, and during a
    // scroll the visitor is watching the page move, not a 22-second ambient
    // drift — the frame budget is better spent on the scroll itself. The clock
    // is shifted by the held duration on resume so the drift continues from
    // where it stopped rather than jumping.
    this._scrolling = false;
    this._onScrollHold = function () {
      self._scrolling = true;
      if (self._sto) clearTimeout(self._sto);
      self._sto = setTimeout(function () { self._scrolling = false; }, 150);
    };
    window.addEventListener("scroll", this._onScrollHold, { passive: true });

    // 30fps is indistinguishable for a drift this slow and halves the work.
    var FRAME_MS = 1000 / 30, lastDraw = -1e9, holdFrom = 0;
    var loop = function () {
      if (!self._running) return;
      if (reduce) {
        gl.uniform1f(self.u_time, 8.0);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        self._running = false;
        return;
      }
      var now = performance.now();
      if (self._scrolling) {
        if (!holdFrom) holdFrom = now;
        self._raf = requestAnimationFrame(loop);
        return;
      }
      if (holdFrom) { self._start += now - holdFrom; holdFrom = 0; }
      if (now - lastDraw >= FRAME_MS) {
        lastDraw = now;
        gl.uniform1f(self.u_time, (now - self._start) / 1000);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }
      self._raf = requestAnimationFrame(loop);
    };
    loop();

    // The hero is one screen tall on a long page, so without this the shader
    // keeps drawing full-resolution frames for a canvas nobody can see, for
    // most of a session. Pause when it leaves the viewport; on resume shift the
    // clock forward by the paused duration so the motion continues from where
    // it stopped instead of jumping.
    if (this._io) { this._io.disconnect(); this._io = null; }
    if (!reduce && window.IntersectionObserver) {
      this._pausedAt = 0;
      this._io = new IntersectionObserver(function (entries) {
        var visible = false;
        for (var i = 0; i < entries.length; i++) if (entries[i].isIntersecting) visible = true;
        if (visible === self._running) return;
        if (visible) {
          if (self._pausedAt) { self._start += performance.now() - self._pausedAt; self._pausedAt = 0; }
          self._running = true;
          self._raf = requestAnimationFrame(loop);
        } else {
          self._pausedAt = performance.now();
          self._running = false;
          if (self._raf) { cancelAnimationFrame(self._raf); self._raf = null; }
        }
      }, { threshold: 0 });
      this._io.observe(canvas);
    }
    return this;
  };

  MeshGradient.prototype.destroy = function () {
    this._running = false;
    if (this._io) { this._io.disconnect(); this._io = null; }
    if (this._onScrollHold) window.removeEventListener("scroll", this._onScrollHold);
    if (this._sto) { clearTimeout(this._sto); this._sto = null; }
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this._rt) { clearTimeout(this._rt); this._rt = null; }
    if (this._onWinResize) window.removeEventListener("resize", this._onWinResize);
    if (this.canvas && this._onLost) {
      this.canvas.removeEventListener("webglcontextlost", this._onLost);
      this.canvas.removeEventListener("webglcontextrestored", this._onRestored);
    }
  };

  window.MeshGradient = MeshGradient;
})();
