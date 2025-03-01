import { boot } from 'quasar/wrappers'
import { createI18n } from 'vue-i18n'
import messages from 'src/i18n'

export default boot(({ app }) => {
  const i18n = createI18n({
    locale: 'ko',
    globalInjection: true,
    messages
  })

  // Set i18n instance on app
  app.use(i18n)
})
