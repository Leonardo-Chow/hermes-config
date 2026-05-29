/**
 * Flutter App Frida Gadget - Template Script
 * 
 * Place this inline in libfrida-gadget.config.so's "code" field via
 * `"interaction": { "type": "script", "on_change": "reload", "code": "..." }`.
 * 
 * ⚠️ IMPORTANT — Flutter HTTP bypasses Java hooks:
 *   Dart uses its own HTTP stack (dart:io HttpClient / dio package).
 *   Java-layer hooks (OkHttp, HttpURLConnection, MethodChannel) do NOT
 *   intercept Dart HTTP requests. For API-level interception you need:
 *     a) MitM proxy (no SSL pinning + user CA installed)
 *     b) Dart AOT symbol hook (experimental, may fail on release builds)
 *     c) libc connect/send/recv hook (sees IP:port only, content encrypted)
 * 
 * What CAN be hooked at Java level (and what this script does):
 *   ✓ AlertDialog (native Android dialogs)
 *   ✓ Google Play BillingClient (query purchases, launch billing flow)
 *   ✓ Flutter MethodChannel (payment browser/channel calls)
 *   ✓ WebView (in-app web payments)
 *   ✗ Dart Widget 弹窗 (Flutter rendered, not native)
 *   ✗ Dart HTTP 请求 (to API endpoints like /live/ticket/my)
 */

Java.perform(function() {
    console.log("[Gadget] Initialized");

    // ===========================================================
    // 1. Block AlertDialog (native dialogs only — NOT Flutter widgets)
    // ===========================================================
    try {
        var AlertDialog = Java.use("android.app.AlertDialog");
        AlertDialog.show.implementation = function() {
            console.log("[Blocked] AlertDialog.show()");
            return null;
        };
        console.log("[+] AlertDialog.show blocked");
    } catch(e) { console.log("[-] AlertDialog hook failed: " + e); }

    // ===========================================================
    // 2. Block Google Play Billing UI
    // ===========================================================
    try {
        var ProxyBilling = Java.use("com.android.billingclient.api.ProxyBillingActivity");
        ProxyBilling.onCreate.implementation = function(bundle) {
            console.log("[Blocked] ProxyBillingActivity - billing UI");
            this.finish();
        };
        console.log("[+] ProxyBillingActivity blocked");
    } catch(e) { console.log("[-] ProxyBilling hook failed: " + e); }

    // ===========================================================
    // 3. Block Flutter → Java MethodChannel (payment browser etc)
    // ===========================================================
    try {
        var MethodChannel = Java.use("io.flutter.plugin.common.MethodChannel");
        MethodChannel.invokeMethod.overload('java.lang.String', 'java.lang.Object').implementation = function(method, args) {
            if (method.toLowerCase().indexOf("pay") >= 0 || 
                method.toLowerCase().indexOf("billing") >= 0) {
                console.log("[Blocked] MethodChannel: " + method);
                return null;
            }
            return this.invokeMethod(method, args);
        };
        console.log("[+] MethodChannel payment calls blocked");
    } catch(e) { console.log("[-] MethodChannel hook failed: " + e); }

    // ===========================================================
    // 4. Socket monitor — log all outbound TCP connections (IP:port)
    //    Useful for identifying API server addresses
    // ===========================================================
    try {
        var connect = Module.findExportByName("libc.so", "connect");
        if (connect) {
            Interceptor.attach(connect, {
                onEnter: function(args) {
                    try {
                        var family = args[1].readU16();
                        if (family === 2) {  // AF_INET
                            var port = ((args[1].readU8(2) & 0xFF) << 8) | (args[1].readU8(3) & 0xFF);
                            var ipBytes = [];
                            for (var i = 0; i < 4; i++) {
                                ipBytes.push(args[1].add(4 + i).readU8());
                            }
                            var ip = ipBytes.join(".");
                            // Skip local and Huawei system servers
                            if (ip.indexOf("192.168") !== 0 && ip !== "127.0.0.1") {
                                console.log("[NET] connect to " + ip + ":" + port);
                            }
                        }
                    } catch(e) {}
                }
            });
            console.log("[+] libc.connect monitored");
        }
    } catch(e) { console.log("[-] Socket monitor hook failed: " + e); }

    // ===========================================================
    // 5. Dart AOT symbol enumeration (for names in .rodata)
    //    Requires: libapp.so has functions in symbols — check with nm -D
    // ===========================================================
    setTimeout(function() {
        try {
            var module = Process.getModuleByName("libapp.so");
            var syms = module.enumerateSymbols();
            console.log("[*] libapp.so symbols: " + syms.length);
            if (syms.length > 10) {
                // Has rich symbols — unlikely for release AOT but worth checking
                console.log("[*] Symbol-rich build detected!");
                var targets = ["ticket", "vip", "pay", "owned", "dialog", "room", "live"];
                for (var i = 0; i < syms.length; i++) {
                    for (var t = 0; t < targets.length; t++) {
                        if (syms[i].name.toLowerCase().indexOf(targets[t]) >= 0) {
                            console.log("[SYM] " + syms[i].name + " @ " + syms[i].address);
                        }
                    }
                }
            }
        } catch(e) {
            console.log("[-] Dart enumeration error: " + e);
        }
    }, 3000);
});
