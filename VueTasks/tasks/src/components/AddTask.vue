<script>
export default {
  name: "AddTask",
  data() {
    return{
      newTask: ''
    }
  },
  methods: {
    addTask(){
      this.$emit('add', this.newTask);
    }
  }
}
</script>

<template>
<div class="input-group">
      <input type="text" v-model="newTask" placeholder="Название задачи" class="form-control"/>
      <button @click="addTask" class="btn btn-primary">Добавить задачу</button>
    </div>
</template>

<style scoped>

</style>