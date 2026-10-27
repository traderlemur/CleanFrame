/* 4K wallpaper. On the TV each wallpaper's packaged UHD clip plays on the video
   plane beneath a transparent web layer, paused on a still frame. The JPEG stays
   until the first frame and returns on any failure. Browsers never start it. */
(function () {
  'use strict';
  var CLIPS = {};
  (window.CleanFrameWallpapers || []).forEach(function (w) { CLIPS[w.id] = 'assets/uhd/' + w.id + '.mp4'; });
  var root = document.documentElement, api = window.webapis && window.webapis.avplay, want = null, active = null, ready = false, token = 0, surface = null, offset = [0, 0];
  // Browser checks stub window.tizen, so the user agent decides.
  function tv() { return !!window.tizen && /Tizen/.test(navigator.userAgent); }
  function reveal(on) { root.className = root.className.replace(/\s*\buhd-on\b/g, '') + (on ? ' uhd-on' : ''); }
  // AVPlay rejects negative coordinates, so the plane drifts over 0-6px, 3px right of and below the stage.
  function place() { try { api.setDisplayRect(offset[0] + 3, offset[1] + 3, 1920, 1080); } catch (e) {} }
  function stop() {
    token++;
    if (active) {
      try { api.stop(); } catch (e) {}
      try { api.close(); } catch (e) {}
    }
    active = null; ready = false; reveal(false);
  }
  // The page reports file:///index.html, so the clip path comes from the package's virtual root.
  function urls(rel) {
    var list = [], dir;
    try { list.push(window.tizen.filesystem.toURI('wgt-package/' + rel)); } catch (e) {}
    try { dir = '/opt/usr/apps/' + window.tizen.application.getAppInfo().packageId + '/res/wgt/'; list.push(dir + rel, 'file://' + dir + rel); } catch (e) {}
    return list;
  }
  function start(id) {
    var my = ++token, list = urls(CLIPS[id]), shown = false, paused = false;
    active = id;
    function bail() { if (my === token) stop(); }
    function attempt(i) {
      if (my !== token) return;
      if (i >= list.length) { bail(); return; }
      try { api.open(list[i]); } catch (e) { attempt(i + 1); return; }
      try { api.setStreamingProperty('SET_MODE_4K', 'TRUE'); } catch (e) {}
      place();
      api.setListener({
        // The first reported play time means a frame is on the plane; pause at one second to hold it.
        oncurrentplaytime: function (ms) {
          if (my !== token) return;
          if (!shown) { shown = true; reveal(true); }
          if (!paused && ms >= 1000) { paused = true; try { api.pause(); } catch (e) {} }
        },
        onerror: bail
      });
      api.prepareAsync(function () {
        if (my !== token) return;
        ready = true;
        try { api.play(); } catch (e) { bail(); }
      }, function () {
        try { api.close(); } catch (e) {}
        attempt(i + 1);
      });
    }
    if (!api) { bail(); return; }
    if (!surface) {
      surface = document.createElement('object');
      surface.type = 'application/avplayer';
      surface.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px';
      document.body.insertBefore(surface, document.body.firstChild);
    }
    attempt(0);
  }
  // Closing while hidden frees the decoder for the app being opened.
  function sync(id) {
    want = id && CLIPS[id] ? id : null;
    if (!tv()) return;
    if (document.hidden) { if (active) stop(); return; }
    if (want === active) return;
    if (active) stop();
    if (want) start(want);
  }
  // OLED drift moves the stage; the video plane follows in 1920 x 1080 coordinates.
  function move(x, y) { offset = [x, y]; if (ready) place(); }
  document.addEventListener('visibilitychange', function () { sync(want); });
  window.CleanFrameUHD = { sync: sync, move: move };
}());
