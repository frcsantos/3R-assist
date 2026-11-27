// Keep in sync with MAX_UPLOAD_BYTES in backend/app/services/file_text.py.
export const MAX_UPLOAD_BYTES = 15 * 1024 * 1024

// Rejects oversize files before any bytes are sent. Uses the same error code
// the backend returns, so existing FILE_TOO_LARGE handling shows the message.
export function assertUploadSize(file) {
  if (file && file.size > MAX_UPLOAD_BYTES) {
    const err = new Error('The uploaded file is too large.')
    err.code = 'FILE_TOO_LARGE'
    throw err
  }
}
