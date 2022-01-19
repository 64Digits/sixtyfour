import Vue from 'vue';
import RecentActivityWidget from './features/recent_activity/RecentActivityWidget.vue';

new Vue({
    el: '#sidebar__recent-activity',
    components: {
        RecentActivityWidget,
    },
    render: (h) => h(RecentActivityWidget),
});
