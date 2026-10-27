# TV and verification status

Recorded through 27 October 2026. This fork runs on Evan's Samsung S90D. The upstream maintainer's Frame results are kept at the end for reference. Other models, firmware and operating systems need their own checks. Repo-only work must not contact the TV.

## Hardware and OS

| Item | This fork's TV |
| --- | --- |
| TV | Samsung 65-inch S90D OLED, QN65S90DAFXZA (not The Frame) |
| Firmware | 2130.0; firmware string T-PTMDAKUC-0090-2130.0, build T-PTMDAKUC-0090-REL-202605141701 |
| OS and architecture | Tizen 9.0.0, ARMv7 / 32-bit ARM, confirmed by developer capability and native probe |
| Native helper environment | SDK user UID 901, .NET 6.0.9 runtime and required native libraries confirmed on this TV |
| Display | App UI renders at 1920x1080 (devicePixelRatio 1); only the video plane is 4K |
| Web engine | Exact Chromium/WebKit version has not been recorded; keep runtime ES5-compatible |

Developer Mode is on: Home → Apps (top banner) → Settings at the bottom of Apps → 12345 on the keypad. Network address, device identifier, signing material and diagnostic dumps are private local configuration.

## Current app and identity

CleanFrame 0.9.0 was signed, installed in place and launched on 27 October. The SDK reported installation complete and the app is in the installed list.

- Package: `Z9MqiMW2do`
- Application: `Z9MqiMW2do.CleanFrame`
- Display name: `CleanFrame`

This fork's changes from upstream: twenty-four wallpapers (mostly Shanghai, plus New York and Tokyo) shown in 4K on the video plane, New York weather under the clock, a slow OLED pixel shift, US streaming apps (Netflix, YouTube, Disney+, HBO Max, Prime Video, Apple TV, Twitch, Hulu, Peacock), a dock ordered by most recently opened app, and no Art Mode control.

## Physically confirmed

Evan confirmed on 26 October:

- 0.6.1 looked broadly right; 0.7.1 opens apps and moves the opened app to the front of the dock.
- On 27 October: 0.8.0 shows the weather under the clock, and the nine added wallpapers look good.
- On 27 October, 4K wallpapers through AVPlay: the packaged clip opened at 3840x2160 and held a still frame. Evan saw a sharper picture with the clock, weather and dock unchanged, and no black areas or flicker. It returned after opening YouTube and after remote power off/on (standby keeps the same app process).
- Physical Home from Netflix and from YouTube opens CleanFrame.
- CleanFrame's Samsung Home action (`com.samsung.tv.csfs`) opens Samsung's normal home screen.
- Powering off with the remote after streaming, then on again, shows CleanFrame.
- After the native restore test, Home from Netflix opened Samsung Home; after reapply it opened CleanFrame again.

App IDs come from this TV's installed-app list: Netflix `org.tizen.netflix-app`, YouTube `9Ur5IzDKqV.TizenYouTube`, Disney+ `MCmYXNxgcu.DisneyPlus`, HBO Max `5b8c3eb16b.BeamCTVDev`, Prime Video `org.tizen.primevideo`, Apple TV `com.samsung.tv.aria-video`, Twitch `Jz7aUrV2Q4.Twitch`, Hulu `LBUAQX1exg.Hulu`, Peacock `gzcc4LRFBF.Peacock`. Other TVs must discover their own IDs.

## Pending checks

- A full mains power cycle (unplugged), as opposed to remote standby.
- Behaviour after a Samsung firmware update. The helper's firmware guard will refuse to run, including restore, until it is reviewed for the new firmware. Keep automatic updates off (Settings → Support → Software Update → Auto Update) so updates happen deliberately, then run `python3 scripts/native-home/run.py status`.

Browser and package checks establish source behaviour and archive contents. CPU-throttled Chromium timings are development comparisons; they are not TV benchmarks. Current browser checks are described in [testing](testing.md).

## Native Home and recovery

Native Home/startup was configured on 26 October with the guarded one-shot helper in `scripts/native-home/`, running as the SDK user. Its guards expect QN65S90DAFXZA, firmware T-PTMDAKUC-0090-2130.0 and `Z9MqiMW2do.CleanFrame`.

| Setting | Original | Applied |
| --- | --- | --- |
| Home operation (`operation/main`) | `com.samsung.tv.csfs` | `Z9MqiMW2do.CleanFrame` |
| `db/appfw/home_appid` | `com.samsung.tv.csfs` | `Z9MqiMW2do.CleanFrame` |
| `db/appfw/startup_appid` | `com.samsung.tv.csfs` | `Z9MqiMW2do.CleanFrame` (derived by the TV) |
| `db/appfw/booting_appid_backup` | `com.samsung.tv.csfs` | `Z9MqiMW2do.CleanFrame` (derived by the TV) |
| `db/first_screen/type` | `com.samsung.tv.csfs` | unchanged |
| `db/menu/smart_hub/ontvsetting/auto_start` | 1 | 1 |

The sequence was apply, readback, physical Home check, exact-value restore (readback identical to the saved original), physical Home check, then reapply with the same readback. The applied state is active.

Restore the original values before uninstalling CleanFrame or changing its identity: `python3 scripts/native-home/run.py restore`, then `query` to confirm. Use it only in an explicitly authorised TV task, with Developer Mode on. The original snapshot is private in `.local/native-home/original.json`, with a copy kept outside the project.

The helper uses undocumented native operations. Its source is in `scripts/native-home/`; compiled tools, original values and diagnostics stay private. Build it with a .NET SDK (8.0 was used) targeting `net6.0`. See [development](development.md), the [setup guide](agent-tv-setup-guide.md) and the [native helper notes](../scripts/native-home/README.md).

Implementation reference: [S90D firmware 2130 native Home work](https://github.com/splitcipher/couchroot/blob/83906b468836869933012da03a4018fb339462b3/docs/devices/s90d/README.md). It matches this TV's model family and firmware line, which is why the helper could be reused with only its guards changed.

## Upstream reference TV

The upstream maintainer's Frame (QA55LS03DAWXXY / LS03D, firmware T-PTMDUABC-0090-2130.0, app `nClrkHome1.FrameHome`) ran 0.6.1 on 20 October. Home from Netflix returned to CleanFrame after the same native change on 19 October; power-on after streaming, native Art Mode and the Samsung Home escape were still pending there.
