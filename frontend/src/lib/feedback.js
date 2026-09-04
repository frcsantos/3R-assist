import { apiFetch } from './api'

export async function submitFeedback({ url, object, feedback_text, user_id = null }) {
  return apiFetch('/feedback', {
    method: 'POST',
    body: JSON.stringify({
      url,
      object,
      feedback_text,
      user_id,
    }),
  })
}
