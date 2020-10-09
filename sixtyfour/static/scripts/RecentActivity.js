/*
    Recent Activity Widget
    =--------------------=
    Load with type="module" in the script tag: Caniuse indicates that script modules are widely
    implemented.
*/

// Remove .min from the path for development mode Vue.
// TODO: Automate all of this with build scripts or Webpack (Look into webpack-loader)
import Vue from '../vendor/vue.esm.browser.js';

// eslint-disable-next-line no-unused-vars
const app = new Vue({
    el: '#app-recent-activity',
    data: {
        message: 'Hello Vue!'
    }
})