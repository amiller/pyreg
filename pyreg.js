
// Base64 code from Tyler Akins -- http://rumkin.com
var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=";

var curpath = document.location.pathname;
var curdir = curpath.substr(0, curpath.lastIndexOf('/')+1);

if (!window.console) console = {log: function(){ }, error: function(){ }};

function output(msg) {
	window.console.error(msg)
}

function Python(port) {
	if (typeof(port) == 'undefined') port = 21000
	
	function remakews() {
		if (ws.readyState == 2)
			ws = makews()
		if (!ws.readyState)
			window.setTimeout(remakews, 500)
	}
	
	function makews() {
		var wsnew = new WebSocket("ws://localhost:" + port + "/ws/websocket");
		wsnew.onopen = function() {
			$.each(messages, function (k, v) {
				ws.send(v)
			})
			messages = []
	  };
	  wsnew.onmessage = function(e) {
			data = JSON.parse(e.data)

	    // e.data contains received string.
			if (typeof(data.push) != 'undefined')	eval(data.push)
			if (typeof(data.sendid) != 'undefined')	window[data.sendid](data)
	  };
	  wsnew.onclose = function() {
			window.setTimeout(remakews, 500)
	  };
		return wsnew
	}
	
	var messages = [];
	var ws = makews()
	var wsc = 0;
	
	function windowize(func) {
		callname = 'wscallback_' + port + '_' + wsc++;
		window[ callname ] = func
		return callname
	}
	
  // Set event handlers.
	function callproc(args, success, error) {
		if (typeof(error) == 'undefined')
			error = function (error) { output(error) }
		if (typeof(success) == 'undefined')
			success = function (){}
		
		function callback(data) {
			if (typeof(data.result) != 'undefined') success(data.result)
			else if (typeof(data.error) != 'undefined') error(data.error)
		}			
		message = JSON.stringify($.extend(args, { sendid: windowize(callback) }))
		if (ws.readyState) {
			ws.send(message)
		} else {
			messages.push(message)
		}
	}
	
	var cursor = null
	
	python = {
		ws: ws,
		eval: function eval(cmd, success) {
			args = {
				action:'eval',
				cmd:cmd,
			}
			callproc(args, success)
		},
		exec: function exec(cmd, success) {
			args = {
				action:'exec',
				cmd:cmd,
			}
			callproc(args, success)
		},
	}
	return python
}


function encode64(input) {
   var output = "";
   var chr1, chr2, chr3;
   var enc1, enc2, enc3, enc4;
   var i = 0;

   do {
      chr1 = input.charCodeAt(i++);
      chr2 = input.charCodeAt(i++);
      chr3 = input.charCodeAt(i++);

      enc1 = chr1 >> 2;
      enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
      enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
      enc4 = chr3 & 63;

      if (isNaN(chr2)) {
         enc3 = enc4 = 64;
      } else if (isNaN(chr3)) {
         enc4 = 64;
      }

      output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2) + 
         keyStr.charAt(enc3) + keyStr.charAt(enc4);
   } while (i < input.length);

   return output;
}

// Do b64 urlsafe, then remove padding equals signs
function b64pad_encode(str) {
	var b = encode64(str);
	var pad = b.indexOf("=");
	if (pad == -1) pad = 0;
	else pad = b.length - pad;
	return { 
		pad: pad,
		query: b.substr(0,b.length-pad)
	};
}

// This might be useful. Not sure right now
String.prototype.escapeHTML = function () {                                        
    return(                                                                 
        this.replace(/&/g,'&amp;').                                         
            replace(/>/g,'&gt;').                                           
            replace(/</g,'&lt;').                                           
            replace(/"/g,'&quot;')                                         
    );                                                                      
};
