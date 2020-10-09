<template>
    <div class="recent-activity__container d-flex">
        <div
            v-if="loading"
            class="recent-activity__spinner spinner-border text-danger"
            role="status"
        >
            <span class="sr-only">Loading...</span>
        </div>
        <div v-else class="list-group">
            <a
                class="d-flex justify-content-between align-items-center recent-activity__item list-group-item"
                v-bind:class="{
                    'recent_activity__item--unread':
                        post.unread || post.num_unread > 0,
                }"
                v-for="post in posts"
                :key="post.id"
                :href="post.url"
                >{{ post.title }}
                <span
                    v-if="post.num_unread > 0"
                    class="badge badge-primary badge-pill"
                    >{{ post.num_unread }}</span
                >
            </a>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Axios from 'axios';
import { DateTime } from 'luxon';

let interval_timer = null;

// Only try fetching recent posts every 10 seconds, give or take.
const refresh_interval_ms = 10000;

export default Vue.component('recent-activity', {
    data: function () {
        return {
            message: 'Hello World',
            posts: [],
            loading: true,
            unreadChanges: [],
        };
    },
    mounted: function () {
        const get_recent = () => {
            Axios.get('/v5/api/recent_activity/get?format=json').then(
                (response) => {
                    this.posts = response?.data || [];
                    for (let post of this.posts) {
                        if (localStorage.getItem(`${post.url}:interacted`)) {
                            const last_time = DateTime.fromISO(
                                localStorage.getItem(`${post.url}:interacted`)
                            );
                            const cur_time = DateTime.fromISO(post.interacted);
                            if (cur_time > last_time) {
                                post.unread = true;
                            } else {
                                post.unread = false;
                            }
                        } else {
                            post.unread = true;
                        }

                        if (
                            localStorage.getItem(`${post.url}:comments_count`)
                        ) {
                            const last_num_comments = parseInt(
                                localStorage.getItem(
                                    `${post.url}:comments_count`
                                ),
                                10
                            );
                            if (post.comments_count > last_num_comments) {
                                post.num_unread =
                                    post.comments_count - last_num_comments;
                            } else {
                                post.num_unread = 0;
                            }
                        } else {
                            post.num_unread = post.comments_count || 0;
                        }
                    }
                    this.loading = false;
                }
            );
        };
        // Do one manual fetch, and then set it on an interval
        get_recent();
        interval_timer = setInterval(get_recent, refresh_interval_ms);
    },

    destroyed: function () {
        if (interval_timer) {
            clearInterval(interval_timer);
        }
    },
});
</script>
