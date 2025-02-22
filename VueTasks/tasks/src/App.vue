<template>
    <NavBar /> <!-- Теперь можем использовать собственный тэг -->
    <TaskList/>
</template>

<script>

import NavBar from "@/components/NavBar.vue"; // импортируем наш компонент

import TaskList from "@/components/TaskList.vue";

export default {
    name: 'App',
    components: {NavBar, TaskList} // добавляем его в список используемых
}
</script>

<style>
</style>