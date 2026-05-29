// Flutter Dart AOT function hook template
// Use when: Flutter app, Frida Gadget injected, need to bypass ticket/VIP/payment
// Works by: enumerating symbols in libapp.so, finding target functions, hooking returns

// ===== CONFIG =====
// Set these for each target app
var TARGET_MODULE = "libapp.so";
var HOOK_RETURN_TRUE = [
    "_hasOwnedRoomTicket",
    "_isTicketOwned",
    "_isPaidTicketStatus",
    "_isVip",
    "_isPremiumMember",
];
var HOOK_RETURN_VOID = [
    "_exitDueToTicket",
    "_pausePlaybackForTicketGate",
    "_buildTicketRequiredOverlay",
    "_buildTicketDialog",
    "_showTicketPayDialog",
    "_showTicketPurchaseSheet",
    "_buyTicketFromDialog",
    "_buyTicketFromSheet",
];

// ===== HOOK ENGINE =====
function hookReturnTrue(module, name) {
    try {
        var symbols = module.enumerateSymbols();
        for (var i = 0; i < symbols.length; i++) {
            if (symbols[i].name.indexOf(name) >= 0) {
                console.log("[+] FOUND: " + symbols[i].name);
                Interceptor.attach(symbols[i].address, {
                    onEnter: function(args) {
                        console.log("[>] " + name);
                    },
                    onLeave: function(retval) {
                        console.log("[✓] " + name + " → TRUE");
                        retval.replace(ptr(1));
                    }
                });
                return true;
            }
        }
        console.log("[-] NOT FOUND: " + name);
        return false;
    } catch(e) {
        console.log("[!] ERROR hooking " + name + ": " + e);
        return false;
    }
}

function hookReturnVoid(module, name) {
    try {
        var symbols = module.enumerateSymbols();
        for (var i = 0; i < symbols.length; i++) {
            if (symbols[i].name.indexOf(name) >= 0) {
                console.log("[+] FOUND (void): " + symbols[i].name);
                Interceptor.attach(symbols[i].address, {
                    onEnter: function(args) {
                        console.log("[BLOCK] " + name + " called → returning");
                    }
                });
                return true;
            }
        }
        return false;
    } catch(e) {
        return false;
    }
}

function hookSocketMonitor() {
    var connect = Module.findExportByName("libc.so", "connect");
    if (!connect) return;
    
    Interceptor.attach(connect, {
        onEnter: function(args) {
            var family = args[1].readU16();
            if (family === 2) {
                var port = ((args[1].readU8(2) & 0xFF) << 8) | (args[1].readU8(3) & 0xFF);
                var ipParts = [];
                for (var i = 0; i < 4; i++) ipParts.push(args[1].add(4 + i).readU8());
                console.log("[NET] connect " + ipParts.join(".") + ":" + port);
            }
        }
    });
}

// ===== MAIN =====
setTimeout(function() {
    try {
        var module = Process.getModuleByName(TARGET_MODULE);
        if (!module) {
            console.log("[!] Module " + TARGET_MODULE + " not found");
            return;
        }
        
        console.log("[*] Module: " + module.name + " base=" + module.base + " size=" + ptr(module.size));
        
        var hooked = 0;
        HOOK_RETURN_TRUE.forEach(function(name) {
            if (hookReturnTrue(module, name)) hooked++;
        });
        HOOK_RETURN_VOID.forEach(function(name) {
            if (hookReturnVoid(module, name)) hooked++;
        });
        
        console.log("[*] Hooked " + hooked + "/" + 
            (HOOK_RETURN_TRUE.length + HOOK_RETURN_VOID.length) + " functions");
        
        hookSocketMonitor();
        
    } catch(e) {
        console.log("[!] INIT ERROR: " + e);
    }
}, 3000);
