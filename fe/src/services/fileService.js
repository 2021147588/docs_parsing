import { api } from '../boot/axios'

export default {
  async getOriData(fileName) {
    return api.get(`/file/getOriData/${fileName}`)
  },
  async postIpPortRe(worker_list) {
    return api.post(`/dbms/check`, worker_list)
  },
}
