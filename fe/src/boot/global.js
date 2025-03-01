import { boot } from 'quasar/wrappers'

// global default variable

export default boot(({ app }) => {
  app.config.globalProperties.$APP_NAME = 'ABC'
})
