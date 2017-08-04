/**
 * 전역변수
 */
var username, authcode;

/**
 * 쿠키에서 AuthCode를 가져옴
 */
const getAuthCode = function () {
    username = getCookie("username");
    authcode = getCookie("authcode");
    return authcode && authcode.trim().length > 0 ? authcode : false;
};

/**
 * 쿠키에 AuthCode를 저장함
 */
const setAuthCode = function (long) {
    if (username && username.trim().length > 0)
        setCookie("username", username, long);
    if (authcode && authcode.trim().length > 0)
        setCookie("authcode", authcode, long);
};

/**
 * 쿠키에 있는 AuthCode를 비움
 */
const clearAuthCode = function () {
    setCookie("authcode", "", false);
    setCookie("username", "", false);
};

/**
 * 쿠키에서 값을 불러옴
 */
const getCookie = function (name) {
    var cookieData = document.cookie;
    var start = cookieData.indexOf(name + '=');
    var value = '';
    if (start !== -1) {
        start += name.length + 1;
        var end = cookieData.indexOf(';', start);
        if (end === -1)
            end = cookieData.length;
        value = cookieData.substring(start, end);
    }
    return value;
};

/**
 * 쿠키에 값을 저장함
 */
const setCookie = function (name, value, long) {
    var expire = new Date();
    if (long)
        expire.setDate(expire.getDate() + 30);
    else
        expire.setDate(expire.getDate() + 1);
    document.cookie = name + '=' + value + '; path=/; expires=' + expire.toGMTString() + ';';
};

/**
 * 로그인
 */
const doLogin = function () {
    username = $("#username").val();
    authcode = Base64.encode(username + ":" + $("#password").val());
    $.ajax({
        url: "/api/login/",
        type: "get",
        async: true,
        beforeSend: function (req) {
            req.setRequestHeader("Authorization", authcode);
        },
        success: function (data, type, res) {
            setAuthCode(authcode, username, $("#remember").is(":checked"));
            const r = JSON.parse(res.responseText);
            const s = '로그인에 성공하였습니다. ' +
                r["user"]["fullname"] + '님 안녕하세요! ' +
                '<a href="/' + r["user"]["app"] + '/">' + r["user"]["app"] + ' 태스크 목록</a>으로 이동합니다.';
            $("#guide").removeClass("alert-info").removeClass("alert-danger").addClass("alert-success").html(s);
            $("#username").attr("disabled", true);
            $("#password").attr("disabled", true);
            $("#signin").attr("disabled", true);
            console.log("[login.html:doLogin.ajax.success]", res.status, res.statusText, r["user"]);
            setTimeout(function () {
                window.location = '/' + r["user"]["app"] + '/';
            }, 1000);
        },
        error: function (res) {
            const s = '로그인에 실패하였습니다. 사용자 정보를 다시 확인해주세요.';
            $("#guide").removeClass("alert-info").removeClass("alert-success").addClass("alert-danger").html(s);
            console.log("[login.html:doLogin.ajax.error]", res.status, res.statusText);
        }
    });
};

/**
 * 로그아웃
 */
const doLogout = function () {
    clearAuthCode();
    window.location = "/login/";
};

/**
 *
 *  Base64 encode / decode
 *  http://www.webtoolkit.info/
 *
 **/
const Base64 = {
    // private property
    _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",

    // public method for encoding
    encode: function (input) {
        var output = "";
        var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        var i = 0;

        input = Base64._utf8_encode(input);

        while (i < input.length) {

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

            output = output +
                this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
                this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);

        }

        return output;
    },

    // public method for decoding
    decode: function (input) {
        var output = "";
        var chr1, chr2, chr3;
        var enc1, enc2, enc3, enc4;
        var i = 0;

        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

        while (i < input.length) {

            enc1 = this._keyStr.indexOf(input.charAt(i++));
            enc2 = this._keyStr.indexOf(input.charAt(i++));
            enc3 = this._keyStr.indexOf(input.charAt(i++));
            enc4 = this._keyStr.indexOf(input.charAt(i++));

            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;

            output = output + String.fromCharCode(chr1);

            if (enc3 != 64) {
                output = output + String.fromCharCode(chr2);
            }
            if (enc4 != 64) {
                output = output + String.fromCharCode(chr3);
            }

        }

        output = Base64._utf8_decode(output);

        return output;

    },

    // private method for UTF-8 encoding
    _utf8_encode: function (string) {
        string = string.replace(/\r\n/g, "\n");
        var utftext = "";

        for (var n = 0; n < string.length; n++) {

            var c = string.charCodeAt(n);

            if (c < 128) {
                utftext += String.fromCharCode(c);
            }
            else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            }
            else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }

        }

        return utftext;
    },

    // private method for UTF-8 decoding
    _utf8_decode: function (utftext) {
        var string = "";
        var i = 0;
        var c = c1 = c2 = 0;

        while (i < utftext.length) {

            c = utftext.charCodeAt(i);

            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            }
            else if ((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            }
            else {
                c2 = utftext.charCodeAt(i + 1);
                c3 = utftext.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }

        }

        return string;
    }
};
