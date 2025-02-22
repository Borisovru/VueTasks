<script>
export default {
  name: "TaskCard",
  props: [
    'task'
  ],
  data() {
    return{
      ThisTask: this.task
    }
  },
  methods: {
    editTask(){
      this.$emit('edit', this.ThisTask);
    },
    deleteTask(){
      this.$emit('delete', this.ThisTask.id);
    }
  }
}
</script>

<template>
    <div :class="['task-item', { 'completed': task.is_done }]">
      <input type="checkbox" v-model="ThisTask.is_done" @change="editTask()" class="form-check-input"/>
      <input v-model="ThisTask.title" :class="{'no_border': true, 'completed-task': ThisTask.is_done}" class="form-control"/>
      <div class="task-buttons">
        <button @click="editTask()" class="btn btn-sm btn-outline-primary">Изменить</button>
        <button @click="deleteTask()" class="btn btn-sm btn-outline-danger">Удалить</button>
      </div>
    </div>
</template>

<style scoped>
    .no_border input {
      border: none;
      background: transparent;
    }
    .task-item {
      display: inline-block;
      margin-right: 10px;
      margin-bottom: 10px;
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 5px;
      width: 200px; /* Фиксированная ширина для задач */
      background-color: #f8f9fa; /* Светлый фон по умолчанию */
      transition: background-color 0.3s ease; /* Плавное изменение цвета */
    }
    .task-item.completed {
      background-color: #d4edda; /* Зеленый фон для выполненных задач */
    }
    .task-item input[type="checkbox"] {
      transform: scale(1.5); /* Увеличиваем чекбокс */
      margin-right: 10px;
    }
    .task-item input[type="text"] {
      width: 100%;
      margin-bottom: 10px;
    }
    .task-buttons {
      display: flex;
      justify-content: space-between;
    }
    .task-buttons button {
      flex: 1;
      margin: 0 2px;
    }
</style>