
// This code was written by Tyler Akins and has been placed in the
// public domain.  It would be nice if you left this header intact.
// Base64 code from Tyler Akins -- http://rumkin.com

var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=";

var curpath = document.location.pathname;
var curdir = curpath.substr(0, curpath.lastIndexOf('/')+1);

function Python(port) {
	return {
		evalpython: function evalpython(cmd, success) {
			args = JSON.stringify({
				action:'rpyceval',
				cmd:cmd,
				port:port,
			})
			callproc(args, success)
		},

		execpython: function execpython(cmd, success) {
			args = JSON.stringify({
				action:'rpycexec',
				cmd:cmd,
				port:port,
			})
			callproc(args, success)
		},

		spawnpython: function spawnpython(script, success) {
			args = JSON.stringify({
				action:'python',
				script:script,
				port:port
			})
			callproc(args, success)
		}
		
		longpoll: function longpoll() {
			function success(data) {
				setTimeout('longpoll()', 10);
			}
			args = JSON.stringify({
				action:'longpoll',
				port:port
			})
		}
	}
}

function callproc(args, success, error) {
	if (typeof(error) == 'undefined')
		error = function (data) { alert('Error making json call') }
		
	$.jsonp({
		url: 'http://localhost:21000/procs/?',
		data: {args:args, dir:curdir},
	  dataType: 'jsonp',
		callbackParameter: 'callback',
		success: success,
		error: error,
	})	
}


function spawnwait(cmd, success) {
	args = JSON.stringify({
		action:'spawn',
		cmd:cmd,
		wait:true
	})
	callproc(args, success)
}

function list(success) {
	args = JSON.stringify({
		action:'list'
	})
	callproc(args, success)
}


function spawn(cmd, success) {
	args = JSON.stringify({
		action:'spawn',
		cmd:cmd,
	})
	callproc(args, success)
}

function killproc(pid, success) {
	args = JSON.stringify({
		action:'kill',
		pid:pid
	})
	callproc(args, success)
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
