<template>
  <div class="" style="margin: 70px;">
    <div class="row" style="height:100px;">
      <div class="col col-md-6" style="font-size: 25px; font-weight: bold;">
        <div style="margin-bottom: 3%;">
          연결정보 &nbsp;
          <q-btn round color="primary" icon="add" @click="addRow()" size="12px"/> &nbsp;
          <q-btn round color="secondary" icon="navigation" @click="sendInfo()" size="12px"/>
        </div>
        <template v-for="(item, index) in rows" :key="index">
          <div style="border: 1px solid black; padding: 3%;">
            <q-input outlined v-model="item.ip" label="IP" />
            <q-input outlined v-model="item.port" label="PORT" />
          </div>
          <br>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import fileService from '../services/fileService'
import { ref } from 'vue'

let rows = ref([
  {ip: '', port: '' },
])

const columns = [
  { name: 'ip', label: 'IP', align: 'center', field: 'ip', required: true },
  { name: 'port', label: 'PORT', align: 'center', field: 'port', required: true },
];


const addRow = () => {
  rows.value.push({ip: '', port: '' })
}
async function sendInfo() {
  console.log(rows.value)
  console.log(rows)
  let res = await fileService.postIpPortRe(rows.value)
  
  console.log(res);
}

</script>

<style lang="sass" scoped>

.column > div
  padding: 10px 15px
.column + .column
  margin-top: 1rem
.row > div
  padding: 10px 15px
.row + .row
  margin-top: 1rem
</style>
