<template>
  <div class="flex h-full flex-col gap-8 p-8">
    <h2
      class="flex gap-2 text-xl font-semibold leading-none h-5 text-ink-gray-9"
    >
      <div>{{ __('Telephony Settings') }}</div>
      <Badge
        v-if="twilio.isDirty || exotel.isDirty || mediumChanged"
        :label="__('Not Saved')"
        variant="subtle"
        theme="orange"
      />
    </h2>
    <div
      v-if="!twilio.get.loading || !exotel.get.loading"
      class="flex-1 flex flex-col gap-8 overflow-y-auto"
    >
      <!-- General -->
      <FormControl
        type="select"
        v-model="defaultCallingMedium"
        :label="__('Default calling medium')"
        :options="[
          { label: __(''), value: '' },
          { label: __('Twilio'), value: 'Twilio' },
          { label: __('Exotel'), value: 'Exotel' },
        ]"
        class="w-1/2"
      />

      <!-- Twilio -->
      <div class="flex flex-col justify-between gap-4">
        <span class="text-base font-semibold text-ink-gray-9">
          {{ __('Twilio') }}
        </span>
        <FieldLayout
          v-if="twilio?.doc && twilioTabs"
          :tabs="twilioTabs"
          :data="twilio.doc"
          doctype="Twilio Settings"
        />
      </div>

      <!-- Exotel -->
      <div class="flex flex-col justify-between gap-4">
        <span class="text-base font-semibold text-ink-gray-9">
          {{ __('Exotel') }}
        </span>
        <FieldLayout
          v-if="exotel?.doc && exotelTabs"
          :tabs="exotelTabs"
          :data="exotel.doc"
          doctype="CRM Exotel Settings"
        />
      </div>
    </div>
    <div v-else class="flex flex-1 items-center justify-center">
      <Spinner class="size-8" />
    </div>
    <div class="flex justify-between gap-2">
      <div>
        <ErrorMessage
          class="mt-2"
          :message="twilio.save.error || exotel.save.error || error"
        />
      </div>
      <Button
        :loading="twilio.save.loading || exotel.save.loading"
        :label="__('Update')"
        variant="solid"
        @click="update"
      />
    </div>
  </div>
</template>
<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import {
  createDocumentResource,
  createResource,
  FormControl,
  Spinner,
  Badge,
  ErrorMessage,
  call,
} from 'frappe-ui'
import { defaultCallingMedium } from '@/composables/settings'
import { createToast, getRandom } from '@/utils'
import { ref, computed, watch } from 'vue'

const twilioFields = createResource({
  url: 'crm.api.doc.get_fields',
  cache: ['fields', 'Twilio Settings'],
  params: {
    doctype: 'Twilio Settings',
    allow_all_fieldtypes: true,
  },
  auto: true,
})

const exotelFields = createResource({
  url: 'crm.api.doc.get_fields',
  cache: ['fields', 'CRM Exotel Settings'],
  params: {
    doctype: 'CRM Exotel Settings',
    allow_all_fieldtypes: true,
  },
  auto: true,
})

const twilio = createDocumentResource({
  doctype: 'Twilio Settings',
  name: 'Twilio Settings',
  fields: ['*'],
  auto: true,
  setValue: {
    onSuccess: () => {
      createToast({
        title: __('Success'),
        text: __('Twilio settings updated successfully'),
        icon: 'check',
        iconClasses: 'text-ink-green-3',
      })
    },
    onError: (err) => {
      createToast({
        title: __('Error'),
        text: err.message + ': ' + err.messages[0],
        icon: 'x',
        iconClasses: 'text-ink-red-4',
      })
    },
  },
})

const exotel = createDocumentResource({
  doctype: 'CRM Exotel Settings',
  name: 'CRM Exotel Settings',
  fields: ['*'],
  auto: true,
  setValue: {
    onSuccess: () => {
      createToast({
        title: __('Success'),
        text: __('Exotel settings updated successfully'),
        icon: 'check',
        iconClasses: 'text-ink-green-3',
      })
    },
    onError: (err) => {
      createToast({
        title: __('Error'),
        text: err.message + ': ' + err.messages[0],
        icon: 'x',
        iconClasses: 'text-ink-red-4',
      })
    },
  },
})

const twilioTabs = computed(() => {
  if (!twilioFields.data) return []
  let _tabs = []
  let fieldsData = twilioFields.data

  if (fieldsData[0].type != 'Tab Break') {
    let _sections = []
    if (fieldsData[0].type != 'Section Break') {
      _sections.push({
        name: 'first_section',
        columns: [{ name: 'first_column', fields: [] }],
      })
    }
    _tabs.push({ name: 'first_tab', sections: _sections })
  }

  fieldsData.forEach((field) => {
    let last_tab = _tabs[_tabs.length - 1]
    let _sections = _tabs.length ? last_tab.sections : []
    if (field.fieldtype === 'Tab Break') {
      _tabs.push({
        label: field.label,
        name: field.fieldname,
        sections: [
          {
            name: 'section_' + getRandom(),
            columns: [{ name: 'column_' + getRandom(), fields: [] }],
          },
        ],
      })
    } else if (field.fieldtype === 'Section Break') {
      _sections.push({
        label: field.label,
        name: field.fieldname,
        hideBorder: field.hide_border,
        columns: [{ name: 'column_' + getRandom(), fields: [] }],
      })
    } else if (field.fieldtype === 'Column Break') {
      _sections[_sections.length - 1].columns.push({
        name: field.fieldname,
        fields: [],
      })
    } else {
      let last_section = _sections[_sections.length - 1]
      let last_column = last_section.columns[last_section.columns.length - 1]
      last_column.fields.push(field)
    }
  })

  return _tabs
})

const exotelTabs = computed(() => {
  if (!exotelFields.data) return []
  let _tabs = []
  let fieldsData = exotelFields.data

  if (fieldsData[0].type != 'Tab Break') {
    let _sections = []
    if (fieldsData[0].type != 'Section Break') {
      _sections.push({
        name: 'first_section',
        columns: [{ name: 'first_column', fields: [] }],
      })
    }
    _tabs.push({ name: 'first_tab', sections: _sections })
  }

  fieldsData.forEach((field) => {
    let last_tab = _tabs[_tabs.length - 1]
    let _sections = _tabs.length ? last_tab.sections : []
    if (field.fieldtype === 'Tab Break') {
      _tabs.push({
        label: field.label,
        name: field.fieldname,
        sections: [
          {
            name: 'section_' + getRandom(),
            columns: [{ name: 'column_' + getRandom(), fields: [] }],
          },
        ],
      })
    } else if (field.fieldtype === 'Section Break') {
      _sections.push({
        label: field.label,
        name: field.fieldname,
        hideBorder: field.hide_border,
        columns: [{ name: 'column_' + getRandom(), fields: [] }],
      })
    } else if (field.fieldtype === 'Column Break') {
      _sections[_sections.length - 1].columns.push({
        name: field.fieldname,
        fields: [],
      })
    } else {
      let last_section = _sections[_sections.length - 1]
      let last_column = last_section.columns[last_section.columns.length - 1]
      last_column.fields.push(field)
    }
  })

  return _tabs
})

const mediumChanged = ref(false)

watch(defaultCallingMedium, () => {
  mediumChanged.value = true
})

function update() {
  if (!validateIfDefaultMediumIsEnabled()) return
  if (mediumChanged.value) {
    updateMedium()
  }
  if (twilio.isDirty) {
    twilio.save.submit()
  }
  if (exotel.isDirty) {
    exotel.save.submit()
  }
}

async function updateMedium() {
  await call('crm.integrations.api.set_default_calling_medium', {
    medium: defaultCallingMedium.value,
  })
  mediumChanged.value = false
  error.value = ''
  createToast({
    title: __('Success'),
    text: __('Default calling medium updated successfully'),
    icon: 'check',
    iconClasses: 'text-ink-green-3',
  })
}

const error = ref('')

function validateIfDefaultMediumIsEnabled() {
  if (defaultCallingMedium.value === 'Twilio' && !twilio.doc.enabled) {
    error.value = __('Twilio is not enabled')
    return false
  }
  if (defaultCallingMedium.value === 'Exotel' && !exotel.doc.enabled) {
    error.value = __('Exotel is not enabled')
    return false
  }
  return true
}
</script>
