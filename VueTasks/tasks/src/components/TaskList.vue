<script>
import AddTask from "@/components/AddTask.vue";
import TaskCard from "@/components/Task.vue";
let host = "http://localhost:3000/api"
export default {
  name: 'TaskList',
  components: {TaskCard, AddTask},
  data() {
    return {
      tasks: [],
      newTask: '',
      error: ''
    }
  },
  methods: {
    addTask(newTask) {
      this.error = '';
      fetch(`${host}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'title': newTask,
          'is_done': false
        })
      }).then(response => {
        if (!response.ok) {
          throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        return response.json();
      }).then(task => {
        this.tasks.push(task);
        newTask = '';
      }).catch(() => {
        this.error = 'Не удалось сохранить задачу.';
      });
    },
    deleteTask(id) {
      this.tasks = this.tasks.filter((t) => t.id !== id);
      fetch(`${host}/${id}/delete`, {method: 'DELETE'});
    },
    editTask(task) {
      fetch(`${host}/${task.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          title: task.title,
          is_done: task.is_done
        }),
        headers: {"Content-type": "application/json; charset=UTF-8"}
      });
    }
  },
  mounted() {
    fetch(`${host}/tasks`)
        .then(response => response.json())
        .then(tasks => {
          this.tasks = tasks;
        })
        .catch(() => {
          this.error = 'Не удалось загрузить список задач с сервера';
        });
  }
}

</script>

<template>
  <div class="container mt-4">
    <h3 class="mb-4">Список задач</h3>
    <!-- Список задач -->
    <div class="d-flex flex-wrap">
      <div v-for="task in tasks" :key="task.id">
        <TaskCard :task="task" @edit="editTask($event)" @delete="deleteTask($event)"/>
      </div>
    </div>
  </div>
  <div class="mt-4">
    <AddTask @add="addTask($event)"/>
    <!-- Сообщение об ошибке -->
    <p v-if="error" class="text-danger mt-2">{{ error }}</p>
  </div>
</template>

<style scoped>

</style>