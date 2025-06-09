// ==UserScript==
// @name         PotDict
// @namespace    http://tampermonkey.net/
// @version      2025-06-07
// @description  A script to use with PotDict
// @author       Demons1014
// @match        *://*/*
// @match        file:///*:/*
// @icon         https://pic1.imgdb.cn/item/6844405458cb8da5c83945c3.jpg
// @grant        GM_xmlhttpRequest
// @run-at       context-menu
// ==/UserScript==

(function() {
    'use strict';
    const selected_text = window.getSelection().toString();
    console.log(`Search: ${selected_text}`)
    GM_xmlhttpRequest({
        method: "POST",
        url: `http://127.0.0.1:8080/${selected_text}`
      });
})();